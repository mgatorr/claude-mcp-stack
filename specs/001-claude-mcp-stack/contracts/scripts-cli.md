# Contract: Script CLIs

The three shipped scripts are the only executable interfaces. Each is built test-first.

## `scripts/validate_registry.py`

- **Invocation**: `python3 scripts/validate_registry.py [--registry registry.json] [--templates-dir templates]`
- **Behavior**: Validates `registry.json` against `contracts/registry.schema.json` (stdlib
  checks): required fields, types, enums (`category`, `runtime`), `id` pattern + uniqueness,
  `secrets[].where_to_get` is an http(s) URL, and every `${TOKEN}` in `args_template`/
  `config_snippet` maps to a declared secret. Then parses each `templates/*.json` and asserts
  it contains no denylisted secret patterns.
- **Exit codes**: `0` valid; `1` validation error (prints the offending field/server and a
  human-readable reason); `2` usage error.
- **Output**: human-readable lines; one error per problem found.

## `scripts/merge_server.py`

- **Invocation**: `python3 scripts/merge_server.py --config <path> --id <server-id> --entry <json>`
  (the `--entry` value is the `config_snippet` object as a JSON string).
- **Behavior**: If the target config already exists, FIRST writes a timestamped backup
  `<path>.bak.<YYYYMMDD-HHMMSS>` next to it (in the same OS config directory, never in the
  repo). Then loads the target JSON (creates `{ "mcpServers": {} }` if absent), adds or
  replaces `mcpServers[<id>]` with the entry, preserves all other keys and top-level fields
  unchanged, and writes atomically. Refuses to replace an existing `mcpServers[<id>]` unless
  `--force` is passed. A `--no-backup` flag is available for callers that manage their own
  backup, but backup-on-write is the default (Constitution III: back up before writing).
- **Exit codes**: `0` merged; `3` would overwrite without `--force`; `1` invalid input;
  `2` usage error.
- **Guarantees (tested)**:
  - Any key not equal to `mcpServers[<id>]` is byte-stable across the merge, including a
    populated `preferences` block and other servers.
  - When the target exists, a `.bak.<timestamp>` copy is created before any write, and its
    contents equal the pre-merge file.

## `scripts/check_no_secrets.sh`

- **Invocation**: `scripts/check_no_secrets.sh [--history]`
- **Behavior**: Layer 1 denylist (known strings + generic regexes for home paths, UUIDs, 32+
  hex tokens, `sk-…`, `Bearer …`). Layer 2 entropy/structure via `gitleaks` or `trufflehog`
  if available; otherwise the regex layer is the backstop. With `--history` (used pre-publish
  and in CI), also scans full git history (`git log -p`).
- **Exit codes**: `0` clean; `1` potential secret found (prints file/location + matched rule,
  never the full secret); `2` usage error.
- **Guarantee (tested)**: a planted fixture secret in the tree (and, with `--history`, in a
  prior commit) is detected and causes a non-zero exit.
