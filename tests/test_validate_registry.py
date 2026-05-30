"""Tests for scripts/validate_registry.py (written before implementation)."""

import copy
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate_registry as vr  # noqa: E402


def _load_real_registry():
    return json.loads((REPO_ROOT / "registry.json").read_text())


def test_real_registry_passes():
    errors = vr.validate_registry(_load_real_registry())
    assert errors == [], f"expected no errors, got: {errors}"


def test_missing_required_field_fails():
    data = _load_real_registry()
    del data["servers"][0]["description"]
    errors = vr.validate_registry(data)
    assert any("description" in e for e in errors)


def test_bad_runtime_enum_fails():
    data = _load_real_registry()
    data["servers"][0]["runtime"] = "docker"
    errors = vr.validate_registry(data)
    assert any("runtime" in e for e in errors)


def test_bad_category_enum_fails():
    data = _load_real_registry()
    data["servers"][0]["category"] = "sports"
    errors = vr.validate_registry(data)
    assert any("category" in e for e in errors)


def test_duplicate_id_fails():
    data = _load_real_registry()
    data["servers"][1]["id"] = data["servers"][0]["id"]
    errors = vr.validate_registry(data)
    assert any("id" in e.lower() and "uniqu" in e.lower() for e in errors)


def test_unknown_token_without_secret_fails():
    data = _load_real_registry()
    # fetch has no secrets; inject a placeholder token with no matching secret
    fetch = next(s for s in data["servers"] if s["id"] == "fetch")
    fetch["config_snippet"]["args"].append("${MYSTERY_TOKEN}")
    errors = vr.validate_registry(data)
    assert any("MYSTERY_TOKEN" in e for e in errors)


def test_bad_where_to_get_url_fails():
    data = _load_real_registry()
    td = next(s for s in data["servers"] if s["id"] == "twelvedata")
    td["secrets"][0]["where_to_get"] = "not-a-url"
    errors = vr.validate_registry(data)
    assert any("where_to_get" in e for e in errors)


def test_version_must_be_one():
    data = _load_real_registry()
    data["version"] = 2
    errors = vr.validate_registry(data)
    assert any("version" in e for e in errors)


def test_denylist_detects_email():
    found = vr.find_denylisted_patterns('contact me at someone@example.com today')
    assert found  # non-empty list of matches


def test_denylist_detects_home_path():
    found = vr.find_denylisted_patterns('/Users/alice/secret/config.json')  # pragma: allowlist secret
    assert found


def test_denylist_clean_text_is_empty():
    found = vr.find_denylisted_patterns('${TWELVEDATA_API_KEY} and a normal sentence')
    assert found == []


# --- US3: extensibility (adding a server is a one-entry change) ---

NEW_ENTRY = {
    "id": "alpha-vantage",
    "description": "Market data via Alpha Vantage.",
    "category": "finance",
    "runtime": "uvx",
    "package": "some-alpha-vantage-mcp",
    "version_pin": "latest",
    "args_template": ["some-alpha-vantage-mcp", "--key", "${ALPHAVANTAGE_API_KEY}"],
    "secrets": [
        {
            "name": "ALPHAVANTAGE_API_KEY",
            "description": "Alpha Vantage API key.",
            "where_to_get": "https://www.alphavantage.co/support/#api-key",
            "required": True,
        }
    ],
    "config_snippet": {
        "command": "uvx",
        "args": ["some-alpha-vantage-mcp", "--key", "${ALPHAVANTAGE_API_KEY}"],
    },
    "healthcheck": "spawn-eof",
}


def test_new_wellformed_entry_validates():
    data = _load_real_registry()
    data["servers"].append(copy.deepcopy(NEW_ENTRY))
    assert vr.validate_registry(data) == []


def test_new_malformed_entry_fails_with_field_name():
    data = _load_real_registry()
    bad = copy.deepcopy(NEW_ENTRY)
    bad["secrets"][0]["where_to_get"] = "ftp://nope"  # not http(s)
    data["servers"].append(bad)
    errors = vr.validate_registry(data)
    assert any("where_to_get" in e for e in errors)
