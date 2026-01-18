---
name: skill-creator
description: Guide for creating new Agent Skills following the Agent Skills open standard. Use this when asked to create a new skill, write a SKILL.md file, or teach Copilot how to perform a specific task.
license: MIT
---

# Agent Skill Creation Guide

This skill helps you create new Agent Skills that follow the Agent Skills open standard (https://agentskills.io).

## When to Use This Skill

Use this skill when:
- Asked to create a new skill for Copilot or other agents
- Need to document a repeatable workflow as a skill
- Want to package domain expertise for agent use
- Creating skills for project-level or personal use

## Skill Basics

Agent Skills are folders containing instructions, scripts, and resources that agents can discover and use to perform specialized tasks more accurately and efficiently.

### Storage Locations

- **Project skills**: `.github/skills/` or `.claude/skills/` (specific to one repository)
- **Personal skills**: `~/.copilot/skills/` or `~/.claude/skills/` (shared across projects)

## Creating a New Skill

### Step 1: Plan the Skill

Before creating a skill, determine:

1. **Purpose**: What specific task or domain does this skill address?
2. **Scope**: Is this project-specific or broadly applicable?
3. **Trigger conditions**: When should Copilot use this skill?
4. **Required context**: What information, tools, or resources does the skill need?
5. **Success criteria**: How will you know the skill is working correctly?

### Step 2: Create the Directory Structure

1. Create a subdirectory for the skill
   - Use lowercase names
   - Use hyphens for spaces (e.g., `webapp-testing`, `api-debugging`)
   - Name should match the skill's `name` in frontmatter
   - Location: `.github/skills/<skill-name>/` for project skills

2. Create the `SKILL.md` file (required)
   - Must be named exactly `SKILL.md`
   - Contains YAML frontmatter and Markdown instructions

3. Add supporting files (optional)
   - Scripts (e.g., `convert.py`, `test.sh`)
   - Examples (e.g., `example-config.json`)
   - Templates (e.g., `template.md`)
   - Documentation (e.g., `README.md`)

### Step 3: Write the SKILL.md File

The `SKILL.md` file must include:

#### Required YAML Frontmatter

```yaml
---
name: skill-name-here
description: Clear description of what the skill does and when Copilot should use it
---
```

**Frontmatter fields:**

- `name` (required): Unique identifier, lowercase, hyphens for spaces
- `description` (required): Describes purpose and trigger conditions
- `license` (optional): License that applies to this skill

#### Markdown Body Structure

The body should include:

1. **Overview**: What the skill does and why it exists
2. **When to use**: Clear trigger conditions
3. **Step-by-step instructions**: Numbered, actionable steps
4. **Tool references**: Specific tools or commands to use
5. **Examples**: Concrete examples of usage
6. **Best practices**: Tips for optimal results
7. **Common pitfalls**: What to avoid

### Step 4: Write Clear Instructions

**Effective instruction patterns:**

✅ **Good**: Specific, actionable, tool-aware
```markdown
1. Use the `list_workflow_runs` tool to look up recent workflow runs
2. Analyze the output to identify failed jobs
3. Use the `get_job_logs` tool with the job ID to retrieve detailed logs
```

❌ **Avoid**: Vague, generic, tool-agnostic
```markdown
1. Check the workflow status
2. Look at the logs
3. Fix the problem
```

**Best practices for instructions:**

- Use numbered steps for sequential workflows
- Reference specific tools, APIs, or commands by name
- Include decision points and conditional logic
- Provide examples inline
- Use code blocks for commands, scripts, or configuration
- Be explicit about expected inputs and outputs
- Mention error handling and fallback strategies

### Step 5: Add Supporting Resources

If your skill needs additional files:

1. **Scripts**: Place executable scripts in the skill directory
   - Name scripts descriptively (e.g., `convert-svg-to-png.sh`)
   - Include shebang lines and comments
   - Make scripts cross-platform when possible

2. **Examples**: Provide example files the agent can reference
   - Use realistic, complete examples
   - Add comments explaining key sections
   - Show multiple scenarios if needed

3. **Templates**: Include templates for repetitive structures
   - Use placeholders clearly (e.g., `{{PLACEHOLDER}}`)
   - Document required substitutions

### Step 6: Test the Skill

1. Place the skill in the appropriate location
2. Restart Copilot or your agent if needed
3. Try prompts that should trigger the skill
4. Verify the agent follows the instructions correctly
5. Iterate based on agent behavior

## Skill Design Principles

### 1. Clarity and Specificity

- Be explicit about steps, tools, and expected outcomes
- Avoid ambiguity that could lead to hallucination
- Use precise terminology

### 2. Tool Integration

- Reference specific tools by name (e.g., MCP server tools, CLI commands)
- Explain how to use each tool in context
- Provide fallback options when tools might not be available

### 3. Contextual Awareness

- Include information about when NOT to use the skill
- Describe prerequisites or requirements
- Mention related skills or workflows

### 4. Maintainability

- Keep skills focused on one task or domain
- Use modular structure for complex workflows
- Version control skills alongside code

### 5. Discoverability

- Write descriptions that match user intent and language
- Include common variations of terminology
- Make trigger conditions obvious

## Skills vs. Custom Instructions

**Use Skills when:**
- Instructions are detailed and multi-step
- Context is only needed for specific tasks
- You want to package reusable workflows
- Instructions include scripts or resources

**Use Custom Instructions when:**
- Guidelines apply to almost every task
- Instructions are simple and brief
- Context is always relevant (e.g., coding standards)

## Example Skill Template

```markdown
---
name: example-skill-name
description: Brief description of what this skill does and when to use it
---

# Skill Title

Brief overview of the skill's purpose.

## When to Use This Skill

Use this skill when:
- Condition 1
- Condition 2
- Condition 3

## Prerequisites

- Required tool or permission
- Required knowledge or context
- Required files or setup

## Instructions

1. First step with specific actions
   - Detail or sub-step
   - Another detail

2. Second step referencing specific tools
   ```bash
   command-example --with-flags
   ```

3. Third step with decision point
   - If condition A: do this
   - If condition B: do that

4. Final step with verification
   - How to confirm success
   - What to check

## Examples

### Example 1: Common scenario

Description of the scenario.

```language
code or command example
```

Expected output or result.

### Example 2: Edge case

Description of the edge case.

```language
code or command example
```

Expected output or result.

## Best Practices

- Best practice 1
- Best practice 2
- Best practice 3

## Common Issues

**Issue**: Description of common problem
**Solution**: How to resolve it

**Issue**: Another common problem
**Solution**: Resolution steps

## Additional Resources

- Link to related documentation
- Link to tool reference
- Link to related skills
```

## Quality Checklist

Before finalizing a skill, verify:

- [ ] Frontmatter includes required `name` and `description`
- [ ] Skill name is lowercase with hyphens
- [ ] Description clearly states when to use the skill
- [ ] Instructions are numbered and actionable
- [ ] Specific tools and commands are named
- [ ] Examples are included and realistic
- [ ] File is named exactly `SKILL.md`
- [ ] Directory name matches skill name in frontmatter
- [ ] Supporting files (if any) are properly referenced
- [ ] Skill has been tested with actual agent prompts
- [ ] Instructions are clear and unambiguous

## Common Mistakes to Avoid

1. **Vague descriptions**: "Help with debugging" → "Guide for debugging failing GitHub Actions workflows"
2. **Generic instructions**: "Fix the issue" → "Use `get_job_logs` tool to retrieve logs, analyze error messages, check for common patterns..."
3. **Missing trigger conditions**: Add clear "when to use" guidance in description
4. **Wrong filename**: Must be `SKILL.md`, not `skill.md` or `README.md`
5. **No examples**: Always include at least one concrete example
6. **Tool-agnostic**: Reference specific tools the agent has access to
7. **Overly broad scope**: Keep skills focused on one task or domain
8. **Missing error handling**: Include what to do when things go wrong

## Supporting Files in This Skill

This skill includes several helpful resources:

- **GETTING-STARTED.md**: A beginner-friendly guide with a complete walkthrough of creating your first skill. Start here if you're new to Agent Skills.

- **QUICKREF.md**: A quick reference guide with checklists, common patterns, and testing tips. Use this for fast lookups while creating skills.

- **skill-template.md**: A ready-to-use template for creating new SKILL.md files. Copy this template and replace the placeholders to quickly create properly formatted skills.

- **validate-skill.py**: A Python validation script that checks skills for compliance with the Agent Skills standard. Run it with `python validate-skill.py path/to/skill/` to verify your skill has proper frontmatter, naming, and recommended sections.

- **example-skill.md**: A complete example skill (GitHub Actions debugging) that demonstrates all the principles and patterns described in this guide. Reference this when creating similar workflow-based skills.

## Integrating with This Repository

When creating skills for this repository:

1. Place project skills in `.github/skills/`
2. Create one directory per skill
3. Follow the naming conventions in this guide
4. Use `validate-skill.py` to check your new skills before committing
5. Consider using `skill-template.md` as a starting point
6. Document any custom MCP tools or repository-specific context
7. Test skills with GitHub Copilot CLI, Copilot coding agent, or VS Code
8. Consider whether documentation in `docs/` should reference the skill

## References

- [Agent Skills Standard](https://agentskills.io)
- [Agent Skills Specification](https://agentskills.io/specification)
- [GitHub Copilot Agent Skills Documentation](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [Example Skills Repository](https://github.com/anthropics/skills)
- [GitHub Awesome Copilot Collection](https://github.com/github/awesome-copilot)

## Version Information

This skill follows the Agent Skills open standard as documented in January 2026.
Compatible with GitHub Copilot, Claude, VS Code, and other skills-supporting agents.
