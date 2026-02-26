#!/usr/bin/env bash
# sync_bundled_assets.sh
#
# Copies bundled asset JSON files from jlpt-bites-ecosystem (source of truth)
# to the Flutter app's assets/data/ directory.
#
# Usage:
#   ./scripts/sync_bundled_assets.sh [--app-dir <path>]
#
# Defaults:
#   APP_DIR = ../jlpt-bites  (sibling directory)
#
# Examples:
#   ./scripts/sync_bundled_assets.sh
#   ./scripts/sync_bundled_assets.sh --app-dir /path/to/jlpt-bites

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ECOSYSTEM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default app path (sibling directory)
APP_DIR="${APP_DIR:-$(cd "$ECOSYSTEM_DIR/../jlpt-bites" 2>/dev/null && pwd || echo "")}"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --app-dir)
      APP_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$APP_DIR" || ! -d "$APP_DIR" ]]; then
  echo "Error: Flutter app directory not found: '${APP_DIR}'"
  echo "Usage: $0 [--app-dir <path>]"
  exit 1
fi

echo "=== sync_bundled_assets.sh ==="
echo "  Source : $ECOSYSTEM_DIR"
echo "  Target : $APP_DIR"
echo ""

copy_file() {
  local src="$1"
  local dst_dir="$2"
  local dst="$dst_dir/$(basename "$src")"

  if [[ ! -f "$src" ]]; then
    echo "  ❌ Source not found: $src"
    return 1
  fi

  mkdir -p "$dst_dir"
  cp "$src" "$dst"
  echo "  ✅ $(basename "$src")"
}

# ── vocabulary/ ─────────────────────────────────────────────────────────────
echo "vocabulary/"
copy_file "$ECOSYSTEM_DIR/backend/vocabulary/data/kanji_reading_drill.json"  "$APP_DIR/assets/data/vocabulary"
copy_file "$ECOSYSTEM_DIR/backend/vocabulary/data/kanji_selection_drill.json" "$APP_DIR/assets/data/vocabulary"
copy_file "$ECOSYSTEM_DIR/backend/vocabulary/data/sentence_drill.json"        "$APP_DIR/assets/data/vocabulary"

# ── kanji_trainer/ ──────────────────────────────────────────────────────────
echo "kanji_trainer/"
copy_file "$ECOSYSTEM_DIR/backend/kanji_trainer/data/kanji_list.json" "$APP_DIR/assets/data/kanji_trainer"

echo ""
echo "Done."
