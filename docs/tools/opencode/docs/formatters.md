# OpenCode — Formatters

> Source: <https://opencode.ai/docs/formatters/>  
> Last updated: April 10, 2026

OpenCode automatically formats files after they are written or edited using language-specific formatters, ensuring code follows your project's style.

---

## How It Works

When OpenCode writes or edits a file, it:

1. Checks the file extension against all enabled formatters
2. Runs the appropriate formatter command on the file
3. Applies the formatting changes automatically

---

## Built-in Formatters

OpenCode auto-detects formatters based on file extensions and project configuration:

| Formatter | Extensions | Requirements |
|-----------|------------|--------------|
| air | `.R` | `air` command available |
| biome | `.js`, `.jsx`, `.ts`, `.tsx`, `.html`, `.css`, `.md`, `.json`, `.yaml`, and more | `biome.json(c)` config file |
| cargofmt | `.rs` | `cargo fmt` command available |
| clang-format | `.c`, `.cpp`, `.h`, `.hpp`, `.ino`, and more | `.clang-format` config file |
| cljfmt | `.clj`, `.cljs`, `.cljc`, `.edn` | `cljfmt` command available |
| dart | `.dart` | `dart` command available |
| dfmt | `.d` | `dfmt` command available |
| gleam | `.gleam` | `gleam` command available |
| gofmt | `.go` | `gofmt` command available |
| htmlbeautifier | `.erb`, `.html.erb` | `htmlbeautifier` command available |
| ktlint | `.kt`, `.kts` | `ktlint` command available |
| mix | `.ex`, `.exs`, `.eex`, `.heex`, `.leex`, `.neex`, `.sface` | `mix` command available |
| nixfmt | `.nix` | `nixfmt` command available |
| ocamlformat | `.ml`, `.mli` | `ocamlformat` command available and `.ocamlformat` config file |
| ormolu | `.hs` | `ormolu` command available |
| oxfmt (Experimental) | `.js`, `.jsx`, `.ts`, `.tsx` | `oxfmt` in `package.json` + experimental env flag |
| pint | `.php` | `laravel/pint` in `composer.json` |
| prettier | `.js`, `.jsx`, `.ts`, `.tsx`, `.html`, `.css`, `.md`, `.json`, `.yaml`, and more | `prettier` in `package.json` |
| rubocop | `.rb`, `.rake`, `.gemspec`, `.ru` | `rubocop` command available |
| ruff | `.py`, `.pyi` | `ruff` command with config |
| rustfmt | `.rs` | `rustfmt` command available |
| shfmt | `.sh`, `.bash` | `shfmt` command available |
| standardrb | `.rb`, `.rake`, `.gemspec`, `.ru` | `standardrb` command available |
| terraform | `.tf`, `.tfvars` | `terraform` command available |
| uv | `.py`, `.pyi` | `uv` command available |
| zig | `.zig`, `.zon` | `zig` command available |

If your project has `prettier` in `package.json`, OpenCode will automatically use it.

---

## Configure

Customize formatters via the `formatter` section in `opencode.json`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "formatter": {}
}
```

Each formatter supports:

| Property | Type | Description |
|----------|------|-------------|
| `disabled` | boolean | Set `true` to disable this formatter |
| `command` | string[] | Command to run for formatting |
| `environment` | object | Environment variables for the formatter |
| `extensions` | string[] | File extensions this formatter handles |

### Disable All Formatters

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "formatter": false
}
```

### Disable a Specific Formatter

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "formatter": {
    "prettier": {
      "disabled": true
    }
  }
}
```

### Custom Formatters

Override built-in formatters or add new ones:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "formatter": {
    "prettier": {
      "command": ["npx", "prettier", "--write", "$FILE"],
      "environment": {
        "NODE_ENV": "development"
      },
      "extensions": [".js", ".ts", ".jsx", ".tsx"]
    },
    "custom-markdown-formatter": {
      "command": ["deno", "fmt", "$FILE"],
      "extensions": [".md"]
    }
  }
}
```

The `$FILE` placeholder is replaced with the path to the file being formatted.
