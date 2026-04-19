#!/usr/bin/env python3
"""
validate-settings.py — Validate ~/.claude/settings.json structure.
Usage: python validate-settings.py [path/to/settings.json]
"""
import json
import sys
from pathlib import Path

VALID_DEFAULT_MODES = {"default", "acceptEdits", "plan", "auto", "dontAsk", "bypassPermissions"}
VALID_UPDATE_CHANNELS = {"latest", "stable"}
VALID_EFFORT_LEVELS = {"low", "medium", "high", "xhigh"}
VALID_VIEW_MODES = {"default", "verbose", "focus"}
VALID_TUI = {"default", "fullscreen"}

KNOWN_TOP_LEVEL_KEYS = {
    "agent", "alwaysThinkingEnabled", "apiKeyHelper", "attribution",
    "autoMemoryDirectory", "autoMode", "autoUpdatesChannel", "availableModels",
    "awaySummaryEnabled", "awsAuthRefresh", "awsCredentialExport",
    "cleanupPeriodDays", "companyAnnouncements", "defaultShell",
    "disableAllHooks", "disableAutoMode", "disableDeepLinkRegistration",
    "disabledMcpjsonServers", "disableSkillShellExecution", "effortLevel",
    "enableAllProjectMcpServers", "enabledMcpjsonServers", "enabledPlugins",
    "env", "fastModePerSessionOptIn", "feedbackSurveyRate", "fileSuggestion",
    "forceLoginMethod", "forceLoginOrgUUID", "hooks", "httpHookAllowedEnvVars",
    "includeCoAuthoredBy", "includeGitInstructions", "language",
    "minimumVersion", "model", "modelOverrides", "otelHeadersHelper",
    "outputStyle", "permissions", "plansDirectory", "prefersReducedMotion",
    "respectGitignore", "sandbox", "showClearContextOnPlanAccept",
    "showThinkingSummaries", "spinnerTipsEnabled", "spinnerTipsOverride",
    "spinnerVerbs", "statusLine", "tui", "useAutoModeDuringPlan",
    "viewMode", "voiceEnabled", "worktree", "allowedHttpHookUrls",
    "allowedMcpServers", "allowManagedHooksOnly", "allowManagedMcpServersOnly",
    "allowManagedPermissionRulesOnly", "blockedMarketplaces", "channelsEnabled",
    "companyAnnouncements", "deniedMcpServers", "feedbackSurveyRate",
    "forceRemoteSettingsRefresh", "pluginTrustMessage", "strictKnownMarketplaces",
    "allowedChannelPlugins", "httpHookAllowedEnvVars", "$schema",
    "autoConnectIde", "autoScrollEnabled", "editorMode", "externalEditorContext",
    "showTurnDuration", "terminalProgressBarEnabled", "teammateMode",
    "autoInstallIdeExtension",
}

GLOBAL_CONFIG_ONLY_KEYS = {
    "autoConnectIde", "autoInstallIdeExtension", "autoScrollEnabled",
    "editorMode", "externalEditorContext", "showTurnDuration",
    "terminalProgressBarEnabled", "teammateMode",
}

PERMISSION_RULE_TOOLS = {
    "Bash", "Read", "Edit", "Write", "Glob", "Grep", "WebFetch", "WebSearch",
    "Agent", "AskUserQuestion", "ExitPlanMode", "mcp__",
}

errors = []
warnings = []

def err(msg): errors.append(f"ERROR: {msg}")
def warn(msg): warnings.append(f"WARNING: {msg}")

def validate_permission_rule(rule, context):
    if not isinstance(rule, str):
        err(f"{context}: rule must be a string, got {type(rule).__name__}")
        return
    if "(" in rule:
        tool = rule[:rule.index("(")]
    else:
        tool = rule
    known = any(tool == t or tool.startswith("mcp__") for t in PERMISSION_RULE_TOOLS)
    if not known and not tool.startswith("mcp__"):
        warn(f"{context}: unknown tool '{tool}' in rule '{rule}'")

def validate_permissions(perms, path):
    if not isinstance(perms, dict):
        err(f"{path}: must be an object")
        return
    for key in ["allow", "deny", "ask"]:
        if key in perms:
            if not isinstance(perms[key], list):
                err(f"{path}.{key}: must be an array")
            else:
                for rule in perms[key]:
                    validate_permission_rule(rule, f"{path}.{key}")
    if "defaultMode" in perms:
        mode = perms["defaultMode"]
        if mode not in VALID_DEFAULT_MODES:
            err(f"{path}.defaultMode: invalid value '{mode}'. Valid: {sorted(VALID_DEFAULT_MODES)}")
    if "additionalDirectories" in perms:
        if not isinstance(perms["additionalDirectories"], list):
            err(f"{path}.additionalDirectories: must be an array")
    if "disableBypassPermissionsMode" in perms:
        if perms["disableBypassPermissionsMode"] != "disable":
            err(f'{path}.disableBypassPermissionsMode: must be "disable"')

def validate_hook_handler(handler, path):
    if not isinstance(handler, dict):
        err(f"{path}: must be an object")
        return
    htype = handler.get("type")
    if not htype:
        err(f"{path}: missing required 'type' field")
        return
    if htype not in {"command", "http", "prompt", "agent"}:
        err(f"{path}.type: invalid value '{htype}'. Valid: command | http | prompt | agent")
    if htype == "command" and "command" not in handler:
        err(f"{path}: command type requires 'command' field")
    if htype == "http" and "url" not in handler:
        err(f"{path}: http type requires 'url' field")
    if htype in {"prompt", "agent"} and "prompt" not in handler:
        err(f"{path}: {htype} type requires 'prompt' field")

def validate_hooks(hooks, path):
    if not isinstance(hooks, dict):
        err(f"{path}: must be an object")
        return
    for event, groups in hooks.items():
        if not isinstance(groups, list):
            err(f"{path}.{event}: must be an array of matcher groups")
            continue
        for i, group in enumerate(groups):
            gpath = f"{path}.{event}[{i}]"
            if not isinstance(group, dict):
                err(f"{gpath}: must be an object with 'hooks' array")
                continue
            if "hooks" not in group:
                err(f"{gpath}: missing required 'hooks' array")
            else:
                for j, h in enumerate(group["hooks"]):
                    validate_hook_handler(h, f"{gpath}.hooks[{j}]")

def validate(data):
    if not isinstance(data, dict):
        err("Top-level value must be a JSON object")
        return

    unknown = set(data.keys()) - KNOWN_TOP_LEVEL_KEYS
    for key in sorted(unknown):
        warn(f"Unknown top-level key: '{key}' (may be new or custom)")

    for key in GLOBAL_CONFIG_ONLY_KEYS:
        if key in data:
            warn(f"'{key}' belongs in ~/.claude.json (global config), not settings.json. It will be ignored here.")

    if "permissions" in data:
        validate_permissions(data["permissions"], "permissions")

    if "hooks" in data:
        validate_hooks(data["hooks"], "hooks")

    if "autoUpdatesChannel" in data:
        ch = data["autoUpdatesChannel"]
        if ch not in VALID_UPDATE_CHANNELS:
            err(f"autoUpdatesChannel: invalid value '{ch}'. Valid: {VALID_UPDATE_CHANNELS}")

    if "effortLevel" in data:
        el = data["effortLevel"]
        if el not in VALID_EFFORT_LEVELS:
            err(f"effortLevel: invalid value '{el}'. Valid: {VALID_EFFORT_LEVELS}")

    if "viewMode" in data:
        vm = data["viewMode"]
        if vm not in VALID_VIEW_MODES:
            err(f"viewMode: invalid value '{vm}'. Valid: {VALID_VIEW_MODES}")

    if "tui" in data:
        t = data["tui"]
        if t not in VALID_TUI:
            err(f"tui: invalid value '{t}'. Valid: {VALID_TUI}")

    if "cleanupPeriodDays" in data:
        v = data["cleanupPeriodDays"]
        if not isinstance(v, int) or v < 1:
            err(f"cleanupPeriodDays: must be an integer >= 1, got {v!r}")

    if "feedbackSurveyRate" in data:
        v = data["feedbackSurveyRate"]
        if not isinstance(v, (int, float)) or not (0 <= v <= 1):
            err(f"feedbackSurveyRate: must be a number between 0 and 1, got {v!r}")

    if "env" in data:
        if not isinstance(data["env"], dict):
            err("env: must be an object (key-value pairs)")
        else:
            for k, v in data["env"].items():
                if not isinstance(v, str):
                    err(f"env.{k}: value must be a string, got {type(v).__name__}")

    if "mcpServers" in data:
        warn("mcpServers: MCP servers should be in ~/.claude.json, not settings.json")

def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".claude" / "settings.json"

    print(f"Validating: {path}")

    if not path.exists():
        print(f"File not found: {path}")
        print("No settings.json exists yet — that's fine, defaults apply.")
        return 0

    try:
        with open(path) as f:
            content = f.read()
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"FATAL: Invalid JSON: {e}")
        return 1

    validate(data)

    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  {e}")
    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  {w}")
    if not errors and not warnings:
        print("OK — no issues found.")
    elif not errors:
        print(f"\nOK with {len(warnings)} warning(s).")

    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
