# Codex Configuration Manager

A skill for viewing, editing, and explaining OpenAI Codex CLI configuration.

> [!NOTE]
> **Codex version:** verified against [Codex CLI 0.162.1](https://github.com/openai/codex/releases/tag/rust-v0.162.1)
> (released 2026-10-09). The reference files distill the official Codex documentation and
> record where the installed CLI differs from it. Codex changes quickly, so re-verify when it
> ships a new release (see [Refreshing the references](#refreshing-the-references)).

## Overview

Codex configuration is TOML, spread across user, project, profile, and machine layers, and
it changes between releases. An agent answering from memory tends to invent keys or reuse
another client's schema. This skill routes each task to the reference material for the config
area involved and loads only that material.

This skill covers:

- `config.toml` layers and precedence, profiles, and project trust
- Model, reasoning effort, custom model providers, and feature flags
- Memories and app (connector) settings
- Sandbox mode, approval policy, permission profiles, auto-review, and `.rules` files
- MCP servers, hooks, skills, and plugins and marketplaces
- The `[agents]` table and where custom agents live (writing agent files is the job of the
  [agent-creator-codex](../agent-creator-codex/README.md) skill)
- `AGENTS.md` and `AGENTS.override.md` discovery
- Authentication, environment variables, and admin-enforced `requirements.toml`, including the
  Browser Use, Computer Use, and desktop-app network requirements
- CLI subcommands, `-c` overrides, sessions, and slash commands

The skill never reads or prints Codex credentials, and it asks before trusting a project or
loosening the sandbox and approval settings.

## Scripts

Both scripts are in `scripts/` and use only the Python standard library.

| Script | What it does |
|---|---|
| `show-config.py` | Displays every Codex config file that exists, with secrets redacted. Needs Python 3.11+ |
| `update-references.py` | Fetches the upstream documentation listed in `sources.json` into a staging directory so the reference files can be refreshed |

## Refreshing the references

Ask the agent to update the skill, or run `python scripts/update-references.py --all` and
follow the self-update procedure in [SKILL.md](SKILL.md). Every command, flag, and feature
written into a reference should be checked against the installed CLI (`codex --help`,
`codex <subcommand> --help`, `codex features list`) before it is kept, and the version
stamped here and in each reference file should move with the CLI release that was used.

## Official Documentation

| Resource | URL |
|---|---|
| Config basics | <https://developers.openai.com/codex/config-basic> |
| Config reference | <https://developers.openai.com/codex/config-reference> |
| Agent approvals and security | <https://developers.openai.com/codex/agent-approvals-security> |
| Hooks | <https://developers.openai.com/codex/hooks> |
| Codex releases | <https://github.com/openai/codex/releases> |
