# Wagtail Unveil

A Wagtail package that helps map and expose admin and frontend URLs in your Wagtail project, useful for testing, documentation, and development.

## Overview

Wagtail Unveil provides tools to discover and list all available admin and frontend URLs in your Wagtail project. This is particularly useful for:

- Discovering all admin URLs for model administration

## Installation

```bash
pip install wagtail-unveil
```

Add to your installed apps:

```python
INSTALLED_APPS = [
    # ...
    "wagtail_unveil",
    # ...
]
```

## Usage

### Command Line

Wagtail Unveil provides a management command to list all admin URLs:

```bash
python manage.py list_admin_urls
```

You can specify options like:

```bash
python manage.py list_admin_urls --base-url=https://example.com --max-instances=5
```

## Helper Modules

The package includes several helper modules:

- `page_helpers.py`: Functions to discover and format page URLs
- `snippet_helpers.py`: Functions to discover and format snippet URLs
- `modeladmin_helpers.py`: Functions to discover and format ModelAdmin URLs
- `media_helpers.py`: Helpers for media-related URLs
- `settings_helpers.py`: Helpers for settings-related URLs

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/wagtail-unveil.git
cd wagtail-unveil

# Install dev dependencies
uv sync

# Install pre-commit hooks
pre-commit install
```

### Run Tests

```bash
python -m pytest # TODO: add test command
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the MIT license.
