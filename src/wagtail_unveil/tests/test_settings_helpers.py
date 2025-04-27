from django.test import TestCase
from io import StringIO

from wagtail_unveil.helpers.settings_helpers import get_settings_admin_urls


class SettingsHelpersTests(TestCase):
    """Tests for the settings_helpers.py module."""
    
    def setUp(self):
        self.output = StringIO()
        self.base_url = "http://testserver"

    def test_get_settings_admin_urls_returns_list(self):
        """Test that get_settings_admin_urls returns a list of URLs."""
        urls = get_settings_admin_urls(self.output, self.base_url)
        
        # Verify the function returns a list
        self.assertIsInstance(urls, list)
        
        # Verify that the function returns some URLs (we can't check exact contents
        # since they depend on installed apps and database state)
        self.assertTrue(len(urls) > 0)
        
        # Verify the format of the entries
        for url_entry in urls:
            # Each entry should be a tuple of (name, type, url)
            self.assertEqual(len(url_entry), 3)
            self.assertIsInstance(url_entry[0], str)  # name
            self.assertIsInstance(url_entry[1], str)  # type (list, edit, delete, etc.)
            self.assertIsInstance(url_entry[2], str)  # URL
            
            # URL should start with the base_url
            self.assertTrue(url_entry[2].startswith(self.base_url))

    def test_get_settings_admin_urls_with_trailing_slash(self):
        """Test that get_settings_admin_urls handles base URLs with trailing slashes correctly."""
        urls = get_settings_admin_urls(self.output, "http://testserver/")
        
        # Check that URLs don't have double slashes
        for url_entry in urls:
            self.assertNotIn("//admin", url_entry[2])
            
    def test_settings_sections_included(self):
        """Test that common settings sections are included in the URLs."""
        urls = get_settings_admin_urls(self.output, self.base_url)
        
        # Extract just the names for easier testing
        url_names = [url[0] for url in urls]
        
        # Check that essential sections are included
        self.assertIn("Settings > Sites", url_names)
        self.assertIn("Settings > Collections", url_names)
        self.assertIn("Settings > Users", url_names)
        self.assertIn("Settings > Groups", url_names)
        
    def test_url_types_included(self):
        """Test that different URL types (list, edit, delete) are included."""
        urls = get_settings_admin_urls(self.output, self.base_url)
        
        # Extract URL types for easier testing
        url_types = [url[1] for url in urls]
        
        # Verify that we have list, edit, and delete URL types
        # Some entities might not have instances, so we check for these types existing in general
        self.assertIn("list", url_types)
        
        # Check for edit and delete URLs if there are instances
        # Skip assertion if site has no data, as this depends on database state
        if "edit" in url_types:
            # If we have edit URLs, we should also have delete URLs
            self.assertIn("delete", url_types)
            
    def test_delete_url_patterns(self):
        """Test that delete URLs follow correct patterns."""
        urls = get_settings_admin_urls(self.output, self.base_url)
        
        for name, type_, url in urls:
            if type_ == "delete":
                # Most delete URLs should end with /delete/
                # Exception: Workflows and workflow tasks use /disable/ pattern
                if "Workflows" in name or "Workflow tasks" in name:
                    self.assertTrue(
                        url.endswith("/disable/") or "/disable/" in url,
                        f"Workflow/task delete URL doesn't use expected pattern: {url}"
                    )
                else:
                    self.assertTrue(
                        url.endswith("/delete/") or "/delete/" in url,
                        f"Delete URL doesn't use expected pattern: {url}"
                    )