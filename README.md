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

## Development

Developer setup instructions can be found in the `docs/developer-setup.md` file.

## Upcoming Features

- Provide the output via a json API endpoint (the output can then be used by other external tools and apps).
- Additonal wagtail admin pages (maybe reports) to show the urls in a more user friendly way.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the MIT license.
