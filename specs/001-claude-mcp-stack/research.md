# Phase 0 Research: claude-mcp-stack

All spec `[NEEDS CLARIFICATION]` items were resolved during `/speckit-clarify`. This document
records the remaining technology and approach decisions.

## R1. Agent instruction format — playbook + manifest

- **Decision**: `AGENTS.md` (process) + `registry.json` (data), with `AGENTS.md` opening with
  a fixed preamble and defining ordered steps, success criteria, and rollback rules.
- **Rationale**: Separating data from process makes adding a server a one-entry change and
  lets the manifest be schema-validated. `AGENTS.md` is the emerging convention agents look
  for at repo root.
- **Alternatives considered**: Single inline `SETUP.md` (mixes data + process, unvalidatable);
  a runnable `install.sh`/`.py` (script-first, opaque, cross-platform fragility, against the
  agent-first goal).

## R2. Secret scan — two layers, tree + history

- **Decision**: `scripts/check_no_secrets.sh` runs (1) a value/pattern denylist — known
  strings plus generic regexes for home paths (`/Users/<u>/`, `/home/<u>/`), UUIDs, 32+ hex <!-- pragma: allowlist secret -->
  tokens, `sk-…`, `Bearer …` — and (2) a structural/entropy scanner via `gitleaks` or
  `trufflehog` when present, with the regex layer as the always-on fallback. It scans the
  working tree AND full git history (`git log -p`) and exits non-zero on any hit.
- **Rationale**: A denylist alone cannot catch unknown/new secrets; entropy/structure catches
  those. History matters because a secret committed then "removed" still ships publicly.
- **Alternatives considered**: Denylist only (misses new secrets); working-tree only (misses
  history); mandatory `gitleaks` install (adds a hard dependency — made optional instead).

## R3. Safe config merge — dedicated tested helper

- **Decision**: `scripts/merge_server.py` performs the merge: write a timestamped `.bak` of
  the existing target first (backup-on-write by default, satisfying Constitution III in code),
  then load target JSON, add/replace only the chosen `mcpServers[<id>]` entry, preserve every
  other key byte-for-stable-order, write atomically; the agent calls it rather than
  hand-editing JSON.
- **Rationale**: Hand-editing JSON free-form risks dropping `preferences`/other servers
  (finding L1). A small, unit-tested helper makes "preserve unrelated keys" structural and
  testable (Principle III, V).
- **Alternatives considered**: Agent edits JSON directly (unverifiable, error-prone); a `jq`
  recipe (adds a dependency and is harder to test/assert on).

## R4. Per-server verification — lightweight liveness

- **Decision**: Launch the server command with stdin closed (EOF) and confirm it starts and
  exits cleanly / stays up briefly without crashing. No MCP `initialize`/`tools/list`
  handshake.
- **Rationale**: Clarified with the user. A full handshake is slow, protocol-version-fragile,
  and the real tool registration is done by the client on reload. Liveness catches the common
  failure (missing package / bad args) cheaply.
- **Alternatives considered**: Full MCP handshake (brittle, slow); config-write-only check
  (too weak — wouldn't catch a broken launch).

## R5. Catalog validation — stdlib JSON Schema-style checks

- **Decision**: `scripts/validate_registry.py` validates `registry.json` against the schema in
  `data-model.md`/`contracts/registry.schema.json` using only the Python standard library
  (explicit field/type/enum checks), and also asserts the `templates/*.json` parse and contain
  only placeholders (no denylisted patterns).
- **Rationale**: Zero third-party dependency keeps the repo trivially runnable in CI and by
  contributors; the schema is small enough that explicit checks are clear and sufficient.
- **Alternatives considered**: `jsonschema` library (extra dependency for a tiny schema);
  Pydantic (heavier; unnecessary).

## R6. Yahoo Finance fork distribution — published fork pinned by tag

- **Decision**: Publish the patched fork to `github.com/mgatorr/mcp-yahoo-finance`, tag a fixed
  version (e.g. `v0.1.3-mcpstack.1`), and reference that tag in `registry.json`. The agent
  clones the tag, runs `uv venv` + `uv pip install -e .`, and uses the produced binary.
- **Rationale**: Pinning to a tag is reproducible and trust-preserving; preserves upstream MIT
  + attribution; gives users the bug-fixed behavior (illiquid symbols no longer crash).
- **Alternatives considered**: Vendor a `.patch` over upstream (fragile if upstream moves);
  reference PyPI (still crashes on illiquid symbols); git `main` (moving target).

## R7. Public identity — GitHub noreply, name-only license

- **Decision**: Commits in both public repos use the maintainer's GitHub noreply email; the
  existing fork commit is re-authored with that identity and an English message; `LICENSE`
  carries "Mario Garrido" with no email.
- **Rationale**: User decision "name yes, Gmail no" — credit without leaking the personal
  email permanently into public history.
- **Alternatives considered**: Real Gmail in commits (leaks email forever); fully anonymous
  (loses the credit/good-impression goal).

## R8. Client config locations

- **Decision**: Desktop/Cowork → the Claude desktop `claude_desktop_config.json` under the
  OS application-support path; Claude Code → project/user `.mcp.json` (or `claude mcp add`).
  The agent asks the user which client when ambiguous and writes to the correct location.
- **Rationale**: These are the two clients the user uses and the two with stable, documented
  config locations. Both use the same `{command, args, env}` server entry shape, so one
  `config_snippet` template serves both with a different destination.
- **Alternatives considered**: Auto-detecting the client (unreliable; prefer asking);
  supporting more clients now (out of scope for v1).
