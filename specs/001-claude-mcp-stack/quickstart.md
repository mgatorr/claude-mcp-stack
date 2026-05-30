# Quickstart: claude-mcp-stack

## For end users (the agent flow)

1. Open Claude Code in any directory.
2. Paste: *"Install the MCP servers from https://github.com/mgatorr/claude-mcp-stack"*.
3. The agent reads `AGENTS.md` + `registry.json`, detects your OS and Claude client, asks
   which servers you want, and prompts for any API keys.
4. It backs up your config, merges the selected servers, and verifies each one starts.
5. Restart your Claude client (Desktop/Cowork: `Cmd+Q` then reopen) to load the new tools.

Manual install (no agent): copy the relevant snippet from `templates/` into your client
config, fill in your keys, and restart the client. See the README "Manual install" section.

## For contributors / maintainers (local dev)

```bash
# 1. Clone
git clone https://github.com/mgatorr/claude-mcp-stack && cd claude-mcp-stack

# 2. Validate the catalog and templates
python3 scripts/validate_registry.py

# 3. Run the test suite (validator, merge helper, secret scan)
python3 -m pytest -q

# 4. Run the secret scan (pre-push gate; --history scans full git history)
scripts/check_no_secrets.sh --history
```

Add a new server: add one entry to `registry.json` (see `contracts/registry.schema.json`),
add `servers/<id>.md`, mirror the entry in `templates/*.json` with placeholders, then run
steps 2–4 above. No change to `AGENTS.md` should be needed.

## Acceptance smoke (maps to spec success criteria)

- `validate_registry.py` exits 0 and rejects a malformed entry (SC-006).
- `merge_server.py` preserves a populated `preferences` block and other servers (SC-003).
- `check_no_secrets.sh` flags a planted fixture secret in tree and history (SC-004).
- A dry agent run on a clean machine adds all servers and passes liveness (SC-001, SC-002).
- The bundled Yahoo Finance server returns "No price data available" for an illiquid symbol
  instead of crashing (SC-007).
