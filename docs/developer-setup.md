# Setting up for development

There is a very basic wagtail app in `./startexample` that can be used to test the package output locally.

## To install the package run the following commands:

```bash
uv sync
sourec .venv/bin/activate
python manage.py migrate
```

## To run the command:

```bash
python manage.py list_admin_urls
```

You should see the console output for the startexample app urls.

## Testing against another wagtail app

You can test the package against another Wagtail app. First, you need to install the package and activate the virtual environment:

```bash
uv sync
source .venv/bin/activate
```

The wagtail bakery demo is a good choice: https://github.com/wagtail/bakerydemo

Follow the instructions in the README to set up the app using the virtual environment method.

Where the README says to run `pip install -r requirements.txt`, you can instead run:

```bash
uv pip install -r requirements/development.txt
```

Add the `wagtail_unveil` package to the `INSTALLED_APPS` list in `bakerydemo/settings/base.py`:

```python
INSTALLED_APPS = [
    ...
    'wagtail_unveil',
    ...
]
```

Then run the following commands to set up the database:

```bash
python manage.py migrate
```

Run the command `python manage.py list_admin_urls` to see the output of the command. It should list the bakerydemo  admin URLs.
