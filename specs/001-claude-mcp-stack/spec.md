# Feature Specification: claude-mcp-stack

**Feature Branch**: `001-claude-mcp-stack`

**Created**: 2026-05-30

**Status**: Draft

**Input**: Approved design doc `docs/superpowers/specs/2026-05-30-claude-mcp-stack-design.md`

## Clarifications

### Session 2026-05-30

- Q: When a prerequisite (Python/Node runner) is missing, should the agent auto-install it? → A: No — the agent MUST ask for explicit confirmation before any system-level install; it never installs system packages silently.
- Q: How deep is the per-server start-up verification? → A: Lightweight process liveness — launch the server and confirm it starts and stays up briefly without crashing (accepts EOF, exits cleanly); not a full MCP handshake.
- Q: Is publishing/tagging the Yahoo Finance fork part of this feature? → A: Yes — explicit delivery tasks (privacy-preserving author identity, rewrite the fork commit, tag a fixed version, create the public repo, push) under the same pre-publish approval gate, so the catalog's pinned reference resolves.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install the whole stack by handing the repo to an agent (Priority: P1)

A developer who uses Claude wants finance/research data tools inside their Claude client.
They paste the repository link to a Claude Code agent and ask it to set everything up. The
agent figures out their operating system and which Claude client they use, confirms the
prerequisites are present, asks for any API keys it needs, and adds the selected servers to
the correct configuration file. When it finishes, the new tools work in their Claude client
and nothing they had configured before was lost.

**Why this priority**: This is the core promise of the project — a one-paste, end-to-end
install. Without it, the repository is just documentation.

**Independent Test**: Point an agent at the repo on a clean machine, accept the default
(all servers), provide test keys when prompted, and confirm each selected server is present
in the client config and starts successfully — with any pre-existing configuration intact.

**Acceptance Scenarios**:

1. **Given** a machine with the prerequisites available and a supported Claude client,
   **When** the agent runs the install for all servers and is given the required keys,
   **Then** every selected server appears in the client configuration and passes its
   start-up check.
2. **Given** a client config that already contains unrelated servers and personal
   preferences, **When** the agent merges the new servers, **Then** all pre-existing
   entries are preserved unchanged.
3. **Given** a server entry that already exists in the config, **When** the agent would
   overwrite it, **Then** the agent asks for confirmation before changing it.
4. **Given** a start-up check fails for a server, **When** the agent detects the failure,
   **Then** it restores the pre-install backup and reports what failed rather than leaving
   a partially modified config.

---

### User Story 2 - Understand and trust the project as a human reader (Priority: P2)

A visitor lands on the repository and needs to quickly understand what it is, whether it is
safe, whether it is official, and how to use it — either through the agent flow or manually.

**Why this priority**: Adoption and credibility depend on a clear, professional first
impression and an explicit security stance.

**Independent Test**: A first-time reader can, from the README alone, state what the project
does, confirm it is not affiliated with Anthropic, see the list of servers and which need
keys, and follow a manual install path without the agent.

**Acceptance Scenarios**:

1. **Given** the README, **When** a reader skims it, **Then** they find the value
   proposition, an explicit non-affiliation disclaimer, a servers overview, a security
   section, and both the agent and manual install paths.
2. **Given** the repository root, **When** a reader looks for project-health signals,
   **Then** they find security, contribution, conduct, and changelog documents and a
   visible license.

---

### User Story 3 - Add a new server to the catalog (Priority: P3)

A contributor wants to add another MCP server to the curated stack.

**Why this priority**: Extensibility keeps the project alive but is not required for the
first release.

**Independent Test**: A contributor adds one catalog entry plus one server document, runs
the provided validation, and the new server is installable by the agent without any change
to the install playbook.

**Acceptance Scenarios**:

1. **Given** a new catalog entry and its server document, **When** the contributor runs the
   catalog validation, **Then** validation passes and the agent can install the new server
   using the same playbook.
2. **Given** a malformed catalog entry, **When** validation runs, **Then** it fails with a
   message identifying the missing or invalid field.

---

### Edge Cases

- **Missing prerequisite**: a required launcher (Python runner or Node runner) is absent —
  the agent attempts the platform-standard install and, if that fails, stops with clear
  manual instructions instead of producing a broken config.
- **Illiquid / dataless symbol in the finance fork**: the bundled Yahoo Finance server must
  return a clear "no data" message rather than crashing (the original defect that motivated
  the fork).
- **Missing or declined API key**: a server requiring a key the user cannot provide is
  skipped with an explanation; other selected servers still install.
- **Unknown or unsupported client**: the agent asks the user to choose a supported client
  rather than guessing and writing to the wrong location.
- **Secret accidentally present before publishing**: the pre-publish scan finds it (in the
  working tree or git history) and blocks publishing.
- **Re-running the install**: running the agent again does not duplicate entries or corrupt
  the config (idempotent).

## Requirements *(mandatory)*

### Functional Requirements

#### Catalog & content

- **FR-001**: The repository MUST provide a machine-readable catalog describing each curated
  server: identifier, description, category, how it is launched, required secrets (with
  where to obtain them), the configuration entry to add, and how to verify it started.
- **FR-002**: The repository MUST provide a human-readable document for each server
  explaining what it does and where to obtain any required key.
- **FR-003**: The catalog MUST cover the curated set: Twelve Data, Yahoo Finance, SEC EDGAR,
  CoinGecko, web fetch, and YouTube transcript.
- **FR-004**: The bundled Yahoo Finance server MUST be referenced as a maintained fork
  pinned to a fixed version, and MUST preserve the upstream license and attribution.
  Publishing that fork is part of this feature's delivery: the fork commit MUST be re-authored
  with a privacy-preserving identity, tagged at a fixed version, and pushed to a public
  repository (under the same pre-publish approval gate) before the catalog reference is
  considered resolvable.

#### Agent install behavior

- **FR-005**: The repository MUST provide an agent playbook that opens with a fixed
  instruction preamble and defines ordered install steps, explicit success criteria, and
  rollback rules.
- **FR-006**: The agent MUST support installing into both supported clients (the desktop
  client and the command-line client) and MUST write to the correct location for the chosen
  client.
- **FR-007**: The agent MUST detect the operating system and verify prerequisites before
  changing anything. If a prerequisite is missing, the agent MUST ask for explicit user
  confirmation before any system-level install (naming the tool and package manager); it
  MUST NOT install system packages silently. If the user declines or the install fails, the
  agent MUST stop with clear manual instructions.
- **FR-008**: The agent MUST let the user choose which servers to install (default: all).
- **FR-009**: The agent MUST prompt for any required secret that is not already configured,
  and MUST NOT write secrets anywhere other than the user's client configuration.
- **FR-010**: Before modifying a client config, the agent MUST create a backup stored only
  in the operating-system configuration location, never inside the repository.
- **FR-011**: The agent MUST merge only the selected server entries and MUST preserve every
  unrelated configuration key unchanged; it MUST ask before overwriting an existing entry.
- **FR-012**: After install, the agent MUST verify each added server with a lightweight
  liveness check (launch the process and confirm it starts and stays up briefly without
  crashing — not a full protocol handshake) and report a summary; on any verification
  failure it MUST restore the backup and not leave a partial configuration.
- **FR-013**: Re-running the install MUST be idempotent (no duplicate or corrupted entries).

#### Security & privacy

- **FR-014**: No secret or personal datum may be committed to the repository or its history;
  all examples and templates MUST contain placeholders only.
- **FR-015**: The repository MUST provide a pre-publish secret scan with two layers — a
  value/pattern denylist (including generic home-path and identifier patterns) and a
  structural/entropy scanner — that runs over both the working tree and the full git history
  and blocks publishing on any finding.
- **FR-016**: Ignore rules MUST exclude real configuration files, backups, environment
  files, and virtual environments from version control.
- **FR-017**: Continuous integration MUST run the catalog validation, the test suite, and
  the secret scan on every change.

#### Presentation & licensing

- **FR-018**: The README MUST include the value proposition, an explicit "not affiliated
  with Anthropic" disclaimer, a servers table, a "how it works" explanation with a diagram,
  an example agent transcript, the security stance, and a manual install fallback.
- **FR-019**: The repository MUST include security, contribution, code-of-conduct, and
  changelog documents, plus issue/PR templates.
- **FR-020**: The repository MUST be released under a permissive license, with the
  maintainer's display name but without a personal email address; public commits MUST use a
  privacy-preserving author identity.
- **FR-021**: All repository artifacts, including commit messages, MUST be written in
  English.

### Key Entities *(include if feature involves data)*

- **Server catalog**: the list of curated servers and, per server, all metadata the agent
  needs to install and verify it.
- **Server entry**: one catalog item — identifier, description, category, launch method,
  required secrets, config entry, verification check, and optional notes.
- **Secret descriptor**: a named credential a server needs, with a human description, where
  to obtain it, and whether it is required.
- **Target client configuration**: the user's existing client config file that the agent
  safely augments.
- **Example template**: a placeholder-only configuration sample for each supported client.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can go from pasting the repo link to working tools in their Claude
  client in a single guided session, providing only their API keys.
- **SC-002**: After install, 100% of selected servers that have valid credentials are
  present in the config and pass their lightweight liveness check (process starts without
  crashing).
- **SC-003**: Across installs, 0 pre-existing configuration keys are lost or altered (only
  selected server entries are added or, with confirmation, replaced).
- **SC-004**: 0 secrets or personal data are present in the published repository or its git
  history, as verified by the scan.
- **SC-005**: A first-time reader can answer "what is it, is it official, is it safe, how do
  I use it" from the README alone.
- **SC-006**: A contributor can add a new server by editing only the catalog and adding one
  document, with validation passing and no change to the install playbook.
- **SC-007**: The bundled Yahoo Finance server returns a clear "no data" result for an
  illiquid or unknown symbol instead of failing.

## Assumptions

- The two supported clients are the Claude desktop application (Cowork) and the Claude
  command-line client; other clients are out of scope for the first release.
- The curated catalog is the six servers listed above; additional servers are future work.
- Users run a mainstream operating system (macOS, Linux, or Windows) with internet access.
- The agent performing the install is a Claude Code agent with permission to run commands
  and edit files on the user's machine, with the user present to approve prompts.
- Publishing the maintained Yahoo Finance fork is part of this feature's delivery (not an
  external prerequisite); its pinned version must resolve once those delivery tasks run.
- Secret rotation and credential issuance for third-party services are the user's
  responsibility; the project only handles placement of keys the user supplies.
