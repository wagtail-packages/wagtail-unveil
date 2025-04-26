# Wagtail Unveil

A Wagtail package that helps map and expose admin and frontend URLs in your Wagtail project.

## Overview

Wagtail Unveil provides a single command to discover and output all available admin and frontend URLs in your Wagtail project.

## Install the package into your Wagtail project

Suggested install method is via pip but you should use the method that best fits your project setup:

```bash
pip install wagtail-unveil
```

**Note**: The package is not yet available on PyPI, so you may need to install it directly from this GitHub repository.

Update your wagtail settings to include `wagtail_unveil`:

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

The command has a few flags that can be used to adjust the output. The flags are all optional:

- `--base_url`: The base URL to use for the output. Auto generated from the Wagtail site settings.
- `--output`: Output the urls to the console or to a file. Default is console.
- `--file`: The file name to output the urls to. This is only used if the output option is set to file the file type is a simple text file.
- `--max-instances`: The maximum number of instances to show for each URL. This is used to adjust the number of instances shown in the output. The default is 1 a value of 0 will show all instances.

## Features

- **URL Discovery**: Automatically discovers and lists all available Wagtail admin and frontend URLs in your project
- **JSON API Endpoint**: Access all your project URLs via a JSON API endpoint, therefore your can use external tools to consume the data
  - Configurable parameters: `max_instances`, `base_url`, `group_by`
  - Grouping options: Group URLs by interface (backend/frontend) or by URL type
  - Comprehensive coverage: Pages, snippets, ModelAdmin, ModelViewSet, settings, images, and documents
  - Detailed metadata with counts for different URL types and categories
- **Command Line Interface**: Use the management command to quickly list and export URLs
- **Configurable Output**: Control the level of detail and output format
- **Report View**: View your project's URLs in a user-friendly Wagtail admin interface
  - Interactive URL validation: Check if URLs are accessible with visual success/error indicators

## Upcoming Features

- Additional Wagtail admin pages to show the URLs in a more user-friendly way
- Enhanced URL validation for checking frontend and backend URLs
- Performance optimizations for larger Wagtail installations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the MIT license.
