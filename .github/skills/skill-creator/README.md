# Skill Creator - Agent Skill

This skill teaches AI agents how to create new Agent Skills following the Agent Skills open standard.

## What's Included

- **SKILL.md** - The main skill file with comprehensive instructions for creating skills
- **skill-template.md** - A template for creating new SKILL.md files
- **validate-skill.py** - Python script to validate skills against the standard
- **README.md** - This file

## Usage

When working with an AI agent (GitHub Copilot, Claude, etc.), this skill will be automatically discovered when you ask to:

- "Create a new skill for..."
- "Write a SKILL.md file for..."
- "How do I create an agent skill?"
- "Help me document this workflow as a skill"

The agent will follow the instructions in SKILL.md to create properly formatted skills.

## Manual Usage

### Using the Template

Copy `skill-template.md` to a new skill directory and replace all placeholders marked with `{{PLACEHOLDER}}`.

### Validating a Skill

Run the validation script to check a skill for common issues:

```bash
python validate-skill.py path/to/skill-directory
```

Example:
```bash
python validate-skill.py .github/skills/my-new-skill/
```

The validator checks for:
- ✅ Correct SKILL.md filename and location
- ✅ Required frontmatter fields (name, description)
- ✅ Proper name format (lowercase with hyphens)
- ✅ Directory name matches skill name
- ⚠️ Recommended sections (examples, when to use, etc.)
- ⚠️ Code blocks and numbered steps
- ⚠️ Supporting files referenced in SKILL.md

## Skill Structure

Every skill should have this structure:

```
.github/skills/skill-name/
├── SKILL.md                 # Required: Main skill file
├── README.md                # Optional: Additional documentation
├── example-file.txt         # Optional: Example files
├── script.py                # Optional: Helper scripts
└── template.json            # Optional: Templates
```

## References

- [Agent Skills Standard](https://agentskills.io)
- [GitHub Copilot Agent Skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [Example Skills Repository](https://github.com/anthropics/skills)

## License

MIT
