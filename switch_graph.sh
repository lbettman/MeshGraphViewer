#!/usr/bin/env bash
set -euo pipefail

choice="${1:-}"

case "$choice" in
  small) src="graph-small.json" ;;
  large) src="graph-large-laidout.json" ;;
  *) echo "Usage: $0 {small|large}" >&2; exit 2 ;;
esac

# Write the active file atomically so the viewer sees a clean update
tmp="$(mktemp)"
cp "$src" "$tmp"
mv "$tmp" graph.json

# Extra timestamp bump (harmless, helps some file watchers)
touch graph.json