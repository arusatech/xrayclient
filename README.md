# XrayClient

A comprehensive Python client for interacting with Xray Cloud's GraphQL API for test management in Jira. This library provides a robust interface for managing test plans, test executions, test runs, defects, evidence, and other Xray-related operations through GraphQL queries and mutations.

## Documentation

- **HTML Documentation**: [View Online](https://github.com/arusatech/xrayclient/tree/main/docs/html)
- **API Reference**: [API Docs](https://github.com/arusatech/xrayclient/tree/main/docs/html/xrayclient.html)

## Features

- **Jira Integration**: Full Jira REST API support for issue management
- **Xray GraphQL API**: Complete Xray Cloud GraphQL API integration
- **Test Management**: Create and manage test plans, test executions, and test runs
- **Evidence Management**: Add attachments and evidence to test runs
- **Defect Management**: Create defects from failed test runs
- **Authentication**: Secure authentication with both Jira and Xray Cloud
- **Error Handling**: Comprehensive error handling and logging
- **Type Hints**: Full type annotation support for better development experience

## Installation

```bash
pip install xrayclient
```

Or install from source:

```bash
git clone https://github.com/arusatech/xrayclient.git
cd xrayclient
pip install -e .
```

## Quick Start

### Basic Setup

```python
from xrayclient.xray_client import XrayGraphQL

# Initialize the client
client = XrayGraphQL()
```

### Environment Variables

Create a `.env` file in your project root with the following variables:

```env
# Jira Configuration
JIRA_SERVER=https://your-instance.atlassian.net
JIRA_USER=your-email@company.com
JIRA_API_KEY=your-jira-api-key

# Xray Cloud Configuration
XRAY_CLIENT_ID=your-xray-client-id
XRAY_CLIENT_SECRET=your-xray-client-secret
XRAY_BASE_URL=https://us.xray.cloud.getxray.app
```

## Usage Examples

### Test Plan Operations

```python
# Get all tests from a test plan
test_plan_tests = client.get_tests_from_test_plan("TEST-123")
print(test_plan_tests)
# Output: {'TEST-124': '10001', 'TEST-125': '10002'}

# Get test plan data with parsed tables
test_plan_data = client.get_test_plan_data("TEST-123")
print(test_plan_data)
```

### Test Execution Management

```python
# Create a test execution from a test plan
test_execution = client.create_test_execution_from_test_plan("TEST-123")
print(test_execution)
# Output: {
#     'TEST-124': {
#         'test_run_id': '5f7c3',
#         'test_execution_key': 'TEST-456',
#         'test_plan_key': 'TEST-123'
#     }
# }

# Create a test execution with specific tests
test_execution = client.create_test_execution(
    test_issue_keys=["TEST-124", "TEST-125"],
    project_key="PROJ",
    summary="Regression Test Execution",
    description="Testing critical features"
)
```

### Test Run Operations

```python
# Get test run status
status, run_id = client.get_test_runstatus("TEST-124", "TEST-456")
print(f"Status: {status}, Run ID: {run_id}")

# Update test run status
success = client.update_test_run_status("test_run_id", "PASS")
print(success)  # True

# Update test run comment
success = client.update_test_run_comment("test_run_id", "Test passed successfully")
print(success)  # True

# Append to existing comment
success = client.append_test_run_comment("test_run_id", "Additional notes")
print(success)  # True
```

### Evidence and Defect Management

```python
# Add evidence to a test run
evidence_added = client.add_evidence_to_test_run("test_run_id", "/path/to/screenshot.png")
print(evidence_added)  # True

# Create a defect from a failed test run
defect = client.create_defect_from_test_run(
    test_run_id="test_run_id",
    project_key="PROJ",
    parent_issue_key="TEST-456",
    defect_summary="Login functionality broken",
    defect_description="Users cannot log in with valid credentials"
)
print(defect)
```

### Test Set Operations

```python
# Get tests from a test set
test_set_tests = client.get_tests_from_test_set("TESTSET-123")
print(test_set_tests)

# Filter test sets by test case
test_sets = client.filter_test_set_by_test_case("TEST-124")
print(test_sets)

# Get tags for a test case
tags = client.filter_tags_by_test_case("TEST-124")
print(tags)
```

### Jira Issue Management

```python
# Create a new Jira issue
issue_key, issue_id = client.create_issue(
    project_key="PROJ",
    summary="New feature implementation",
    description="Implement new login flow",
    issue_type="Story",
    priority="High",
    labels=["feature", "login"],
    attachments=["/path/to/screenshot.png"]
)
print(f"Created issue {issue_key} with ID {issue_id}")

# Get issue details
issue = client.get_issue("PROJ-123", fields=["summary", "status", "assignee"])
print(f"Issue: {issue['summary']} - Status: {issue['status']['name']}")

# Update issue summary
success = client.update_issue_summary("PROJ-123", "Updated summary")
print(success)  # True
```

## API Reference

### JiraHandler Class

The base class providing Jira REST API functionality.

#### Methods

- `create_issue(project_key, summary, description, **kwargs)` - Create a new Jira issue
- `get_issue(issue_key, fields=None)` - Retrieve a Jira issue
- `update_issue_summary(issue_key, new_summary)` - Update issue summary
- `make_jira_request(jira_key, url, method, payload, **kwargs)` - Make custom Jira requests
- `download_jira_attachment_by_id(attachment_id, mime_type)` - Download attachments

### XrayGraphQL Class

Extends JiraHandler to provide Xray Cloud GraphQL API functionality.

#### Authentication & Setup
- `__init__()` - Initialize XrayGraphQL client
- `_get_auth_token()` - Authenticate with Xray Cloud API
- `_make_graphql_request(query, variables)` - Make GraphQL requests

#### Test Plan Operations
- `get_tests_from_test_plan(test_plan)` - Get tests from test plan
- `get_test_plan_data(test_plan)` - Get parsed test plan data

#### Test Set Operations
- `get_tests_from_test_set(test_set)` - Get tests from test set
- `filter_test_set_by_test_case(test_key)` - Filter test sets by test case
- `filter_tags_by_test_case(test_key)` - Get tags for test case

#### Test Execution Operations
- `get_tests_from_test_execution(test_execution)` - Get tests from test execution
- `get_test_execution(test_execution)` - Get detailed test execution info
- `create_test_execution(test_issue_keys, project_key, summary, description)` - Create test execution
- `create_test_execution_from_test_plan(test_plan)` - Create test execution from plan
- `add_test_execution_to_test_plan(test_plan, test_execution)` - Add execution to plan

#### Test Run Operations
- `get_test_runstatus(test_case, test_execution)` - Get test run status
- `get_test_run_by_id(test_case_id, test_execution_id)` - Get test run by ID
- `update_test_run_status(test_run_id, test_run_status)` - Update test run status
- `update_test_run_comment(test_run_id, test_run_comment)` - Update test run comment
- `get_test_run_comment(test_run_id)` - Get test run comment
- `append_test_run_comment(test_run_id, test_run_comment)` - Append to comment

#### Evidence & Defect Management
- `add_evidence_to_test_run(test_run_id, evidence_path)` - Add evidence
- `create_defect_from_test_run(test_run_id, project_key, parent_issue_key, defect_summary, defect_description)` - Create defect

## Requirements

- Python >= 3.12
- jira >= 3.10.5, < 4.0.0
- jsonpath-nz >= 1.0.6, < 2.0.0
- requests >= 2.31.0, < 3.0.0

## Development

### Setup Development Environment

```bash
git clone https://github.com/arusatech/xrayclient.git
cd xrayclient
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=xrayclient --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m slow
```

### Code Quality

The project uses:
- **pytest** for testing
- **pytest-cov** for coverage reporting
- **pytest-mock** for mocking in tests
- **Type hints** for better code documentation

## Error Handling

The library implements comprehensive error handling:

- All methods return `None` for failed operations instead of raising exceptions
- Detailed logging for debugging and error tracking
- Automatic retry logic for transient failures
- Graceful handling of authentication failures

## Security

- Uses environment variables for sensitive configuration
- Supports API key authentication for both Jira and Xray
- Implements proper token management and refresh
- Handles secure file uploads for evidence

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact: yakub@arusatech.com

## Changelog

### Version 0.1.0
- Initial release
- Jira REST API integration
- Xray Cloud GraphQL API integration
- Complete test management functionality
- Evidence and defect management
- Comprehensive error handling and logging

## Step 1: Install pdoc

```bash
# Install pdoc
poetry add --group dev pdoc

# Or with pip
pip install pdoc
```

## Step 2: Update pyproject.toml to include pdoc

```toml:pyproject.toml
[project]
name = "xrayclient"
version = "0.1.0"
description = "Python Client for Xray Test Management for Jira"
authors = [
    {name = "yakub@arusatech.com"}
]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "jira (>=3.10.5,<4.0.0)",
    "jsonpath-nz (>=1.0.6,<2.0.0)",
    "requests (>=2.31.0,<3.0.0)"
]

[tool.poetry]
name = "xrayclient"
version = "0.1.0"
description = "Python Client for Xray Test Management for Jira"
authors = ["yakub@arusatech.com"]
license = "MIT"
readme = "README.md"
homepage = "https://github.com/arusatech/xrayclient"
repository = "https://github.com/arusatech/xrayclient"
keywords = ["xray", "jira", "test-management", "graphql", "api-client"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Software Development :: Testing",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
packages = [{include = "xrayclient"}]

[tool.poetry.dependencies]
python = "^3.12"
jira = "^3.10.5"
jsonpath-nz = "^1.0.6"
requests = "^2.31.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.4.1"
pytest-cov = "^4.1.0"
pytest-mock = "^3.11.1"
pdoc = "^14.4.0"

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--tb=short",
    "--strict-markers",
    "--disable-warnings",
    "--cov=xrayclient",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-report=xml:coverage.xml"
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow running tests"
]

[tool.pdoc]
# pdoc configuration
docformat = "google"
template_directory = "docs/templates"
output_directory = "docs/html"
```

## Step 3: Create Documentation Directory Structure

```bash
# Create documentation directories
mkdir -p docs/html
mkdir -p docs/templates
```

## Step 4: Create a Custom pdoc Template (Optional)

Create `docs/templates/head.html` for custom styling:

```html:docs/templates/head.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ module_name }}{% endblock %} - XrayClient Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
        }
        .header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        .content {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        pre {
            background: #f5f5f5;
            padding: 1rem;
            border-radius: 4px;
            overflow-x: auto;
        }
        code {
            background: #f0f0f0;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', monospace;
        }
        .method {
            margin-bottom: 2rem;
            padding: 1rem;
            border-left: 4px solid #667eea;
            background: #f8f9fa;
        }
        .method h3 {
            margin-top: 0;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>XrayClient Documentation</h1>
        <p>Python Client for Xray Test Management for Jira</p>
    </div>
    <div class="content">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

## Step 5: Generate Documentation

```bash
# Generate HTML documentation
poetry run pdoc --html --output-dir docs/html xrayclient

# Or with more options
poetry run pdoc --html --output-dir docs/html --template-dir docs/templates xrayclient
```

## Step 6: Create a Documentation Script

Create `scripts/generate_docs.py`:

```python:scripts/generate_docs.py
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
    docs_dir = project_root / "docs" / "html"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Run pdoc
    cmd = [
        sys.executable, "-m", "pdoc",
        "--html",
        "--output-dir", str(docs_dir),
        "--template-dir", str(project_root / "docs" / "templates"),
        "xrayclient"
    ]
    
    print("Generating documentation...")
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        print(f"Documentation generated successfully in {docs_dir}")
        print(f"Open {docs_dir / 'xrayclient.html'} in your browser to view the docs")
    else:
        print("Failed to generate documentation")
        sys.exit(1)

if __name__ == "__main__":
    generate_docs()
```

## Step 7: Add Documentation to PyPI Package

Update your `pyproject.toml` to include documentation files:

```toml:pyproject.toml
[project]
name = "xrayclient"
version = "0.1.0"
description = "Python Client for Xray Test Management for Jira"
authors = [
    {name = "yakub@arusatech.com"}
]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "jira (>=3.10.5,<4.0.0)",
    "jsonpath-nz (>=1.0.6,<2.0.0)",
    "requests (>=2.31.0,<3.0.0)"
]

[tool.poetry]
name = "xrayclient"
version = "0.1.0"
description = "Python Client for Xray Test Management for Jira"
authors = ["yakub@arusatech.com"]
license = "MIT"
readme = "README.md"
homepage = "https://github.com/arusatech/xrayclient"
repository = "https://github.com/arusatech/xrayclient"
documentation = "https://arusatech.github.io/xrayclient/"
keywords = ["xray", "jira", "test-management", "graphql", "api-client"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Software Development :: Testing",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
packages = [{include = "xrayclient"}]
include = [
    "docs/html/**/*",
    "README.md",
    "LICENSE"
]

[tool.poetry.dependencies]
python = "^3.12"
jira = "^3.10.5"
jsonpath-nz = "^1.0.6"
requests = "^2.31.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.4.1"
pytest-cov = "^4.1.0"
pytest-mock = "^3.11.1"
pdoc = "^14.4.0"

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--tb=short",
    "--strict-markers",
    "--disable-warnings",
    "--cov=xrayclient",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-report=xml:coverage.xml"
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow running tests"
]

[tool.pdoc]
docformat = "google"
template_directory = "docs/templates"
output_directory = "docs/html"
```

## Step 8: Create a MANIFEST.in file

Create `MANIFEST.in` to ensure documentation is included:

```text:MANIFEST.in
include README.md
include LICENSE
include CHANGELOG.md
recursive-include docs/html *
recursive-include docs/templates *
```

## Step 9: Update .gitignore

```gitignore:.gitignore
# Add these lines to your existing .gitignore
dist/
build/
*.egg-info/
.pytest_cache/
htmlcov/
coverage.xml

# Don't ignore docs/html (we want to include it in the package)
!docs/html/
```

## Step 10: Create a Documentation Generation Workflow

Create `.github/workflows/docs.yml`:

```yaml:.github/workflows/docs.yml
name: Generate Documentation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        echo "$HOME/.local/bin" >> $GITHUB_PATH
    
    - name: Install dependencies
      run: poetry install
    
    - name: Generate documentation
      run: poetry run python scripts/generate_docs.py
    
    - name: Upload documentation artifacts
      uses: actions/upload-artifact@v3
      with:
        name: documentation
        path: docs/html/
```

## Step 11: Update README.md with Documentation Links

```markdown:README.md
<code_block_to_apply_changes_from>
```

## Step 12: Build and Publish with Documentation

```bash
# Generate documentation first
poetry run python scripts/generate_docs.py

# Build package (includes documentation)
poetry build

# Publish to PyPI
poetry publish
```

## Step 13: Alternative: Host Documentation on GitHub Pages

Create `.github/workflows/docs-pages.yml`:

```yaml:.github/workflows/docs-pages.yml
name: Deploy Documentation to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        echo "$HOME/.local/bin" >> $GITHUB_PATH
    
    - name: Install dependencies
      run: poetry install
    
    - name: Generate documentation
      run: poetry run python scripts/generate_docs.py
    
    - name: Setup Pages
      uses: actions/configure-pages@v3
    
    - name: Upload artifact
      uses: actions/upload-pages-artifact@v2
      with:
        path: docs/html/
    
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v2
```

## Step 14: Update pyproject.toml with GitHub Pages URL

```toml:pyproject.toml
[tool.poetry]
# ... existing configuration ...
documentation = "https://arusatech.github.io/xrayclient/"
# ... rest of configuration ...
```

## Complete Documentation Workflow

1. **Generate docs**: `poetry run python scripts/generate_docs.py`
2. **Build package**: `poetry build` (includes docs)
3. **Publish**: `poetry publish`
4. **Deploy to GitHub Pages**: Automatic via GitHub Actions

## Benefits of This Approach

1. **Documentation included in PyPI package** - Users get docs with the package
2. **Automated generation** - Docs are always up-to-date
3. **GitHub Pages hosting** - Public documentation website
4. **Custom styling** - Professional-looking documentation
5. **Version control** - Docs are tracked with code

This setup provides comprehensive documentation that's both included in your PyPI package and hosted online for easy access.
