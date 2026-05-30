#!/usr/bin/env bash
# Two-layer secret scan for claude-mcp-stack.
#
#   Layer 1: value/pattern denylist (emails, home paths, UUIDs, 32+ hex tokens,
#            sk-... keys, Bearer tokens), with an allowlist for documentation
#            domains (RFC 2606) and GitHub noreply addresses.
#   Layer 2: structural/entropy scan via gitleaks or trufflehog if installed.
#
# Scans the working tree by default; with --history also scans full git history.
# Usage: check_no_secrets.sh [--root DIR] [--history]
# Exit: 0 clean | 1 potential secret found | 2 usage error.

set -u

ROOT=""
SCAN_HISTORY=false

while [ $# -gt 0 ]; do
  case "$1" in
    --root) ROOT="${2:-}"; shift 2 || { echo "error: --root needs a value" >&2; exit 2; } ;;
    --history) SCAN_HISTORY=true; shift ;;
    -h|--help) echo "Usage: check_no_secrets.sh [--root DIR] [--history]"; exit 0 ;;
    *) echo "error: unknown argument '$1'" >&2; exit 2 ;;
  esac
done

if [ -z "$ROOT" ]; then
  ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi
if [ ! -d "$ROOT" ]; then
  echo "error: root not a directory: $ROOT" >&2; exit 2
fi

# Denylist rules: "name|ERE"
RULES=(
  "email|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
  "home-path-macos|/Users/[^/[:space:]\"]+/"  # pragma: allowlist secret
  "home-path-linux|/home/[^/[:space:]\"]+/"  # pragma: allowlist secret
  "uuid|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
  "hex-token|[0-9a-f]{32,}"
  "sk-token|sk-[A-Za-z0-9]{16,}"
  "bearer|Bearer[[:space:]]+[A-Za-z0-9._-]{8,}"
)

# Matches we treat as legitimate placeholders (not secrets).
ALLOW_RE='users\.noreply\.github\.com|@example\.(com|org|net)|example\.com|example\.org'
# Lines carrying this marker are intentional (regex defs, test fixtures, docs).
PRAGMA='pragma: allowlist secret'

found=0

# --- Layer 1: working-tree scan ---
for rule in "${RULES[@]}"; do
  name="${rule%%|*}"
  regex="${rule#*|}"
  # Recursive, line-numbered, skip binaries and noise dirs.
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    # Drop allowlisted placeholder lines (doc domains, noreply) and pragma'd lines.
    if printf '%s' "$line" | grep -Eq "$ALLOW_RE" \
       || printf '%s' "$line" | grep -qF "$PRAGMA"; then
      continue
    fi
    if [ "$found" -eq 0 ]; then
      echo "Potential secrets found (working tree):"
    fi
    found=1
    # Print file:line and the rule, never the full matched secret.
    echo "  [$name] ${line%%:*}:$(printf '%s' "$line" | cut -d: -f2)"
  done < <(grep -rEnI \
            --exclude-dir=.git --exclude-dir=.venv --exclude-dir=venv \
            --exclude-dir=node_modules --exclude-dir=.pytest_cache --exclude-dir=.specify \
            -- "$regex" "$ROOT" 2>/dev/null)
done

# --- Layer 2: entropy / structural scanner (optional) ---
if command -v gitleaks >/dev/null 2>&1; then
  if ! gitleaks detect --source "$ROOT" --no-banner >/dev/null 2>&1; then
    echo "  [gitleaks] reported potential secrets in $ROOT"
    found=1
  fi
elif command -v trufflehog >/dev/null 2>&1; then
  if trufflehog filesystem "$ROOT" --no-update --fail >/dev/null 2>&1; then
    : # exit 0 == clean
  else
    echo "  [trufflehog] reported potential secrets in $ROOT"
    found=1
  fi
fi

# --- Optional: git history scan ---
if [ "$SCAN_HISTORY" = true ] && git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  for rule in "${RULES[@]}"; do
    name="${rule%%|*}"
    regex="${rule#*|}"
    # Scan only ADDED file-content lines across history (skip diff/commit metadata
    # such as 'index <sha>' lines and Co-Authored-By trailers), excluding vendored
    # tooling (.specify); drop allowlisted placeholders and pragma'd lines.
    if git -C "$ROOT" log -p --all -- . ':(exclude).specify' 2>/dev/null \
        | grep -E '^\+' 2>/dev/null | grep -vE '^\+\+\+' 2>/dev/null \
        | grep -E -- "$regex" 2>/dev/null \
        | grep -Ev "$ALLOW_RE" 2>/dev/null \
        | grep -vF "$PRAGMA" 2>/dev/null | grep -q .; then
      if [ "$found" -eq 0 ]; then echo "Potential secrets found:"; fi
      echo "  [history:$name] match in git history"
      found=1
    fi
  done
fi

if [ "$found" -ne 0 ]; then
  echo "FAIL: potential secrets detected. Resolve before publishing."
  exit 1
fi
echo "OK: no secrets detected."
exit 0
