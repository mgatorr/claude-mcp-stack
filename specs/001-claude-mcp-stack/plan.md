# Implementation Plan: claude-mcp-stack

**Branch**: `main` | **Date**: 2026-05-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-claude-mcp-stack/spec.md`

## Summary

Build a public, agent-first repository that lets a Claude Code agent install a curated set
of finance/research MCP servers into Claude Desktop/Cowork and Claude Code, end-to-end. The
repository splits **data** (a machine-readable `registry.json` catalog) from **process** (an
`AGENTS.md` install playbook), backed by three small, test-first scripts (catalog validator,
safe config-merge helper, two-layer secret scan), professional docs, and CI. One component is
maintained by us — a patched `mcp-yahoo-finance` fork — published under the same pre-publish
approval gate so the catalog's pinned reference resolves.

## Technical Context

**Language/Version**: Python 3.10+ (validator, merge helper) and Bash (secret scan,
prerequisite checks); content as JSON + Markdown.

**Primary Dependencies**: Python standard library only for shipped scripts (`json`, `re`,
`pathlib`, `math`); `pytest` for tests; `gitleaks` **or** `trufflehog` for the entropy layer
of the secret scan, with a pure-regex fallback when neither is installed. Runtime launchers
for the servers themselves are `uvx` and `npx` (not repository dependencies); `uv` builds the
Yahoo Finance fork.

**Storage**: Flat files in the repo (`registry.json`, `templates/*.json`, Markdown docs). No
database.

**Testing**: `pytest` for unit tests (validator schema checks, merge key-preservation,
secret-scan detection); GitHub Actions runs validator + tests + secret scan on every push/PR.

**Target Platform**: The agent install targets macOS, Linux, and Windows. Repository CI runs
on Ubuntu (GitHub Actions).

**Project Type**: Tooling / "recipe" repository — catalog data + documentation + small helper
scripts. Not an application or library.

**Performance Goals**: Not latency-sensitive (install is interactive). The validator and
secret scan MUST complete in a few seconds on the repo.

**Constraints**: No secret or personal data in the repo or git history; placeholder-only
templates; idempotent, backup-first installs; MIT license; upstream MIT preserved; all
artifacts in English; "not affiliated with Anthropic" disclaimer.

**Scale/Scope**: 6 curated servers, 2 client targets, ~25 files. Designed so adding a server
is one catalog entry + one doc.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| I. Security & Privacy First | Placeholder-only templates; two-layer secret scan over tree + history; `.gitignore` blocks real configs/`*.bak`/`.env`/venvs | PASS (design enforces) |
| II. Agent-First, Human-Legible | `AGENTS.md` (process) + `registry.json` (data) split; polished README; fixed agent preamble + success/rollback | PASS |
| III. Idempotent & Safe Installs | Backup-first, merge-only-selected, preserve unrelated keys, verify-or-rollback; tested by merge key-preservation test | PASS |
| IV. Recipe, Not a Vendor Dump | Third-party via `uvx`/`npx`; fork keeps upstream MIT + attribution; registry pins fork by tag | PASS |
| V. Test-First for Real Code | Validator, merge helper, secret scan each built test-first; CI runs them | PASS (enforced in tasks) |
| VI. Professional Presentation | SECURITY/CONTRIBUTING/CODE_OF_CONDUCT/CHANGELOG + README disclaimer/diagram/transcript; English only | PASS |

No violations. Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/001-claude-mcp-stack/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (registry schema + script/agent contracts)
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
claude-mcp-stack/
├── README.md                      # human entry point (structure per spec FR-018)
├── AGENTS.md                      # agent entry point: preamble + ordered playbook + success/rollback
├── registry.json                  # catalog of the 6 servers (data)
├── SECURITY.md  CONTRIBUTING.md  CODE_OF_CONDUCT.md  CHANGELOG.md
├── LICENSE                        # MIT, name only (no email)
├── .gitignore                     # real configs, *.bak, .env, venvs
├── templates/
│   ├── claude_desktop_config.example.json   # Desktop/Cowork, placeholders only
│   └── claude_code.mcp.example.json         # Claude Code (.mcp.json), placeholders only
├── servers/                       # one doc per server (what it does, where to get the key)
│   ├── twelvedata.md  yahoo-finance.md  sec-edgar.md
│   └── coingecko.md   fetch.md          youtube-transcript.md
├── scripts/
│   ├── validate_registry.py       # registry schema validator (+ template placeholder check)
│   ├── merge_server.py            # safe, idempotent config merge (preserves unrelated keys)
│   └── check_no_secrets.sh        # two-layer secret scan (tree + git history)
├── tests/
│   ├── test_validate_registry.py
│   ├── test_merge_server.py
│   └── test_check_no_secrets.py   # invokes the shell scanner on fixtures
├── assets/
│   └── how-it-works.mmd           # Mermaid source for the architecture diagram
└── .github/
    ├── workflows/ci.yml           # validator + pytest + secret scan
    ├── ISSUE_TEMPLATE/add-server.md
    └── PULL_REQUEST_TEMPLATE.md
```

Separate published repository (delivery task, not part of this tree):
`mcp-yahoo-finance` fork → `github.com/mgatorr/mcp-yahoo-finance`, pinned by tag in `registry.json`.

**Structure Decision**: A single flat tooling repo. `registry.json` is the data spine;
`scripts/` holds the only executable code (test-first); `templates/`, `servers/`, and the
root docs are content. This keeps each unit focused and makes "add a server" a one-entry +
one-doc change (SC-006).

## Complexity Tracking

No constitution violations; no entries required.
