# Contract: Agent Install Playbook (`AGENTS.md`)

Defines the behavior an installing agent MUST exhibit. This is the human-readable contract;
`AGENTS.md` is the shipped artifact.

## Preamble (fixed, first lines of AGENTS.md)

> You are installing MCP servers for a Claude client. Read `registry.json` for the catalog.
> Follow the steps below in order. NEVER write any secret, API key, or the user's personal
> data into this repository. Ask the user before overwriting anything.

## Ordered steps

1. **Detect** OS and target client (Desktop/Cowork vs Claude Code); ask if ambiguous.
2. **Prerequisites**: check `uvx` and `node`/`npx`. If missing, **ask for explicit
   confirmation** (name tool + package manager) before any system-level install; never
   install silently. If declined or failing, stop with manual instructions.
3. **Selection**: read `registry.json`; ask which servers to install (default: all).
4. **Secrets**: for each selected server, prompt for any `required` secret not already set.
   Never write secrets anywhere but the target client config; never echo entered values.
5. **Local fork (yahoo-finance)**: clone the pinned tag, `uv venv`, `uv pip install -e .`,
   resolve the binary path.
6. **Merge**: call `merge_server.py` per selected server — it writes a timestamped `.bak`
   next to the target (in the OS config dir, never the repo) before any write; preserve all
   unrelated keys; ask before overwriting an existing entry (`--force`).
7. **Verify**: lightweight liveness per added server (spawn with EOF, expect no crash);
   report a summary.

## Success criteria

- Every selected server with valid credentials is present in the config AND passed liveness.
- No unrelated config key changed.
- No secret written outside the target config; nothing secret printed.

## Failure / rollback

- On any liveness failure or unsafe merge, restore the backup and report exactly what failed.
- Never leave a half-merged config.

## Idempotency

- Re-running produces no duplicate entries and no corruption; an already-correct entry is a
  no-op (or a confirmed replace).
