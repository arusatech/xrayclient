#!/usr/bin/env python3
"""
Script to generate documentation using pdoc.
"""

import subprocess
import sys
import os
from pathlib import Path

def generate_docs():
    """Generate HTML documentation using pdoc."""
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Create docs directory if it doesn't exist
    docs_dir = os.path.join(project_root, "docs", "html")
    os.makedirs(docs_dir, exist_ok=True)
    
    # Run pdoc
    cmd = [
        sys.executable, "-m", "pdoc",
        "--output-dir", str(docs_dir),
        "--template-dir", str(os.path.join(project_root, "docs", "templates")),
        "xrayclient"
    ]
    
    print("Generating documentation...")
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        print(f"Documentation generated successfully in {docs_dir}")
        print(f"Open {os.path.join(docs_dir, 'xrayclient.html')} in your browser to view the docs")
    else:
        print("Failed to generate documentation")
        sys.exit(1)

if __name__ == "__main__":
    generate_docs() 