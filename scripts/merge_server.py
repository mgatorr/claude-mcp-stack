#!/usr/bin/env python3
"""Safely merge one MCP server entry into a client config (claude_desktop_config.json
or .mcp.json), preserving every unrelated key.

Backup-on-write by default (Constitution III): if the target exists, a timestamped
`<config>.bak.<YYYYMMDD-HHMMSS-microseconds>` copy is written before any modification.

Stdlib only. Exit codes: 0 merged | 3 would overwrite without --force | 1 invalid input
| 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Merge an MCP server entry into a config.")
    parser.add_argument("--config", required=True, help="target client config path")
    parser.add_argument("--id", required=True, help="server id (mcpServers key)")
    parser.add_argument("--entry", required=True, help="config_snippet object as JSON")
    parser.add_argument("--force", action="store_true", help="replace an existing entry")
    parser.add_argument("--no-backup", action="store_true", help="do not write a .bak copy")
    args = parser.parse_args(argv)

    try:
        entry = json.loads(args.entry)
    except json.JSONDecodeError as exc:
        print(f"error: --entry is not valid JSON: {exc}", file=sys.stderr)
        return 1
    if not isinstance(entry, dict):
        print("error: --entry must be a JSON object", file=sys.stderr)
        return 1

    config_path = Path(args.config)
    exists = config_path.exists()

    if exists:
        try:
            data = json.loads(config_path.read_text())
        except json.JSONDecodeError as exc:
            print(f"error: {config_path} is not valid JSON: {exc}", file=sys.stderr)
            return 1
        if not isinstance(data, dict):
            print("error: config root must be a JSON object", file=sys.stderr)
            return 1
    else:
        data = {}

    servers = data.get("mcpServers")
    if servers is None:
        servers = {}
        data["mcpServers"] = servers
    elif not isinstance(servers, dict):
        print("error: 'mcpServers' must be an object", file=sys.stderr)
        return 1

    if args.id in servers and not args.force:
        print(
            f"refusing to overwrite existing server '{args.id}' without --force",
            file=sys.stderr,
        )
        return 3

    # Backup before any write (only when the target already exists).
    if exists and not args.no_backup:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = config_path.with_name(config_path.name + f".bak.{stamp}")
        shutil.copy2(config_path, backup)

    servers[args.id] = entry

    # Atomic write: temp file in same dir, then replace.
    target_dir = config_path.parent if str(config_path.parent) else Path(".")
    target_dir.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(target_dir), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
        os.replace(tmp, config_path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise

    print(f"OK: merged server '{args.id}' into {config_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
