#!/usr/bin/env python3
"""
Script to sync version between pyproject.toml and __init__.py
"""

import re
from pathlib import Path

def sync_version():
    """Sync version between pyproject.toml and __init__.py"""
    
    project_root = Path(__file__).parent.parent
    pyproject_file = project_root / "pyproject.toml"
    init_file = project_root / "xrayclient" / "__init__.py"
    
    # Read pyproject.toml
    with open(pyproject_file, 'r') as f:
        pyproject_content = f.read()
    
    # Extract version from pyproject.toml
    version_match = re.search(r'version = "([^"]+)"', pyproject_content)
    if not version_match:
        print("Could not find version in pyproject.toml")
        return
    
    version = version_match.group(1)
    print(f"Found version in pyproject.toml: {version}")
    
    # Read __init__.py
    with open(init_file, 'r') as f:
        init_content = f.read()
    
    # Update version in __init__.py
    new_init_content = re.sub(
        r'__version__ = "[^"]*"',
        f'__version__ = "{version}"',
        init_content
    )
    
    # Write back to __init__.py
    with open(init_file, 'w') as f:
        f.write(new_init_content)
    
    print(f"Updated __init__.py with version: {version}")

if __name__ == "__main__":
    sync_version() 