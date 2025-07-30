[![PyPI version](https://badge.fury.io/py/pysciiart.svg)](https://badge.fury.io/py/pysciiart)

# pysciiart

A Python library for generating ASCII art from high-level data structures. Create structured text layouts, diagrams, and graphs with automatic positioning and linking.

## Features

- **Widget-based rendering system** with containers, borders, padding, and text components
- **Automatic graph layout** with intelligent node positioning and link routing
- **Color support** via termcolor for terminal output
- **Flexible composition** of complex ASCII diagrams from simple components

## Installation

Install from PyPI:

```bash
pip install pysciiart
```

For development:

```bash
poetry install
poetry shell
```

## Quick Start

```python
from pysciiart.widget import Border, Paragraph, VBox

# Create simple text widgets
title = Border(Paragraph(["My Diagram"]), title="Main")
content = Border(Paragraph(["Content here", "More content"]))

# Compose into layout
layout = VBox([title, content])

# Render to ASCII
print(layout.render())
```

## Development

### Running Tests
```bash
poetry run pytest
poetry run pytest --log-cli-level=INFO  # with detailed logging
```

### Building
```bash
poetry build  # Creates wheel and source distributions
```

### Deployment
1. Update version in `src/pysciiart/__init__.py` and `pyproject.toml`
2. Commit and tag with version number
3. Build: `poetry build`
4. Upload: `poetry publish`
