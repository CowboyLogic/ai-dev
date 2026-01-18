#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import * as fs from 'fs/promises';
import * as path from 'path';

const server = new Server({
  name: 'file-system-agent',
  version: '1.0.0'
}, {
  capabilities: {
    tools: {
      'read-file': {
        description: 'Read the contents of a file',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Absolute or relative path to the file to read'
            },
            encoding: {
              type: 'string',
              description: 'File encoding (default: utf-8)',
              default: 'utf-8'
            }
          },
          required: ['path']
        }
      },
      'write-file': {
        description: 'Write content to a file',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Absolute or relative path to the file to write'
            },
            content: {
              type: 'string',
              description: 'Content to write to the file'
            },
            encoding: {
              type: 'string',
              description: 'File encoding (default: utf-8)',
              default: 'utf-8'
            }
          },
          required: ['path', 'content']
        }
      },
      'list-directory': {
        description: 'List contents of a directory',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Absolute or relative path to the directory to list',
              default: '.'
            }
          }
        }
      },
      'create-directory': {
        description: 'Create a new directory',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Absolute or relative path for the new directory'
            },
            recursive: {
              type: 'boolean',
              description: 'Create parent directories if they don\'t exist',
              default: false
            }
          },
          required: ['path']
        }
      },
      'delete-file': {
        description: 'Delete a file or directory',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Absolute or relative path to the file/directory to delete'
            },
            recursive: {
              type: 'boolean',
              description: 'Delete directories recursively',
              default: false
            }
          },
          required: ['path']
        }
      },
      'file-info': {
        description: 'Get information about a file or directory',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Absolute or relative path to check'
            }
          },
          required: ['path']
        }
      }
    },
    resources: {
      'file:///*': {
        description: 'Access to local files',
        mimeType: 'text/plain'
      }
    }
  }
});

// Tool handlers
server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'read-file':
        const content = await fs.readFile(args.path, args.encoding || 'utf-8');
        return {
          content: [{ type: 'text', text: content.toString() }]
        };

      case 'write-file':
        await fs.writeFile(args.path, args.content, args.encoding || 'utf-8');
        return {
          content: [{ type: 'text', text: `Successfully wrote to ${args.path}` }]
        };

      case 'list-directory':
        const dirPath = args.path || '.';
        const entries = await fs.readdir(dirPath, { withFileTypes: true });
        const formatted = entries.map(entry => ({
          name: entry.name,
          type: entry.isDirectory() ? 'directory' : 'file',
          path: path.join(dirPath, entry.name)
        }));
        return {
          content: [{ type: 'text', text: JSON.stringify(formatted, null, 2) }]
        };

      case 'create-directory':
        await fs.mkdir(args.path, { recursive: args.recursive || false });
        return {
          content: [{ type: 'text', text: `Created directory: ${args.path}` }]
        };

      case 'delete-file':
        const stat = await fs.stat(args.path);
        if (stat.isDirectory()) {
          await fs.rmdir(args.path, { recursive: args.recursive || false });
        } else {
          await fs.unlink(args.path);
        }
        return {
          content: [{ type: 'text', text: `Deleted: ${args.path}` }]
        };

      case 'file-info':
        const stats = await fs.stat(args.path);
        const info = {
          path: args.path,
          size: stats.size,
          isDirectory: stats.isDirectory(),
          isFile: stats.isFile(),
          created: stats.birthtime.toISOString(),
          modified: stats.mtime.toISOString(),
          permissions: stats.mode.toString(8)
        };
        return {
          content: [{ type: 'text', text: JSON.stringify(info, null, 2) }]
        };

      default:
        return {
          content: [{ type: 'text', text: `Unknown tool: ${name}` }],
          isError: true
        };
    }
  } catch (error) {
    return {
      content: [{ type: 'text', text: `Error: ${error.message}` }],
      isError: true
    };
  }
});

// Resource handler
server.setRequestHandler('resources/read', async (request) => {
  const { uri } = request.params;

  if (!uri.startsWith('file://')) {
    throw new Error('Only file:// URIs are supported');
  }

  const filePath = uri.replace('file://', '');
  try {
    const content = await fs.readFile(filePath, 'utf-8');
    return {
      contents: [{
        uri,
        mimeType: 'text/plain',
        text: content
      }]
    };
  } catch (error) {
    throw new Error(`Failed to read file: ${error.message}`);
  }
});

// Start the server
const transport = new StdioServerTransport();
server.connect(transport).catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});

console.error('File System Agent MCP server started');