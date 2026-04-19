# Google Style Documentation Quick Reference

A fast reference for Google documentation style guidelines. Use this for quick lookups while writing or reviewing documentation.

## Quick Checklist

### Title and Introduction
- [ ] Title uses sentence case (only capitalize first word and proper nouns)
- [ ] Title is task-oriented (e.g., "Set up authentication")
- [ ] First paragraph states purpose and outcome
- [ ] No "This document..." or "In this guide..." phrases

### Voice and Tone
- [ ] Use "you" (second person)
- [ ] Use active voice
- [ ] Use present tense
- [ ] Be conversational and direct
- [ ] Use contractions when natural

### Instructions
- [ ] Number steps sequentially
- [ ] One action per step
- [ ] Use imperative mood (commands)
- [ ] Show expected results
- [ ] Include verification steps

### Formatting
- [ ] Inline code uses backticks: `code`
- [ ] UI elements are bold: **Button Name**
- [ ] Placeholders: ALL_CAPS or `<angle-brackets>`
- [ ] Links use descriptive text
- [ ] Proper heading hierarchy (no skipped levels)

### Code Examples
- [ ] Complete and runnable
- [ ] Include all necessary imports
- [ ] Add explanatory comments
- [ ] Show error handling
- [ ] Specify language in code blocks

### Accessibility
- [ ] Use inclusive language
- [ ] Gender-neutral pronouns (they/their)
- [ ] Descriptive link text (not "click here")
- [ ] Alt text for images
- [ ] Proper heading hierarchy

## Quick Commands

### Formatting Elements

| Element | Format | Example |
|---------|--------|---------|
| Inline code | Backticks | `variable_name` |
| UI elements | Bold | Click **Save** |
| Placeholders | ALL_CAPS or brackets | `PROJECT_ID` or `<project-id>` |
| File paths | Backticks, forward slash | `config/settings.json` |
| Command line | Code block with bash | ```bash<br>command --flag``` |

### Document Structure Template

```markdown
# Task-oriented title

Brief overview paragraph stating purpose and outcome.

## Before you begin

- Prerequisite 1
- Prerequisite 2

## Main task heading

1. First step with action.
   Result or explanation.

2. Second step:
   ```language
   code example
   ```
   Expected output.

3. Final step and verification.

## What's next

- [Related task 1](link)
- [Related task 2](link)
```

## Word Choice

### Use These ✅

| Instead of | Use |
|------------|-----|
| click on | click |
| type in | enter |
| e.g. | for example |
| i.e. | that is |
| log in / login | sign in |
| log out | sign out |
| checkbox | checkbox (one word) |
| email | email (not e-mail) |
| filename | filename (one word) |
| dropdown | drop-down (adjective) |

### Avoid These ❌

| Don't Use | Why | Use Instead |
|-----------|-----|-------------|
| please | Unnecessary politeness | (Just give the instruction) |
| simply, just, easy | Subjective, condescending | (Omit or be specific) |
| obviously, clearly | If it were, you wouldn't document it | (Omit) |
| whitelist/blacklist | Not inclusive | allowlist/blocklist |
| master/slave | Not inclusive | primary/secondary |
| sanity check | Ableist | verify, check |
| he/she, his/her | Not inclusive | they, their |

## Common Patterns

### API Reference Entry

```markdown
## functionName()

Brief description of what the function does.

### Syntax

```language
functionName(param1, param2)
```

### Parameters

- `param1` (type, required/optional): Description.
- `param2` (type, required/optional): Description.

### Returns

Description of return value.

### Example

```language
// Explanatory comment
const result = functionName(arg1, arg2);
```

### Exceptions

- Error type: When it occurs.
```

### Procedural Steps

```markdown
## Task heading

1. First action.
   ```bash
   command --flag VALUE
   ```
   Expected result: Description.

2. Second action.
   Additional detail or context.

3. Verify the result:
   - Expected behavior 1
   - Expected behavior 2
```

### Note/Caution/Warning

```markdown
**Note:** Additional helpful information.

**Caution:** Warning about potential issues.

**Warning:** Critical alert about data loss or security.
```

## Lists

### Bulleted Lists (Unordered)
- Use for non-sequential items
- Start with capital letter
- Use parallel structure
- Use periods for complete sentences

### Numbered Lists (Sequential)
1. Use for steps or ranked items
2. Start with capital letter
3. Always use periods for all items

## Code Block Languages

Common language identifiers for code blocks:

```
```bash         # Shell commands
```python       # Python code
```javascript   # JavaScript
```typescript   # TypeScript
```json         # JSON data
```yaml         # YAML configuration
```java         # Java
```csharp       # C#
```go           # Go
```sql          # SQL queries
```
```

## Testing Your Documentation

1. **Read aloud**: Does it sound natural?
2. **Follow steps**: Can you complete the task using only the documentation?
3. **Test code**: Do all examples run without errors?
4. **Check links**: Do all hyperlinks work?
5. **Verify accuracy**: Is all technical information correct?
6. **Scan for clarity**: Can someone skim and find what they need?

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Passive voice: "The file is created by the system" | Active: "The system creates the file" |
| Future tense: "The function will return..." | Present: "The function returns..." |
| Multiple actions per step | Split into separate numbered steps |
| Code without context | Add comments, imports, setup code |
| Vague placeholders | Explain what each placeholder represents |
| Inconsistent terminology | Choose one term and use throughout |
| Generic link text like "here" | Use descriptive text: "authentication guide" |

## Voice Examples

### Second Person ✅
"You can configure the settings in the admin panel."

### Third Person ❌
"Users can configure the settings..." or "One can configure..."

### Active Voice ✅
"The API returns an error."

### Passive Voice ❌
"An error is returned by the API."

### Present Tense ✅
"The function returns a string."

### Future Tense ❌
"The function will return a string."

### Imperative ✅
"Click **Save** to save your changes."

### Conditional ❌
"You should click Save to save your changes."

## Links to Full Resources

- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Highlights](https://developers.google.com/style/highlights)
- [Word List](https://developers.google.com/style/word-list)
- [API Reference](https://developers.google.com/style/api-reference-comments)

---

*Print this for quick reference while writing documentation.*
