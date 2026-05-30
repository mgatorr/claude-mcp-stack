# Pull Request

## What does this change?

<!-- Brief description. If adding a server, name it. -->

## Checklist

- [ ] `python3 scripts/validate_registry.py` passes
- [ ] `python3 -m pytest -q` passes
- [ ] `scripts/check_no_secrets.sh --history` is clean
- [ ] No secrets or personal data added (templates are placeholder-only)
- [ ] Docs updated (README / `servers/*.md` / CHANGELOG as applicable)
- [ ] All changes and commit messages are in English

## If adding a server

- [ ] One entry added to `registry.json` (valid per the schema)
- [ ] `servers/<id>.md` added
- [ ] Entry mirrored (placeholders only) in both `templates/` files
- [ ] No change required to `AGENTS.md`
