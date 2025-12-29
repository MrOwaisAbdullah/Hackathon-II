#!/usr/bin/env python3
"""Check for problematic import patterns in a package.

This script scans your package for:
1. Absolute imports to your own package (should be relative)
2. Missing __init__.py files
3. Incorrect import patterns

Usage:
    python check-imports.py your_package/
"""

import sys
from pathlib import Path
from typing import List


def check_imports(package_dir: str, package_name: str) -> List[str]:
    """Check for problematic import patterns.

    Args:
        package_dir: Path to package directory
        package_name: Name of the package (e.g., 'teamflow_console')

    Returns:
        List of issues found
    """
    issues = []
    pkg_path = Path(package_dir)

    if not pkg_path.exists():
        issues.append(f"Package directory not found: {package_dir}")
        return issues

    # Find all Python files in package
    py_files = list(pkg_path.rglob("*.py"))

    print(f"Scanning {len(py_files)} files in {package_name}/")
    print("=" * 60)

    for py_file in py_files:
        relative_path = py_file.relative_to(pkg_path)
        file_path_str = str(relative_path)

        try:
            content = py_file.read_text()
        except Exception as e:
            issues.append(f"Could not read {file_path_str}: {e}")
            continue

        # Check for absolute imports to own package
        for line_num, line in enumerate(content.split('\n'), 1):
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Check for absolute imports
            if line.startswith(f"from {package_name}."):
                issue = f"{file_path_str}:{line_num} - Absolute import: {line}"
                issues.append(issue)

            # Check for old-style absolute imports
            elif line.startswith(f"import {package_name}."):
                issue = f"{file_path_str}:{line_num} - Absolute import: {line}"
                issues.append(issue)

    # Check for missing __init__.py files
    all_dirs = {d for d in pkg_path.rglob("*") if d.is_dir()}
    for dir_path in sorted(all_dirs):
        init_file = dir_path / "__init__.py"
        if not init_file.exists():
            relative_path = dir_path.relative_to(pkg_path)
            issues.append(f"Missing __init__.py: {package_name}/{relative_path}/")

    return issues


def print_results(issues: List[str]) -> bool:
    """Print check results.

    Args:
        issues: List of issues found

    Returns:
        True if no issues, False otherwise
    """
    if not issues:
        print("\n[SUCCESS] No import issues found!")
        print("=" * 60)
        print("\n✓ All imports use relative syntax")
        print("✓ All directories have __init__.py")
        return True

    print(f"\n[FOUND] {len(issues)} issue(s):")
    print("=" * 60)
    for issue in issues:
        print(f"  • {issue}")

    print("\n" + "=" * 60)
    print("\nFixes needed:")
    print("  1. Replace absolute imports with relative:")
    print("     from package.module import -> from .module import")
    print("     from package.lib.module -> from ..lib.module import")
    print("  2. Add empty __init__.py files to all package directories")

    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python check-imports.py <package-dir>")
        print("\nExample:")
        print("  python check-imports.py teamflow_console/")
        sys.exit(1)

    package_dir = sys.argv[1]
    package_name = Path(package_dir).name

    issues = check_imports(package_dir, package_name)
    success = print_results(issues)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
