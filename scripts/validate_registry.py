#!/usr/bin/env python3
"""Validate registry.json against the claude-mcp-stack schema, and check that
example templates contain placeholders only.

Stdlib only. Exit codes: 0 valid; 1 validation error(s); 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CATEGORIES = {"finance", "crypto", "web", "media"}
RUNTIMES = {"uvx", "npx", "local"}
ID_RE = re.compile(r"^[a-z0-9-]+$")
SECRET_NAME_RE = re.compile(r"^[A-Z0-9_]+$")
TOKEN_RE = re.compile(r"\$\{([A-Za-z0-9_]+)\}")
URL_RE = re.compile(r"^https?://")

# Patterns that must never appear in placeholder-only files.
_DENYLIST = [
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("home-path-macos", re.compile(r"/Users/[^/\s\"]+/")),  # pragma: allowlist secret
    ("home-path-linux", re.compile(r"/home/[^/\s\"]+/")),  # pragma: allowlist secret
    ("uuid", re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")),
    ("hex-token", re.compile(r"\b[0-9a-f]{32,}\b")),
    ("sk-token", re.compile(r"\bsk-[A-Za-z0-9]{16,}\b")),
    ("bearer", re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{8,}\b")),
]


def find_denylisted_patterns(text: str) -> list[str]:
    """Return a list of 'rule: match' strings for any denylisted pattern found."""
    hits: list[str] = []
    for name, rx in _DENYLIST:
        for m in rx.findall(text):
            hits.append(f"{name}: {m if isinstance(m, str) else m[0]}")
    return hits


def _tokens_in(value) -> set[str]:
    """Collect ${TOKEN} names appearing in a string / list / dict structure."""
    found: set[str] = set()
    if isinstance(value, str):
        found.update(TOKEN_RE.findall(value))
    elif isinstance(value, list):
        for item in value:
            found |= _tokens_in(item)
    elif isinstance(value, dict):
        for item in value.values():
            found |= _tokens_in(item)
    return found


def _validate_secret(secret, where: str, errors: list[str]) -> None:
    if not isinstance(secret, dict):
        errors.append(f"{where}: secret must be an object")
        return
    for field in ("name", "description", "where_to_get", "required"):
        if field not in secret:
            errors.append(f"{where}: secret missing required field '{field}'")
    name = secret.get("name", "")
    if isinstance(name, str) and name and not SECRET_NAME_RE.match(name):
        errors.append(f"{where}: secret name '{name}' must match ^[A-Z0-9_]+$")
    wtg = secret.get("where_to_get", "")
    if not (isinstance(wtg, str) and URL_RE.match(wtg)):
        errors.append(f"{where}: secret '{name}' where_to_get must be an http(s) URL")
    if "required" in secret and not isinstance(secret["required"], bool):
        errors.append(f"{where}: secret '{name}' required must be boolean")


def _validate_server(server, idx: int, seen_ids: set[str], errors: list[str]) -> None:
    where = f"servers[{idx}]"
    if not isinstance(server, dict):
        errors.append(f"{where}: must be an object")
        return

    required = [
        "id", "description", "category", "runtime", "package",
        "version_pin", "args_template", "secrets", "config_snippet", "healthcheck",
    ]
    for field in required:
        if field not in server:
            errors.append(f"{where}: missing required field '{field}'")

    sid = server.get("id", "")
    if isinstance(sid, str) and sid:
        where = f"servers[{idx}] (id={sid})"
        if not ID_RE.match(sid):
            errors.append(f"{where}: id must match ^[a-z0-9-]+$")
        if sid in seen_ids:
            errors.append(f"{where}: id is not unique")
        seen_ids.add(sid)

    if server.get("category") not in CATEGORIES:
        errors.append(f"{where}: category must be one of {sorted(CATEGORIES)}")
    if server.get("runtime") not in RUNTIMES:
        errors.append(f"{where}: runtime must be one of {sorted(RUNTIMES)}")

    for strfield in ("description", "package", "version_pin", "healthcheck"):
        val = server.get(strfield)
        if strfield in server and not (isinstance(val, str) and val.strip()):
            errors.append(f"{where}: '{strfield}' must be a non-empty string")

    if "args_template" in server and not isinstance(server["args_template"], list):
        errors.append(f"{where}: args_template must be a list")

    secrets = server.get("secrets")
    secret_names: set[str] = set()
    if not isinstance(secrets, list):
        errors.append(f"{where}: secrets must be a list")
    else:
        for s in secrets:
            _validate_secret(s, where, errors)
            if isinstance(s, dict) and isinstance(s.get("name"), str):
                secret_names.add(s["name"])

    snippet = server.get("config_snippet")
    if not isinstance(snippet, dict):
        errors.append(f"{where}: config_snippet must be an object")
    else:
        cmd = snippet.get("command")
        if not (isinstance(cmd, str) and cmd.strip()):
            errors.append(f"{where}: config_snippet.command must be a non-empty string")
        if "args" in snippet and not isinstance(snippet["args"], list):
            errors.append(f"{where}: config_snippet.args must be a list")
        if "env" in snippet and not isinstance(snippet["env"], dict):
            errors.append(f"{where}: config_snippet.env must be an object")

    # Every ${TOKEN} must map to a declared secret name for this server.
    used = _tokens_in(server.get("args_template", []))
    used |= _tokens_in(server.get("config_snippet", {}))
    for token in sorted(used - secret_names):
        errors.append(f"{where}: placeholder ${{{token}}} has no matching declared secret")


def validate_registry(data) -> list[str]:
    """Return a list of human-readable validation errors ([] means valid)."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["registry root must be an object"]
    if data.get("version") != 1:
        errors.append("version must equal 1")
    servers = data.get("servers")
    if not isinstance(servers, list) or not servers:
        errors.append("servers must be a non-empty list")
        return errors
    seen_ids: set[str] = set()
    for idx, server in enumerate(servers):
        _validate_server(server, idx, seen_ids, errors)
    return errors


def validate_templates(templates_dir: Path) -> list[str]:
    errors: list[str] = []
    if not templates_dir.is_dir():
        return errors
    for path in sorted(templates_dir.glob("*.json")):
        text = path.read_text()
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}: invalid JSON ({exc})")
            continue
        for hit in find_denylisted_patterns(text):
            errors.append(f"{path.name}: denylisted pattern -> {hit}")
    return errors


def main(argv=None) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Validate registry.json and templates.")
    parser.add_argument("--registry", default=str(repo_root / "registry.json"))
    parser.add_argument("--templates-dir", default=str(repo_root / "templates"))
    args = parser.parse_args(argv)

    try:
        data = json.loads(Path(args.registry).read_text())
    except FileNotFoundError:
        print(f"error: registry not found: {args.registry}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: registry.json is not valid JSON: {exc}", file=sys.stderr)
        return 1

    errors = validate_registry(data)
    errors += validate_templates(Path(args.templates_dir))

    if errors:
        print(f"FAIL: {len(errors)} problem(s) found:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK: registry.json and templates are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
