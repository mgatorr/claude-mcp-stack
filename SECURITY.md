# Security Policy

## Our stance on secrets

`claude-mcp-stack` is a public recipe. It must never contain secrets or personal data:

- All templates and examples are **placeholder-only** (`${TWELVEDATA_API_KEY}`,
  `"Jane Doe jane@example.com"`, etc.).
- Your API keys are written **only** to your local client configuration during install,
  never to this repository.
- A two-layer secret scan (`scripts/check_no_secrets.sh`) runs in CI over the working tree
  and the full git history; any finding blocks the pipeline.
- `.gitignore` excludes real client configs, `*.bak`, `.env`, and virtual environments.

If you ever expose an API key (in a screenshot, a paste, or a commit), **rotate it** at the
provider immediately — rotation invalidates the leaked value.

## Reporting a vulnerability

If you find a security issue in this repository (e.g. a way the install playbook could leak
or mishandle a secret, or a secret accidentally committed):

- **Preferred:** open a [GitHub Security Advisory](https://github.com/mgatorr/claude-mcp-stack/security/advisories/new)
  (private).
- Alternatively, open a regular issue **without** including any secret value.

Please do not include real keys, tokens, or personal data in reports. We aim to acknowledge
reports within a few days.

## Scope

This project orchestrates third-party MCP servers; vulnerabilities in those upstream servers
should be reported to their respective maintainers.
