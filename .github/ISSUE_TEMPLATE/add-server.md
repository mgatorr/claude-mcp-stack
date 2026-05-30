---
name: Add a server
about: Propose a new MCP server for the curated catalog
title: "add server: <id>"
labels: ["add-server"]
---

Please mirror the fields of a `registry.json` entry (see the schema in
`specs/001-claude-mcp-stack/contracts/registry.schema.json`).

- **id** (lowercase, `[a-z0-9-]`):
- **description** (one line):
- **category** (`finance` / `crypto` / `web` / `media`):
- **runtime** (`uvx` / `npx` / `local`):
- **package** (PyPI/npm id, or git URL for `local`):
- **version_pin** (tag/version; a moving tag is fine for `npx`, a fixed tag for `local`):
- **secrets** (for each: NAME, what it's for, where_to_get URL, required?):
- **config_snippet** (the `command` + `args` + optional `env`, placeholders only):
- **healthcheck** (e.g. `spawn-eof`):

### Checklist

- [ ] Placeholders only — no real keys, emails, or paths
- [ ] Every `${TOKEN}` has a matching `secrets` entry
- [ ] I can add `servers/<id>.md` and mirror the entry in `templates/`
- [ ] I understand no change to `AGENTS.md` should be required
