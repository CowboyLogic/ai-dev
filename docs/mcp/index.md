# Model Context Protocol (MCP) Servers

Sample configurations for connecting MCP servers to OpenCode.

Model Context Protocol (MCP) extends an AI assistant with tools, data sources, and prompts
served by a separate process. For the protocol itself, see the
[official MCP documentation](https://modelcontextprotocol.io) and the
[MCP specification](https://spec.modelcontextprotocol.io).

## Sample configurations

The samples live in [`harness/opencode-samples/mcp/`](https://github.com/CowboyLogic/ai-dev/tree/main/harness/opencode-samples/mcp)
in the repository, not on this site. Each is a `.jsonc` file in the native OpenCode V2 format.

| File | Server | How it runs |
|---|---|---|
| [`sample-docker-mcp.jsonc`](https://github.com/CowboyLogic/ai-dev/blob/main/harness/opencode-samples/mcp/sample-docker-mcp.jsonc) | A placeholder container image | Local, through `docker run` |
| [`sample-npx-mcp.jsonc`](https://github.com/CowboyLogic/ai-dev/blob/main/harness/opencode-samples/mcp/sample-npx-mcp.jsonc) | Snyk security scanning | Local, through `npx` |
| [`docker-desktop-github-mcp.jsonc`](https://github.com/CowboyLogic/ai-dev/blob/main/harness/opencode-samples/mcp/docker-desktop-github-mcp.jsonc) | GitHub, from the Docker Desktop MCP Toolbox | Local, through `docker run` |

The standard OpenCode sample also configures a remote server, GitHub's hosted MCP endpoint.
See the [OpenCode overview](../harness/opencode/index.md) for that sample.

## Use a sample

1. Open the sample and copy its `mcp.servers` entry into your `opencode.json` or
   `opencode.jsonc`, under the same `mcp.servers` key.
2. Replace the image, package, and environment variable names with your own.
3. Set each environment variable the entry reads (see [Secrets](#secrets)).
4. Start `opencode` and run `opencode mcp list` to see whether the server connected.

Servers connect automatically. Add `"disabled": true` to keep one configured without
connecting it.

The field reference for local and remote servers, OAuth, and timeouts is the
[MCP servers section of the OpenCode Configuration Guide](../harness/opencode/configuration.md#mcp-servers).
It is not repeated here.

## Secrets

Never put a token in a configuration file. OpenCode substitutes `{env:NAME}` from your
shell environment, so each entry names the variable and the shell supplies the value.

```bash
# Linux and macOS
export GITHUB_TOKEN="your-token"
export SNYK_TOKEN="your-token"
```

```powershell
# Windows PowerShell
$env:GITHUB_TOKEN = "your-token"
$env:SNYK_TOKEN = "your-token"
```

> [!WARNING]
> `$NAME` and `${NAME}` are not expanded inside JSON strings. Use `{env:NAME}`. If a
> server rejects a credential that looks correct, check for shell syntax first.

Keep any file that holds a real credential out of version control.

## Running servers safely

- **Containers:** use `--rm` so containers do not accumulate, and `-i` so stdin stays open
  for the stdio transport. Do not run the container detached. Tag the image with a
  version rather than `latest` once you depend on it.
- **npx:** `-y` installs without prompting, so check that you trust the package first, and
  pin a version for reproducible runs.
- **Databases and other stateful servers:** use read-only credentials against a
  development instance. Never hand a server production credentials.
- **Permissions:** MCP tools are permission actions named `<server>_<tool>`, and an action
  no rule mentions is allowed. To deny a server's tools for an agent, add a rule such as
  `{ "action": "docker-desktop-github_*", "resource": "*", "effect": "deny" }`. V2 has no
  `tools` map.

## Troubleshooting

| Symptom | What to check |
|---|---|
| Server never connects or times out | `docker` or `npx` is installed and on `PATH`. For Docker, Docker Desktop is running and the image has been pulled. Raise `timeout.catalog` if listing tools is slow. |
| Tools are missing from the assistant | `opencode mcp list` shows the server connected. The server is not marked `"disabled": true`. Restart OpenCode after editing the config. |
| `401 Unauthorized` or similar | The environment variable is set in the shell that started OpenCode, the entry uses `{env:NAME}`, and the token has not expired and has the scopes the server needs. |
| Docker command fails | Run the same `docker run` command by hand to see the error. Check that the image name and tag exist. |
| Editor flags `mcp.servers` | The published `$schema` still describes V1. See the [warning in the Configuration Guide](../harness/opencode/configuration.md). |

## Further reading

- [OpenCode Configuration Guide](../harness/opencode/configuration.md): V2 configuration, permissions, and the MCP field reference
- [OpenCode V2 MCP documentation](https://opencode.ai/v2/docs/mcp-servers/)
- [Official MCP documentation](https://modelcontextprotocol.io)
