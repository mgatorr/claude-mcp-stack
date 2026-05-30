"""Tests for scripts/merge_server.py (written before implementation)."""

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "merge_server.py"

ENTRY = '{"command": "uvx", "args": ["mcp-server-fetch"]}'


def _run(*args):
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def _existing_config(tmp_path):
    cfg = tmp_path / "claude_desktop_config.json"
    cfg.write_text(json.dumps({
        "mcpServers": {"existing": {"command": "npx", "args": ["-y", "x"]}},
        "preferences": {"theme": "dark", "nested": {"a": 1, "b": [1, 2, 3]}},
        "topLevel": "keep-me",
    }, indent=2))
    return cfg


def test_adds_entry_and_preserves_unrelated_keys(tmp_path):
    cfg = _existing_config(tmp_path)
    r = _run("--config", str(cfg), "--id", "fetch", "--entry", ENTRY)
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(cfg.read_text())
    assert data["mcpServers"]["fetch"] == {"command": "uvx", "args": ["mcp-server-fetch"]}
    assert data["mcpServers"]["existing"] == {"command": "npx", "args": ["-y", "x"]}
    assert data["preferences"] == {"theme": "dark", "nested": {"a": 1, "b": [1, 2, 3]}}
    assert data["topLevel"] == "keep-me"


def test_creates_config_when_absent(tmp_path):
    cfg = tmp_path / "new.json"
    r = _run("--config", str(cfg), "--id", "fetch", "--entry", ENTRY)
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(cfg.read_text())
    assert data["mcpServers"]["fetch"]["command"] == "uvx"


def test_refuses_overwrite_without_force(tmp_path):
    cfg = _existing_config(tmp_path)
    r = _run("--config", str(cfg), "--id", "existing", "--entry", ENTRY)
    assert r.returncode == 3
    # unchanged
    data = json.loads(cfg.read_text())
    assert data["mcpServers"]["existing"] == {"command": "npx", "args": ["-y", "x"]}


def test_replaces_with_force(tmp_path):
    cfg = _existing_config(tmp_path)
    r = _run("--config", str(cfg), "--id", "existing", "--entry", ENTRY, "--force")
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(cfg.read_text())
    assert data["mcpServers"]["existing"] == {"command": "uvx", "args": ["mcp-server-fetch"]}


def test_backup_created_and_equals_pre_merge(tmp_path):
    cfg = _existing_config(tmp_path)
    pre = cfg.read_text()
    r = _run("--config", str(cfg), "--id", "fetch", "--entry", ENTRY)
    assert r.returncode == 0, r.stdout + r.stderr
    backups = list(tmp_path.glob("claude_desktop_config.json.bak.*"))
    assert len(backups) == 1, f"expected one backup, found {backups}"
    assert backups[0].read_text() == pre


def test_no_backup_flag_suppresses_backup(tmp_path):
    cfg = _existing_config(tmp_path)
    r = _run("--config", str(cfg), "--id", "fetch", "--entry", ENTRY, "--no-backup")
    assert r.returncode == 0, r.stdout + r.stderr
    assert list(tmp_path.glob("*.bak.*")) == []
