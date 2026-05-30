# AGENTS.md — install playbook

> You are installing MCP servers for a Claude client. Read `registry.json` for the catalog.
> Follow the steps below in order. NEVER write any secret, API key, or the user's personal
> data into this repository. Ask the user before overwriting anything.

This file tells an agent how to install the curated servers end-to-end. Humans: see
`README.md`.

## Inputs

- `registry.json` — the catalog (one entry per server; fields per
  `specs/001-claude-mcp-stack/contracts/registry.schema.json`).
- `templates/` — placeholder-only example configs for each client.
- `scripts/merge_server.py` — safe, backup-first config merge (use it; do not hand-edit JSON).

## Steps (in order)

1. **Detect environment.** Determine the OS (macOS, Linux, Windows) and the target client:
   - Claude Desktop / Cowork → `claude_desktop_config.json` in the OS application-support dir.
   - Claude Code → the project/user `.mcp.json` (or `claude mcp add`).
   If the client is ambiguous, ask the user; do not guess.

2. **Check prerequisites.** Verify `uvx` (for Python servers) and `node`/`npx` (for Node
   servers) are available. If one is missing, **ask for explicit confirmation before any
   system-level install**, naming the tool and the package manager you would use
   (Homebrew / apt / winget). NEVER install system packages silently. If the user declines
   or the install fails, stop and print clear manual instructions.

3. **Select servers.** Read `registry.json` and ask which servers to install. Default: all.

4. **Collect secrets.** For each selected server, read its `secrets`. For every `required`
   secret not already configured, prompt the user (show `description` and `where_to_get`).
   NEVER write a secret anywhere except the user's client config, and NEVER echo an entered
   secret value back into the chat, a log, or a file.

5. **Build the local fork (yahoo-finance).** Clone the pinned tag from the entry's `package`
   URL at `version_pin`, then `uv venv` and `uv pip install -e .`. Resolve the produced
   binary path (`.venv/bin/mcp-yahoo-finance`; Windows `.venv\Scripts\mcp-yahoo-finance.exe`)
   and use it as that server's `command`.

6. **Merge (safe + idempotent).** For each selected server, build its config entry from
   `config_snippet` (substituting the collected secrets) and call:
   `python3 scripts/merge_server.py --config <client-config> --id <id> --entry '<json>'`.
   The helper writes a timestamped `.bak` next to the target before any write. It refuses to
   replace an existing entry unless you pass `--force` — only do so after the user confirms.
   Do not touch any unrelated key.

7. **Verify (liveness).** For each newly added server, perform a lightweight liveness check:
   launch its `command`+`args` with stdin closed (EOF) and confirm it starts and exits
   cleanly / stays up briefly without crashing. This is NOT a full MCP handshake — the client
   registers tools on reload. Report a summary of added / skipped / verified servers, then
   tell the user to restart the client (Desktop/Cowork: `Cmd+Q` and reopen).

## Success criteria

- Every selected server with valid credentials is present in the client config AND passed
  the liveness check.
- No unrelated config key changed.
- No secret was written outside the client config; nothing secret was printed.

## Failure / rollback

- If any liveness check fails or a merge cannot be completed safely, restore the `.bak` the
  helper created and report exactly what failed. NEVER leave a half-merged config.

## Idempotency

- Re-running this playbook MUST NOT create duplicate entries or corrupt the config. An
  already-correct entry is a no-op (or a user-confirmed replace via `--force`).
