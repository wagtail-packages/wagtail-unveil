import re
from getpass import getpass
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from requests.exceptions import RequestException
from wagtail.models import Site, get_page_models
from wagtail.snippets.models import get_snippet_models

from wagtail_unveil.helpers.document_helpers import DocumentHelper
from wagtail_unveil.helpers.image_helpers import ImageHelper
from wagtail_unveil.helpers.modeladmin_helpers import ModelAdminHelper
from wagtail_unveil.helpers.modelviewset_helpers import (
    ModelViewSetHelper,
    get_modelviewset_models,
)
from wagtail_unveil.helpers.page_helpers import PageHelper
from wagtail_unveil.helpers.settings_helpers import get_settings_admin_urls
from wagtail_unveil.helpers.site_helpers import SiteHelper
from wagtail_unveil.helpers.snippet_helpers import SnippetHelper


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
            help="Maximum instances to show per model (default: 1, use 0 for unlimited)",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Check URL accessibility with the provided credentials",
        )
        parser.add_argument(
            "--username",
            type=str,
            help="Username for authentication (can also be set with WAGTAIL_UNVEIL_CHECK_USERNAME setting)",
        )
        parser.add_argument(
            "--password",
            type=str,
            help="Password for authentication (can also be set with WAGTAIL_UNVEIL_CHECK_PASSWORD setting)",
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
        check_urls = options.get("check", False)
        
        # Get credentials from command line or settings if check is enabled
        username = None
        password = None
        if check_urls:
            username = options.get("username") or getattr(settings, "WAGTAIL_UNVEIL_CHECK_USERNAME", None)
            password = options.get("password") or getattr(settings, "WAGTAIL_UNVEIL_CHECK_PASSWORD", None)
            
            # If credentials are not provided, prompt for them
            if not username:
                username = input("Admin username: ")
            if not password:
                password = getpass("Admin password: ")
                
            if not username or not password:
                self.stdout.write(
                    self.style.WARNING(
                        "URL checking disabled: No credentials provided."
                    )
                )
                check_urls = False
            else:
                self.stdout.write(self.style.SUCCESS(f"URL checking enabled with username: {username}"))
        
        # Get max_instances from command line argument first, then settings, or fall back to 1
        max_instances = options.get("max_instances")
        if max_instances is None:
            max_instances = getattr(settings, 'WAGTAIL_UNVEIL_MAX_INSTANCES', 1)

        self.stdout.write(self.style.SUCCESS("Finding all Wagtail models..."))

        urls = []

        # Get site default pages
        site_helper = SiteHelper(output=self.stdout, base_url=base_url, max_instances=max_instances)
        site_urls = site_helper.site_urls()
        urls.extend(site_urls)

        # Get all page models
        page_models = get_page_models()
        self.stdout.write(f"Found {len(page_models)} page models:")
        for model in page_models:
            self.stdout.write(f"  - {model.__name__}")

        # Get URLs for page models
        page_helper = PageHelper(self.stdout, base_url, max_instances)
        page_urls = page_helper.page_urls()
        urls.extend(page_urls)

        # Get all snippet models
        snippet_models = get_snippet_models()
        self.stdout.write(f"Found {len(snippet_models)} snippet models:")
        for model in snippet_models:
            self.stdout.write(f"  - {model.__name__}")

        # Get URLs for snippet models
        snippet_helper = SnippetHelper(self.stdout, base_url, max_instances)
        snippet_urls = snippet_helper.snippet_urls()
        urls.extend(snippet_urls)

        # Get generic Django models with ModelAdmin
        modeladmin_helper = ModelAdminHelper(self.stdout, base_url, max_instances)
        modeladmin_models = modeladmin_helper.get_modeladmin_models()
        self.stdout.write(f"Found {len(modeladmin_models)} modeladmin models:")
        for model in modeladmin_models:
            self.stdout.write(f"  - {model.__name__}")

        # Get URLs for modeladmin models
        modeladmin_urls = modeladmin_helper.modeladmin_urls()
        urls.extend(modeladmin_urls)

        # Get models registered with ModelViewSet
        modelviewset_models = get_modelviewset_models()
        self.stdout.write(f"Found {len(modelviewset_models)} modelviewset models:")
        for model in modelviewset_models:
            self.stdout.write(f"  - {model.__name__}")

        # Get URLs for modelviewset models
        modelviewset_helper = ModelViewSetHelper(
            self.stdout,
            base_url,
            max_instances,
        )
        modelviewset_urls = modelviewset_helper.modelviewset_urls()
        urls.extend(modelviewset_urls)

        # Get image admin URLs
        self.stdout.write("Getting image admin URLs...")
        image_helper = ImageHelper(self.stdout, base_url, max_instances)
        image_urls = image_helper.image_urls()
        urls.extend(image_urls)

        # Get document admin URLs
        self.stdout.write("Getting document admin URLs...")
        document_helper = DocumentHelper(self.stdout, base_url, max_instances)
        document_urls = document_helper.document_urls()
        urls.extend(document_urls)

        # Get settings admin URLs
        self.stdout.write("Getting settings admin URLs...")
        settings_urls = get_settings_admin_urls(self.stdout, base_url)
        urls.extend(settings_urls)

        # Process URLs with checking if enabled
        if check_urls:
            self.stdout.write(self.style.SUCCESS("Checking URL accessibility..."))
            
            # Establish a session for better performance and cookie handling
            session = self._create_admin_session(base_url, username, password)
            if session:
                self.stdout.write(self.style.SUCCESS("Successfully authenticated with Wagtail admin"))
                checked_urls = []
                success_count = 0
                failure_count = 0
                
                for url_data in urls:
                    display_name, instance_name, url_type, url = url_data
                    status = self._check_url_with_session(session, url)
                    checked_urls.append((display_name, instance_name, url_type, url, status))
                    
                    # Count successes and failures
                    if status == "OK":
                        success_count += 1
                    else:
                        failure_count += 1
                
                # Replace the original URLs with the checked ones
                urls = checked_urls
            else:
                self.stdout.write(self.style.ERROR("Failed to authenticate with Wagtail admin"))
                check_urls = False
                success_count = 0
                failure_count = 0
        
        # Group URLs by frontend vs backend
        frontend_urls = [url for url in urls if url[2] == "frontend"]
        backend_urls = [url for url in urls if url[2] != "frontend"]

        # Output the URLs
        if output_type == "console":
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS("FRONTEND URLS"))
            self.stdout.write("=" * 50)
            for url_data in frontend_urls:
                if check_urls:
                    display_name, _, _, url, status = url_data
                    if status == "OK":
                        status_str = self.style.SUCCESS(f"[{status}]")
                    else:
                        status_str = self.style.ERROR(f"[{status}]")
                    self.stdout.write(f"{display_name}: {url} {status_str}")
                else:
                    display_name, _, _, url = url_data
                    self.stdout.write(f"{display_name}: {url}")

            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS("BACKEND URLS"))
            self.stdout.write("=" * 50)

            # Group backend URLs by type
            admin_urls = [url for url in backend_urls if url[2] == "admin"]
            edit_urls = [url for url in backend_urls if url[2] == "edit"]
            list_urls = [url for url in backend_urls if url[2] == "list"]
            delete_urls = [url for url in backend_urls if url[2] == "delete"]
            other_urls = [url for url in backend_urls if url[2] not in ["admin", "edit", "list", "delete"]]

            if admin_urls:
                self.stdout.write("\n" + "-" * 25 + " ADMIN " + "-" * 25)
                for url_data in admin_urls:
                    if check_urls:
                        display_name, _, _, url, status = url_data
                        if status == "OK":
                            status_str = self.style.SUCCESS(f"[{status}]")
                        else:
                            status_str = self.style.ERROR(f"[{status}]")
                        self.stdout.write(f"{display_name}: {url} {status_str}")
                    else:
                        display_name, _, _, url = url_data
                        self.stdout.write(f"{display_name}: {url}")

            if list_urls:
                self.stdout.write("\n" + "-" * 25 + " LIST " + "-" * 25)
                for url_data in list_urls:
                    if check_urls:
                        display_name, _, _, url, status = url_data
                        if status == "OK":
                            status_str = self.style.SUCCESS(f"[{status}]")
                        else:
                            status_str = self.style.ERROR(f"[{status}]")
                        self.stdout.write(f"{display_name}: {url} {status_str}")
                    else:
                        display_name, _, _, url = url_data
                        self.stdout.write(f"{display_name}: {url}")

            if edit_urls:
                self.stdout.write("\n" + "-" * 25 + " EDIT " + "-" * 25)
                for url_data in edit_urls:
                    if check_urls:
                        display_name, _, _, url, status = url_data
                        if status == "OK":
                            status_str = self.style.SUCCESS(f"[{status}]")
                        else:
                            status_str = self.style.ERROR(f"[{status}]")
                        self.stdout.write(f"{display_name}: {url} {status_str}")
                    else:
                        display_name, _, _, url = url_data
                        self.stdout.write(f"{display_name}: {url}")

            if delete_urls:
                self.stdout.write("\n" + "-" * 25 + " DELETE " + "-" * 25)
                for url_data in delete_urls:
                    if check_urls:
                        display_name, _, _, url, status = url_data
                        if status == "OK":
                            status_str = self.style.SUCCESS(f"[{status}]")
                        else:
                            status_str = self.style.ERROR(f"[{status}]")
                        self.stdout.write(f"{display_name}: {url} {status_str}")
                    else:
                        display_name, _, _, url = url_data
                        self.stdout.write(f"{display_name}: {url}")

            if other_urls:
                self.stdout.write("\n" + "-" * 25 + " OTHER " + "-" * 25)
                for url_data in other_urls:
                    if check_urls:
                        display_name, _, _, url, status = url_data
                        if status == "OK":
                            status_str = self.style.SUCCESS(f"[{status}]")
                        else:
                            status_str = self.style.ERROR(f"[{status}]")
                        self.stdout.write(f"{display_name}: {url} {status_str}")
                    else:
                        display_name, _, _, url = url_data
                        self.stdout.write(f"{display_name}: {url}")
        else:
            with open(output_file, "w") as f:
                f.write("=" * 50 + "\n")
                f.write("FRONTEND URLS\n")
                f.write("=" * 50 + "\n")
                for url_data in frontend_urls:
                    if check_urls:
                        display_name, _, _, url, status = url_data
                        status_str = f"[{status}]" if status else ""
                        # Note: Terminal colors don't work in files, but consistent format
                        f.write(f"{display_name}: {url} {status_str}\n")
                    else:
                        display_name, _, _, url = url_data
                        f.write(f"{display_name}: {url}\n")

                f.write("\n" + "=" * 50 + "\n")
                f.write("BACKEND URLS\n")
                f.write("=" * 50 + "\n")

                # Group backend URLs by type
                admin_urls = [url for url in backend_urls if url[2] == "admin"]
                edit_urls = [url for url in backend_urls if url[2] == "edit"]
                list_urls = [url for url in backend_urls if url[2] == "list"]
                delete_urls = [url for url in backend_urls if url[2] == "delete"]
                other_urls = [url for url in backend_urls if url[2] not in ["admin", "edit", "list", "delete"]]

                if admin_urls:
                    f.write("\n" + "-" * 25 + " ADMIN " + "-" * 25 + "\n")
                    for url_data in admin_urls:
                        if check_urls:
                            display_name, _, _, url, status = url_data
                            status_str = f"[{status}]" if status else ""
                            f.write(f"{display_name}: {url} {status_str}\n")
                        else:
                            display_name, _, _, url = url_data
                            f.write(f"{display_name}: {url}\n")

                if list_urls:
                    f.write("\n" + "-" * 25 + " LIST " + "-" * 25 + "\n")
                    for url_data in list_urls:
                        if check_urls:
                            display_name, _, _, url, status = url_data
                            status_str = f"[{status}]" if status else ""
                            f.write(f"{display_name}: {url} {status_str}\n")
                        else:
                            display_name, _, _, url = url_data
                            f.write(f"{display_name}: {url}\n")

                if edit_urls:
                    f.write("\n" + "-" * 25 + " EDIT " + "-" * 25 + "\n")
                    for url_data in edit_urls:
                        if check_urls:
                            display_name, _, _, url, status = url_data
                            status_str = f"[{status}]" if status else ""
                            f.write(f"{display_name}: {url} {status_str}\n")
                        else:
                            display_name, _, _, url = url_data
                            f.write(f"{display_name}: {url}\n")

                if delete_urls:
                    f.write("\n" + "-" * 25 + " DELETE " + "-" * 25 + "\n")
                    for url_data in delete_urls:
                        if check_urls:
                            display_name, _, _, url, status = url_data
                            status_str = f"[{status}]" if status else ""
                            f.write(f"{display_name}: {url} {status_str}\n")
                        else:
                            display_name, _, _, url = url_data
                            f.write(f"{display_name}: {url}\n")

                if other_urls:
                    f.write("\n" + "-" * 25 + " OTHER " + "-" * 25 + "\n")
                    for url_data in other_urls:
                        if check_urls:
                            display_name, _, _, url, status = url_data
                            status_str = f"[{status}]" if status else ""
                            f.write(f"{display_name}: {url} {status_str}\n")
                        else:
                            display_name, _, _, url = url_data
                            f.write(f"{display_name}: {url}\n")
                
                # Add URL check summary to the end of the file
                if check_urls:
                    f.write("\n" + "=" * 50 + "\n")
                    f.write("URL CHECK SUMMARY\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Successful URLs: {success_count}\n")
                    f.write(f"Failed URLs: {failure_count}\n")
                    success_rate = (success_count / len(urls)) * 100 if urls else 0
                    f.write(f"Success rate: {success_rate:.1f}%\n")

            self.stdout.write(self.style.SUCCESS(f"URLs written to {output_file}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Found {len(urls)} total URLs ({len(frontend_urls)} frontend, {len(backend_urls)} backend)"
            )
        )
        
        # Display summary of successful and failed URLs if check was performed
        if check_urls:
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS("URL CHECK SUMMARY"))
            self.stdout.write("=" * 50)
            self.stdout.write(self.style.SUCCESS(f"Successful URLs: {success_count}"))
            self.stdout.write(self.style.ERROR(f"Failed URLs: {failure_count}"))
            success_rate = (success_count / len(urls)) * 100 if urls else 0
            self.stdout.write(f"Success rate: {success_rate:.1f}%")

    def _create_admin_session(self, base_url, username, password):
        """
        Create and return a requests session logged into the Wagtail admin.
        Returns the session object if successful, None otherwise.
        """
        session = requests.Session()
        
        # First get the login page to extract CSRF token
        login_url = urljoin(base_url, '/admin/login/')
        try:
            response = session.get(login_url, timeout=10)
            response.raise_for_status()
            
            # Extract CSRF token from the login page
            csrf_token = None
            match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
            if match:
                csrf_token = match.group(1)
            else:
                self.stdout.write(self.style.ERROR("Could not find CSRF token in login page"))
                return None
                
            # Now attempt to log in
            login_data = {
                'csrfmiddlewaretoken': csrf_token,
                'username': username,
                'password': password,
                'next': '/admin/'
            }
            
            response = session.post(login_url, data=login_data, headers={
                'Referer': login_url
            }, timeout=10)
            
            # Check if login was successful by looking for error messages or checking if we're still on login page
            if '/admin/login/' in response.url or 'Please enter the correct username and password' in response.text:
                self.stdout.write(self.style.ERROR("Login failed: Invalid credentials"))
                return None
            
            # Verify access to a protected page to confirm authentication
            verify_url = urljoin(base_url, '/admin/')
            verify_response = session.get(verify_url, timeout=10)
            
            # If we get redirected back to login or get permission denied, authentication failed
            if '/admin/login/' in verify_response.url or verify_response.status_code == 403:
                self.stdout.write(self.style.ERROR("Login verification failed: Redirected to login page"))
                return None
                
            return session
                
        except RequestException as e:
            self.stdout.write(self.style.ERROR(f"Error creating admin session: {str(e)}"))
            return None
    
    def _check_url_with_session(self, session, url):
        """Check if a URL is accessible using the established session."""
        try:
            response = session.get(url, timeout=10, allow_redirects=True)
            
            # Consider redirects that end with a 200 as success
            if response.status_code == 200:
                return "OK"
            elif response.status_code in (401, 403):
                return "AUTH FAILED"
            elif response.status_code in (404, 410):
                return "NOT FOUND"
            elif response.status_code >= 500:
                return f"SERVER ERROR ({response.status_code})"
            else:
                return f"ERROR ({response.status_code})"
        except RequestException as e:
            # Isolate the most relevant part of the error
            error_msg = str(e)
            if len(error_msg) > 50:  # Truncate long error messages
                error_msg = error_msg[:47] + "..."
            return f"ERROR ({error_msg})"

    def _check_url_accessibility(self, url, username, password):
        """
        Legacy method for individual URL checking without session.
        Consider using _check_url_with_session instead.
        """
        try:
            response = requests.get(url, auth=(username, password), timeout=10)
            if response.status_code == 200:
                return "OK"
            elif response.status_code == 401 or response.status_code == 403:
                return "AUTH FAILED"
            else:
                return f"ERROR ({response.status_code})"
        except RequestException as e:
            return f"ERROR ({str(e)})"
