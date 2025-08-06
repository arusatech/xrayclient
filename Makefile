.PHONY: docs build publish clean

# Generate documentation
docs:
	poetry run python scripts/generate_docs.py

# Build package
build: docs
	poetry build

# Publish to PyPI
publish: build
	poetry publish

# Clean build artifacts
clean:
	rm -rf dist/ build/ *.egg-info/ .pytest_cache/ htmlcov/ coverage.xml

# Install dependencies
install:
	poetry install

# Run tests
test:
	poetry run pytest

# Generate docs and open in browser
docs-open: docs
	start docs/html/xrayclient.html  # Windows
	# open docs/html/xrayclient.html  # macOS
	# xdg-open docs/html/xrayclient.html  # Linux 