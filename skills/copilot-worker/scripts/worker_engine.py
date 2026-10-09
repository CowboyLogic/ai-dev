#!/usr/bin/env python3
"""Drive one GitHub Copilot SDK session for the copilot-worker supervisor.

The policy in this module is pure and imports nothing from the SDK, so it can be
tested on its own. Only the driver imports the SDK.
"""

from __future__ import annotations

import asyncio
import base64
import binascii
import json
import ntpath
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any

WINDOWS = os.name == "nt"
READ_TOOLS = ("view", "rg", "glob")
# The runtime's shell is bash on macOS and Linux, and PowerShell on Windows: pwsh.exe when
# it is installed, otherwise Windows PowerShell.
SHELL_TOOLS = {
    False: ("bash", "read_bash", "stop_bash", "list_bash"),
    True: ("powershell", "read_powershell", "stop_powershell", "list_powershell"),
}


def tools_for(windows: bool) -> dict[str, tuple[str, ...]]:
    return {
        "research": READ_TOOLS,
        "review": READ_TOOLS,
        "implement": (*READ_TOOLS, "apply_patch", *SHELL_TOOLS[windows]),
    }


TOOLS = tools_for(WINDOWS)
# The SDK and the Copilot runtime it downloads this skill is built against. The runtime is
# not chosen here: each SDK release carries its own, so the two move together.
PINS_FILE = Path(__file__).with_name("pins.json")
# The supervisor enforces the real timeout. This margin keeps the SDK's own wait,
# which defaults to 60 seconds, from ending a run first.
SEND_TIMEOUT_MARGIN = 60

# An accident guard, not a sandbox: an interpreter given code (python -c, a script
# file, a variable holding a command name) can still run anything.
DENIED_PROGRAMS = {"gh", "sudo", "doas", "runas", "gsudo"}
DENIED_GIT_SUBCOMMANDS = {"push", "remote", "worktree", "send-pack"}
_SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "fish"}
# Programs that run another command, with their options that take a separate value and
# the number of plain arguments that come before the command they run.
_WRAPPERS = {
    "env": ({"-u", "-P", "-S", "-C", "-a", "--unset", "--chdir", "--split-string", "--argv0"}, 0),
    "command": (set(), 0),
    "exec": ({"-a"}, 0),
    "nohup": (set(), 0),
    "time": ({"-f", "-o", "--format", "--output"}, 0),
    "nice": ({"-n", "--adjustment"}, 0),
    "timeout": ({"-s", "-k", "--signal", "--kill-after"}, 1),
    "xargs": ({
        "-I", "-J", "-R", "-S", "-n", "-L", "-P", "-d", "-E", "-s", "-a", "--max-args", "--max-lines", "--max-procs",
        "--max-chars", "--delimiter", "--eof", "--arg-file", "--process-slot-var",
    }, 0),
    "stdbuf": ({"-i", "-o", "-e", "--input", "--output", "--error"}, 0),
    "caffeinate": ({"-t", "-w"}, 0),
    "script": ({"-c", "--command"}, 1),
}
# Wrapper options whose value is itself a command line, which is checked in turn.
_COMMAND_OPTIONS = {"env": ("-S", "--split-string"), "script": ("-c", "--command")}
# Shell reserved words that precede a command: "! gh" and "if gh" still run gh.
_RESERVED_PREFIXES = {"!", "if", "then", "else", "elif", "do", "while", "until", "coproc"}
# Environment variables through which git reads aliases or a different config file.
_GIT_CONFIG_FILE_VARIABLES = {"GIT_CONFIG", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM"}
# Builtins that put an assignment into the shell session, where the next command sees it.
_EXPORTERS = {"export", "declare", "typeset", "readonly", "local"}
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_REDIRECT = re.compile(r"^\d*(>>?|<<?|&>|>&)")
_BARE_REDIRECT = re.compile(r"^\d*(>>?|<<?|&>|>&)$")
# Command separators, plus grouping and substitution, so "(gh ...)", "{ gh ...; }",
# "$(gh ...)" and "`gh ...`" are each checked as a command of their own.
_SEPARATORS = re.compile(r"\|\||&&|\$\(|[;|&\n(){}`]")
# git options that take a separate value before the subcommand.
_GIT_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"}
# Copilot runtime settings in the environment, such as COPILOT_ALLOW_ALL or
# COPILOT_CLI_PATH, could pre-approve tools or replace the pinned runtime.
_KEPT_COPILOT_VARIABLES = {"COPILOT_GITHUB_TOKEN"}
_MAX_DEPTH = 5
_EXECUTABLE_EXTENSIONS = {".exe", ".com", ".cmd", ".bat", ".ps1"}


def _program_name(word: str) -> str:
    """The name a word runs as: C:\\Tools\\GH.EXE and /usr/bin/gh both run gh.

    Lowercase, because macOS and Windows file systems are case-insensitive. Windows also
    finds a program without its extension and ignores trailing dots and spaces.
    """
    name = ntpath.basename(word).lower().rstrip(". ")
    stem, extension = os.path.splitext(name)
    return stem if extension in _EXECUTABLE_EXTENSIONS else name


def _words(segment: str) -> list[str]:
    try:
        return shlex.split(segment)
    except ValueError:
        # Unbalanced quotes: still check the plain words rather than skipping the check.
        return segment.split()


def _denied_git(args: list[str], aliases: frozenset[str]) -> str | None:
    index = 0
    while index < len(args) and args[index].startswith("-"):
        option = args[index]
        separate = args[index + 1] if index + 1 < len(args) else ""
        if option.startswith("--config-env"):
            value = option.partition("=")[2] or separate
        elif option.startswith("-c") and not option.startswith("--"):
            value = separate if option == "-c" else option[2:]
        else:
            value = ""
        if value.lower().startswith("alias."):
            return "git alias"
        index += 2 if option in _GIT_VALUE_OPTIONS else 1
    if index >= len(args):
        return None
    subcommand, rest = args[index].lower(), args[index + 1:]
    if subcommand in DENIED_GIT_SUBCOMMANDS:
        return f"git {subcommand}"
    # An alias already in the repository or global config can stand for git push.
    if subcommand in aliases:
        return "git alias"
    if subcommand == "config":
        for arg in rest:
            if arg.lower().startswith("alias."):
                return "git config alias"
            if arg.lower().startswith("remote."):
                return "git config remote"
    return None


def _denied_assignment(word: str, windows: bool = WINDOWS) -> str | None:
    """Deny NAME=value words that make git resolve an alias or read a config file we cannot see."""
    name, _, value = word.partition("=")
    if windows:
        # Windows environment names are case-insensitive, and Git for Windows reads
        # /dev/null as the null device.
        name = name.upper()
        null_device = value.lower() in ("", "nul", "/dev/null")
    else:
        null_device = value in ("", os.devnull)
    if name.startswith("GIT_CONFIG_KEY_") or name == "GIT_CONFIG_PARAMETERS":
        return "git alias" if "alias." in value.lower() else None
    if name in _GIT_CONFIG_FILE_VARIABLES and not null_device:
        return "a git config file from the environment"
    return None


def _scan_option(
    wrapper: str, words: list[str], index: int, value_options: set[str]
) -> tuple[str | None, int]:
    """Return (command line the option carries, if any, words the option consumes).

    Short options may be clustered (script -qc CMD, env -iS CMD): the first letter that
    takes a value ends the cluster, and the rest of the word, or else the next word, is
    that value.
    """
    option = words[index]
    command_options = _COMMAND_OPTIONS.get(wrapper, ())
    following = words[index + 1] if index + 1 < len(words) else ""
    if option.startswith("--"):
        key, equals, attached = option.partition("=")
        if equals:
            return (attached if key in command_options else None), 1
        if key in command_options:
            return following, 2
        return None, 2 if key in value_options else 1
    letters = option[1:]
    for position, letter in enumerate(letters):
        flag, rest = "-" + letter, letters[position + 1:]
        if flag in command_options:
            return (rest, 1) if rest else (following, 2)
        if flag in value_options:
            return None, 1 if rest else 2
    return None, 1


def _denied_words(words: list[str], depth: int, aliases: frozenset[str]) -> str | None:
    index = 0
    while index < len(words):
        word = words[index]
        name = _program_name(word)
        if _ASSIGNMENT.match(word):
            denied = _denied_assignment(word)
            if denied:
                return denied
            index += 1
        elif word in _RESERVED_PREFIXES:
            index += 1
        elif _REDIRECT.match(word):
            index += 2 if _BARE_REDIRECT.match(word) else 1
        elif name in _WRAPPERS:
            value_options, positionals = _WRAPPERS[name]
            index += 1
            while index < len(words) and words[index].startswith("-"):
                payload, width = _scan_option(name, words, index, value_options)
                if payload is not None:
                    denied = _denied_command(payload, aliases, depth + 1)
                    if denied:
                        return denied
                index += width
            index += positionals
        else:
            break
    if index >= len(words):
        return None
    program, args = _program_name(words[index]), words[index + 1:]
    if program in DENIED_PROGRAMS:
        return program
    if program in _EXPORTERS:
        for arg in args:
            denied = _denied_assignment(arg) if _ASSIGNMENT.match(arg) else None
            if denied:
                return denied
        return None
    if program == "eval":
        return _denied_command(" ".join(args), aliases, depth + 1)
    if program in _SHELLS:
        for position, arg in enumerate(args[:-1]):
            if arg.startswith("-") and not arg.startswith("--") and "c" in arg[1:]:
                return _denied_command(args[position + 1], aliases, depth + 1)
        return None
    if program.startswith("git-"):
        program, args = "git", [program[4:], *args]
    if program == "git":
        return _denied_git(args, aliases)
    return None


def _split_commands(text: str) -> tuple[list[str], bool]:
    """Split on separators the shell would act on, leaving quoted text whole.

    This keeps a payload such as bash -c 'echo ok; git push' in one piece, so that the
    recursive check sees it intact. Inside double quotes only $( and a backtick still
    start a command. Also return whether every quote was closed.
    """
    segments: list[str] = []
    current: list[str] = []
    quote = ""
    index = 0

    def cut() -> None:
        segments.append("".join(current))
        current.clear()

    while index < len(text):
        char, pair = text[index], text[index:index + 2]
        if char == "\\" and quote != "'" and len(pair) == 2:
            current.append(pair)
            index += 2
            continue
        if quote == "'":
            quote = "" if char == "'" else quote
        elif quote == '"':
            if char == '"':
                quote = ""
            elif pair == "$(" or char == "`":
                cut()
                index += len(pair) if pair == "$(" else 1
                continue
        elif char in "'\"":
            quote = char
        elif pair in ("||", "&&", "$("):
            cut()
            index += 2
            continue
        elif char in ";|&\n(){}`":
            cut()
            index += 1
            continue
        current.append(char)
        index += 1
    cut()
    return segments, not quote


def _denied_command(text: str, aliases: frozenset[str], depth: int = 0) -> str | None:
    if depth > _MAX_DEPTH:
        return "a command nested too deeply to check"
    # The shell removes a backslash-newline pair before it splits words, so a command
    # continued across lines is still one command.
    text = text.replace("\\\n", "")
    segments, balanced = _split_commands(text)
    if not balanced:
        # An unclosed quote would swallow what follows it, so also check the plain split.
        segments += _SEPARATORS.split(text)
    for segment in segments:
        denied = _denied_words(_words(segment), depth, aliases)
        if denied:
            return denied
    return None


# PowerShell and cmd.exe, which the runtime's shell uses on Windows. The same deny list,
# with the same limits: an accident guard, not a sandbox.

# PowerShell reads typographic quotes as quotes, and en and em dashes as hyphens, so an
# en dash before Command is -Command.
_PS_CHARACTERS = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u2013": "-", "\u2014": "-", "\u2015": "-",
})
# Keywords that can precede a command: "return gh" and "if (x) { gh }" still run gh.
_PS_KEYWORDS = {
    "if", "elseif", "else", "while", "do", "until", "for", "foreach", "switch", "try", "catch",
    "finally", "trap", "return", "throw", "exit", "break", "continue", "begin", "process", "end",
    "clean", "function", "filter", "-not", "!",
}
_PS_TYPE = re.compile(r"^\[[\w.\[\], ]*\]$")
_PS_REDIRECT = re.compile(r"^(?:[\d*]?>>?(?:&\d)?|<)")
_PS_BARE_REDIRECT = re.compile(r"^(?:[\d*]?>>?|<)$")
_PS_VARIABLE = re.compile(r"^\$\{?(?:(?P<scope>[A-Za-z]+):)?(?P<name>[\w?]+)\}?")
_PS_ASSIGNMENT_OPERATOR = re.compile(r"^(?:[-+*/%]|\?\?)?=(?!=)(?P<rest>.*)$", re.DOTALL)
_SET_ENVIRONMENT_VARIABLE = re.compile(
    r"SetEnvironmentVariable\s*\(\s*['\"]?(?P<name>[\w]+)['\"]?\s*,\s*['\"]?(?P<value>[^'\",)]*)",
    re.IGNORECASE,
)
_PS_COMMON_PARAMETERS = (
    "erroraction", "warningaction", "informationaction", "errorvariable", "warningvariable",
    "informationvariable", "outvariable", "outbuffer", "pipelinevariable", "progressaction",
)
_PS_COMMON_ALIASES = {
    "ea": "erroraction", "wa": "warningaction", "infa": "informationaction", "ev": "errorvariable",
    "wv": "warningvariable", "iv": "informationvariable", "ov": "outvariable", "ob": "outbuffer",
    "pv": "pipelinevariable", "proga": "progressaction",
}
_START_PROCESS = {"start-process", "start", "saps"}
_START_PROCESS_PARAMETERS = (
    "filepath", "argumentlist", "credential", "workingdirectory", "redirectstandarderror",
    "redirectstandardinput", "redirectstandardoutput", "verb", "windowstyle", "environment",
)
_START_PROCESS_ALIASES = {
    "pspath": "filepath", "path": "filepath", "args": "argumentlist", "rse": "redirectstandarderror",
    "rsi": "redirectstandardinput", "rso": "redirectstandardoutput",
}
_INVOKE_EXPRESSION = {"invoke-expression", "iex"}
_ALIAS_SETTERS = {"set-alias", "new-alias", "sal", "nal"}
_ENV_SETTERS = {"set-item", "new-item", "si", "ni", "set-content", "add-content", "ac"}
_ENV_SETTER_PARAMETERS = ("path", "literalpath", "value", "name", "itemtype", "credential")
_WSL_VALUE_OPTIONS = {"-d", "--distribution", "-u", "--user", "--cd", "--shell-type", "--distribution-id"}
_CMD_SEPARATORS = "&|()\n\r"
_CMD_PREFIXES = {"call", "do", "else"}


def _split_powershell(text: str) -> tuple[list[str], bool]:
    """Split on PowerShell's separators, leaving quoted text whole.

    A $( ) subexpression inside a double-quoted string is code, so it is split too; the
    string resumes after its closing parenthesis. Also return whether every quote closed.
    """
    segments: list[str] = []
    current: list[str] = []
    quote = ""
    depth = 0
    # The parenthesis depth at which each open subexpression returns to its string.
    resume: list[int] = []
    index = 0

    def cut() -> None:
        segments.append("".join(current))
        current.clear()

    while index < len(text):
        char, pair = text[index], text[index:index + 2]
        if char == "`" and quote != "'" and len(pair) == 2:
            current.append(pair)
            index += 2
            continue
        if quote == "'":
            quote = "" if char == "'" else quote
        elif quote == '"':
            if char == '"':
                quote = ""
            elif pair == "$(":
                cut()
                resume.append(depth)
                depth += 1
                quote = ""
                index += 2
                continue
        elif char in "'\"":
            quote = char
        elif pair == "${":
            # ${name} is a variable name, not a block: keep it whole.
            end = text.find("}", index)
            end = len(text) if end < 0 else end + 1
            current.append(text[index:end])
            index = end
            continue
        elif pair in ("||", "&&"):
            cut()
            index += 2
            continue
        elif pair in ("$(", "@(", "@{"):
            cut()
            depth += 1
            index += 2
            continue
        elif char in "({":
            cut()
            depth += 1
            index += 1
            continue
        elif char in ")}":
            cut()
            depth = max(depth - 1, 0)
            if resume and depth == resume[-1]:
                resume.pop()
                quote = '"'
            index += 1
            continue
        elif char in ";|&\n\r":
            cut()
            index += 1
            continue
        current.append(char)
        index += 1
    cut()
    return segments, not quote


def _powershell_words(segment: str) -> list[str]:
    """Split a segment into words, removing quotes and backtick escapes."""
    words: list[str] = []
    current: list[str] = []
    quote = ""
    started = False
    index = 0
    while index < len(segment):
        char = segment[index]
        if char == "`" and quote != "'" and index + 1 < len(segment):
            current.append(segment[index + 1])
            started = True
            index += 2
            continue
        if quote:
            if char != quote:
                current.append(char)
            elif segment[index + 1:index + 2] == quote:
                # A doubled quote inside a string of the same kind is one literal quote.
                current.append(char)
                index += 1
            else:
                quote = ""
        elif char in "'\"":
            quote = char
            started = True
        elif char.isspace():
            if started:
                words.append("".join(current))
                current.clear()
                started = False
        else:
            current.append(char)
            started = True
        index += 1
    if started:
        words.append("".join(current))
    return words


def _ps_arguments(
    args: list[str], parameters: tuple[str, ...], aliases: dict[str, str]
) -> tuple[dict[str, str], list[str]]:
    """Bind PowerShell arguments: named values by unambiguous prefix, then positionals.

    An option that names no known valued parameter is taken as a switch.
    """
    known = (*parameters, *_PS_COMMON_PARAMETERS)
    every_alias = {**_PS_COMMON_ALIASES, **aliases}
    named: dict[str, str] = {}
    positionals: list[str] = []
    index = 0
    while index < len(args):
        arg = args[index]
        if len(arg) > 1 and arg[0] == "-" and (arg[1].isalpha() or arg[1] == "_"):
            key, colon, attached = arg[1:].partition(":")
            key = key.lower()
            matches = [every_alias[key]] if key in every_alias else [
                name for name in known if name.startswith(key)]
            if len(matches) == 1:
                if colon:
                    named[matches[0]] = attached
                    index += 1
                else:
                    named[matches[0]] = args[index + 1] if index + 1 < len(args) else ""
                    index += 2
                continue
        else:
            positionals.append(arg)
        index += 1
    return named, positionals


def _denied_env_assignment(name: str, value: str) -> str | None:
    return _denied_assignment(f"{name.upper()}={value}", windows=True)


def _denied_start_process(args: list[str], aliases: frozenset[str], depth: int) -> str | None:
    named, positionals = _ps_arguments(args, _START_PROCESS_PARAMETERS, _START_PROCESS_ALIASES)
    if named.get("verb", "").lower() == "runas":
        return "Start-Process -Verb RunAs"
    file = named.get("filepath") or (positionals.pop(0) if positionals else "")
    arguments = named.get("argumentlist") or (positionals.pop(0) if positionals else "")
    if not file:
        return None
    # The argument list is one Windows command line or a comma-separated array of words.
    words = [file, *(word for word in re.split(r"[\s,]+", arguments) if word)]
    return _denied_windows_invocation(words, depth + 1, aliases)


def _denied_powershell_host(args: list[str], aliases: frozenset[str], depth: int) -> str | None:
    """pwsh and powershell: check -Command, -EncodedCommand, and a bare command line."""
    for index, arg in enumerate(args):
        if arg == "-":
            return None
        if len(arg) > 1 and arg[0] in "-/":
            key, colon, attached = arg[1:].lstrip("-").partition(":")
            key = key.lower()
            rest = [attached] if colon else args[index + 1:]
            if key and "command".startswith(key):
                return _denied_powershell(" ".join(rest), aliases, depth + 1)
            if key in ("e", "ec") or (len(key) > 1 and "encodedcommand".startswith(key)):
                try:
                    decoded = base64.b64decode(rest[0] if rest else "", validate=True).decode("utf-16-le")
                except (binascii.Error, UnicodeDecodeError, ValueError):
                    return "an encoded command that could not be decoded"
                return _denied_powershell(decoded, aliases, depth + 1)
            if key == "f" or (len(key) > 1 and "file".startswith(key)):
                # A script file runs whatever it holds, as an interpreter given code does.
                return None
            continue
        # A bare word starts a command to Windows PowerShell and a script to pwsh. It may
        # also be the value of the option before it, so keep scanning when it passes.
        denied = _denied_powershell(" ".join(args[index:]), aliases, depth + 1)
        if denied:
            return denied
    return None


def _denied_wsl(args: list[str], aliases: frozenset[str], depth: int) -> str | None:
    """wsl runs a command in Linux: with --exec as plain words, otherwise through a shell."""
    index = 0
    while index < len(args):
        arg = args[index]
        if arg in ("-e", "--exec"):
            return _denied_words(args[index + 1:], depth + 1, aliases)
        if arg == "--":
            return _denied_command(" ".join(args[index + 1:]), aliases, depth + 1)
        if not arg.startswith("-"):
            return _denied_command(" ".join(args[index:]), aliases, depth + 1)
        index += 2 if arg in _WSL_VALUE_OPTIONS else 1
    return None


def _cmd_payload(words: list[str]) -> str:
    """The command line cmd /c runs, rebuilt from words whose quotes are gone.

    The caller quotes a word that holds whitespace, as PowerShell does when it starts a
    program. cmd.exe then usually drops the first and last quote of the line.
    """
    line = " ".join(
        f'"{word}"' if any(char.isspace() for char in word) else word for word in words if word
    )
    if line.startswith('"'):
        last = line.rfind('"')
        line = line[1:last] + line[last + 1:]
    return line


def _denied_windows_invocation(words: list[str], depth: int, aliases: frozenset[str]) -> str | None:
    """Check one program and its arguments, from either PowerShell or cmd.exe."""
    if depth > _MAX_DEPTH:
        return "a command nested too deeply to check"
    if not words:
        return None
    program, args = _program_name(words[0]), words[1:]
    if program in DENIED_PROGRAMS:
        return program
    if program.startswith("git-"):
        program, args = "git", [program[4:], *args]
    if program == "git":
        return _denied_git(args, aliases)
    if program in ("pwsh", "powershell", "powershell_ise"):
        return _denied_powershell_host(args, aliases, depth)
    if program == "cmd":
        for index, arg in enumerate(args):
            if arg.lower()[:2] in ("/c", "/k", "/r"):
                return _denied_cmd(_cmd_payload([arg[2:], *args[index + 1:]]), aliases, depth + 1)
        return None
    if program == "wsl":
        return _denied_wsl(args, aliases, depth)
    if program in _SHELLS or program in _WRAPPERS or program == "eval":
        # POSIX programs that run another command, as installed by Git for Windows.
        return _denied_words([program, *args], depth, aliases)
    if program in _START_PROCESS:
        return _denied_start_process(args, aliases, depth)
    if program in _INVOKE_EXPRESSION:
        named, positionals = _ps_arguments(args, ("command",), {})
        return _denied_powershell(named.get("command") or " ".join(positionals), aliases, depth + 1)
    if program in _ALIAS_SETTERS:
        for arg in args:
            target = _program_name(arg)
            if target in DENIED_PROGRAMS or target == "git" or target.startswith("git-"):
                return f"a PowerShell alias for {target}"
        return None
    if program in _ENV_SETTERS:
        named, positionals = _ps_arguments(args, _ENV_SETTER_PARAMETERS, {"pspath": "literalpath"})
        path = named.get("path") or named.get("literalpath") or (positionals.pop(0) if positionals else "")
        if path.lower().startswith("env:"):
            value = named.get("value") or (positionals.pop(0) if positionals else "")
            return _denied_env_assignment(path[4:], value)
    return None


def _denied_powershell_words(words: list[str], depth: int, aliases: frozenset[str]) -> str | None:
    words = list(words)
    index = 0
    while index < len(words):
        word = words[index]
        if word in ("", "&", ".") or word.lower() in _PS_KEYWORDS or _PS_TYPE.match(word):
            index += 1
            continue
        if _PS_REDIRECT.match(word):
            index += 2 if _PS_BARE_REDIRECT.match(word) else 1
            continue
        if not word.startswith("$"):
            break
        variable = _PS_VARIABLE.match(word)
        attached = _PS_ASSIGNMENT_OPERATOR.match(word[variable.end():]) if variable else None
        following = words[index + 1] if index + 1 < len(words) else ""
        separate = None if attached else _PS_ASSIGNMENT_OPERATOR.match(following)
        if variable is None or not (attached or separate):
            # A variable or an expression in command position: & $tool runs whatever it holds.
            return None
        # The value starts in the word holding the operator, or else in the word after it.
        start, rest = (index, attached.group("rest")) if attached else (index + 1, separate.group("rest"))
        if rest:
            words[start] = rest
            index = start
        else:
            index = start + 1
        value = words[index] if index < len(words) else ""
        if (variable.group("scope") or "").lower() == "env":
            denied = _denied_env_assignment(variable.group("name"), value)
            if denied:
                return denied
        # The value is checked as a command in turn: $out = gh pr list runs gh.
    if index >= len(words):
        return None
    return _denied_windows_invocation(words[index:], depth, aliases)


def _denied_powershell(text: str, aliases: frozenset[str], depth: int = 0) -> str | None:
    if depth > _MAX_DEPTH:
        return "a command nested too deeply to check"
    # A backtick at the end of a line continues the command on the next.
    text = text.translate(_PS_CHARACTERS).replace("`\r\n", "").replace("`\n", "")
    segments, balanced = _split_powershell(text)
    if not balanced:
        # An unclosed quote would swallow what follows it, so also check the plain split.
        segments += re.split(r"[;|&\n\r(){}]", text)
    for segment in segments:
        denied = _denied_powershell_words(_powershell_words(segment), depth, aliases)
        if denied:
            return denied
    for match in _SET_ENVIRONMENT_VARIABLE.finditer(text):
        denied = _denied_env_assignment(match.group("name"), match.group("value"))
        if denied:
            return denied
    return None


def _cmd_words(segment: str) -> list[str]:
    """cmd.exe words: whitespace separates, and only double quotes quote."""
    words: list[str] = []
    current: list[str] = []
    quote = started = False
    for char in segment:
        if char == '"':
            quote = not quote
            started = True
        elif not quote and char.isspace():
            if started:
                words.append("".join(current))
                current.clear()
                started = False
        else:
            current.append(char)
            started = True
    if started:
        words.append("".join(current))
    return words


def _denied_cmd_words(words: list[str], depth: int, aliases: frozenset[str]) -> str | None:
    # @ hides the command's echo, and cmd.exe skips commas, semicolons, and = before a
    # command name: "@gh" and ",gh" both run gh.
    words = [word.lstrip("@,;=") for word in words]
    index = 0
    while index < len(words):
        word = words[index].lower()
        if not word or word in _CMD_PREFIXES:
            index += 1
        elif _REDIRECT.match(word):
            index += 2 if _BARE_REDIRECT.match(word) else 1
        elif word == "if":
            # The condition's length varies, so check a command starting at each word.
            for start in range(index + 1, len(words)):
                denied = _denied_windows_invocation(words[start:], depth, aliases)
                if denied:
                    return denied
            return None
        elif word == "start":
            # start takes /options and an optional window title, in any order, before the
            # command. Quotes are gone by now, so try the first two plain words as the command.
            rest, start, tried = words[index + 1:], 0, 0
            while start < len(rest) and tried < 2:
                if rest[start].startswith("/"):
                    start += 2 if rest[start].lower() == "/d" else 1
                    continue
                denied = _denied_windows_invocation(rest[start:], depth, aliases)
                if denied:
                    return denied
                start, tried = start + 1, tried + 1
            return None
        elif word == "set":
            for arg in words[index + 1:]:
                name, equals, value = arg.partition("=")
                if equals:
                    denied = _denied_env_assignment(name, value)
                    if denied:
                        return denied
            return None
        else:
            break
    if index >= len(words):
        return None
    return _denied_windows_invocation(words[index:], depth, aliases)


def _denied_cmd(text: str, aliases: frozenset[str], depth: int = 0) -> str | None:
    if depth > _MAX_DEPTH:
        return "a command nested too deeply to check"
    segments: list[str] = []
    current: list[str] = []
    quote = False
    index = 0
    while index < len(text):
        char = text[index]
        if char == "^" and not quote and index + 1 < len(text):
            # A caret escapes the next character; a caret before a newline continues the line.
            if text[index + 1] not in "\r\n":
                current.append(text[index + 1])
            index += 2
            continue
        if char == '"':
            quote = not quote
            current.append(char)
        elif char in _CMD_SEPARATORS and not quote:
            segments.append("".join(current))
            current.clear()
        else:
            current.append(char)
        index += 1
    segments.append("".join(current))
    if quote:
        segments += re.split(r"[&|()\n\r]", text)
    for segment in segments:
        denied = _denied_cmd_words(_cmd_words(segment), depth, aliases)
        if denied:
            return denied
    return None


def configured_aliases(workspace: str) -> frozenset[str]:
    """Names of the git aliases the workspace's repository and global config define."""
    try:
        result = subprocess.run(
            ["git", "-C", workspace, "config", "--get-regexp", r"^alias\."],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return frozenset()
    keys = (line.split(None, 1)[0] for line in result.stdout.splitlines() if line.strip())
    return frozenset(key.split(".", 1)[1].lower() for key in keys)


def _inside(path: str | None, workspace: str) -> bool:
    if not path or path.startswith("~") or "$" in path:
        # Reject forms the runtime might expand before reading.
        return False
    if not os.path.isabs(path):
        path = os.path.join(workspace, path)
    # normcase folds case and slashes on Windows, where C:\W and c:/w are the same folder.
    real = os.path.normcase(os.path.realpath(path))
    root = os.path.normcase(os.path.realpath(workspace))
    return real == root or real.startswith(root.rstrip(os.sep) + os.sep)


def decide(
    kind: str, fields: dict, workspace: str, mode: str, aliases: frozenset[str] = frozenset()
) -> tuple[bool, str]:
    """Return (allowed, reason) for one permission request. Unknown kinds are rejected."""
    if kind == "shell":
        if mode != "implement":
            return False, f"shell commands are not allowed in {mode} mode"
        segments = [segment for segment in fields.get("segments") or [] if segment]
        if not segments:
            return False, "shell request carried no command text"
        for segment in segments:
            # On Windows the shell is PowerShell, but a command may still be written for
            # bash or cmd.exe, so it must pass the POSIX check and the PowerShell check.
            denied = _denied_command(segment, aliases) or (
                WINDOWS and _denied_powershell(segment, aliases)) or None
            if denied:
                return False, f"copilot-worker denied command: {denied}"
        return True, "allowed"
    if kind in ("read", "write"):
        if kind == "write" and mode != "implement":
            return False, f"writes are not allowed in {mode} mode"
        if not _inside(fields.get("path"), workspace):
            return False, f"{fields.get('path')!r} is outside the workspace"
        return True, "allowed"
    return False, f"copilot-worker does not allow {kind} requests"


def request_kind(request: Any) -> str:
    """Map an SDK permission request class to a policy kind: PermissionRequestShell -> shell."""
    name = type(request).__name__.removeprefix("PermissionRequest")
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower() or "unknown"


def request_fields(request: Any) -> dict:
    kind = request_kind(request)
    if kind == "shell":
        texts = [getattr(request, "full_command_text", None)]
        for part in [*(getattr(request, "command_segments", None) or []),
                     *(getattr(request, "commands", None) or [])]:
            texts += [getattr(part, "full_command_text", None), getattr(part, "identifier", None)]
        return {"segments": [text for text in texts if text]}
    if kind in ("read", "write"):
        path = (getattr(request, "resolved_path", None) or getattr(request, "path", None)
                or getattr(request, "file_name", None))
        return {"path": path}
    return {}


def scrub_environment(environ: dict) -> dict:
    return {
        key: value for key, value in environ.items()
        if not key.startswith("COPILOT_") or key in _KEPT_COPILOT_VARIABLES
    }


def client_options(config: dict, env: dict) -> dict:
    # An isolated Copilot home keeps the user's hooks, skills, and MCP config out.
    return {
        "working_directory": config["workspace"],
        "base_directory": config["copilotHome"],
        "env": env,
    }


def session_options(config: dict) -> dict:
    options = {
        "model": config["model"],
        "working_directory": config["workspace"],
        "available_tools": TOOLS[config["mode"]],
        "session_limits": {"max_ai_credits": config["credits"]},
        "enable_skills": False,
        # Repository .github/hooks would run commands and could settle permissions first.
        "enable_file_hooks": False,
        "disabled_mcp_servers": ["github-mcp-server"],
    }
    if config.get("effort"):
        options["reasoning_effort"] = config["effort"]
    return options


def session_kwargs(config: dict, on_permission: Any, on_event: Any, tools: Any) -> dict:
    """Everything create_session receives. drive() passes exactly this."""
    return {
        **session_options(config),
        "available_tools": tools,
        "on_permission_request": on_permission,
        "on_event": on_event,
    }


def send_options(config: dict) -> dict:
    return {"timeout": float(config["timeout"] + SEND_TIMEOUT_MARGIN)}


def summarize_usage(calls: list[dict]) -> dict:
    keys = ("inputTokens", "outputTokens", "cacheReadTokens", "cacheWriteTokens")
    total = sum(call.get("totalNanoAiu") or 0 for call in calls)
    summary = {key: sum(call.get(key) or 0 for call in calls) for key in keys}
    summary.update({
        "aiCredits": round(total / 1e9, 4),
        "totalNanoAiu": total,
        "modelCalls": len(calls),
        "models": sorted({call["model"] for call in calls if call.get("model")}),
    })
    return summary


def _usage_call(data: Any) -> dict:
    copilot_usage = getattr(data, "copilot_usage", None)
    return {
        "totalNanoAiu": getattr(copilot_usage, "total_nano_aiu", 0) or 0,
        "inputTokens": getattr(data, "input_tokens", 0),
        "outputTokens": getattr(data, "output_tokens", 0),
        "cacheReadTokens": getattr(data, "cache_read_tokens", 0),
        "cacheWriteTokens": getattr(data, "cache_write_tokens", 0),
        "model": getattr(data, "model", None),
    }


def load_pins() -> dict:
    return json.loads(PINS_FILE.read_text(encoding="utf-8"))


def pin_problem(info: dict, pins: dict) -> str | None:
    """Describe how the installed SDK or runtime differs from pins.json, if it does."""
    differences = [
        f"{label} is {info.get(installed)}, pinned to {pins.get(pinned)}"
        for label, installed, pinned in (
            ("github-copilot-sdk", "sdkVersion", "sdk"), ("runtime", "runtimeVersion", "runtime"),
        )
        if info.get(installed) != pins.get(pinned)
    ]
    return "; ".join(differences) or None


def versions() -> dict:
    from importlib.metadata import version

    from copilot._cli_version import CLI_VERSION

    return {"sdkVersion": version("github-copilot-sdk"), "runtimeVersion": CLI_VERSION}


async def drive(run_dir: Path) -> None:
    # Scrub before the SDK loads: it reads COPILOT_* settings from this process too.
    env = scrub_environment(dict(os.environ))
    os.environ.clear()
    os.environ.update(env)

    from copilot import CopilotClient, ToolSet
    from copilot.rpc import PermissionDecisionApproveOnce, PermissionDecisionReject

    config = json.loads((run_dir / "engine.json").read_text(encoding="utf-8"))
    prompt = (run_dir / "task.md").read_text(encoding="utf-8")
    (run_dir / "runtime.json").write_text(json.dumps(versions()) + "\n", encoding="utf-8")
    calls: list[dict] = []
    response = ""
    aliases = configured_aliases(config["workspace"])

    with open(run_dir / "events.jsonl", "a", encoding="utf-8") as events, \
            open(run_dir / "permissions.jsonl", "a", encoding="utf-8") as permissions:

        def on_permission(request: Any, _invocation: Any) -> Any:
            kind, fields = request_kind(request), request_fields(request)
            allowed, reason = decide(kind, fields, config["workspace"], config["mode"], aliases)
            permissions.write(json.dumps(
                {"kind": kind, "fields": fields, "allowed": allowed, "reason": reason}) + "\n")
            permissions.flush()
            if allowed:
                return PermissionDecisionApproveOnce()
            return PermissionDecisionReject(feedback=reason)

        def on_event(event: Any) -> None:
            nonlocal response
            events.write(json.dumps(event.to_dict(), default=str) + "\n")
            events.flush()
            name = type(event.data).__name__
            if name == "AssistantUsageData":
                calls.append(_usage_call(event.data))
            elif name == "AssistantMessageData":
                content = getattr(event.data, "content", None)
                if isinstance(content, str) and content.strip():
                    response = content

        tools = ToolSet()
        for tool in TOOLS[config["mode"]]:
            tools.add_builtin(tool)
        try:
            async with CopilotClient(**client_options(config, env)) as client:
                session = await client.create_session(
                    **session_kwargs(config, on_permission, on_event, tools)
                )
                await session.send_and_wait(prompt, **send_options(config))
        finally:
            (run_dir / "response.md").write_text(response, encoding="utf-8")
            (run_dir / "usage.json").write_text(
                json.dumps(summarize_usage(calls), indent=2) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    if argv == ["--version"]:
        info = versions()
        print(f"github-copilot-sdk {info['sdkVersion']} (runtime {info['runtimeVersion']})")
        return 0
    if argv == ["--check-pins"]:
        problem = pin_problem(versions(), load_pins())
        print(f"pin mismatch: {problem}" if problem else "pins ok")
        return 1 if problem else 0
    if len(argv) != 1:
        print("usage: worker_engine.py RUN_DIR | --version | --check-pins", file=sys.stderr)
        return 2
    problem = pin_problem(versions(), load_pins())
    if problem:
        print(f"pin mismatch: {problem}. See references/upgrading.md.", file=sys.stderr)
        return 3
    asyncio.run(drive(Path(argv[0])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
