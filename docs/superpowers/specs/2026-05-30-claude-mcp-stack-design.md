# claude-mcp-stack — Design Spec

**Date:** 2026-05-30
**Status:** Approved design, pending spec review
**Author:** Mario Garrido (with Claude)

## 1. Purpose

A curated, **agent-first** repository that lets anyone point a Claude Code agent at
the repo URL and have it install a vetted set of finance/research MCP servers into
their Claude client — fully, end-to-end — while a human-readable `README.md`
explains what the project is.

The repo is a **recipe**, not a vendor dump: it documents and orchestrates
third-party MCP servers (launched via `uvx`/`npx`) plus one server maintained by us
(a patched fork of `mcp-yahoo-finance`). It never copies third-party server code.

**Tagline:** "An agent-first installer recipe for finance & research MCP servers."

**Disclaimer:** the project is **not affiliated with, endorsed by, or sponsored by
Anthropic**. "Claude" is used only to describe the target client. This line appears
near the top of the README.

**Upstream credit:** the README has an acknowledgements section crediting every
third-party server (and Max Scheijen for `mcp-yahoo-finance`), reinforcing the
"recipe, not a vendor dump" framing.

**Language:** every artifact in the repo — including commit messages — is written in
**English**.

## 2. Scope

### In scope
- Agent-first install playbook covering **both** targets:
  - Claude Desktop / Cowork → `claude_desktop_config.json`
  - Claude Code (CLI) → `.mcp.json` / `claude mcp add`
- End-to-end agent behavior: detect OS, check/install prerequisites (`uvx`, `node`/`npx`),
  prompt for missing secrets, idempotently merge server entries, build the local
  yahoo-finance fork, and verify each server starts.
- Catalog of the current 6 servers: `twelvedata`, `yahoo-finance`, `sec-edgar`,
  `coingecko`, `fetch`, `youtube-transcript`.
- A separate published fork repo: `github.com/mgatorr/mcp-yahoo-finance` (already patched).

### Out of scope (YAGNI)
- A runnable installer script (`install.sh`/`.py`) as the primary path — rejected in
  favor of an agent playbook (transparent, cross-platform, no execution trust needed).
- Vendoring third-party MCP source code.
- Configuring clients other than Claude Desktop/Cowork and Claude Code.
- Auto-rotating or storing any secret.

## 3. Approach

Chosen approach: **Playbook + manifest** (data/process split).

- `AGENTS.md` holds the **process** (ordered install playbook).
- `registry.json` holds the **data** (machine-readable catalog of servers).

Adding a new MCP later = one JSON entry + one human doc, no playbook rewrite. The
manifest is schema-validated so entries can't silently drift.

Rejected alternatives: a single inline `SETUP.md` (mixes data + process, unvalidatable)
and a runnable installer script (script-first, not agent-first; cross-platform fragility).

## 4. Repository layout

```
claude-mcp-stack/
├── README.md                  # humans: structured per §12
├── AGENTS.md                  # agent entrypoint: preamble + end-to-end playbook (§6)
├── registry.json              # agent data: catalog of the 6 MCP servers
├── SECURITY.md                # vulnerability-reporting policy + secret-handling stance
├── CONTRIBUTING.md            # how to add a server (1 registry entry + 1 doc), run tests/scan
├── CODE_OF_CONDUCT.md         # Contributor Covenant
├── CHANGELOG.md               # Keep a Changelog format; registry versioning policy
├── templates/
│   ├── claude_desktop_config.example.json   # Cowork/Desktop, placeholders only
│   └── claude_code.mcp.example.json         # Claude Code (.mcp.json), placeholders only
├── servers/                   # one human doc per server: what it does, where to get the API key
│   ├── twelvedata.md  yahoo-finance.md  sec-edgar.md
│   └── coingecko.md   fetch.md          youtube-transcript.md
├── scripts/
│   ├── validate_registry.py   # validates registry.json shape + example configs parse
│   └── check_no_secrets.sh    # pre-push secret scan (see §7)
├── tests/
│   └── test_registry.py       # validator + example-JSON validity + merge-preserves-other-keys
├── assets/
│   └── how-it-works.mmd        # Mermaid source for the architecture diagram
├── .github/
│   ├── workflows/ci.yml        # runs validator + secret scan + tests on every PR
│   ├── ISSUE_TEMPLATE/add-server.md   # mirrors the registry schema
│   └── PULL_REQUEST_TEMPLATE.md
├── LICENSE                    # MIT
├── .gitignore                 # ignores real configs / secrets / venvs / *.bak (see §7)
└── docs/superpowers/specs/    # this design doc
```

## 5. `registry.json` schema

Top-level: `{ "version": 1, "servers": [ <server>, ... ] }`.

Each `<server>` object:

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | unique key used as the `mcpServers` key (e.g. `"twelvedata"`) |
| `description` | string | one line, human + agent |
| `category` | string | e.g. `"finance"`, `"crypto"`, `"web"`, `"media"` |
| `runtime` | enum | `"uvx"` \| `"npx"` \| `"local"` |
| `package` | string | PyPI/npm package or, for `local`, the fork git URL |
| `args_template` | array | argv with `${SECRET_NAME}` placeholders |
| `secrets` | array | each: `{ name, description, where_to_get (URL), required (bool) }` |
| `config_snippet` | object | per-target snippet templates (`desktop`, `claude_code`) with placeholders |
| `healthcheck` | string | how the agent confirms it starts (e.g. spawn with EOF, expect clean exit) |
| `notes` | string | optional (e.g. Windows binary path for the local fork) |

`yahoo-finance` is `runtime: "local"`: `package` = `https://github.com/mgatorr/mcp-yahoo-finance`,
with install steps (clone → `uv venv` → `uv pip install -e .`), command path
`<repo>/.venv/bin/mcp-yahoo-finance` (and a `notes` field for Windows
`.venv\Scripts\mcp-yahoo-finance.exe`).

## 6. `AGENTS.md` playbook (agent behavior)

**Fixed entrypoint preamble** (first lines of the file, to reduce agent variance):
> You are installing MCP servers for a Claude client. Read `registry.json` for the
> catalog. Follow the steps below in order. NEVER write any secret, API key, or the
> user's personal data into this repository. Ask the user before overwriting anything.

Ordered, idempotent steps:

1. **Detect environment:** OS (macOS/Linux/Windows) and target client. If ambiguous, ask the user.
2. **Prerequisites:** check `uvx` and `node`/`npx`. If missing, attempt the OS-standard
   install path (brew / apt / winget) and, on failure, print clear manual instructions and stop.
3. **Selection:** read `registry.json`; ask the user which servers to install (default: all).
4. **Secrets:** for each selected server, prompt for any `required` secret that the user
   hasn't already configured. Secrets are entered by the user at install time and written
   only into their local client config — never into the repo.
5. **yahoo-finance (local):** clone the fork, create venv, `uv pip install -e .`, resolve the binary path.
6. **Merge (idempotent + safe):**
   - Back up the target config file first (timestamped `.bak`), written **only** to the
     OS config directory — never inside this repo.
   - Merge only the selected server keys into `mcpServers`; preserve every unrelated key
     and other top-level fields (`preferences`, `coworkUserFilesPath`, etc.) byte-for-byte.
   - If a server key already exists, ask before overwriting.
   - Never echo entered secret values back into the transcript, logs, or any file other
     than the target config.
7. **Verify:** start each newly added server (per its `healthcheck`) and report a summary
   of what was added, skipped, and verified.

**Success criteria:** every selected server is present in the target config AND passed its
healthcheck; no unrelated config key changed; no secret written outside the target config.

**Failure / rollback:** if any healthcheck fails or the merge cannot be completed safely,
restore the `.bak` and report exactly what failed. Never leave a half-merged config.
Users are told (in README and the preamble) to read this playbook before running it,
since prerequisite installs (brew/apt/winget) are privileged actions.

## 7. Security (hard requirements)

This repo is public. No critical or personal data may ever be committed.

- **Templates are authored by hand with placeholders.** They are NOT generated by copying
  the user's real `claude_desktop_config.json` (which contains the full `preferences`
  block, account UUID, device name, etc.).
- **Never in the repo:** real API keys (e.g. the Twelve Data key), personal email/name in
  the SEC user-agent, account UUIDs, device names, and absolute home paths
  (`/Users/<user>/…`). Use `${TWELVEDATA_API_KEY}`, a clearly fake placeholder like <!-- pragma: allowlist secret -->
  `"Jane Doe jane@example.com"`, `$HOME`/`~`, and per-OS path resolution instead.
- **SEC user-agent is the highest copy-paste risk.** `servers/sec-edgar.md` and the
  templates must use the fake placeholder and explicitly warn that whatever the user puts
  there is sent with every SEC request (semi-public). Verify the generated doc never
  contains a real address.
- **`.gitignore`** blocks `*.local.json`, real config files (`claude_desktop_config*.json`),
  `*.bak`, `.env`, `.venv`, and caches.
- **Pre-push secret scan (`scripts/check_no_secrets.sh`) — two layers, blocks publishing
  on any hit, and runs against BOTH the working tree AND full git history of either repo:**
  1. **Denylist (value-based):** the Twelve Data key string; the maintainer's personal email;
     the bare name `Mario Garrido`; the bare username `mgatorr`; the maintainer's device name;
     the account UUID; plus **generic regexes** (not hardcoded to one user): `/Users/[^/\s]+/`, <!-- pragma: allowlist secret -->
     `/home/[^/\s]+/`, and a UUID-shaped pattern. <!-- pragma: allowlist secret -->
  2. **Structural/entropy (pattern-based):** a real scanner (`gitleaks` or `trufflehog`,
     or, as a fallback, regexes for 32+ hex tokens, `sk-…`, `Bearer …`, AWS/Google key
     shapes). This is what catches *new/unknown* secrets a denylist can't.
- **CI** (`.github/workflows/ci.yml`) runs the same scan + validator + tests on every PR.
- **`SECURITY.md`** (real file, surfaced in GitHub's Security tab) documents the
  secret-handling stance and a vulnerability-reporting path. The README's "Security &
  secrets" section tells users their keys stay local and advises rotation if exposed.

## 8. Licensing & public identity

- **`claude-mcp-stack`:** MIT (permissive, ubiquitous, maximizes reuse). `LICENSE` with
  copyright "© 2026 Mario Garrido" — **name only, no email**.
- **`mcp-yahoo-finance` fork:** stays **MIT**, preserving the upstream copyright
  "© 2025 Max Scheijen". We do not relicense. Our modifications are documented in the
  fork's README/commit history; upstream `LICENSE` is kept verbatim.

**Public identity policy ("name yes, Gmail no"):**
- Commits in both public repos are authored with the **GitHub noreply email**
  (`<id>+mgatorr@users.noreply.github.com`), not the maintainer's personal email.
- The existing fork commit `397d567` (currently authored with the personal email, with a
  Spanish message) is **rewritten** before first push: new noreply author + an English
  commit message. Per-repo `git config user.email` is set to the noreply address so future
  commits stay private.
- Display name "Mario Garrido" remains visible (credit/good impression); the Gmail does not.

## 9. Testing

The only real code is `scripts/validate_registry.py`; it is built test-first (TDD):

- `registry.json` parses and matches the schema in §5 (every server has all required fields,
  `runtime` is a valid enum, `secrets[].where_to_get` is a URL).
- Both example config files in `templates/` are valid JSON and contain only placeholders
  (assert none of the denylisted secret patterns appear).
- **Merge safety:** a test feeds a config containing a populated `preferences` block plus
  unrelated servers, merges a new server, and asserts every pre-existing key is preserved
  byte-for-byte (guards §6 step 6 / finding L1).

Markdown docs are not unit-tested; the secret scan (§7) covers them.

**CI:** `.github/workflows/ci.yml` runs the validator, the test suite, and the secret scan
(§7) on every push and PR, and powers the README status badge.

## 10. Delivery

**Required user action (now, independent of the repo):** rotate the Twelve Data API key at
twelvedata.com — it has been exposed in cleartext (finding C1).

- Build both repos locally with commits (English messages; noreply author per §8).
- Re-point the fork's git remote: it currently points at upstream `maxscheijen`. Add an
  `mgatorr` remote and rewrite commit `397d567` (author + English message) before push, so
  an accidental `git push origin` cannot target upstream.
- `registry.json` references the fork **pinned to a tag/commit**, not bare `main`
  (reproducibility/trust). The referenced URL must match the real published location.
- Run the two-layer secret scan (§7) over working tree **and git history** of both repos.
- Publish to GitHub (`mgatorr`) **only after explicit user approval** (user chose
  "local first, review, then push"). Order: publish the fork first (the stack depends on
  its URL), then `claude-mcp-stack`. After push, set the GitHub repo description + topics
  (`mcp`, `claude`, `model-context-protocol`, `claude-code`, `agents`).

## 11. Community & contribution docs

A serious public repo ships these (findings from the documentation review):

- **SECURITY.md** — reporting path + secret-handling stance (§7).
- **CONTRIBUTING.md** — how to add a server (one `registry.json` entry + one `servers/*.md`),
  how to run the validator/tests, and the secret-scan gate.
- **CODE_OF_CONDUCT.md** — Contributor Covenant.
- **CHANGELOG.md** — Keep a Changelog format; documents how the `registry.json` catalog is
  versioned over time.
- **`.github/`** — `ISSUE_TEMPLATE/add-server.md` (mirrors the registry schema),
  `PULL_REQUEST_TEMPLATE.md`, and `workflows/ci.yml`.
- **Badges** — license, CI status, "MCP servers: 6".

## 12. README structure (humans)

The README is the entire first impression and must be authored deliberately:

1. **Title + tagline + "not affiliated with Anthropic" disclaimer** (§1) + badges.
2. **What it is** — the recipe/agent-first value prop in 2–3 lines.
3. **Quickstart** — the "paste this repo link to a Claude Code agent" flow.
4. **Example agent transcript** — one concrete dialogue (detect OS → choose servers →
   prompt for key → merge → verify) so the unfamiliar UX is legible and proven.
5. **How it works** — short narrative + a **Mermaid diagram** (user → paste URL → agent
   reads AGENTS.md → registry.json → merges into client config → verify).
6. **Supported clients** — Claude Desktop/Cowork and Claude Code.
7. **Servers table** — name, category, runtime (uvx/npx/local), API key required?, link to
   `servers/*.md`.
8. **Prerequisites** — `uvx`, `node`/`npx`.
9. **Manual install** — fallback for users who don't want the agent flow.
10. **Security & secrets** — keys stay local; rotation advice; link to SECURITY.md.
11. **Scope / What this is NOT** — reuse §2 out-of-scope (transparency, maturity signal).
12. **FAQ** — "Is this official?", "Are my keys safe?", "Why an agent instead of a script?",
    "Can I add my own server?".
13. **Acknowledgements** (upstream credit, §1) + **License** (MIT, with badge).
