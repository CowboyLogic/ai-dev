# High-Fidelity Context Scaffolder

Generate machine-optimized XML context files for AI agent orchestration. The skill scaffolds
a `.agents/` directory with `AGENTS.xml` and `ARCHITECTURE.xml`, plus a short `AGENTS.md`
shim that points agents to them, so agents understand a codebase at session start without
spending tokens exploring it.

- **Skill name:** `high-fidelity-context-scaffolder`
- **Last updated:** 2026-04-19
- **Source:** [skills/high-fidelity-context-scaffolder](https://github.com/CowboyLogic/ai-dev/tree/main/skills/high-fidelity-context-scaffolder)

---

## What it does

XML tags act as semantic anchors for model attention, and a static XML prefix keeps the
KV cache stable across turns. The skill converts a repository's directives into that form.

**Generated structure:**

```text
repository-root/
├── .agents/
│   ├── AGENTS.xml          # Repository-specific directives
│   └── ARCHITECTURE.xml    # Technical stack and project specifications
└── AGENTS.md               # Shim that directs agents to the XML files
```

**Two modes:**

- **Migrate** — if `AGENTS.md` already exists, the skill extracts its purpose, repository
  map, management protocols, and documentation standards into XML, and keeps the original
  as `AGENTS.md.backup`.
- **Generate** — if there is no `AGENTS.md`, the skill scans the repository (directories,
  package manifests, build and CI configuration, README) to detect the stack and structure,
  then builds the XML from that analysis.

**File contents:**

| File | Main elements |
|------|---------------|
| `AGENTS.xml` | `purpose_and_scope`, `instruction_priority`, `repository_map`, `management_protocols` (update triggers, documentation standards, output handling) |
| `ARCHITECTURE.xml` | `project_metadata`, `technology_stack`, `directory_structure`, `documentation_system`, `development_workflow`, `constraints` |
| `AGENTS.md` | A shim of fewer than ten lines that tells agents to read the XML files |

The skill finishes by checking that each generated file is well-formed XML and reporting
what it created and where the information came from.

> [!TIP]
> Review the generated XML before committing it. Where the repository structure or build
> process is unclear, the skill marks the gap with a comment instead of guessing.

---

## Included files

| File | Contents |
|------|----------|
| `SKILL.md` | Detection logic, step-by-step instructions, and examples |
| `agents-xml-template.xml` | Template for `AGENTS.xml` |
| `architecture-xml-template.xml` | Template for `ARCHITECTURE.xml` |
| `agents-md-shim-template.md` | Template for the `AGENTS.md` shim |
| `high-fidelity-context.md` | Background on the High-Fidelity XML approach |
| `QUICKREF.md` | Quick reference |

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill high-fidelity-context-scaffolder -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill high-fidelity-context-scaffolder --agent <agent> -g
```

### Verify installation

```bash
npx skills ls -g
```
