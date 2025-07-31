# mdformat-tight-lists

[![Build Status][ci-badge]][ci-link]
[![PyPI version][pypi-badge]][pypi-link]

An [mdformat](https://github.com/executablebooks/mdformat) plugin that formats Markdown lists to be tight (no empty lines between list items) following mdformat-style rules.

## Installation

```bash
pip install mdformat-tight-lists
```

Or with [pipx](https://pipx.pypa.io/) for command-line usage:

```bash
pipx install mdformat
pipx inject mdformat mdformat-tight-lists
```

## Usage

After installation, mdformat will automatically use this plugin when formatting Markdown files:

```bash
mdformat your-file.md
```

### Features

- **Smart List Formatting**: Automatically creates tight lists by removing unnecessary empty lines
- **List Type Detection**: Different top-level markers (`-`, `*`, `+`) are treated as separate lists
- **Nested List Handling**: Properly handles transitions between ordered and unordered lists
- **Multi-Paragraph Support**: Preserves loose formatting when list items contain multiple paragraphs
- **Frontmatter Compatible**: Works seamlessly with YAML frontmatter

### Examples

**Input:**
```markdown
- Item 1

- Item 2

- Item 3
```

**Output:**
```markdown
- Item 1
- Item 2
- Item 3
```

**Multi-paragraph items (loose list preserved):**
```markdown
- First item with multiple paragraphs

  Second paragraph of first item

- Second item
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/jdmonaco/mdformat-tight-lists.git
cd mdformat-tight-lists

# Install development environment with uv
uv sync
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=mdformat_tight_lists

# Run tests verbosely
uv run pytest -v
```

### Adding Tests

To add new test cases, edit `tests/fixtures.md` following the existing format:
- Test title
- Input markdown (between dots)
- Expected output (between dots)

## Publishing

This package is automatically published to PyPI when a version tag is pushed:

```bash
# Update version in mdformat_tight_lists/__init__.py
# Commit and push changes
git add -A
git commit -m "Bump version to X.Y.Z"
git push

# Create and push a version tag
git tag vX.Y.Z
git push origin vX.Y.Z
```

The GitHub Actions workflow will automatically build and publish to PyPI.

## License

MIT - see LICENSE file for details.

[ci-badge]: https://github.com/jdmonaco/mdformat-tight-lists/workflows/CI/badge.svg?branch=main
[ci-link]: https://github.com/jdmonaco/mdformat-tight-lists/actions?query=workflow%3ACI+branch%3Amain+event%3Apush
[pypi-badge]: https://img.shields.io/pypi/v/mdformat-tight-lists.svg
[pypi-link]: https://pypi.org/project/mdformat-tight-lists

