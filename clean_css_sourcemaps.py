#!/usr/bin/env python
"""
Script to remove source map references from CSS files
This helps avoid deployment issues with missing .map files
"""

import os
import re
from pathlib import Path


def remove_source_map_references(css_file_path):
    """Remove sourceMappingURL references from CSS file"""
    try:
        with open(css_file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Remove source map references
        content = re.sub(
            r"/\*# sourceMappingURL=.*?\*/", "", content, flags=re.MULTILINE
        )

        # Clean up extra whitespace
        content = content.rstrip() + "\n" if content.strip() else content

        with open(css_file_path, "w", encoding="utf-8") as file:
            file.write(content)

        print(f"✓ Cleaned: {css_file_path}")
        return True
    except Exception as e:
        print(f"✗ Error cleaning {css_file_path}: {e}")
        return False


def main():
    """Main function to clean all CSS files"""
    base_dir = Path(__file__).parent
    static_dir = base_dir / "static"

    if not static_dir.exists():
        print("Static directory not found!")
        return

    # Find all CSS files
    css_files = []
    for root, dirs, files in os.walk(static_dir):
        for file in files:
            if file.endswith(".css"):
                css_files.append(os.path.join(root, file))

    print(f"Found {len(css_files)} CSS files to clean...")

    cleaned_count = 0
    for css_file in css_files:
        if remove_source_map_references(css_file):
            cleaned_count += 1

    print(f"\nCleaned {cleaned_count}/{len(css_files)} CSS files successfully!")


if __name__ == "__main__":
    main()
