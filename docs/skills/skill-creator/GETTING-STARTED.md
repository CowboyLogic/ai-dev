# Getting Started with the Skill Creator

This guide shows you how to use the skill-creator skill to create your first Agent Skill.

## For AI Agents (Automatic)

If you're an AI agent (GitHub Copilot, Claude, etc.), you'll automatically use this skill when users ask questions about creating skills. Just follow the instructions in SKILL.md.

## For Humans (Manual)

### Quick Start: Create Your First Skill

**Step 1: Choose a task to document**

Think of a repeatable workflow or specialized knowledge you want to capture. Examples:
- Debugging a specific type of error
- Following a code review checklist
- Setting up a particular technology stack
- Analyzing performance metrics

**Step 2: Copy the template**

```bash
# Create a new skill directory
mkdir .github/skills/my-new-skill

# Copy the template
cp .github/skills/skill-creator/skill-template.md .github/skills/my-new-skill/SKILL.md
```

**Step 3: Fill in the template**

Open `.github/skills/my-new-skill/SKILL.md` and replace all `{{PLACEHOLDERS}}`:

```yaml
---
name: my-new-skill
description: A clear description of what this does and when to use it
---
```

**Step 4: Write the instructions**

Follow these guidelines:
- Use numbered steps for sequential tasks
- Reference specific tools or commands
- Include at least one example
- Add "When to Use" conditions

**Step 5: Validate your skill**

```bash
python .github/skills/skill-creator/validate-skill.py .github/skills/my-new-skill/
```

Fix any errors shown by the validator.

**Step 6: Test with an agent**

1. Restart your AI agent (if needed)
2. Ask a question that should trigger your skill
3. Verify the agent uses your instructions
4. Iterate based on results

## Example Walkthrough

Let's create a simple skill for reviewing pull requests.

### 1. Create the directory

```bash
mkdir .github/skills/pr-review-checklist
```

### 2. Create SKILL.md

```markdown
---
name: pr-review-checklist
description: Systematic checklist for reviewing pull requests. Use when asked to review a PR or provide code review feedback.
---

# Pull Request Review Checklist

A structured approach to conducting thorough code reviews.

## When to Use This Skill

Use when:
- Asked to review a pull request
- Providing code review feedback
- Checking if a PR is ready to merge

## Instructions

1. **Check PR description**
   - Verify it explains what changed and why
   - Confirm it links to related issues
   - Check if it includes testing instructions

2. **Review code changes**
   - Look for potential bugs or logic errors
   - Check naming conventions and code style
   - Verify error handling is appropriate
   - Ensure no sensitive data is exposed

3. **Verify tests**
   - Check if new code has test coverage
   - Run tests locally if possible
   - Look for edge cases that should be tested

4. **Check documentation**
   - Verify README updates if needed
   - Check if new features are documented
   - Ensure comments explain complex logic

5. **Provide feedback**
   - Be constructive and specific
   - Suggest alternatives when requesting changes
   - Approve if all checks pass

## Examples

### Example 1: Security Review

```markdown
**Security Concern**: API keys visible in code
**Suggestion**: Move credentials to environment variables
**Reference**: See `.env.example` for the pattern we use
```

### Example 2: Performance Review

```markdown
**Performance**: Database query in loop (lines 45-52)
**Suggestion**: Fetch all records once before the loop
**Impact**: Reduces queries from N+1 to 1
```

## Best Practices

- Focus on important issues first
- Be specific with line numbers
- Explain the "why" behind suggestions
- Acknowledge good practices you see
```

### 3. Validate

```bash
python .github/skills/skill-creator/validate-skill.py .github/skills/pr-review-checklist/
```

### 4. Test

Ask Copilot: "Please review this pull request" - it should now follow your checklist!

## Tips for Success

### Make Skills Discoverable

Write descriptions that match how users will ask:
- ✅ "Use when debugging API failures"
- ❌ "API-related helper"

### Be Specific with Tools

Reference actual tools the agent has access to:
- ✅ "Use the `list_workflow_runs` tool"
- ❌ "Check the workflow status"

### Include Real Examples

Show concrete examples, not abstract patterns:
- ✅ Complete code snippet with real values
- ❌ "Do something like X"

### Keep Skills Focused

One skill = One task or domain:
- ✅ "GitHub Actions debugging"
- ❌ "General debugging and testing"

## Common Questions

**Q: Where should I put my skill?**  
A: For project-specific skills, use `.github/skills/`. For personal skills you'll use across projects, use `~/.copilot/skills/`.

**Q: How do I know if my skill is being used?**  
A: Ask the agent a question that should trigger it. Well-written agents will mention when they're using a skill.

**Q: Can I update a skill after creating it?**  
A: Yes! Skills are just Markdown files. Edit them anytime and the agent will use the updated version.

**Q: Do I need to restart my agent after creating a skill?**  
A: It depends on the agent. GitHub Copilot and Claude typically discover new skills automatically, but you may need to reload VS Code.

**Q: Can I share skills with my team?**  
A: Yes! Skills in `.github/skills/` are committed to the repository and available to everyone working on the project.

## Need Help?

- Read the full guide: [SKILL.md](SKILL.md)
- Check the quick reference: [QUICKREF.md](QUICKREF.md)
- See a complete example: [example-skill.md](example-skill.md)
- Use the template: [skill-template.md](skill-template.md)

## Next Steps

1. Create your first skill using this guide
2. Test it with your AI agent
3. Share useful skills with your team
4. Iterate based on how well agents follow the instructions

Happy skill building! 🚀
