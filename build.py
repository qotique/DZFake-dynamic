#!/usr/bin/env python3
"""Cross-platform build script for PyArmor obfuscation."""
import subprocess
import sys
import shutil
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    src = root / "src" / "a2s_proxy.py"
    dist = root / "src" / "dist"

    if not src.is_file():
        print(f"Error: {src} not found")
        sys.exit(1)

    print("=== Building obfuscated dist ===")

    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir(parents=True)

    subprocess.run(
        [sys.executable, "-m", "pyarmor", "gen", "-r", "-O", str(dist), str(src)],
        check=True,
    )

    print(f"=== Done. Obfuscated files in {dist} ===")
    print(f"Run with: python {dist / 'a2s_proxy.py'}")

if __name__ == "__main__":
    main()
