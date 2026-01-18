# Quick Reference: Creating Agent Skills

## Minimal Skill Structure

```markdown
---
name: my-skill-name
description: What it does and when to use it
---

# Skill Title

Instructions go here.
```

## File Checklist

- [ ] Directory: `.github/skills/my-skill-name/`
- [ ] File: `SKILL.md` (exact casing)
- [ ] Name: lowercase-with-hyphens
- [ ] Frontmatter: `name` and `description` fields
- [ ] Body: Clear, numbered instructions
- [ ] Examples: At least one concrete example

## Validation

```bash
python validate-skill.py .github/skills/my-skill-name/
```

## Common Patterns

### Tool-based workflow
```markdown
1. Use `tool_name` to retrieve data
2. Analyze the results for patterns
3. Use `another_tool` with specific parameters
4. Verify the outcome
```

### Conditional logic
```markdown
1. Check the current state
   - If condition A: proceed to step 2
   - If condition B: skip to step 4
2. Perform action for condition A
...
```

### Error handling
```markdown
1. Attempt primary approach using `tool_name`
2. If that fails, try fallback:
   - Check for common error X
   - If X occurs, do Y
3. Verify success criteria
```

## Trigger Description Tips

✅ Good triggers:
- "Use when debugging API failures"
- "Guide for creating React components with TypeScript"
- "Use when asked to optimize database queries"

❌ Vague triggers:
- "Helps with coding"
- "Useful for development"
- "General purpose assistant"

## Name vs. Description

- **Name**: Identifier (e.g., `api-debugging-guide`)
- **Description**: When + What (e.g., "Guide for debugging API failures. Use when API endpoints return errors or unexpected responses.")

## Testing Your Skill

1. Create the skill in `.github/skills/`
2. Restart Copilot or agent
3. Ask a question that should trigger it
4. Verify the agent references your skill
5. Check if instructions are followed correctly
6. Iterate based on behavior

## Resources

- Full guide: `SKILL.md` in this directory
- Template: `skill-template.md`
- Example: `example-skill.md`
- Validator: `validate-skill.py`
