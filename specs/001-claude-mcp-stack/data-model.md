# Phase 1 Data Model: claude-mcp-stack

The data spine is `registry.json`. Entities below map directly to its structure and drive
`scripts/validate_registry.py` and `contracts/registry.schema.json`.

## Entity: Catalog (root of `registry.json`)

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `version` | integer | yes | `== 1` for this schema revision |
| `servers` | array<ServerEntry> | yes | non-empty; unique `id` across entries |

## Entity: ServerEntry

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `id` | string | yes | `^[a-z0-9-]+$`; unique; used as the `mcpServers` key |
| `description` | string | yes | one line, non-empty |
| `category` | string | yes | one of: `finance`, `crypto`, `web`, `media` |
| `runtime` | string (enum) | yes | one of: `uvx`, `npx`, `local` |
| `package` | string | yes | PyPI/npm package id; for `local`, the fork git URL |
| `version_pin` | string | yes | tag/version for reproducibility (e.g. `@latest` allowed only for `npx` convenience tools; `local` MUST be a tag) |
| `args_template` | array<string> | yes | argv with `${SECRET_NAME}` placeholders only |
| `secrets` | array<SecretDescriptor> | yes | may be empty `[]` |
| `config_snippet` | ConfigSnippet | yes | the entry to merge into `mcpServers` |
| `healthcheck` | string | yes | how to liveness-check (e.g. `spawn-eof`) |
| `notes` | string | no | e.g. Windows binary path for `local` |

**State/lifecycle**: a ServerEntry is either fully installable (all required secrets supplied)
or *skipped* at install time (a required secret the user cannot provide). No persisted state.

## Entity: SecretDescriptor

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `name` | string | yes | `^[A-Z0-9_]+$`; matches a `${name}` in `args_template`/`config_snippet` |
| `description` | string | yes | human explanation |
| `where_to_get` | string | yes | absolute `http(s)://` URL |
| `required` | boolean | yes | if true and unprovided → server skipped |

## Entity: ConfigSnippet

Shape shared by both client targets (the agent writes it to the right location per client).

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `command` | string | yes | launcher or absolute binary path (for `local`) |
| `args` | array<string> | no | argv; placeholders allowed |
| `env` | object<string,string> | no | values may be `${SECRET_NAME}` placeholders |

Validation: every `${TOKEN}` appearing in `args`/`env`/`args_template` MUST correspond to a
declared `secrets[].name`; no literal secret values allowed (placeholder-only).

## Entity: ExampleTemplate (files under `templates/`)

| File | Represents | Rules |
|------|------------|-------|
| `claude_desktop_config.example.json` | Desktop/Cowork config sample | valid JSON; `mcpServers` keyed by `id`; placeholders only |
| `claude_code.mcp.example.json` | Claude Code `.mcp.json` sample | valid JSON; placeholders only |

Both MUST contain zero denylisted patterns (real keys, emails, home paths) — enforced by the
validator and the secret scan.

## Entity: TargetClientConfig (external, user's machine — not in repo)

The user's existing client config the agent augments. Invariants the merge MUST hold:

- All pre-existing keys (other servers, `preferences`, top-level fields) preserved unchanged.
- Only the selected `mcpServers[<id>]` entries added; existing entry replaced only after
  explicit confirmation.
- A timestamped backup is created in the OS config directory before writing.

## Relationships

- `Catalog 1—* ServerEntry`
- `ServerEntry 1—* SecretDescriptor` (0..n)
- `ServerEntry 1—1 ConfigSnippet`
- `ServerEntry.config_snippet`/`args_template` placeholders `*—1 SecretDescriptor.name`
- `ExampleTemplate.mcpServers[id]` references `ServerEntry.id` (examples mirror the catalog)
