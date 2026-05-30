# claude-mcp-stack — agent context

This repository is an agent-first installer recipe for a curated set of MCP servers. When a
user asks you to install the servers, follow `AGENTS.md` and read `registry.json`.

Hard rules (see `docs/constitution.md`):
- Never write secrets or personal data into this repository.
- Templates are placeholder-only.
- Installs are backup-first and idempotent; never clobber unrelated config keys.
- All artifacts are in English.

<!-- SPECKIT START -->
Active feature plan: `specs/001-claude-mcp-stack/plan.md`
Spec: `specs/001-claude-mcp-stack/spec.md` · Constitution: `docs/constitution.md`
<!-- SPECKIT END -->
