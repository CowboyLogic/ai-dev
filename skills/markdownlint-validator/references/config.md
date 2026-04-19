# Markdownlint Configuration Reference

How to configure markdownlint for a project, disable/customize rules, and suppress violations inline.

---

## Configuration File Formats

markdownlint resolves config from the **nearest** config file walking up from each linted file.

### `.markdownlint.json` (recommended)

```json
{
  "default": true,
  "MD013": {
    "line_length": 120,
    "code_blocks": false,
    "tables": false
  },
  "MD033": {
    "allowed_elements": ["details", "summary", "br"]
  },
  "MD041": false
}
```

### `.markdownlint.yaml` / `.markdownlint.yml`

```yaml
default: true
MD013:
  line_length: 120
  code_blocks: false
  tables: false
MD033:
  allowed_elements:
    - details
    - summary
    - br
MD041: false
```

### `.markdownlint.jsonc` (supports comments)

```jsonc
{
  // Enable all rules by default
  "default": true,
  // Disable line length globally — long URLs are common
  "MD013": false
}
```

---

## Key Config Patterns

### Disable a rule entirely

```json
{
  "MD013": false
}
```

Or by alias:

```json
{
  "line-length": false
}
```

### Configure rule parameters

```json
{
  "MD013": {
    "line_length": 120,
    "heading_line_length": 120,
    "code_block_line_length": 120,
    "code_blocks": false,
    "tables": false,
    "headings": false
  }
}
```

### Allow specific HTML elements (MD033)

```json
{
  "MD033": {
    "allowed_elements": ["details", "summary", "br", "kbd", "sub", "sup"]
  }
}
```

### Enforce proper name capitalization (MD044)

```json
{
  "MD044": {
    "names": ["JavaScript", "TypeScript", "GitHub", "VS Code"],
    "code_blocks": false
  }
}
```

### Require ordered list numbering (MD029)

```json
{
  "MD029": {
    "style": "ordered"
  }
}
```

### Allow multiple H1s in changelog-style docs (MD024)

```json
{
  "MD024": {
    "siblings_only": true
  }
}
```

---

## Common Project Configurations

### Documentation site (MkDocs, Docusaurus, GitHub Pages)

```json
{
  "default": true,
  "MD013": {
    "line_length": 120,
    "code_blocks": false,
    "tables": false
  },
  "MD033": {
    "allowed_elements": ["details", "summary", "br", "kbd"]
  },
  "MD041": false
}
```

Why: Documentation files are often rendered with long lines acceptable, HTML callout elements are common, and some files are fragments without H1.

### Repository README / general markdown

```json
{
  "default": true,
  "MD013": {
    "line_length": 100
  },
  "MD033": false
}
```

### Strict technical writing

```json
{
  "default": true,
  "MD013": {
    "line_length": 80,
    "strict": true
  }
}
```

---

## Inline Suppression

Use HTML comments to suppress specific rules for regions or individual lines.

### Disable for a region

```markdown
<!-- markdownlint-disable MD013 -->
This is a very long line that exceeds the configured line length but cannot be easily wrapped.
<!-- markdownlint-enable MD013 -->
```

### Disable for next line only

```markdown
<!-- markdownlint-disable-next-line MD033 -->
<details><summary>Click to expand</summary>
```

### Disable for current line only

```markdown
Some text <!-- markdownlint-disable-line MD013 -->
```

### Disable multiple rules at once

```markdown
<!-- markdownlint-disable MD013 MD033 MD041 -->
...content...
<!-- markdownlint-enable MD013 MD033 MD041 -->
```

### Disable all rules for a region

```markdown
<!-- markdownlint-disable -->
...content with any violations...
<!-- markdownlint-enable -->
```

### Capture / restore rule state

```markdown
<!-- markdownlint-capture -->
<!-- markdownlint-disable MD013 -->
...long lines here...
<!-- markdownlint-restore -->
```

> Prefer `markdownlint-capture` + `markdownlint-restore` over `disable`/`enable` to preserve any previously customized rule state.

---

## Front Matter in Config Files

markdownlint-cli2 supports `<!-- markdownlint-configure-file { ... } -->` at the top of a file to apply per-file config inline:

```markdown
<!-- markdownlint-configure-file { "MD013": { "line_length": 120 } } -->
# My Document
```

---

## VS Code Integration

Install the [markdownlint VS Code extension](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint).

Config is read from the nearest `.markdownlint.*` file. Workspace-level config in `.vscode/settings.json`:

```json
{
  "markdownlint.config": {
    "MD013": false,
    "MD033": {
      "allowed_elements": ["details", "summary"]
    }
  }
}
```

> `.markdownlint.*` file settings take precedence over VS Code settings.

---

## CLI Integration

### markdownlint-cli

```bash
# Install
npm install -g markdownlint-cli

# Lint all markdown in docs/
markdownlint "docs/**/*.md"

# Auto-fix
markdownlint --fix "docs/**/*.md"

# Use explicit config file
markdownlint --config .markdownlint.json "docs/**/*.md"
```

### markdownlint-cli2

```bash
# Install
npm install -g markdownlint-cli2

# Lint (uses .markdownlint.* config automatically)
markdownlint-cli2 "docs/**/*.md"

# Fix
markdownlint-cli2 --fix "docs/**/*.md"
```

### Config file location with CLI

markdownlint-cli2 searches for config files in this order (first match wins):

1. `.markdownlint.jsonc`
2. `.markdownlint.json`
3. `.markdownlint.yaml`
4. `.markdownlint.yml`
5. `.markdownlint-cli2.jsonc`
6. `.markdownlint-cli2.json`
7. `.markdownlint-cli2.yaml`
8. `.markdownlint-cli2.yml`

---

## Per-Directory Configuration

Place a `.markdownlint.json` in a subdirectory to override config only for that directory and below.

```
project/
├── .markdownlint.json           ← applies to all files
├── docs/
│   ├── .markdownlint.json       ← overrides for docs/ only
│   └── api/
│       └── .markdownlint.json   ← overrides for docs/api/ only
```

---

## GitHub Actions / CI Integration

```yaml
- name: Lint markdown
  uses: DavidAnson/markdownlint-cli2-action@v17
  with:
    globs: "docs/**/*.md"
    config: ".markdownlint.json"
```

Or using markdownlint-cli directly:

```yaml
- name: Lint markdown
  run: |
    npm install -g markdownlint-cli
    markdownlint "docs/**/*.md"
```
