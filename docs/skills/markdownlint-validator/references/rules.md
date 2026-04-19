# Markdownlint Rules Reference

All rules for [DavidAnson/markdownlint](https://github.com/DavidAnson/markdownlint) MD001–MD060.

**Fixable (✓)** = `markdownlint --fix` can auto-correct. **Fixable (some)** = partially auto-fixable.

---

## Headings

| Rule | Alias | What It Checks | Fixable | Key Parameters |
|---|---|---|---|---|
| MD001 | `heading-increment` | Heading levels increment by one at a time | — | `front_matter_title` (regex, default `^\s*title\s*[:=]`) |
| MD003 | `heading-style` | Consistent heading style (ATX vs setext) | — | `style`: `consistent` (default) / `atx` / `atx_closed` / `setext` / `setext_with_atx` |
| MD018 | `no-missing-space-atx` | Space required after `#` in ATX headings | ✓ | — |
| MD019 | `no-multiple-space-atx` | Only one space allowed after `#` in ATX headings | ✓ | — |
| MD020 | `no-missing-space-closed-atx` | Space required inside `#` in closed ATX headings | ✓ | — |
| MD021 | `no-multiple-space-closed-atx` | Only one space inside `#` in closed ATX headings | ✓ | — |
| MD022 | `blanks-around-headings` | Headings must be surrounded by blank lines | ✓ | `lines_above`: 1, `lines_below`: 1 |
| MD023 | `heading-start-left` | Headings must start at beginning of line | ✓ | — |
| MD024 | `no-duplicate-heading` | No duplicate heading text | — | `siblings_only`: false |
| MD025 | `single-title` / `single-h1` | Only one top-level heading per document | — | `level`: 1, `front_matter_title` |
| MD026 | `no-trailing-punctuation` | No trailing punctuation in headings | ✓ | `punctuation`: `.,;:!。，；：！` |
| MD036 | `no-emphasis-as-heading` | Emphasis not used as a heading substitute | — | `punctuation`: `.,;:!?。，；：！？` |
| MD041 | `first-line-heading` / `first-line-h1` | First line must be a top-level heading | — | `level`: 1, `front_matter_title`, `allow_preamble` |
| MD043 | `required-headings` | Required heading structure (structure enforcement) | — | `headings`: `[]`, `match_case`: false |

---

## Whitespace

| Rule | Alias | What It Checks | Fixable | Key Parameters |
|---|---|---|---|---|
| MD009 | `no-trailing-spaces` | No trailing spaces on lines | ✓ | `br_spaces`: 2, `code_blocks`: false, `strict`: false |
| MD010 | `no-hard-tabs` | No hard tab characters | ✓ | `code_blocks`: true, `ignore_code_languages`: [], `spaces_per_tab`: 1 |
| MD012 | `no-multiple-blanks` | No more than one consecutive blank line | ✓ | `maximum`: 1 |
| MD027 | `no-multiple-space-blockquote` | Only one space after `>` in blockquotes | ✓ | `list_items`: true |
| MD030 | `list-marker-space` | Correct number of spaces after list markers | ✓ | `ul_single`: 1, `ul_multi`: 1, `ol_single`: 1, `ol_multi`: 1 |
| MD037 | `no-space-in-emphasis` | No spaces inside emphasis markers (`*`, `_`) | ✓ | — |
| MD038 | `no-space-in-code` | No unnecessary spaces inside code span backticks | ✓ | — |
| MD039 | `no-space-in-links` | No spaces inside link text brackets | ✓ | — |

---

## Blank Lines

| Rule | Alias | What It Checks | Fixable | Key Parameters |
|---|---|---|---|---|
| MD022 | `blanks-around-headings` | Blank lines around headings | ✓ | `lines_above`: 1, `lines_below`: 1 |
| MD028 | `no-blanks-blockquote` | Blank lines inside blockquotes (parser inconsistency) | — | — |
| MD031 | `blanks-around-fences` | Blank lines around fenced code blocks | ✓ | `list_items`: true |
| MD032 | `blanks-around-lists` | Blank lines around lists | ✓ | — |
| MD047 | `single-trailing-newline` | File ends with a single newline | ✓ | — |
| MD058 | `blanks-around-tables` | Blank lines around tables | ✓ | — |

---

## Line Length

| Rule | Alias | What It Checks | Fixable | Key Parameters |
|---|---|---|---|---|
| MD013 | `line-length` | Lines must not exceed configured length | — | `line_length`: 80, `heading_line_length`: 80, `code_block_line_length`: 80, `code_blocks`: true, `tables`: true, `headings`: true, `strict`: false, `stern`: false |

> Lines without whitespace beyond the limit (e.g., long URLs) are exempt by default. Use `strict: true` to disable this exemption.

---

## Code

| Rule | Alias | What It Checks | Fixable | Key Parameters |
|---|---|---|---|---|
| MD014 | `commands-show-output` | No `$` prefix on shell commands when no output shown | ✓ | — |
| MD031 | `blanks-around-fences` | Fenced code blocks surrounded by blank lines | ✓ | `list_items`: true |
| MD040 | `fenced-code-language` | Fenced code blocks must specify a language | — | `allowed_languages`: [], `language_only`: false |
| MD046 | `code-block-style` | Consistent code block style (fenced vs indented) | — | `style`: `consistent` / `fenced` / `indented` |
| MD048 | `code-fence-style` | Consistent fence style (backtick vs tilde) | — | `style`: `consistent` / `backtick` / `tilde` |

---

## Lists

| Rule | Alias | What It Checks | Fixable | Key Parameters |
|---|---|---|---|---|
| MD004 | `ul-style` | Consistent unordered list marker style | ✓ (some) | `style`: `consistent` / `asterisk` / `dash` / `plus` / `sublist` |
| MD005 | `list-indent` | Consistent indentation for list items at same level | ✓ (some) | — |
| MD007 | `ul-indent` | Unordered lists indented by configured spaces | ✓ (some) | `indent`: 2, `start_indent`: 2, `start_indented`: false |
| MD029 | `ol-prefix` | Ordered list item prefix style | ✓ (some) | `style`: `one_or_ordered` (default) / `one` / `ordered` / `zero` |
| MD030 | `list-marker-space` | Spaces after list markers | ✓ | `ul_single`: 1, `ol_single`: 1 |
| MD032 | `blanks-around-lists` | Lists surrounded by blank lines | ✓ | — |

---

## Links

| Rule | Alias | What It Checks | Fixable | Key Parameters |
|---|---|---|---|---|
| MD011 | `no-reversed-links` | Link syntax not reversed (`(text)[url]`) | ✓ | — |
| MD034 | `no-bare-urls` | URLs must use angle brackets or be in code spans | ✓ | — |
| MD039 | `no-space-in-links` | No spaces inside link text | ✓ | — |
| MD042 | `no-empty-links` | No empty link destinations | — | — |
| MD051 | `link-fragments` | Link fragments (`#anchor`) must match actual headings | ✓ | `ignore_case`: false, `ignored_pattern`: `` |
| MD052 | `reference-links-images` | Reference links/images use defined labels | — | `shortcut_syntax`: false, `ignored_labels`: `["x"]` |
| MD053 | `link-image-reference-definitions` | All link/image reference definitions are used | ✓ | `ignored_definitions`: `["//"]` |
| MD054 | `link-image-style` | Consistent link/image style | ✓ | `autolink`, `inline`, `full`, `collapsed`, `shortcut`, `url_inline` (all default `true`) |
| MD059 | `descriptive-link-text` | Link text must be descriptive (not "click here", "here", etc.) | — | `prohibited_texts`: `["click here","here","link","more"]` |

---

## Images

| Rule | Alias | What It Checks | Fixable | Key Parameters |
|---|---|---|---|---|
| MD045 | `no-alt-text` | Images must have alt text | — | — |

---

## Tables

| Rule | Alias | What It Checks | Fixable | Key Parameters |
|---|---|---|---|---|
| MD055 | `table-pipe-style` | Consistent leading/trailing pipe usage in tables | — | `style`: `consistent` (default) / `leading_and_trailing` / `leading_only` / `no_leading_or_trailing` / `trailing_only` |
| MD056 | `table-column-count` | All rows must have same number of cells | — | — |
| MD058 | `blanks-around-tables` | Tables surrounded by blank lines | ✓ | — |
| MD060 | `table-column-style` | Consistent column padding style in tables | — | `style`: `any` (default) / `aligned` / `compact` / `tight`; `aligned_delimiter`: false |

---

## Blockquotes

| Rule | Alias | What It Checks | Fixable | Key Parameters |
|---|---|---|---|---|
| MD027 | `no-multiple-space-blockquote` | Only one space after `>` | ✓ | `list_items`: true |
| MD028 | `no-blanks-blockquote` | Blank lines inside blockquotes cause inconsistent rendering | — | — |

---

## Emphasis & Style

| Rule | Alias | What It Checks | Fixable | Key Parameters |
|---|---|---|---|---|
| MD036 | `no-emphasis-as-heading` | Bold/italic lines not used as heading substitutes | — | `punctuation`: `.,;:!?。，；：！？` |
| MD037 | `no-space-in-emphasis` | No spaces inside `*` / `_` emphasis markers | ✓ | — |
| MD049 | `emphasis-style` | Consistent emphasis style (`*` vs `_`) | ✓ | `style`: `consistent` / `asterisk` / `underscore` |
| MD050 | `strong-style` | Consistent strong style (`**` vs `__`) | ✓ | `style`: `consistent` / `asterisk` / `underscore` |

---

## HTML & Special Content

| Rule | Alias | What It Checks | Fixable | Key Parameters |
|---|---|---|---|---|
| MD033 | `no-inline-html` | No raw HTML in Markdown | — | `allowed_elements`: [], `table_allowed_elements`: [] |
| MD044 | `proper-names` | Proper names have correct capitalization | ✓ | `names`: [], `code_blocks`: true, `html_elements`: true |

---

## Horizontal Rules

| Rule | Alias | What It Checks | Fixable | Key Parameters |
|---|---|---|---|---|
| MD035 | `hr-style` | Consistent horizontal rule style | — | `style`: `consistent` |

---

## Deprecated / Removed Rules

The following rules were removed from the rule set and should not be configured:

| Rule | Notes |
|---|---|
| MD002 | Removed — heading-increment superseded by MD001 |
| MD006 | Removed — list indentation for root-level items |
| MD015–MD017 | Removed — list syntax rules superseded |
| MD057 | Removed |

---

## GitHub Heading Fragment Algorithm (MD051)

When writing link fragments to anchor headings, GitHub generates them as:

1. Convert heading text to lowercase
2. Remove punctuation characters (except `-`)
3. Replace spaces with `-`
4. Append `-N` for duplicates (N starts at 1)

Examples:

| Heading | Fragment |
|---|---|
| `## API Reference` | `#api-reference` |
| `## API Reference` (2nd) | `#api-reference-1` |
| `## My Heading (2026)` | `#my-heading-2026` |
| `## FAQ: What is X?` | `#faq-what-is-x` |
