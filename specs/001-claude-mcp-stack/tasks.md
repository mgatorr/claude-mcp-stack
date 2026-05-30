---
description: "Task list for claude-mcp-stack implementation"
---

# Tasks: claude-mcp-stack

**Input**: Design documents from `specs/001-claude-mcp-stack/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: REQUIRED — the constitution (Principle V) mandates test-first for all shipped
scripts. Test tasks precede their implementation and MUST be observed to fail first.

**Organization**: Grouped by user story. US1 (agent install) is the MVP.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 / US2 / US3 for user-story phases only

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project skeleton and licensing.

- [X] T001 [P] Create MIT `LICENSE` with "Copyright (c) 2026 Mario Garrido" (name only, no email)
- [X] T002 [P] Create `.gitignore` ignoring `claude_desktop_config*.json`, `*.bak`, `.env`, `.venv/`, `__pycache__/`, `*.py[oc]`
- [X] T003 Create directory skeleton: `scripts/`, `tests/`, `templates/`, `servers/`, `assets/`, `.github/workflows/`, `.github/ISSUE_TEMPLATE/`

**Checkpoint**: Empty, licensed repo skeleton ready.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The catalog data spine and the shared validation + security tooling that every
user story depends on.

**⚠️ CRITICAL**: No user story work begins until this phase is complete.

- [X] T004 Author `registry.json` with the 6 server entries (twelvedata, yahoo-finance, sec-edgar, coingecko, fetch, youtube-transcript) per `specs/001-claude-mcp-stack/data-model.md` and `contracts/registry.schema.json` (placeholders only; yahoo-finance `runtime: local` with a tag placeholder to be pinned in T018)
- [X] T005 [P] Write FAILING tests in `tests/test_validate_registry.py`: valid registry passes; missing required field fails; bad `runtime`/`category` enum fails; `${TOKEN}` without matching `secrets[].name` fails; a template containing a denylisted pattern fails
- [X] T006 Implement `scripts/validate_registry.py` (stdlib only) to make T005 pass; run it against `registry.json` and confirm exit 0
- [X] T007 [P] Write FAILING tests in `tests/test_check_no_secrets.py`: clean tree exits 0; a planted fixture secret in the tree exits 1; with `--history`, a secret in a prior commit is detected
- [X] T008 Implement `scripts/check_no_secrets.sh` (Layer 1 denylist + generic regexes for home paths/UUIDs/32-hex/`sk-`/`Bearer`; Layer 2 gitleaks/trufflehog if present; `--history` scans `git log -p`) to make T007 pass
- [X] T009 [P] Author `templates/claude_desktop_config.example.json` — placeholders only, `mcpServers` mirroring the catalog ids
- [X] T010 [P] Author `templates/claude_code.mcp.example.json` — placeholders only
- [X] T011 Run `python3 scripts/validate_registry.py` (validates catalog + both templates) and confirm exit 0

**Checkpoint**: Valid catalog, working validator and secret scan, placeholder templates.

---

## Phase 3: User Story 1 - Install the whole stack via an agent (Priority: P1) 🎯 MVP

**Goal**: An agent can read the repo and install the selected servers end-to-end, safely.

**Independent Test**: On a clean machine, an agent installs all servers from `registry.json`
using `AGENTS.md`, merges them with `merge_server.py` (no unrelated key lost), and each passes
a liveness check.

### Tests for User Story 1 ⚠️ (write first, must fail)

- [X] T012 [P] [US1] Write FAILING tests in `tests/test_merge_server.py`: adds `mcpServers[id]`; preserves a populated `preferences` block and other servers byte-stable; creates `{mcpServers:{}}` when absent; refuses to overwrite an existing id without `--force`; replaces with `--force`; **when the target exists, a `.bak.<timestamp>` copy is created before any write and its contents equal the pre-merge file** (Constitution III); `--no-backup` suppresses it

### Implementation for User Story 1

- [X] T013 [US1] Implement `scripts/merge_server.py` (stdlib, **backup-on-write by default** to `<path>.bak.<timestamp>` with `--no-backup` opt-out, atomic write, `--force` semantics, exit codes per `contracts/scripts-cli.md`) to make T012 pass
- [X] T014 [US1] Write `AGENTS.md`: fixed preamble + ordered steps + success criteria + rollback, exactly per `contracts/agent-playbook.md` (prereq install requires explicit confirmation; liveness = spawn-with-EOF)
- [X] T015 [P] [US1] Write `servers/twelvedata.md` and `servers/sec-edgar.md` (what it does + where to get the key / required SEC user-agent, with a fake placeholder + warning)
- [X] T016 [P] [US1] Write `servers/yahoo-finance.md`, `servers/coingecko.md`, `servers/fetch.md`, `servers/youtube-transcript.md` (keyless; yahoo-finance notes the fork + illiquid-symbol fix)
- [X] T017 [US1] Prepare the yahoo-finance fork for publication (LOCAL only): in `~/workspace/mcp-yahoo-finance` **run the fork's test suite and confirm green (evidence for SC-007: illiquid/unknown symbol returns "no data", no crash)**, set repo-local noreply `user.email`, re-author commit `397d567` with an English message, merge the fix into `main`, tag `v0.1.3-mcpstack.1` (no push yet)
- [X] T018 [US1] Pin the fork in `registry.json`: set yahoo-finance `package` to the fork URL and `version_pin` to `v0.1.3-mcpstack.1`; re-run `scripts/validate_registry.py` (exit 0)

**Checkpoint**: MVP — the agent install path is complete and the merge helper is proven safe.

---

## Phase 4: User Story 2 - Understand and trust the project as a human (Priority: P2)

**Goal**: A first-time reader understands what it is, that it is unofficial, that it is safe,
and how to use it; the repo presents as a serious project with CI.

**Independent Test**: From the README alone a reader can answer "what / official? / safe? /
how"; the repo exposes SECURITY/CONTRIBUTING/COC/CHANGELOG and CI runs green.

- [X] T019 [P] [US2] Create `assets/how-it-works.mmd` (Mermaid: user → paste URL → agent reads AGENTS.md → registry.json → merge into client config → verify)
- [X] T020 [US2] Write `README.md` per spec §FR-018 / design §12: title + tagline + "not affiliated with Anthropic" disclaimer + badges; what it is; quickstart (paste-link); example agent transcript; how it works + the diagram; supported clients; servers table; prerequisites; manual install; security & secrets; scope/what-this-is-NOT; FAQ; acknowledgements (upstream credit); license
- [X] T021 [P] [US2] Write `SECURITY.md` (secret-handling stance + vulnerability-reporting path)
- [X] T022 [P] [US2] Write `CONTRIBUTING.md` (add a server = one `registry.json` entry + one `servers/*.md`; how to run validator/tests/secret-scan; English-only; commit/identity rules)
- [X] T023 [P] [US2] Write `CODE_OF_CONDUCT.md` (Contributor Covenant)
- [X] T024 [P] [US2] Write `CHANGELOG.md` (Keep a Changelog; `0.1.0` Unreleased with initial catalog)
- [X] T025 [P] [US2] Write `.github/PULL_REQUEST_TEMPLATE.md`
- [X] T026 [US2] Write `.github/workflows/ci.yml` running `validate_registry.py`, `pytest`, and `check_no_secrets.sh` on push/PR (Ubuntu)

**Checkpoint**: The repo reads as a polished, trustworthy project and is green in CI.

---

## Phase 5: User Story 3 - Add a new server to the catalog (Priority: P3)

**Goal**: A contributor can add a server by editing only the catalog + one doc, validated.

**Independent Test**: Adding a sample entry + doc passes validation with no playbook change; a
malformed entry fails validation with a clear message.

- [X] T027 [P] [US3] Write `.github/ISSUE_TEMPLATE/add-server.md` mirroring the `registry.json` schema fields (id, category, runtime, package, secrets, where_to_get)
- [X] T028 [US3] Add a test in `tests/test_validate_registry.py` proving a brand-new well-formed entry validates AND a malformed new entry fails with a field-identifying message (extends T005); confirm `AGENTS.md` requires no change to install it

**Checkpoint**: Extensibility is demonstrated and guarded by tests.

---

## Phase 6: Polish, Verification & Gated Publication

**Purpose**: Final verification and the approval-gated release of both repos.

**Status (2026-05-30):** History squashed to a single clean noreply initial commit; full
verification green locally AND in CI. Both repos pushed **PRIVATE** for review first:
`github.com/mgatorr/mcp-yahoo-finance` and `github.com/mgatorr/claude-mcp-stack`. Flipping
to **public** is the remaining step, pending the maintainer's review on GitHub.

- [X] T029 Full verification green: `validate_registry.py`, `pytest` (24), `check_no_secrets.sh --history` — all clean after the squash, locally and in CI.
- [X] T030 [P] `CHANGELOG.md` 0.1.0 entry written; README CI badge references `.github/workflows/ci.yml`.
- [X] T031 Fork published **PRIVATE** at `github.com/mgatorr/mcp-yahoo-finance` with tag `v0.1.3-mcpstack.1` (only noreply/upstream authors reachable).
- [X] T032 `claude-mcp-stack` published **PRIVATE**: history squashed to one clean noreply initial commit (no rewrite needed for a new repo), `check_no_secrets.sh --history` clean, pushed, description + topics set.
- [ ] T033 Go public (pending maintainer review on GitHub): flip both repos to public, then confirm pinned fork URL/tag resolves, CI green, README renders (diagram + badges).

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (P1)**: no dependencies.
- **Foundational (P2)**: depends on Setup; BLOCKS all user stories (catalog + validator + scan + templates).
- **US1 (P3)**: depends on Foundational. MVP.
- **US2 (P4)**: depends on Foundational. NOTE (finding I1): CI (T026) runs `pytest`, which
  includes US1's `tests/test_merge_server.py` (T012). For CI to pass green, US1's tests +
  `merge_server.py` (T012/T013) must exist. Therefore T026 effectively depends on US1, and
  US2 is not fully independent of US1 for a green pipeline — sequence US1 before T026 (or
  scope CI to currently-present tests if US2 is delivered first).
- **US3 (P5)**: depends on Foundational (validator); independent of US1/US2.
- **Polish (P6)**: depends on all desired stories; T031–T032 are gated on explicit user approval.

### Within each story

- Tests before implementation (T005→T006, T007→T008, T012→T013); verify red first.
- `registry.json` (T004) before anything that validates or mirrors it.
- Fork prep (T017) before pinning it in the catalog (T018).

### Parallel opportunities

- Setup: T001, T002 in parallel.
- Foundational: T005 and T007 (different test files) in parallel; T009 and T010 in parallel.
- US1: T015 and T016 (different docs) in parallel; T012 parallel with the doc tasks.
- US2: T019, T021, T022, T023, T024, T025 are all different files → parallel; T020 (README) and T026 (CI) after.

---

## Parallel Example: Foundational

```bash
# Author the two failing test suites together (different files):
Task: "Write failing tests in tests/test_validate_registry.py"   # T005
Task: "Write failing tests in tests/test_check_no_secrets.py"     # T007

# Author the two placeholder templates together:
Task: "Author templates/claude_desktop_config.example.json"        # T009
Task: "Author templates/claude_code.mcp.example.json"              # T010
```

---

## Implementation Strategy

### MVP first (User Story 1)

1. Phase 1 Setup → 2. Phase 2 Foundational → 3. Phase 3 US1 → **STOP & validate**: an agent
   can install the stack safely; merge proven non-destructive. This is a demoable MVP.

### Incremental delivery

- Add US2 (presentation + CI) → repo looks professional and is green.
- Add US3 (extensibility) → contributors can add servers safely.
- Phase 6 → verify everything, then publish both repos **only after explicit approval**.

---

## Notes

- [P] = different files, no incomplete dependencies.
- Verify each test FAILS before implementing (Principle V).
- Commit after each task or logical group; English messages; noreply author identity.
- Nothing is pushed to public remotes until T031/T032, which require explicit user approval
  and a clean `--history` secret scan.
