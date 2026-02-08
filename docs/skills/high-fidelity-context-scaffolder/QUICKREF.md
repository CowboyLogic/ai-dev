# Quick Reference: High-Fidelity XML Scaffolder

Fast lookup guide for agents using this skill.

## Decision Tree

```
Does AGENTS.md exist?
├─ YES → Migrate Mode
│  ├─ Read AGENTS.md
│  ├─ Extract content sections
│  ├─ Map to XML structure
│  ├─ Backup original
│  └─ Generate files
│
└─ NO → Analysis Mode
   ├─ Scan repository structure
   ├─ Detect technology stack
   ├─ Read README.md
   ├─ Identify key directories
   └─ Generate files
```

## Generation Checklist

### Step 1: Detection
- [ ] Search for AGENTS.md in root
- [ ] Read content if found
- [ ] Determine mode (Migrate vs. Analysis)

### Step 2: Repository Analysis
- [ ] List root directory
- [ ] Identify major directories (src/, docs/, tests/)
- [ ] Detect tech stack (package.json, pyproject.toml, etc.)
- [ ] Read README.md for context
- [ ] Check for build configs

### Step 3: Generate AGENTS.xml
- [ ] Create `.agents/` directory
- [ ] Load template
- [ ] Fill in purpose and scope
- [ ] Map repository structure
- [ ] Define management protocols
- [ ] Write to `.agents/AGENTS.xml`

### Step 4: Generate ARCHITECTURE.xml
- [ ] Load template
- [ ] Fill in project metadata
- [ ] Document technology stack
- [ ] Map directory structure
- [ ] Define development workflow
- [ ] Define constraints
- [ ] Write to `.agents/ARCHITECTURE.xml`

### Step 5: Generate AGENTS.md Shim
- [ ] Load shim template
- [ ] Verify file paths are correct
- [ ] Write to root `AGENTS.md`

### Step 6: Verification
- [ ] Verify all files created
- [ ] Validate XML structure (no unclosed tags)
- [ ] Check file paths are correct
- [ ] Report results to user

## Common Placeholders to Replace

### AGENTS.xml
- `{{DESCRIBE_REPOSITORY_PURPOSE_AND_SCOPE}}`
- `{{DESCRIBE_README_PURPOSE}}`
- `{{CONFIG_FILE}}` and `{{DESCRIBE_CONFIG_FILE_PURPOSE}}`
- `{{DOCS_DIRECTORY}}`, `{{SOURCE_DIRECTORY}}`, `{{TESTS_DIRECTORY}}`
- `{{OUTPUT_DIRECTORY}}`, `{{CONFIG_DIRECTORY}}`
- `{{DESCRIBE_DOCUMENTATION_STANDARDS}}`
- `{{DESCRIBE_OUTPUT_HANDLING_POLICY}}`

### ARCHITECTURE.xml
- `{{PROJECT_NAME}}`, `{{PROJECT_DESCRIPTION}}`, `{{PROJECT_VERSION}}`
- `{{REPOSITORY_URL}}`
- `{{PRIMARY_LANGUAGE}}`
- `{{FRAMEWORK_NAME_AND_VERSION}}`
- `{{BUILD_TOOL}}`, `{{PACKAGE_MANAGER}}`
- `{{DIRECTORY_PATH}}`, `{{DESCRIBE_DIRECTORY_PURPOSE}}`
- `{{SETUP_COMMAND}}`, `{{BUILD_COMMAND}}`, `{{TEST_COMMAND}}`, `{{RUN_COMMAND}}`
- `{{DOCUMENTATION_FORMAT}}`, `{{DOCUMENTATION_BUILD_COMMAND}}`

## Technology Detection Patterns

| File/Directory | Indicates |
|----------------|-----------|
| package.json | Node.js/npm project |
| pyproject.toml | Python/Poetry project |
| requirements.txt | Python/pip project |
| Cargo.toml | Rust/Cargo project |
| go.mod | Go project |
| pom.xml | Java/Maven project |
| build.gradle | Java/Gradle project |
| *.csproj, *.sln | .NET project |
| Gemfile | Ruby/Bundler project |
| composer.json | PHP/Composer project |
| mkdocs.yml | MkDocs documentation |
| Dockerfile | Docker containerization |
| .github/workflows/ | GitHub Actions CI/CD |

## XML Structure Quick Reference

### AGENTS.xml Basic Structure
```xml
<repository_directives version="1.0">
  <purpose_and_scope>...</purpose_and_scope>
  <instruction_priority>...</instruction_priority>
  <repository_map>
    <path location="...">...</path>
  </repository_map>
  <management_protocols>
    <update_triggers_agents_xml>...</update_triggers_agents_xml>
    <documentation_standards>...</documentation_standards>
    <output_handling>...</output_handling>
  </management_protocols>
</repository_directives>
```

### ARCHITECTURE.xml Basic Structure
```xml
<architecture_specification version="1.0">
  <project_metadata>...</project_metadata>
  <technology_stack>...</technology_stack>
  <directory_structure>...</directory_structure>
  <documentation_system>...</documentation_system>
  <development_workflow>...</development_workflow>
  <constraints>...</constraints>
</architecture_specification>
```

## Tool Usage Patterns

### File Operations
```markdown
- file_search: Find AGENTS.md or config files
- read_file: Load content for analysis
- list_dir: Scan directory structure
- create_directory: Create .agents/ folder
- create_file: Write generated XML files
- run_in_terminal: Backup original AGENTS.md
```

### Search Patterns
```markdown
- Search for AGENTS.md: file_search with pattern "**/AGENTS.md"
- Find config files: file_search with pattern "**/{package.json,pyproject.toml,Cargo.toml}"
- List root: list_dir with path to repository root
```

## Validation Tips

### XML Validation
- Check all tags are closed properly
- Verify no angle brackets in content (use &lt; &gt;)
- Ensure proper nesting hierarchy
- Check version attribute exists on root element

### Content Validation
- All major directories documented
- Technology stack accurately identified
- File paths use correct separators (/)
- Placeholders are replaced with real values
- Management protocols reflect repository reality

## Error Recovery

### Issue: Can't determine technology stack
**Solution**: Look for multiple indicators, check package manager files, examine file extensions in src/

### Issue: Complex repository structure
**Solution**: Document major directories first, use generic descriptions, add comments for clarification

### Issue: Migration loses information
**Solution**: Review original AGENTS.md thoroughly, create custom XML tags if needed, preserve all sections

### Issue: XML validation fails
**Solution**: Check for unclosed tags, escape special characters (&, <, >), verify proper nesting

## Testing Checklist

- [ ] Files created in correct locations
- [ ] XML validates (no syntax errors)
- [ ] Shim points to correct paths
- [ ] All placeholders replaced
- [ ] Technology stack accurate
- [ ] Directory map complete
- [ ] Original file backed up (if applicable)
- [ ] User informed of changes

## Quick Commands Reference

### Backup Original
```bash
mv AGENTS.md AGENTS.md.backup
```

### Create Directory
```bash
mkdir -p .agents
```

### Validate XML (if xmllint available)
```bash
xmllint --noout .agents/AGENTS.xml
xmllint --noout .agents/ARCHITECTURE.xml
```

## Tags You Can Add

### Optional AGENTS.xml Tags
- `<version_control>`
- `<testing_protocols>`
- `<deployment_protocols>`
- `<security_requirements>`
- `<api_guidelines>`

### Optional ARCHITECTURE.xml Tags
- `<continuous_integration>`
- `<data_layer>`
- `<api_specifications>`
- `<infrastructure>`
- `<monitoring>`
- `<localization>`
- `<accessibility>`

## Field Mapping (AGENTS.md → AGENTS.xml)

| AGENTS.md Section | AGENTS.xml Tag |
|-------------------|----------------|
| Introduction/Overview | `<purpose_and_scope>` |
| Priority/Precedence | `<instruction_priority>` |
| File structure listing | `<repository_map>` |
| "Update when..." rules | `<update_triggers_agents_xml>` |
| Format requirements | `<documentation_standards>` |
| Output/build rules | `<output_handling>` |
| Custom sections | Create custom tags |

---

**Remember**: Be specific, maintain structure, and verify all outputs!
