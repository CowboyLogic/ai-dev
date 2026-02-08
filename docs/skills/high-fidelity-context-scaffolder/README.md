# High-Fidelity XML Context Scaffolder

A skill for generating machine-optimized AI agent directive files using the High-Fidelity XML approach.

## What This Skill Does

This skill helps AI agents create the High-Fidelity XML infrastructure for agent orchestration in any repository. It generates:

- **`.agents/AGENTS.xml`**: Repository-specific directives and file structure
- **`.agents/ARCHITECTURE.xml`**: Technical stack and project specifications
- **`AGENTS.md`**: Shim file that directs agents to the XML files

## When to Use

Use this skill when:

- Setting up AI agent directives for a new repository
- Migrating from Markdown-based instructions to XML
- Converting existing `AGENTS.md` into High-Fidelity XML format
- Creating consistent agent directive structure across repositories

## How It Works

The skill uses intelligent detection:

1. **If `AGENTS.md` exists**: Analyzes and migrates content to XML structure
2. **If no `AGENTS.md`**: Scans repository structure and generates XML from analysis

## Quick Start for Agents

To use this skill:

```
Read and follow the instructions in SKILL.md
```

Key steps:
1. Detect existing AGENTS.md (if present)
2. Analyze repository structure
3. Generate `.agents/AGENTS.xml` from template
4. Generate `.agents/ARCHITECTURE.xml` from template
5. Create `AGENTS.md` shim file
6. Verify and report results

## Files in This Skill

- **`SKILL.md`**: Complete instructions for agents (REQUIRED)
- **`agents-xml-template.xml`**: Template for AGENTS.xml
- **`architecture-xml-template.xml`**: Template for ARCHITECTURE.xml
- **`agents-md-shim-template.md`**: Template for AGENTS.md shim
- **`README.md`**: This file (for humans)
- **`QUICKREF.md`**: Quick reference guide

## Benefits of High-Fidelity XML

- **Better Anchoring**: XML tags act as semantic anchors for AI attention
- **KV-Cache Stability**: Static XML prefixes improve performance
- **Reduced Context Drift**: Clear boundaries prevent instruction loss
- **Modular Loading**: Load only necessary context modules
- **Conflict Resolution**: Priority system resolves directive conflicts

## Example Output Structure

```
repository-root/
├── .agents/
│   ├── AGENTS.xml          # Repository directives
│   └── ARCHITECTURE.xml    # Technical specifications
└── AGENTS.md               # Discovery shim
```

## References

- [High-Fidelity XML Concept](high-fidelity-context.md)
- [Agent Skills Standard](https://agentskills.io)
- [Anthropic: Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

## License

MIT

## Version

1.0 - February 2026
