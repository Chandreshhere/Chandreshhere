#!/usr/bin/env bash
# Fill every placeholder in README.md in one shot.
#
#   ./tools/set-username.sh <github-username> [linkedin-handle] [email]
#
# Re-runnable: it rewrites the placeholders, so run it again to correct a typo
# only if you haven't already replaced them (otherwise just edit README.md).

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "usage: $0 <github-username> [linkedin-handle] [email]" >&2
  exit 1
fi

GH="$1"
LI="${2:-}"
EMAIL="${3:-}"
README="$(dirname "$0")/../README.md"

if [ ! -f "$README" ]; then
  echo "README.md not found next to tools/" >&2
  exit 1
fi

# Verify the account exists before wiring it into a dozen card URLs.
if command -v curl >/dev/null; then
  code=$(curl -s -o /dev/null -w '%{http_code}' "https://api.github.com/users/$GH")
  case "$code" in
    200) echo "✓ github.com/$GH exists" ;;
    404) echo "✗ github.com/$GH does not exist — check the spelling" >&2; exit 1 ;;
    *)   echo "? could not verify (HTTP $code), continuing anyway" ;;
  esac
fi

cp "$README" "$README.bak"
echo "  backup: README.md.bak"

# macOS and GNU sed disagree about -i, so route through a temp file.
tmp=$(mktemp)
sed "s|__USERNAME__|$GH|g" "$README" > "$tmp" && mv "$tmp" "$README"
echo "  username -> $GH"

if [ -n "$LI" ]; then
  tmp=$(mktemp)
  sed "s|__LINKEDIN__|$LI|g" "$README" > "$tmp" && mv "$tmp" "$README"
  echo "  linkedin -> $LI"
fi

if [ -n "$EMAIL" ]; then
  tmp=$(mktemp)
  sed "s|__EMAIL__|$EMAIL|g" "$README" > "$tmp" && mv "$tmp" "$README"
  echo "  email    -> $EMAIL"
fi

left=$(grep -o '__[A-Z]*__' "$README" | sort -u || true)
if [ -n "$left" ]; then
  echo "still to fill in by hand:"
  echo "$left" | sed 's/^/  /'
fi

echo "done — now run: python3 tools/preview.py"
