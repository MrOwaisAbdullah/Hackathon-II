#!/usr/bin/env python3
"""Verify wheel contents before publishing.

This script inspects a built wheel file and verifies that all
expected files and directories are present.

Usage:
    python verify-wheel.py dist/your_package-0.1.0-py3-none-any.whl
"""

import sys
import zipfile
from pathlib import Path


def verify_wheel(wheel_path: str, package_name: str) -> bool:
    """Verify wheel contents.

    Args:
        wheel_path: Path to the .whl file
        package_name: Name of the package (e.g., 'teamflow_console')

    Returns:
        True if verification passes, False otherwise
    """
    print(f"Verifying: {wheel_path}")
    print("=" * 60)

    # Expected files and directories
    expected_files = {
        f"{package_name}/__init__.py",
        f"{package_name}/cli/__init__.py",
        f"{package_name}/lib/__init__.py",
        f"{package_name}/models/__init__.py",
        f"{package_name}/services/__init__.py",
    }

    # Check that wheel exists
    wheel_file = Path(wheel_path)
    if not wheel_file.exists():
        print(f"[ERROR] Wheel file not found: {wheel_path}")
        return False

    # Open and inspect wheel
    with zipfile.ZipFile(wheel_file, 'r') as zf:
        all_files = set(zf.namelist())

        print("\nChecking expected files:")
        print("-" * 40)

        all_present = True
        for expected in expected_files:
            if expected in all_files:
                print(f"  [OK] {expected}")
            else:
                print(f"  [MISSING] {expected}")
                all_present = False

        print("\nAll files in wheel:")
        print("-" * 40)
        for name in sorted(all_files):
            if name.startswith(package_name):
                print(f"  {name}")

        print("\nMetadata:")
        print("-" * 40)
        if f"{package_name}.dist-info/METADATA" in all_files:
            metadata = zf.read(f"{package_name}.dist-info/METADATA").decode('utf-8')
            for line in metadata.split('\n')[:10]:
                if line.strip():
                    print(f"  {line}")

        if f"{package_name}.dist-info/RECORD" in all_files:
            print(f"\n  [OK] RECORD file present")

    print("\n" + "=" * 60)
    if all_present:
        print("[SUCCESS] Wheel verification passed!")
        return True
    else:
        print("[FAILURE] Wheel verification failed!")
        print("\nMissing files indicate:")
        print("  - .gitignore may be excluding directories")
        print("  - Build config (pyproject.toml) may be wrong")
        print("  - __init__.py files may be missing")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify-wheel.py <wheel-file>")
        print("\nExample:")
        print("  python verify-wheel.py dist/teamflow_console-0.1.0-py3-none-any.whl")
        sys.exit(1)

    wheel_path = sys.argv[1]

    # Extract package name from wheel filename
    # e.g., teamflow_console-0.1.0-py3-none-any.whl -> teamflow_console
    wheel_name = Path(wheel_path).stem
    if '-' in wheel_name:
        package_name = wheel_name.split('-')[0]
    else:
        package_name = wheel_name

    success = verify_wheel(wheel_path, package_name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
