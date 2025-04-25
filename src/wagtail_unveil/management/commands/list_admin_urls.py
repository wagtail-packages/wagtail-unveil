from django.core.management.base import BaseCommand
from wagtail.models import Site
from wagtail.snippets.models import get_snippet_models

from wagtail_unveil.helpers.media_helpers import (
    get_document_admin_urls,
    get_image_admin_urls,
)
from wagtail_unveil.helpers.modeladmin_helpers import (
    get_modeladmin_models,
    get_modeladmin_urls,
)
from wagtail_unveil.helpers.page_helpers import (
    get_page_models,
    get_page_urls,
    get_site_urls,
)
from wagtail_unveil.helpers.settings_helpers import get_settings_admin_urls
from wagtail_unveil.helpers.snippet_helpers import (
    get_modelviewset_models,
    get_modelviewset_urls,
    get_snippet_urls,
)


class Command(BaseCommand):
    help = "Lists admin URLs for all Wagtail models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--base-url",
            type=str,
            help="Base URL of the site (default: auto-detected from default site)",
        )
        parser.add_argument(
            "--output",
            type=str,
            choices=["console", "file"],
            default="console",
            help="Output to console or file (default: console)",
        )
        parser.add_argument(
            "--file",
            type=str,
            default="admin_urls.txt",
            help="File to output to (default: admin_urls.txt)",
        )
        parser.add_argument(
            "--max-instances",
            type=int,
            default=1,
            help="Maximum instances to show per model (default: 1, use 0 for unlimited)",
        )

    def handle(self, *args, **options):
        # Get base URL from options or use default site
        base_url = options.get("base_url")
        if base_url is None:
            try:
                default_site = Site.objects.filter(is_default_site=True).first()
                if default_site:
                    # Build URL from site settings
                    if default_site.port == 80 or default_site.port == 443:
                        port_string = ""
                    else:
                        port_string = f":{default_site.port}"

                    protocol = "https" if default_site.port == 443 else "http"
                    base_url = f"{protocol}://{default_site.hostname}{port_string}"
                    self.stdout.write(
                        f"Using auto-detected URL from default site: {base_url}"
                    )
                else:
                    # Fallback to localhost if no default site exists
                    base_url = "http://localhost:8000"
                    self.stdout.write(
                        f"No default site found, using fallback URL: {base_url}"
                    )
            except (AttributeError, Site.DoesNotExist, ImportError) as e:
                # Fallback if there's an error
                base_url = "http://localhost:8000"
                self.stdout.write(
                    self.style.WARNING(
                        f"Error detecting site URL: {str(e)}. Using fallback URL: {base_url}"
                    )
                )

        output_type = options["output"]
        output_file = options["file"]
        max_instances = options.get("max_instances")

        self.stdout.write(self.style.SUCCESS("Finding all Wagtail models..."))

        urls = []

        # Get site default pages
        site_urls = get_site_urls(self.stdout, base_url)
        urls.extend(site_urls)

        # Get all page models
        page_models = get_page_models()
        self.stdout.write(f"Found {len(page_models)} page models:")
        for model in page_models:
            self.stdout.write(f"  - {model.__name__}")

        # Get URLs for page models
        page_urls = get_page_urls(self.stdout, base_url, max_instances)
        urls.extend(page_urls)

        # Get all snippet models
        snippet_models = get_snippet_models()
        self.stdout.write(f"Found {len(snippet_models)} snippet models:")
        for model in snippet_models:
            self.stdout.write(f"  - {model.__name__}")

        # Get URLs for snippet models
        snippet_urls = get_snippet_urls(
            self.stdout, base_url, max_instances
        )
        urls.extend(snippet_urls)

        # Get generic Django models with ModelAdmin
        modeladmin_models, modeladmin_url_paths = get_modeladmin_models()
        self.stdout.write(f"Found {len(modeladmin_models)} modeladmin models:")
        for model in modeladmin_models:
            self.stdout.write(f"  - {model.__name__}")

        # Get URLs for modeladmin models
        modeladmin_urls = get_modeladmin_urls(
            self.stdout,
            modeladmin_models,
            modeladmin_url_paths,
            base_url,
            max_instances,
        )
        urls.extend(modeladmin_urls)

        # Get models registered with ModelViewSet
        modelviewset_models, modelviewset_url_paths = get_modelviewset_models()
        self.stdout.write(f"Found {len(modelviewset_models)} modelviewset models:")
        for model in modelviewset_models:
            self.stdout.write(f"  - {model.__name__}")

        # Get URLs for modelviewset models
        modelviewset_urls = get_modelviewset_urls(
            self.stdout,
            modelviewset_models,
            modelviewset_url_paths,
            base_url,
            max_instances,
        )
        urls.extend(modelviewset_urls)

        # Get image admin URLs
        self.stdout.write("Getting image admin URLs...")
        image_urls = get_image_admin_urls(self.stdout, base_url, max_instances)
        urls.extend(image_urls)

        # Get document admin URLs
        self.stdout.write("Getting document admin URLs...")
        document_urls = get_document_admin_urls(self.stdout, base_url, max_instances)
        urls.extend(document_urls)

        # Get settings admin URLs
        self.stdout.write("Getting settings admin URLs...")
        settings_urls = get_settings_admin_urls(self.stdout, base_url)
        urls.extend(settings_urls)

        # Group URLs by frontend vs backend
        frontend_urls = [url for url in urls if url[1] == "frontend"]
        backend_urls = [url for url in urls if url[1] != "frontend"]

        # Output the URLs
        if output_type == "console":
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS("FRONTEND URLS"))
            self.stdout.write("=" * 50)
            for model_name, url_type, url in frontend_urls:
                self.stdout.write(f"{model_name}: {url}")

            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS("BACKEND URLS"))
            self.stdout.write("=" * 50)

            # Group backend URLs by type
            admin_urls = [url for url in backend_urls if url[1] == "admin"]
            edit_urls = [url for url in backend_urls if url[1] == "edit"]
            list_urls = [url for url in backend_urls if url[1] == "list"]
            other_urls = [
                url for url in backend_urls if url[1] not in ["admin", "edit", "list"]
            ]

            if admin_urls:
                self.stdout.write("\n" + "-" * 25 + " ADMIN " + "-" * 25)
                for model_name, url_type, url in admin_urls:
                    self.stdout.write(f"{model_name}: {url}")

            if list_urls:
                self.stdout.write("\n" + "-" * 25 + " LIST " + "-" * 25)
                for model_name, url_type, url in list_urls:
                    self.stdout.write(f"{model_name}: {url}")

            if edit_urls:
                self.stdout.write("\n" + "-" * 25 + " EDIT " + "-" * 25)
                for model_name, url_type, url in edit_urls:
                    self.stdout.write(f"{model_name}: {url}")

            if other_urls:
                self.stdout.write("\n" + "-" * 25 + " OTHER " + "-" * 25)
                for model_name, url_type, url in other_urls:
                    self.stdout.write(f"{model_name} [{url_type}]: {url}")
        else:
            with open(output_file, "w") as f:
                f.write("=" * 50 + "\n")
                f.write("FRONTEND URLS\n")
                f.write("=" * 50 + "\n")
                for model_name, url_type, url in frontend_urls:
                    f.write(f"{model_name}: {url}\n")

                f.write("\n" + "=" * 50 + "\n")
                f.write("BACKEND URLS\n")
                f.write("=" * 50 + "\n")

                # Group backend URLs by type
                admin_urls = [url for url in backend_urls if url[1] == "admin"]
                edit_urls = [url for url in backend_urls if url[1] == "edit"]
                list_urls = [url for url in backend_urls if url[1] == "list"]
                other_urls = [
                    url
                    for url in backend_urls
                    if url[1] not in ["admin", "edit", "list"]
                ]

                if admin_urls:
                    f.write("\n" + "-" * 25 + " ADMIN " + "-" * 25 + "\n")
                    for model_name, url_type, url in admin_urls:
                        f.write(f"{model_name}: {url}\n")

                if list_urls:
                    f.write("\n" + "-" * 25 + " LIST " + "-" * 25 + "\n")
                    for model_name, url_type, url in list_urls:
                        f.write(f"{model_name}: {url}\n")

                if edit_urls:
                    f.write("\n" + "-" * 25 + " EDIT " + "-" * 25 + "\n")
                    for model_name, url_type, url in edit_urls:
                        f.write(f"{model_name}: {url}\n")

                if other_urls:
                    f.write("\n" + "-" * 25 + " OTHER " + "-" * 25 + "\n")
                    for model_name, url_type, url in other_urls:
                        f.write(f"{model_name} [{url_type}]: {url}\n")

            self.stdout.write(self.style.SUCCESS(f"URLs written to {output_file}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Found {len(urls)} total URLs ({len(frontend_urls)} frontend, {len(backend_urls)} backend)"
            )
        )
