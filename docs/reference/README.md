# Reference Materials

This directory contains **authoritative source files** and **actual configuration files** that are referenced by the documentation but kept separate for easy access and use.

## Directory Structure

```
reference/
├── agents/                    # AI agent behavior definitions
│   ├── baseline-behaviors.md  # Authoritative LLM baseline (source)
│   └── inquisitive-agent.md  # Alternative agent personality
├── opencode/                  # OpenCode actual configuration files
│   ├── standard-config/       # Single-file configuration
│   │   ├── opencode.json
│   │   └── AGENTS.md
│   └── agent-subagent-config/ # Modular agent configuration
│       ├── opencode.json
│       ├── README.md
│       ├── agent/
│       └── prompts/
└── mcp/                       # MCP server sample configurations
    └── sample-configs/
        ├── docker-desktop-github-mcp.json
        ├── sample-docker-mcp.json
        └── sample-npx-mcp.json
```

## Purpose

### Why Separate Reference Materials?

**Documentation (`docs/tools/`, `docs/agents/`, etc.)**
- User-facing guides and tutorials
- Explanations and examples
- How-to instructions
- Conceptual information

**Reference Materials (`docs/reference/`)**
- Actual configuration files users copy
- Authoritative source files
- AI assistant technical guides
- Working code and configs

## Contents

### Agents

**[`agents/baseline-behaviors.md`](agents/baseline-behaviors.md)**
- The authoritative LLM baseline behavioral model
- Source of truth for AI assistant behavior
- Referenced by [`../agents/baseline-behaviors.md`](../agents/baseline-behaviors.md) (documentation version)

**[`agents/inquisitive-agent.md`](agents/inquisitive-agent.md)**
- Alternative agent personality focused on thorough research
- Example of customizing agent behavior

### OpenCode

**[`opencode/standard-config/`](opencode/standard-config/AGENTS.md)**
- Single-file OpenCode configuration
- `opencode.json` - Ready to copy and use
- `AGENTS.md` - Technical guide for AI assistants

**[`opencode/agent-subagent-config/`](opencode/agent-subagent-config/README.md)**
- Modular agent configuration pattern
- 13 specialized subagents in individual files
- Complete working example

### MCP

**[`mcp/sample-configs/`](mcp/sample-configs/README.md)**
- Working MCP server configuration examples
- Docker, NPX, and remote server configs
- Copy and adapt for your projects

## Usage

### For Users

**Copy configurations:**
```bash
# OpenCode standard config
cp docs/reference/opencode/standard-config/opencode.json .opencode.json

# OpenCode agent/subagent config
cp -r docs/reference/opencode/agent-subagent-config/* .

# MCP config examples
cp docs/reference/mcp/sample-configs/sample-docker-mcp.json ./mcp-config.json
```

**Reference behaviors:**
- Read `agents/baseline-behaviors.md` for AI assistant behavioral baseline
- Copy patterns from configurations
- Adapt to your specific needs

### For AI Assistants

**Read these files to understand:**
- How to behave: `agents/baseline-behaviors.md`
- Configuration structure: `opencode/*/AGENTS.md`
- Available tools: MCP sample configs

**Follow the instruction hierarchy:**
1. User directives (highest priority)
2. Project-specific rules
3. Tool-specific guidelines (AGENTS.md files here)
4. Baseline behaviors (foundation)

### For Contributors

When updating configurations:
1. Update the authoritative source in `reference/`
2. Update corresponding documentation in `docs/`
3. Ensure examples match actual configs
4. Test configurations work as documented

## Documentation Links

- **User Guides:** [`../tools/opencode/`](../tools/opencode/index.md), [`../agents/`](../agents/baseline-behaviors.md)
- **Configuration Guides:** [`../tools/opencode/configuration.md`](../tools/opencode/configuration.md)
- **MCP Documentation:** [`../mcp/overview.md`](../mcp/overview.md)
- **Getting Started:** [`../getting-started/overview.md`](../getting-started/overview.md)

---

**Note:** These are living references. They are updated as tools evolve and best practices emerge.
