# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the catalog is versioned via
the `version` field in `registry.json`.

## [Unreleased]

### Added

- README visuals: hero banner, a hero-styled "how it works" graphic, and an animated
  agent-install demo GIF.
- CI hardening: a Python 3.10 / 3.12 test matrix and a dedicated secret-scan job (the repo
  scanner over working tree + full history, plus `gitleaks`); least-privilege `permissions`
  and `concurrency` cancellation.
- `.gitleaks.toml` allowlist for the deliberate (fake) test fixtures.

## [0.1.0] - 2026-05-30

### Added

- Initial curated catalog (`registry.json`, schema version 1) with 6 servers: twelvedata,
  yahoo-finance, sec-edgar, coingecko, fetch, youtube-transcript.
- Agent install playbook (`AGENTS.md`) for Claude Desktop/Cowork and Claude Code.
- Placeholder-only example templates for both clients.
- Tooling (test-first): `validate_registry.py`, `merge_server.py` (backup-first, safe merge),
  `check_no_secrets.sh` (two-layer secret scan over tree + history).
- Per-server docs, README, SECURITY, CONTRIBUTING, CODE_OF_CONDUCT, and CI.
- Bundled Yahoo Finance fork pinned at `v0.1.3-mcpstack.1` with an illiquid-symbol crash fix.

[Unreleased]: https://github.com/mgatorr/claude-mcp-stack/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mgatorr/claude-mcp-stack/releases/tag/v0.1.0
