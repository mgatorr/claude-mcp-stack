"""Tests for scripts/check_no_secrets.sh (written before implementation)."""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_no_secrets.sh"


def _run(*args, cwd=None):
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_clean_tree_passes(tmp_path):
    (tmp_path / "config.example.json").write_text(
        '{"mcpServers": {"x": {"command": "uvx", "args": ["${API_KEY}"]}}}'
    )
    result = _run("--root", str(tmp_path))
    assert result.returncode == 0, result.stdout + result.stderr


def test_planted_email_fails(tmp_path):
    (tmp_path / "leak.md").write_text("contact ops@acme-corp.io for access")  # pragma: allowlist secret
    result = _run("--root", str(tmp_path))
    assert result.returncode == 1


def test_documentation_email_is_allowed(tmp_path):
    # RFC 2606 documentation domains and GitHub noreply are legitimate placeholders.
    (tmp_path / "ex.md").write_text(
        'Use "Jane Doe jane@example.com"; commits use 1+u@users.noreply.github.com'
    )
    result = _run("--root", str(tmp_path))
    assert result.returncode == 0, result.stdout + result.stderr


def test_planted_hex_token_fails(tmp_path):
    (tmp_path / "leak.txt").write_text("key = 0123456789abcdef0123456789abcdef")  # pragma: allowlist secret
    result = _run("--root", str(tmp_path))
    assert result.returncode == 1


def test_history_detects_removed_secret(tmp_path):
    # Build a tiny git repo: commit a secret, then remove it from the working tree.
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.test"], cwd=tmp_path, check=True)  # pragma: allowlist secret
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    secret = tmp_path / "secret.txt"
    secret.write_text("token ops@acme-corp.io leaked")  # pragma: allowlist secret
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "add secret"], cwd=tmp_path, check=True)
    secret.unlink()
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "remove secret"], cwd=tmp_path, check=True)

    # Working tree is clean now → default scan passes...
    assert _run("--root", str(tmp_path)).returncode == 0
    # ...but --history finds it in a prior commit.
    assert _run("--root", str(tmp_path), "--history").returncode == 1
