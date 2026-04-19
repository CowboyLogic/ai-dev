# Copilot CLI Core Configuration Reference

## config.json

**Location**: `~/.copilot/config.json` (or `$COPILOT_HOME/config.json`)

```json
{
  "trusted_folders": [
    "/home/user/projects/my-app",
    "/home/user/safe-dir"
  ]
}
```

### trusted_folders (array)

Controls where Copilot can read, modify, and execute files.

- Add a path permanently by editing this array
- During CLI startup you're prompted to trust the current directory for the session or permanently
- **Security note**: only trust directories whose contents you control

```json
{
  "trusted_folders": [
    "/home/user/projects",
    "C:\\Users\\user\\projects"
  ]
}
```

---

## Permissions (CLI flags, not config.json)

Permissions are passed as CLI flags or used as interactive slash commands. They are **not** persisted in config.json unless you add them to a shell alias or startup script.

### Tool permissions

| Flag | Effect |
|------|--------|
| `--allow-all-tools` | Skip approval for any tool |
| `--allow-tool='shell'` | Allow shell tool without prompts |
| `--allow-tool='shell(git status)'` | Allow specific command |
| `--allow-tool='MCP_SERVER_NAME'` | Allow all tools from an MCP server |
| `--allow-tool='MCP_SERVER(tool_name)'` | Allow specific MCP tool |
| `--deny-tool='shell(rm)'` | Block a specific command (takes precedence) |
| `--allow-all-tools --deny-tool='shell(rm)'` | Allow all except `rm` |

### Path permissions

| Flag | Effect |
|------|--------|
| (default) | Access to cwd, subdirectories, and system temp |
| `--allow-all-paths` | Disable all path verification |
| `--disallow-temp-dir` | Remove temp directory access |

### URL permissions

| Flag | Effect |
|------|--------|
| (default) | All URLs require approval |
| `--allow-all-urls` | Skip URL verification |
| `--allow-url=github.com` | Pre-approve a domain |
| `--deny-url=example.com` | Block a domain |

### Master override

```bash
--allow-all       # combines --allow-all-tools + --allow-all-paths + --allow-all-urls
--yolo            # alias for --allow-all
```

Interactive equivalents (during a session): `/allow-all` or `/yolo`

### Approval prompt options (during session)

1. **Allow once** — current command only
2. **Allow for session** — rest of current session
3. **Cancel** — reject, ask Claude for alternative

---

## Auth

### Credential resolution order

1. `COPILOT_GITHUB_TOKEN` env var
2. `GH_TOKEN` env var
3. `GITHUB_TOKEN` env var
4. OAuth token from system keychain
5. GitHub CLI token fallback (`gh auth status`)

### Supported token types

| Type | Prefix | Supported |
|------|--------|-----------|
| OAuth token | `gho_` | Yes |
| Fine-grained PAT | `github_pat_` | Yes (needs Copilot Requests permission) |
| GitHub App user-to-server | `ghu_` | Yes (env var only) |
| Classic PAT | `ghp_` | No |

### Keychain storage locations

| Platform | Location |
|----------|----------|
| macOS | Keychain Access (service: `copilot-cli`) |
| Windows | Credential Manager |
| Linux | libsecret (GNOME Keyring / KWallet) |
| Fallback | Plaintext in `~/.copilot/config.json` |

### Auth commands

```bash
copilot login       # OAuth device flow — opens browser
/login              # same, inside session
/logout             # removes local token
/user list          # list authenticated accounts
/user switch        # switch between accounts
```

---

## BYOK (Bring Your Own Key)

Use a custom model provider instead of GitHub-hosted models. GitHub auth becomes optional.

### Required environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `COPILOT_PROVIDER_BASE_URL` | Yes | API endpoint base URL |
| `COPILOT_MODEL` | Yes | Model identifier |
| `COPILOT_PROVIDER_API_KEY` | No* | API key (*not needed for local models like Ollama) |
| `COPILOT_PROVIDER_TYPE` | No | `openai` (default) \| `azure` \| `anthropic` |
| `COPILOT_OFFLINE` | No | `true` = disable all GitHub server contact & telemetry |

> Model must support **tool calling** and **streaming**. Recommended minimum: 128k context window.

### Provider examples

**Ollama (local, no key needed)**
```bash
export COPILOT_PROVIDER_BASE_URL=http://localhost:11434
export COPILOT_MODEL=llama3.2
```

**OpenAI**
```bash
export COPILOT_PROVIDER_BASE_URL=https://api.openai.com/v1
export COPILOT_PROVIDER_API_KEY=sk-...
export COPILOT_MODEL=gpt-4o
```

**Azure OpenAI**
```bash
export COPILOT_PROVIDER_BASE_URL=https://YOUR-RESOURCE.openai.azure.com/openai/deployments/YOUR-DEPLOYMENT
export COPILOT_PROVIDER_TYPE=azure
export COPILOT_PROVIDER_API_KEY=YOUR-KEY
export COPILOT_MODEL=YOUR-DEPLOYMENT
```

**Anthropic**
```bash
export COPILOT_PROVIDER_TYPE=anthropic
export COPILOT_PROVIDER_BASE_URL=https://api.anthropic.com
export COPILOT_PROVIDER_API_KEY=sk-ant-...
export COPILOT_MODEL=claude-opus-4-5
```

**vLLM / other OpenAI-compatible**
```bash
export COPILOT_PROVIDER_BASE_URL=http://localhost:8000/v1
export COPILOT_PROVIDER_API_KEY=your-key
export COPILOT_MODEL=meta-llama/Llama-3-8b-instruct
```

---

## Interactive slash commands (inside sessions)

| Command | Purpose |
|---------|---------|
| `/model` | Change the active model |
| `/compact` | Manually compress conversation context |
| `/context` | View token usage breakdown |
| `/mcp` | List configured MCP servers |
| `/skills list` | Show available skills |
| `/allow-all` / `/yolo` | Enable all permissions for session |
| `/login` / `/logout` | Manage authentication |
| `/feedback` | Submit feedback or bug reports |
| `/fleet` | Start multi-step implementation plan |
| `/chronicle` | View session history and analytics |
