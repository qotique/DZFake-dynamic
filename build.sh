#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/src/a2s_proxy.py"
DIST="$SCRIPT_DIR/src/dist"

if [ ! -f "$SRC" ]; then
    echo "Error: $SRC not found"
    exit 1
fi

echo "=== Building obfuscated dist ==="

# Clean previous build
rm -rf "$DIST"
mkdir -p "$DIST"

# Obfuscate with PyArmor
pyarmor gen -r -O "$DIST" "$SRC"

echo "=== Done. Obfuscated files in $DIST ==="
echo "Run with: python $DIST/a2s_proxy.py"
