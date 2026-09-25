# Google Style Docs

Write and review technical documentation following the
[Google Developer Documentation Style Guide](https://developers.google.com/style). Covers
document structure, voice and tone, formatting of code and UI elements, step-by-step
instructions, inclusive and accessible language, and word choice.

- **Skill name:** `google-style-docs`
- **Last updated:** 2026-04-19
- **Source:** [skills/google-style-docs](https://github.com/CowboyLogic/ai-dev/tree/main/skills/google-style-docs)

---

## What it does

The skill applies Google's style principles — clarity, consistency, accessibility,
inclusivity, and writing for a global audience — whenever an agent writes new documentation
or reviews existing docs. It works for tutorials, how-to guides, conceptual overviews, and
API reference.

**Guidance areas:**

| Area | Key rules |
|------|-----------|
| Structure | Plan purpose, audience, scope, and document type; outline from overview to next steps |
| Titles and introductions | Sentence case, task-oriented titles; state the outcome in the first sentence |
| Voice and tone | Second person, active voice, present tense, direct and conversational |
| Formatting | Backticks for code, bold for UI elements, consistent placeholders such as `PROJECT_ID` |
| Instructions | Numbered steps, one action per step, imperative mood, expected results shown |
| Inclusive and accessible writing | Gender-neutral pronouns, allowlist/blocklist, descriptive link text, alt text, no skipped heading levels |
| Lists | Parallel structure; periods only for complete sentences |
| Code examples | Self-contained, runnable, with comments that explain intent and realistic error handling |
| Word choice | "Click" not "click on", "sign in" not "log in", no "please", "simply", or Latin abbreviations |

The skill ends with a quality checklist that an agent uses to review a draft for structure,
style, formatting, accessibility, and accuracy.

> [!NOTE]
> The skill treats Google's guide as recommendations. When it conflicts with an established
> project convention, consistency within the project takes priority.

---

## Included files

| File | Contents |
|------|----------|
| `SKILL.md` | Full instructions, examples, word list, and quality checklist |
| `QUICKREF.md` | Quick-reference checklists and common patterns |
| `example-deployment-guide.md` | A complete how-to guide written to the style |

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill google-style-docs -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill google-style-docs --agent <agent> -g
```

### Verify installation

```bash
npx skills ls -g
```
