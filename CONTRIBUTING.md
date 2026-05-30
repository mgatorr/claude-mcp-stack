# Contributing to claude-mcp-stack

Thanks for helping improve the stack! The project is designed so that **adding a server is a
one-entry change**.

## Add a new MCP server

1. **Add one entry to `registry.json`** following the schema in
   [`specs/001-claude-mcp-stack/contracts/registry.schema.json`](specs/001-claude-mcp-stack/contracts/registry.schema.json):
   `id`, `description`, `category`, `runtime` (`uvx`/`npx`/`local`), `package`, `version_pin`,
   `args_template`, `secrets` (with `where_to_get`), `config_snippet`, `healthcheck`.
   - Use `${SECRET_NAME}` placeholders only — **never** real keys.
   - Every `${TOKEN}` must have a matching entry in that server's `secrets`.
2. **Add `servers/<id>.md`** describing what the server does and where to get any key.
3. **Mirror the entry** (with placeholders) in both files under `templates/`.

No change to `AGENTS.md` should be needed — the playbook is data-driven.

## Run the checks locally

```bash
python3 scripts/validate_registry.py        # catalog + templates
python3 -m pytest -q                         # validator, merge, secret-scan tests
scripts/check_no_secrets.sh --history        # two-layer secret scan (tree + history)
```

All three must pass. CI runs the same checks on every pull request.

## Tests come first

Per the project [constitution](.specify/memory/constitution.md), any change to a shipped
script (`validate_registry.py`, `merge_server.py`, `check_no_secrets.sh`) is **test-first**:
add a failing test, then make it pass.

## Conventions

- **English** for all files and commit messages.
- Keep commits small and focused.
- Configure your Git author to a privacy-preserving identity (e.g. a GitHub `noreply` email).
- If a line legitimately contains a pattern the secret scanner would flag (a regex
  definition, a test fixture), mark it with `pragma: allowlist secret`.

## Code of Conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
