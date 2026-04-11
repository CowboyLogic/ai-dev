# OpenCode — LSP Servers

> Source: <https://opencode.ai/docs/lsp/>  
> Last updated: April 10, 2026

OpenCode integrates with Language Server Protocol (LSP) to help the LLM interact with your codebase using diagnostics.

---

## How It Works

When OpenCode opens a file, it:

1. Checks the file extension against all enabled LSP servers
2. Starts the appropriate LSP server if not already running

LSP servers are automatically enabled when matching file extensions are detected and requirements are met.

Disable automatic LSP server downloads:

```bash
export OPENCODE_DISABLE_LSP_DOWNLOAD=true
```

---

## Built-in LSP Servers

| Server | Extensions | Requirements |
|--------|------------|--------------|
| astro | `.astro` | Auto-installs for Astro projects |
| bash | `.sh`, `.bash`, `.zsh`, `.ksh` | Auto-installs bash-language-server |
| clangd | `.c`, `.cpp`, `.cc`, `.cxx`, `.c++`, `.h`, `.hpp` | Auto-installs for C/C++ projects |
| clojure-lsp | `.clj`, `.cljs`, `.cljc`, `.edn` | `clojure-lsp` command |
| csharp | `.cs` | `.NET SDK` installed |
| dart | `.dart` | `dart` command |
| deno | `.ts`, `.tsx`, `.js`, `.jsx`, `.mjs` | `deno` command (auto-detects `deno.json`) |
| elixir-ls | `.ex`, `.exs` | `elixir` command |
| eslint | `.ts`, `.tsx`, `.js`, `.jsx`, `.vue`, and more | `eslint` in project |
| fsharp | `.fs`, `.fsi`, `.fsx` | `.NET SDK` installed |
| gleam | `.gleam` | `gleam` command |
| gopls | `.go` | `go` command |
| hls | `.hs`, `.lhs` | `haskell-language-server-wrapper` command |
| jdtls | `.java` | Java SDK 21+ |
| julials | `.jl` | `julia` and `LanguageServer.jl` |
| kotlin-ls | `.kt`, `.kts` | Auto-installs for Kotlin projects |
| lua-ls | `.lua` | Auto-installs for Lua projects |
| nixd | `.nix` | `nixd` command |
| ocaml-lsp | `.ml`, `.mli` | `ocamllsp` command |
| oxlint | `.ts`, `.tsx`, `.js`, `.jsx`, `.vue`, `.astro`, `.svelte` | `oxlint` in project |
| php intelephense | `.php` | Auto-installs for PHP projects |
| prisma | `.prisma` | `prisma` command |
| pyright | `.py`, `.pyi` | `pyright` in project |
| ruby-lsp | `.rb`, `.rake`, `.gemspec` | `ruby` and `gem` commands |
| rust | `.rs` | `rust-analyzer` command |
| sourcekit-lsp | `.swift`, `.objc`, `.objcpp` | `swift` installed (Xcode on macOS) |
| svelte | `.svelte` | Auto-installs for Svelte projects |
| terraform | `.tf`, `.tfvars` | Auto-installs from GitHub releases |
| tinymist | `.typ`, `.typc` | Auto-installs from GitHub releases |
| typescript | `.ts`, `.tsx`, `.js`, `.jsx`, `.mjs`, `.cjs` | `typescript` in project |
| vue | `.vue` | Auto-installs for Vue projects |
| yaml-ls | `.yaml`, `.yml` | Auto-installs Red Hat yaml-language-server |
| zls | `.zig`, `.zon` | `zig` command |

---

## Configure

Customize via the `lsp` section in `opencode.json`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "lsp": {}
}
```

Each LSP server supports:

| Property | Type | Description |
|----------|------|-------------|
| `disabled` | boolean | Set `true` to disable this server |
| `command` | string[] | Command to start the server |
| `extensions` | string[] | File extensions to handle |
| `env` | object | Environment variables for the server |
| `initialization` | object | Initialization options for the LSP `initialize` request |

### Environment Variables

```jsonc
{
  "lsp": {
    "rust": {
      "env": {
        "RUST_LOG": "debug"
      }
    }
  }
}
```

### Initialization Options

```jsonc
{
  "lsp": {
    "typescript": {
      "initialization": {
        "preferences": {
          "importModuleSpecifierPreference": "relative"
        }
      }
    }
  }
}
```

### Disable All LSP Servers

```jsonc
{
  "lsp": false
}
```

### Disable a Specific Server

```jsonc
{
  "lsp": {
    "typescript": {
      "disabled": true
    }
  }
}
```

### Custom LSP Servers

```jsonc
{
  "lsp": {
    "custom-lsp": {
      "command": ["custom-lsp-server", "--stdio"],
      "extensions": [".custom"]
    }
  }
}
```

---

## Additional Information

### PHP Intelephense License

PHP Intelephense offers premium features via a license key. Place the key (only) in:

- **macOS/Linux:** `$HOME/intelephense/license.txt`
- **Windows:** `%USERPROFILE%/intelephense/license.txt`
