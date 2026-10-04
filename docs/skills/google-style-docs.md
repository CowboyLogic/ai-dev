# Google Style Docs

Write and review technical documentation following the
[Google Developer Documentation Style Guide](https://developers.google.com/style). Covers
document structure, voice and tone, formatting of code and UI elements, step-by-step
instructions, inclusive and accessible language, and word choice.

- **Skill name:** `google-style-docs`
- **Source:** [skills/google-style-docs](https://github.com/CowboyLogic/ai-dev/tree/main/skills/google-style-docs)

---

## What it does

The skill applies Google's style principles — clarity, consistency, accessibility,
inclusivity, and writing for a global audience — whenever an agent writes new documentation
or reviews existing docs. It ends with a quality checklist an agent uses to review a draft,
and includes a quick reference and a complete sample how-to guide written to the style.

## Where it applies

Use it for tutorials, how-to guides, conceptual overviews, and API reference. The skill
treats Google's guide as recommendations, so an established project convention takes
priority when the two conflict.

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
