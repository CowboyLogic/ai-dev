#!/usr/bin/env python3
"""
validate-settings.py — Validate a Claude Code settings.json file (read-only).

Usage:
    python validate-settings.py [path/to/settings.json] [--scope user|project|local|managed]

Defaults to ~/.claude/settings.json. The scope is inferred from the path when
--scope isn't given (managed-settings.json -> managed, settings.local.json ->
local, ~/.claude/settings.json -> user, other .claude/settings.json -> project)
and is used to flag keys that the file's scope can't set.

Key lists mirror https://code.claude.com/docs/en/settings-reference.md and
https://code.claude.com/docs/en/hooks.md. Refresh them during self-update.
"""
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------
VALID_DEFAULT_MODES = {"default", "manual", "acceptEdits", "plan", "auto", "dontAsk", "bypassPermissions"}
PROJECT_IGNORED_DEFAULT_MODES = {"auto", "bypassPermissions"}
VALID_EFFORT_LEVELS = {"low", "medium", "high", "xhigh"}
VALID_MAX_EFFORT_LEVELS = VALID_EFFORT_LEVELS | {"max"}

ENUMS = {
    "autoUpdatesChannel": {"latest", "stable"},
    "effortLevel": VALID_EFFORT_LEVELS,
    "maxEffortLevel": VALID_MAX_EFFORT_LEVELS,
    "viewMode": {"default", "verbose", "focus"},
    "tui": {"default", "fullscreen"},
    "editorMode": {"normal", "vim"},
    "defaultShell": {"bash", "powershell"},
    "teammateMode": {"in-process", "auto", "tmux", "iterm2"},
    "preferredNotifChannel": {"auto", "terminal_bell", "iterm2", "iterm2_with_bell",
                              "kitty", "ghostty", "notifications_disabled"},
    "feedbackDrafts": {"notify", "quiet", "off"},
    "askUserQuestionTimeout": {"60s", "5m", "10m", "never"},
    "dialogExpiry": {"60s", "5m", "10m", "never"},
    "promptCacheTtl": {"5m", "1h"},
    "subagentPromptCacheTtl": {"5m", "1h"},
    "workflowSizeGuideline": {"unrestricted", "small", "medium", "large"},
    "crossSessionInbound": {"accept", "hold", "refuse"},
    "forceLoginMethod": {"claudeai", "console", "gateway"},
    "managedSourcesBehavior": {"first-wins", "merge"},
    "parentSettingsBehavior": {"first-wins", "merge"},
    "disableAutoMode": {"disable"},
    "disableDeepLinkRegistration": {"disable"},
}
VALID_THEMES = {"auto", "dark", "light", "dark-daltonized", "light-daltonized", "dark-ansi", "light-ansi"}
VALID_TIME_FORMAT_PRESETS = {"auto", "12-hour", "24-hour", "24-hour-utc"}
VALID_SKILL_OVERRIDES = {"on", "name-only", "user-invocable-only", "off"}
VALID_HANDLER_TYPES = {"command", "http", "mcp_tool", "prompt", "agent"}
VALID_STRICT_PLUGIN_KINDS = {"skills", "agents", "hooks", "mcp"}

HOOK_EVENTS = {
    "SessionStart", "Setup", "InstructionsLoaded", "UserPromptSubmit", "UserPromptExpansion",
    "MessageDisplay", "PreToolUse", "PermissionRequest", "PostToolUse", "PostToolUseFailure",
    "PostToolBatch", "PermissionDenied", "Notification", "SubagentStart", "SubagentStop",
    "TeammateIdle", "TaskCreated", "TaskCompleted", "Stop", "StopFailure", "PreCompact",
    "PostCompact", "ConfigChange", "CwdChanged", "DirectoryAdded", "FileChanged",
    "WorktreeCreate", "WorktreeRemove", "PreModelSwitch", "PostModelSwitch", "SessionEnd",
    "Elicitation", "ElicitationResult",
}
NO_MATCHER_EVENTS = {
    "UserPromptSubmit", "PostToolBatch", "Stop", "TeammateIdle", "TaskCreated", "TaskCompleted",
    "WorktreeCreate", "WorktreeRemove", "MessageDisplay", "CwdChanged",
}
TOOL_EVENTS = {"PreToolUse", "PostToolUse", "PostToolUseFailure", "PermissionRequest", "PermissionDenied"}

# ---------------------------------------------------------------------------
# Keys by scope (Scope field of each settings-reference entry)
# ---------------------------------------------------------------------------
ANY_FILE_KEYS = {
    "advisorModel", "agent", "agentPushNotifEnabled", "allowedHttpHookUrls", "allowedMcpServers",
    "alwaysThinkingEnabled", "apiKeyHelper", "attribution", "autoCompactEnabled",
    "autoCompactWindow", "autoMemoryDirectory", "autoMemoryEnabled", "autoScrollEnabled",
    "autoUpdatesChannel", "availableModels", "awaySummaryEnabled", "awsAuthRefresh",
    "awsCredentialExport", "axScreenReader", "bashOutputMaxChars", "claudeMdExcludes",
    "cleanupPeriodDays", "companyAnnouncements", "crossSessionInbound", "defaultShell",
    "deniedMcpServers", "disableAgentView", "disableAllHooks", "disableAutoMode",
    "disableBundledSkills", "disableClaudeAiConnectors", "disableDeepLinkRegistration",
    "disableRemoteControl", "disableSkillShellExecution", "disableWorkflows",
    "disabledMcpjsonServers", "editorMode", "effortLevel", "emojiCompletionEnabled",
    "enableAllProjectMcpServers", "enableArtifact", "enableWorkflows", "enabledMcpjsonServers",
    "enabledPlugins", "enforceAvailableModels", "env", "extraKnownMarketplaces", "fallbackModel",
    "fastMode", "fastModePerSessionOptIn", "feedbackSurveyRate", "fileCheckpointingEnabled",
    "fileSuggestion", "forceLoginMethod", "forceLoginOrgUUID", "gcpAuthRefresh", "hooks",
    "httpHookAllowedEnvVars", "includeGitInstructions", "inputNeededNotifEnabled",
    "isolatePeerMachines", "language", "maxEffortLevel", "minimumVersion", "model",
    "modelOverrides", "modelSettings", "otelHeadersHelper", "outputStyle", "permissions",
    "plansDirectory", "prUrlTemplate", "preferredNotifChannel", "prefersReducedMotion",
    "promptCacheTtl", "promptSuggestionEnabled", "remote", "remoteControlAtStartup",
    "respectGitignore", "respondToBashCommands", "sandbox", "showClearContextOnPlanAccept",
    "showThinkingSummaries", "showTurnDuration", "skillListingBudgetFraction",
    "skillListingMaxDescChars", "skillOverrides", "skipWebFetchPreflight", "spinnerTipsEnabled",
    "spinnerTipsOverride", "spinnerVerbs", "statusLine", "subagentPromptCacheTtl",
    "subagentStatusLine", "switchModelsOnFlag", "syntaxHighlightingDisabled", "teammateMode",
    "terminalProgressBarEnabled", "terminalTitleFromRename", "theme", "timeFormat", "timeZone",
    "tui", "ultracode", "verbose", "viewMode", "voice", "wheelScrollAccelerationEnabled",
    "workflowKeywordTriggerEnabled", "workflowSizeGuideline", "worktree",
}
# Read only from user settings, --settings, and managed settings
USER_OR_MANAGED_KEYS = {
    "askUserQuestionTimeout", "autoContinueAtUsageLimit", "autoMode", "bashEditDiffEnabled",
    "desktopSessionCleanupPeriodDays", "dialogExpiry", "feedbackDrafts", "footerLinksRegexes",
    "modelPicker", "pluginConfigs", "processWrapper", "skipAutoPermissionPrompt", "spellcheck",
    "sshConfigs", "vimInsertModeRemaps",
}
# Read from user, local, managed (and --settings) — not from shared project settings
USER_LOCAL_OR_MANAGED_KEYS = {
    "skipDangerousModePermissionPrompt", "syncClaudeAiPlugins", "syncClaudeAiSkills",
    "useAutoModeDuringPlan",
}
MANAGED_ONLY_KEYS = {
    "allowAllClaudeAiMcps", "allowManagedHooksOnly", "allowManagedMcpServersOnly",
    "allowManagedPermissionRulesOnly", "allowedChannelPlugins", "blockedMarketplaces",
    "browserExternalPageTools", "channelsEnabled", "claudeMd", "disableBrowserExternalNavigation",
    "disableCommandPluginSources", "disableDesktopLocalSessions", "disableMobileSimulatorTools",
    "disableSideloadFlags", "forceLoginGatewayUrl", "forceRemoteSettingsRefresh",
    "gatewayInternalNetworks", "managedMcpServers", "managedSourcesBehavior", "modelPricing",
    "parentSettingsBehavior", "pluginSuggestionMarketplaces", "pluginTrustMessage", "policyHelper",
    "requiredMaximumVersion", "requiredMinimumVersion", "sshHostAllowlist",
    "strictKnownMarketplaces", "strictPluginOnlyCustomization", "wslInheritsWindowsSettings",
}
MANAGED_ONLY_SANDBOX_PATHS = {
    ("filesystem", "allowManagedReadPathsOnly"), ("network", "allowManagedDomainsOnly"),
    ("bwrapPath",), ("socatPath",),
}
USER_OR_MANAGED_SANDBOX_PATHS = {
    ("allowAppleEvents",), ("ripgrep",), ("filesystem", "disabled"),
    ("network", "strictAllowlist"), ("network", "tlsTerminate"),
    ("credentials", "allowPlaintextInject"), ("credentials", "awsPairs"), ("credentials", "sigv4"),
}

DEPRECATED_KEYS = {
    "voiceEnabled": "deprecated since v2.1.92; use voice.enabled",
    "includeCoAuthoredBy": "deprecated since v2.0.62; use attribution (ignored once attribution.commit/pr is set)",
    "disableArtifact": "deprecated; use enableArtifact: false (disableArtifact: false is ignored)",
    "keybindingFlavor": "deprecated since v2.1.261 and has no effect",
}
REMOVED_KEYS = {
    "taskOutputMaxChars": "removed in v2.1.277 with the TaskOutput tool; has no effect",
}
GLOBAL_CONFIG_ONLY_KEYS = {
    "autoConnectIde", "autoInstallIdeExtension", "copyOnSelect", "diffTool", "externalEditorContext",
}
REMOVED_GLOBAL_CONFIG_KEYS = {
    "permissionExplainerEnabled": "removed in v2.1.257",
    "teammateDefaultModel": "removed in v2.1.234",
}

KNOWN_TOP_LEVEL_KEYS = (
    {"$schema"} | ANY_FILE_KEYS | USER_OR_MANAGED_KEYS | USER_LOCAL_OR_MANAGED_KEYS
    | MANAGED_ONLY_KEYS | set(DEPRECATED_KEYS) | set(REMOVED_KEYS)
)
KNOWN_PERMISSION_KEYS = {
    "allow", "deny", "ask", "defaultMode", "additionalDirectories",
    "blockReadsOutsideWorkingDirectories", "disableBypassPermissionsMode", "disableAutoMode",
}

PERMISSION_RULE_TOOLS = {
    "Bash", "Read", "Edit", "Write", "Glob", "Grep", "WebFetch", "WebSearch", "Agent",
    "AskUserQuestion", "ExitPlanMode", "PowerShell", "Cd", "NotebookEdit", "Skill", "TaskStop",
    "Monitor", "LSP", "Artifact", "MultiEdit",
}
FILE_PATH_RULE_TOOLS_IGNORED = {"Write", "NotebookEdit", "Glob", "MultiEdit"}

errors = []
warnings = []


def err(msg):
    errors.append(f"ERROR: {msg}")


def warn(msg):
    warnings.append(f"WARNING: {msg}")


def infer_scope(path: Path) -> str:
    resolved = path.expanduser().resolve()
    if resolved.name == "managed-settings.json" or resolved.parent.name == "managed-settings.d":
        return "managed"
    if resolved.name == "settings.local.json":
        return "local"
    if resolved == (Path.home() / ".claude" / "settings.json").resolve():
        return "user"
    if resolved.name == "settings.json" and resolved.parent.name == ".claude":
        return "project"
    return "unknown"


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------
def validate_permission_rule(rule, context, list_name):
    if not isinstance(rule, str):
        err(f"{context}: rule must be a string, got {type(rule).__name__}")
        return
    tool = rule[:rule.index("(")] if "(" in rule else rule
    specifier = rule[rule.index("(") + 1:-1] if "(" in rule and rule.endswith(")") else None

    if tool.startswith("mcp__"):
        if "(" in rule:
            warn(f"{context}: '{rule}' — mcp__ rules with parentheses are skipped when loaded from settings")
        if list_name == "allow" and "*" in tool and not re.match(r"^mcp__[^*_][^*]*?__", tool):
            warn(f"{context}: allow-rule glob '{rule}' needs a literal mcp__<server>__ prefix; it will be skipped")
        return
    if any(c in tool for c in "*?"):
        if list_name == "allow":
            warn(f"{context}: tool-name glob '{rule}' is skipped in allow rules (deny/ask only)")
        return
    if tool not in PERMISSION_RULE_TOOLS:
        warn(f"{context}: unknown tool '{tool}' in rule '{rule}'")
    if specifier and tool in FILE_PATH_RULE_TOOLS_IGNORED and ":" not in specifier:
        target = "Read" if tool == "Glob" else "Edit"
        warn(f"{context}: path rule '{rule}' is never consulted; write {target}({specifier}) instead")
    if specifier and list_name == "allow" and not specifier.startswith("domain:") \
            and not specifier.rstrip().endswith(":*") and re.match(r"^\w+\s*:", specifier):
        warn(f"{context}: parameter rule '{rule}' only works in deny/ask, not allow")
    if list_name == "allow" and tool == "Bash" and specifier and re.match(r"^\S+ \*", specifier) \
            and specifier.count("*") >= 1 and not specifier.endswith(" *"):
        warn(f"{context}: '{rule}' has a wildcard before the subcommand; Claude Code warns about this at startup")


def validate_permissions(perms, path, scope):
    if not isinstance(perms, dict):
        err(f"{path}: must be an object")
        return
    for key in perms:
        if key not in KNOWN_PERMISSION_KEYS:
            warn(f"{path}.{key}: unknown permissions key")
    for key in ["allow", "deny", "ask"]:
        if key in perms:
            if not isinstance(perms[key], list):
                err(f"{path}.{key}: must be an array")
            else:
                for rule in perms[key]:
                    validate_permission_rule(rule, f"{path}.{key}", key)
    if "defaultMode" in perms:
        mode = perms["defaultMode"]
        if mode not in VALID_DEFAULT_MODES:
            err(f"{path}.defaultMode: invalid value '{mode}'. Valid: {sorted(VALID_DEFAULT_MODES)}")
        elif mode in PROJECT_IGNORED_DEFAULT_MODES and scope in {"project", "local"}:
            warn(f"{path}.defaultMode: '{mode}' doesn't take effect from {scope} settings; set it in ~/.claude/settings.json")
    if "additionalDirectories" in perms and not isinstance(perms["additionalDirectories"], list):
        err(f"{path}.additionalDirectories: must be an array")
    if "blockReadsOutsideWorkingDirectories" in perms and not isinstance(perms["blockReadsOutsideWorkingDirectories"], bool):
        err(f"{path}.blockReadsOutsideWorkingDirectories: must be a Boolean")
    for key in ["disableBypassPermissionsMode", "disableAutoMode"]:
        if key in perms and perms[key] != "disable":
            err(f'{path}.{key}: must be "disable"')


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------
def validate_hook_handler(handler, path, event):
    if not isinstance(handler, dict):
        err(f"{path}: must be an object")
        return
    htype = handler.get("type")
    if not htype:
        err(f"{path}: missing required 'type' field")
        return
    if htype not in VALID_HANDLER_TYPES:
        err(f"{path}.type: invalid value '{htype}'. Valid: {' | '.join(sorted(VALID_HANDLER_TYPES))}")
    if htype == "command" and "command" not in handler:
        err(f"{path}: command type requires 'command' field")
    if htype == "command" and "args" in handler and not isinstance(handler["args"], list):
        err(f"{path}.args: must be an array (exec form)")
    if htype == "command" and handler.get("shell") not in (None, "bash", "powershell"):
        err(f"{path}.shell: must be \"bash\" or \"powershell\"")
    if htype == "http" and "url" not in handler:
        err(f"{path}: http type requires 'url' field")
    if htype in {"prompt", "agent"} and "prompt" not in handler:
        err(f"{path}: {htype} type requires 'prompt' field")
    if htype == "mcp_tool":
        for req in ("server", "tool"):
            if req not in handler:
                err(f"{path}: mcp_tool type requires '{req}' field")
        if event == "Setup":
            warn(f"{path}: mcp_tool hooks are always skipped on Setup")
    if "if" in handler and event not in TOOL_EVENTS:
        warn(f"{path}.if: 'if' is only evaluated on tool events; this handler will never run on {event}")
    if "timeout" in handler and not isinstance(handler["timeout"], (int, float)):
        err(f"{path}.timeout: must be a number of seconds")
    if handler.get("once") is not None:
        warn(f"{path}.once: only honored in skill frontmatter; ignored in settings files")
    if "suppressOutput" in handler:
        warn(f"{path}.suppressOutput: not a handler field (it's a JSON output field, and has no effect)")


def validate_hooks(hooks, path):
    if not isinstance(hooks, dict):
        err(f"{path}: must be an object")
        return
    for event, groups in hooks.items():
        if event not in HOOK_EVENTS:
            warn(f"{path}.{event}: unknown hook event")
        if not isinstance(groups, list):
            err(f"{path}.{event}: must be an array of matcher groups")
            continue
        for i, group in enumerate(groups):
            gpath = f"{path}.{event}[{i}]"
            if not isinstance(group, dict):
                err(f"{gpath}: must be an object with 'hooks' array")
                continue
            matcher = group.get("matcher")
            if matcher not in (None, "", "*") and event in NO_MATCHER_EVENTS:
                warn(f"{gpath}.matcher: {event} doesn't support matchers; it is silently ignored")
            if isinstance(matcher, str) and re.fullmatch(r"mcp__[A-Za-z0-9_-]+", matcher):
                warn(f"{gpath}.matcher: '{matcher}' is an exact string and matches no tool; use '{matcher}__.*'")
            if "hooks" not in group:
                err(f"{gpath}: missing required 'hooks' array")
            elif not isinstance(group["hooks"], list):
                err(f"{gpath}.hooks: must be an array")
            else:
                for j, h in enumerate(group["hooks"]):
                    validate_hook_handler(h, f"{gpath}.hooks[{j}]", event)


# ---------------------------------------------------------------------------
# Sandbox
# ---------------------------------------------------------------------------
def dig(obj, keys):
    for k in keys:
        if not isinstance(obj, dict) or k not in obj:
            return None
        obj = obj[k]
    return obj


def validate_sandbox(sb, scope):
    if not isinstance(sb, dict):
        err("sandbox: must be an object")
        return
    for keys in MANAGED_ONLY_SANDBOX_PATHS:
        if dig(sb, keys) is not None and scope not in {"managed", "unknown"}:
            warn(f"sandbox.{'.'.join(keys)}: managed-only; ignored in {scope} settings")
    for keys in USER_OR_MANAGED_SANDBOX_PATHS:
        if dig(sb, keys) is not None and scope in {"project", "local"}:
            warn(f"sandbox.{'.'.join(keys)}: user-or-managed only; ignored in {scope} settings")
    creds = sb.get("credentials", {})
    if isinstance(creds, dict):
        for lst in ("files", "envVars"):
            for idx, entry in enumerate(creds.get(lst, []) or []):
                if isinstance(entry, dict) and entry.get("mode") not in ("deny", "mask"):
                    err(f"sandbox.credentials.{lst}[{idx}].mode: must be \"deny\" or \"mask\"")
                elif isinstance(entry, dict) and entry.get("mode") == "mask" and scope in {"project", "local"}:
                    warn(f"sandbox.credentials.{lst}[{idx}]: mask entries are dropped from {scope} settings")
        sig = creds.get("sigv4")
        if isinstance(sig, dict):
            for k, v in sig.items():
                if k not in ("streaming", "presigned", "sigv4a"):
                    warn(f"sandbox.credentials.sigv4.{k}: unknown field")
                elif v not in ("deny", "passthrough"):
                    err(f"sandbox.credentials.sigv4.{k}: must be \"deny\" or \"passthrough\"")


# ---------------------------------------------------------------------------
# Top level
# ---------------------------------------------------------------------------
def validate(data, scope):
    if not isinstance(data, dict):
        err("Top-level value must be a JSON object")
        return

    for key in sorted(set(data) - KNOWN_TOP_LEVEL_KEYS - GLOBAL_CONFIG_ONLY_KEYS - set(REMOVED_GLOBAL_CONFIG_KEYS)):
        if key == "mcpServers":
            continue
        warn(f"Unknown top-level key: '{key}' (may be new or custom)")

    for key, msg in DEPRECATED_KEYS.items():
        if key in data:
            warn(f"'{key}' is {msg}")
    for key, msg in REMOVED_KEYS.items():
        if key in data:
            warn(f"'{key}' was {msg}")
    for key in GLOBAL_CONFIG_ONLY_KEYS:
        if key in data:
            warn(f"'{key}' belongs in ~/.claude.json (global config), not settings.json")
    for key, msg in REMOVED_GLOBAL_CONFIG_KEYS.items():
        if key in data:
            warn(f"'{key}' is a ~/.claude.json key that was {msg}; it has no effect")

    if scope not in {"managed", "unknown"}:
        for key in sorted(MANAGED_ONLY_KEYS & set(data)):
            warn(f"'{key}' is managed-only; ignored in {scope} settings")
    if scope in {"project", "local"}:
        for key in sorted(USER_OR_MANAGED_KEYS & set(data)):
            warn(f"'{key}' is read only from user/managed/--settings; ignored in {scope} settings")
    if scope == "project":
        for key in sorted(USER_LOCAL_OR_MANAGED_KEYS & set(data)):
            warn(f"'{key}' is ignored in shared project settings (.claude/settings.json)")

    if "permissions" in data:
        validate_permissions(data["permissions"], "permissions", scope)
    if "hooks" in data:
        validate_hooks(data["hooks"], "hooks")
    if "sandbox" in data:
        validate_sandbox(data["sandbox"], scope)

    for key, valid in ENUMS.items():
        if key in data and data[key] not in valid:
            err(f"{key}: invalid value {data[key]!r}. Valid: {sorted(valid)}")

    if "theme" in data:
        t = data["theme"]
        if not isinstance(t, str) or (t not in VALID_THEMES and not t.startswith("custom:")):
            err(f"theme: invalid value {t!r}. Valid: {sorted(VALID_THEMES)} or 'custom:<slug>'")

    if "timeFormat" in data:
        tf = data["timeFormat"]
        if not isinstance(tf, str) or (tf not in VALID_TIME_FORMAT_PRESETS and "%" not in tf):
            err(f"timeFormat: {tf!r} is neither a preset {sorted(VALID_TIME_FORMAT_PRESETS)} nor a strftime pattern")

    if "modelSettings" in data:
        ms = data["modelSettings"]
        if not isinstance(ms, dict):
            err("modelSettings: must be an object keyed by model name")
        else:
            for model, entry in ms.items():
                if not isinstance(entry, dict):
                    err(f"modelSettings.{model}: must be an object")
                    continue
                if "effortLevel" in entry and entry["effortLevel"] not in VALID_EFFORT_LEVELS:
                    err(f"modelSettings.{model}.effortLevel: invalid value {entry['effortLevel']!r}")
                if "maxEffortLevel" in entry and entry["maxEffortLevel"] not in VALID_MAX_EFFORT_LEVELS:
                    err(f"modelSettings.{model}.maxEffortLevel: invalid value {entry['maxEffortLevel']!r}")

    if "autoMode" in data:
        am = data["autoMode"]
        if not isinstance(am, dict):
            err("autoMode: must be an object")
        else:
            for k, v in am.items():
                if k in ("environment", "allow", "soft_deny", "hard_deny"):
                    if not isinstance(v, list):
                        err(f"autoMode.{k}: must be an array of strings")
                    elif k != "environment" and "$defaults" not in v:
                        warn(f"autoMode.{k}: no \"$defaults\" entry — this replaces the built-in {k} rules")
                elif k == "classifyAllShell":
                    if not isinstance(v, bool):
                        err("autoMode.classifyAllShell: must be a Boolean")
                else:
                    warn(f"autoMode.{k}: unknown field")

    if "attribution" in data:
        a = data["attribution"]
        if a is False:
            warn("attribution: false requires Claude Code v2.1.281+; older versions skip the whole settings file")
        elif not isinstance(a, dict):
            err("attribution: must be an object or false")
        else:
            for k in a:
                if k not in ("commit", "pr", "sessionUrl"):
                    warn(f"attribution.{k}: unknown field")

    if "voice" in data:
        v = data["voice"]
        if not isinstance(v, dict):
            err("voice: must be an object")
        else:
            if v.get("mode") not in (None, "hold", "tap"):
                err(f"voice.mode: invalid value {v.get('mode')!r}. Valid: hold | tap")
            if v.get("autoSubmit") and v.get("mode") == "tap":
                warn("voice.autoSubmit applies in hold mode only; it has no effect with mode \"tap\"")

    if "skillOverrides" in data and isinstance(data["skillOverrides"], dict):
        for name, val in data["skillOverrides"].items():
            if val not in VALID_SKILL_OVERRIDES:
                err(f"skillOverrides.{name}: invalid value {val!r}. Valid: {sorted(VALID_SKILL_OVERRIDES)}")

    if "strictPluginOnlyCustomization" in data:
        v = data["strictPluginOnlyCustomization"]
        if not (v is True or (isinstance(v, list) and set(v) <= VALID_STRICT_PLUGIN_KINDS)):
            err(f"strictPluginOnlyCustomization: must be true or a subset of {sorted(VALID_STRICT_PLUGIN_KINDS)}")

    if "worktree" in data and isinstance(data["worktree"], dict):
        wt = data["worktree"]
        if wt.get("baseRef") not in (None, "fresh", "head"):
            err("worktree.baseRef: must be \"fresh\" or \"head\"")
        if wt.get("bgIsolation") not in (None, "worktree", "none"):
            err("worktree.bgIsolation: must be \"worktree\" or \"none\"")

    for key in ("statusLine", "subagentStatusLine", "fileSuggestion"):
        if key in data:
            v = data[key]
            if not isinstance(v, dict) or v.get("type") != "command" or "command" not in v:
                err(f"{key}: must be {{\"type\": \"command\", \"command\": \"...\"}}")

    if "footerLinksRegexes" in data and isinstance(data["footerLinksRegexes"], list):
        for idx, entry in enumerate(data["footerLinksRegexes"]):
            if isinstance(entry, dict) and entry.get("type") != "regex":
                warn(f"footerLinksRegexes[{idx}]: entries take \"type\": \"regex\"")

    if "cleanupPeriodDays" in data:
        v = data["cleanupPeriodDays"]
        if not isinstance(v, int) or isinstance(v, bool) or v < 1:
            err(f"cleanupPeriodDays: must be an integer >= 1, got {v!r}")

    if "feedbackSurveyRate" in data:
        v = data["feedbackSurveyRate"]
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not (0 <= v <= 1):
            err(f"feedbackSurveyRate: must be a number between 0 and 1, got {v!r}")

    if "autoCompactWindow" in data:
        v = data["autoCompactWindow"]
        if not isinstance(v, int) or isinstance(v, bool) or not (100000 <= v <= 1000000):
            err(f"autoCompactWindow: must be an integer from 100000 to 1000000, got {v!r}")

    if "bashOutputMaxChars" in data:
        v = data["bashOutputMaxChars"]
        if not isinstance(v, int) or isinstance(v, bool) or v < 1:
            err(f"bashOutputMaxChars: must be a positive integer, got {v!r}")
        elif not (4000 <= v <= 128000):
            warn(f"bashOutputMaxChars: {v} is clamped into 4000..128000")

    if "skillListingBudgetFraction" in data:
        v = data["skillListingBudgetFraction"]
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not (0 < v <= 1):
            err(f"skillListingBudgetFraction: must be > 0 and <= 1, got {v!r}")

    if "fallbackModel" in data:
        v = data["fallbackModel"]
        if not isinstance(v, list):
            err("fallbackModel: must be an array of model aliases or IDs")
        elif len(set(v)) > 3:
            warn("fallbackModel: only the first three distinct allowed models are used")

    if "env" in data:
        if not isinstance(data["env"], dict):
            err("env: must be an object (key-value pairs)")
        else:
            for k, v in data["env"].items():
                if not isinstance(v, str):
                    err(f"env.{k}: value must be a string, got {type(v).__name__}")

    if "mcpServers" in data:
        warn("mcpServers: MCP servers belong in ~/.claude.json or .mcp.json, not settings.json")


def main():
    args = sys.argv[1:]
    scope = None
    if "--scope" in args:
        idx = args.index("--scope")
        if idx + 1 >= len(args) or args[idx + 1] not in {"user", "project", "local", "managed"}:
            print("ERROR: --scope requires one of: user, project, local, managed")
            return 2
        scope = args[idx + 1]
        del args[idx:idx + 2]
    path = Path(args[0]).expanduser() if args else Path.home() / ".claude" / "settings.json"
    scope = scope or infer_scope(path)

    print(f"Validating: {path} (scope: {scope})")

    if not path.exists():
        print(f"File not found: {path}")
        print("No settings file exists yet — that's fine, defaults apply.")
        return 0

    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"FATAL: Invalid JSON: {e}")
        return 1

    validate(data, scope)

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
