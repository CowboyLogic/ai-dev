---
name: high-fidelity-context-scaffolder
description: Generate High-Fidelity XML context files for AI agent orchestration, including .agents/ folder structure, AGENTS.xml, ARCHITECTURE.xml, and AGENTS.md shim. Use when setting up machine-optimized agent directives for a repository.
license: MIT
---

# High-Fidelity XML Context Scaffolder

This skill helps you create the High-Fidelity XML infrastructure for AI agent orchestration in any repository. It generates machine-optimized instruction files that leverage XML's structural advantages for better agent performance, context stability, and KV-cache efficiency.

## When to Use This Skill

Use this skill when:
- Setting up AI agent directives for a new repository
- Migrating from Markdown-based instructions to XML-based structure
- Establishing machine-optimized "Operating System" for agents
- Converting existing `AGENTS.md` into the High-Fidelity XML format
- Creating a consistent agent directive structure across multiple repositories

## What This Skill Creates

The skill generates the following structure:

```
repository-root/
├── .agents/
│   ├── AGENTS.xml          # Repository-specific directives
│   └── ARCHITECTURE.xml    # Technical stack and project specifications
└── AGENTS.md               # Shim file for agent discoverability
```

## Prerequisites

- Write access to the repository root
- Understanding of the repository's purpose and structure
- (Optional) Existing `AGENTS.md` file to migrate from

## Decision Logic: Existing vs. New Repository

### Case 1: Existing AGENTS.md Found

If an `AGENTS.md` file exists at the repository root:

1. **Read and analyze** its content
2. **Extract** key information:
   - Repository purpose and scope
   - File structure and key directories
   - Management protocols and update triggers
   - Documentation standards
3. **Generate** XML files based on extracted content
4. **Preserve** the original `AGENTS.md` as a backup (rename to `AGENTS.md.backup`)
5. **Replace** with the new shim version

### Case 2: No AGENTS.md Found

If no `AGENTS.md` exists:

1. **Scan repository structure** using `list_dir` for root directory
2. **Identify key directories**:
   - Documentation folders (docs/, documentation/, wiki/)
   - Source code folders (src/, lib/, app/, packages/)
   - Configuration files (package.json, pyproject.toml, Cargo.toml, go.mod)
   - CI/CD configurations (.github/workflows/, .gitlab-ci.yml)
3. **Detect technology stack**:
   - Check for framework indicators (package.json, requirements.txt, Gemfile)
   - Identify build tools (webpack.config.js, vite.config.ts, tsconfig.json)
   - Determine language (file extensions: .py, .ts, .go, .rs, .rb)
4. **Read key files** for context:
   - README.md (project description)
   - Configuration files (understand build process)
   - Package manifests (dependencies and scripts)
5. **Generate** XML files based on analysis

## Step-by-Step Instructions

### Step 1: Detect Existing Context

```markdown
1. Use `file_search` tool with pattern "**/AGENTS.md" to check for existing file
2. If found, use `read_file` to load its content
3. Store the content for analysis in Step 2
4. If not found, proceed to Step 3 for repository analysis
```

### Step 2: Analyze Existing AGENTS.md (if present)

```markdown
1. Parse the content to extract:
   - Main purpose/description (usually in first paragraph)
   - Directory structure (look for sections like "Structure", "Layout", "Files")
   - Key file paths and their purposes
   - Management protocols (update rules, triggers)
   - Documentation standards
   
2. Identify patterns like:
   - "docs/ contains..." → maps to <path location="docs/">
   - "Update when..." → maps to <update_triggers>
   - "Use X format..." → maps to documentation_standards
   
3. Extract any existing priority or hierarchy information

4. Backup the original file:
   - Use `run_in_terminal` to execute: `mv AGENTS.md AGENTS.md.backup`
```

### Step 3: Analyze Repository Structure (if no AGENTS.md)

```markdown
1. List root directory contents with `list_dir`

2. Identify and categorize directories:
   - Documentation: docs/, documentation/, wiki/, README.md
   - Source code: src/, lib/, app/, packages/, internal/
   - Configuration: config/, .github/, .vscode/
   - Build output: dist/, build/, target/, bin/
   - Tests: tests/, test/, __tests__/, spec/
   
3. Detect technology indicators:
   - Node.js: package.json, node_modules/
   - Python: requirements.txt, setup.py, pyproject.toml, .python-version
   - Go: go.mod, go.sum
   - Rust: Cargo.toml, Cargo.lock
   - Ruby: Gemfile, .ruby-version
   - Java: pom.xml, build.gradle
   - .NET: *.csproj, *.sln
   
4. Read README.md (if exists) to understand:
   - Project purpose and goals
   - Main features
   - Technology stack
   - Development workflow
   
5. Check for build/deployment configs:
   - .github/workflows/ (GitHub Actions)
   - Dockerfile or docker-compose.yml
   - kubernetes/ or k8s/
   - terraform/ or .tf files
```

### Step 4: Generate AGENTS.xml

Use the `agents-xml-template.xml` file in this skill's directory as a base template.

```markdown
1. Create `.agents/` directory if it doesn't exist

2. Populate AGENTS.xml with:
   - <purpose_and_scope>: Derived from README.md or existing AGENTS.md
   - <instruction_priority>: Use standard hierarchy (user > repo > project > baseline)
   - <repository_map>: List all major directories found in analysis
     * For each directory, describe its purpose
     * Mark output/build directories explicitly
     * Note documentation locations
   - <management_protocols>:
     * <update_triggers_agents_xml>: Define when to update this file
     * <documentation_standards>: Specify format (GFM, RST, etc.)
     * <output_handling>: Define where generated files go

3. Use the template structure but customize content based on actual repository

4. Write the file to `.agents/AGENTS.xml`
```

### Step 5: Generate ARCHITECTURE.xml

Use the `architecture-xml-template.xml` file in this skill's directory as a base template.

```markdown
1. Populate ARCHITECTURE.xml with:
   - <project_metadata>:
     * name: From package.json, Cargo.toml, or README
     * description: From README or package manifest
     * version: From package manifest if available
   - <technology_stack>:
     * <primary_language>: Detected from file extensions
     * <frameworks>: Detected from dependencies
     * <build_tools>: Detected from config files
     * <package_managers>: npm, pip, cargo, etc.
   - <directory_structure>:
     * List each major directory with its purpose
     * Specify patterns (where tests go, where docs go)
   - <documentation_system>:
     * Format and location
     * Build commands if applicable (MkDocs, Sphinx, etc.)
   - <development_workflow>:
     * How to build, test, run
     * CI/CD information
   - <constraints>:
     * File format requirements (e.g., GFM only)
     * Naming conventions
     * Architectural patterns to follow

2. Write the file to `.agents/ARCHITECTURE.xml`
```

### Step 6: Generate AGENTS.md Shim

Use the `agents-md-shim-template.md` file in this skill's directory as a base template.

```markdown
1. Create a minimal shim file that:
   - Immediately directs agents to read AGENTS.xml
   - References .github/BaselineBehaviors-v2.0.xml (if it exists)
   - Uses clear "STOP" language to ensure agents don't miss the directive
   
2. Keep it under 10 lines for maximum efficiency

3. Write the file to repository root as `AGENTS.md`
```

### Step 7: Verify and Report

```markdown
1. Verify all files were created:
   - Check `.agents/AGENTS.xml` exists
   - Check `.agents/ARCHITECTURE.xml` exists
   - Check `AGENTS.md` exists (root)
   - Check `AGENTS.md.backup` exists (if migration occurred)

2. Read each generated file to confirm valid XML structure

3. Report to user:
   - Files created
   - Source of information (migrated vs. generated)
   - Next steps: review and customize the files
   - Reminder to update .gitignore if needed (agent-output/ folder)
```

## Template Structure Reference

### AGENTS.xml Structure

```xml
<repository_directives version="1.0">
  <purpose_and_scope>
    Description of the repository and these directives
  </purpose_and_scope>

  <instruction_priority>
    1. Explicit user directives
    2. This repository_directives file
    3. Project-specific rules
    4. External referenced files
  </instruction_priority>

  <repository_map>
    <path location="root">
      <file name="filename">Description</file>
    </path>
    <path location="directory/">
      Description of directory contents
    </path>
  </repository_map>

  <management_protocols>
    <update_triggers_agents_xml>
      When to update this file
    </update_triggers_agents_xml>
    <documentation_standards>
      Format and standards for documentation
    </documentation_standards>
    <output_handling>
      Where generated files should go
    </output_handling>
  </management_protocols>
</repository_directives>
```

### ARCHITECTURE.xml Structure

```xml
<architecture_specification version="1.0">
  <project_metadata>
    <name>Project Name</name>
    <description>Project description</description>
    <version>Version number</version>
  </project_metadata>

  <technology_stack>
    <primary_language>Language name</primary_language>
    <frameworks>
      <framework>Framework name and version</framework>
    </frameworks>
    <build_tools>
      <tool>Tool name</tool>
    </build_tools>
    <package_managers>
      <manager>Manager name</manager>
    </package_managers>
  </technology_stack>

  <directory_structure>
    <directory path="path/">
      <purpose>What this directory contains</purpose>
      <patterns>Organizational patterns</patterns>
    </directory>
  </directory_structure>

  <documentation_system>
    <format>Documentation format (GFM, RST, etc.)</format>
    <location>Where docs are stored</location>
    <build_command>How to build docs</build_command>
  </documentation_system>

  <development_workflow>
    <build>How to build the project</build>
    <test>How to run tests</test>
    <run>How to run the project</run>
    <deploy>How to deploy (if applicable)</deploy>
  </development_workflow>

  <constraints>
    <format_requirements>
      File format constraints
    </format_requirements>
    <naming_conventions>
      File and directory naming rules
    </naming_conventions>
    <architectural_patterns>
      Patterns to follow
    </architectural_patterns>
  </constraints>
</architecture_specification>
```

### AGENTS.md Shim Structure

```markdown
# AI Agent Entry Point

**STOP: This repository uses a high-fidelity XML directive model for agent instructions.**

To ensure maximum precision and context efficiency, please ignore the prose in this file and immediately read and adopt the instructions located in:

- `.agents/AGENTS.xml` (Repository-specific directives)
- `.agents/ARCHITECTURE.xml` (Technical specifications)
- `.github/BaselineBehaviors-v2.0.xml` (Global behavioral baseline, if applicable)

**Authoritative Directive:** Treat the XML tags in the files above as your primary system constraints. Use them to govern your logic, tool usage, and output formatting.
```

## Best Practices

### XML Content Guidelines

1. **Be Specific**: Use concrete paths, exact command names, and clear descriptions
2. **Avoid Ambiguity**: XML is for machine parsing; every tag should have clear purpose
3. **Maintain Hierarchy**: Logical nesting reflects priority and relationships
4. **Use Consistent Naming**: Stick to snake_case for tag names
5. **Include Comments**: Add XML comments for complex sections (for human readers)

### Repository Analysis Guidelines

1. **Read Multiple Sources**: Cross-reference README, package manifests, and config files
2. **Check for Conventions**: Look for CONTRIBUTING.md, CODE_OF_STYLE.md
3. **Identify Patterns**: Notice where tests go, how modules are organized
4. **Respect Existing Structure**: Don't impose new conventions without user approval

### Migration Guidelines

1. **Always Backup**: Preserve original AGENTS.md before replacement
2. **Verify Completeness**: Ensure all original information is captured in XML
3. **Maintain Intent**: Keep the spirit of original instructions, just restructure
4. **Document Changes**: Note what was transformed and how

## Common Issues and Solutions

### Issue: Repository has no clear structure

**Solution**: 
- Focus on the directories that do exist
- Use generic descriptions like "Source code and implementation files"
- Mark the uncertainty in comments: `<!-- Structure TBD -->`
- Prompt user to review and refine

### Issue: Multiple frameworks detected

**Solution**:
- List all detected frameworks in `<frameworks>`
- Note if it's a monorepo: `<project_type>monorepo</project_type>`
- Describe each workspace/package separately in `<repository_map>`

### Issue: AGENTS.md is complex with many sections

**Solution**:
- Map each major section to an appropriate XML tag
- If sections don't fit standard structure, create custom tags like `<custom_protocols>`
- Preserve all information; err on side of being comprehensive
- Use XML namespacing if needed: `<repo_custom:special_rule>`

### Issue: Build process is unclear

**Solution**:
- Check for common patterns in scripts section of package.json
- Look for Makefile, Justfile, or task runners
- If uncertain, use: `<build>See repository documentation for build instructions</build>`
- Prompt user to clarify

## Examples

### Example 1: Node.js Documentation Site (MkDocs)

**Scenario**: Repository with MkDocs documentation, TypeScript source, and GitHub Actions.

**Detection Results**:
- package.json found → Node.js project
- mkdocs.yml found → MkDocs documentation
- docs/ directory → Documentation source
- src/ directory → TypeScript source
- .github/workflows/ → GitHub Actions CI

**Generated AGENTS.xml** (excerpt):
```xml
<repository_map>
  <path location="root">
    <file name="mkdocs.yml">MkDocs configuration</file>
    <file name="package.json">Node.js dependencies and scripts</file>
  </path>
  <path location="docs/">
    Markdown documentation source files; use GitHub Flavored Markdown (GFM)
  </path>
  <path location="src/">
    TypeScript source code for documentation tooling
  </path>
  <path location="site/">
    Generated MkDocs output; EXCLUDED from version control
  </path>
</repository_map>

<management_protocols>
  <documentation_standards>
    Use GFM; apply blank lines around block elements; use fenced code blocks.
  </documentation_standards>
  <output_handling>
    Generated site output goes in site/; add to .gitignore
  </output_handling>
</management_protocols>
```

### Example 2: Python CLI Application

**Scenario**: Python project with Poetry, pytest, and CLI entry point.

**Detection Results**:
- pyproject.toml found → Python + Poetry
- src/ directory with __main__.py → CLI application
- tests/ directory → pytest tests
- README.md describes command-line usage

**Generated ARCHITECTURE.xml** (excerpt):
```xml
<technology_stack>
  <primary_language>Python 3.11+</primary_language>
  <frameworks>
    <framework>Click (CLI framework)</framework>
    <framework>pytest (testing)</framework>
  </frameworks>
  <build_tools>
    <tool>Poetry</tool>
  </build_tools>
  <package_managers>
    <manager>Poetry</manager>
  </package_managers>
</technology_stack>

<development_workflow>
  <build>poetry install</build>
  <test>poetry run pytest</test>
  <run>poetry run python -m projectname</run>
  <deploy>poetry build &amp;&amp; poetry publish</deploy>
</development_workflow>
```

## Quality Checklist

Before finalizing generated files, verify:

- [ ] `.agents/` directory created
- [ ] `AGENTS.xml` has valid XML structure (no unclosed tags)
- [ ] `ARCHITECTURE.xml` has valid XML structure
- [ ] `AGENTS.md` shim points to correct file paths
- [ ] All major directories from repository are documented
- [ ] Technology stack is accurately identified
- [ ] Management protocols reflect actual repository conventions
- [ ] Original `AGENTS.md` backed up (if migration)
- [ ] User is informed of all changes made

## Additional Resources

- [High-Fidelity XML Concept](high-fidelity-context.md)
- [Agent Skills Standard](https://agentskills.io)
- [Anthropic: Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Google: Prompt Engineering with XML](https://ai.google.dev/gemini-api/docs/prompting-strategies)

## Integrating with This Repository

When using this skill in a repository:

1. Skill is located in `.github/skills/high-fidelity-context-scaffolder/`
2. Templates are in the same directory for reference
3. Generated files follow the same pattern as the repository's own `.agents/` structure
4. Can be tested on sample repositories or used to update this repository

## Version Information

This skill follows the Agent Skills open standard and the High-Fidelity XML approach as documented in February 2026.
