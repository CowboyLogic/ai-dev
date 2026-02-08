# Migration Guide: Transitioning to High-Fidelity XML Directives

This guide outlines the process for migrating your repository's AI instructions from standard `AGENTS.md` files to the machine-optimized **High-Fidelity XML** system.

---

## Phase 1: Preparation

### 1. Create the Infrastructure

Establish a dedicated directory for machine instructions to separate them from human-facing documentation.

* Create a `.agents/` directory in the root of your project.
* Ensure `.gitignore` is updated to allow these XML files while still excluding the `agent-output/` directory.

### 2. Identify Core Directives

Review your existing `AGENTS.md` and identify three core categories of information:

* **Workflows**: How the agent should handle file edits and Git operations.
* **Architecture**: Technical stack, file structures, and formatting rules.
* **Priorities**: Which instructions take precedence when conflicts arise.

---

## Phase 2: Conversion

### 1. Implement the Repository Directives (`.agents/AGENTS.xml`)

Extract the "How-To" rules from your Markdown file and wrap them in functional tags.

* **Logic**: Use `<management_protocols>` to define update triggers and output handling.
* **Hierarchy**: Explicitly define the `<instruction_priority>` to resolve logical conflicts.

### 2. Define the Technical Map (`.agents/ARCHITECTURE.xml`)

Extract the project specifications to ensure the agent understands the environment.

* **Stack**: Define the `<tech_stack>` (e.g., MkDocs, GFM, Python).
* **Logic**: Map out the `<file_system_logic>` to prevent the agent from modifying restricted directories.

### 3. Initialize the Manifest (`.agents/manifest.xml`)

Create the bootstrap loader that connects your local rules to the global organization baseline.

* Link to the central `.github/LLM-BaselineBehaviors.xml` as `priority="1"`.
* Link to your new local XML files as subsequent priorities.

---

## Phase 3: The "Shim" Implementation

To ensure agents can still find your instructions, replace the content of your root `AGENTS.md` with a **Shim Pointer**.

```markdown
# AI Agent Entry Point
**STOP: This repository uses a high-fidelity XML directive model.**
Initialize by reading `.agents/manifest.xml` before taking any action.
```

## Phase 4: Validation

After migration, verify the agent’s adherence by performing a "Dry Run":

1. Instruction Check: Ask the agent: "Summarize your current behavioral priorities based on the manifest."
2. Output Check: Direct the agent to generate a test file and ensure it is placed correctly in agent-output/ as defined in your new <management_protocols>.
3. Log Check: Ensure the agent creates a PLAN.md in background mode before modifying code.
