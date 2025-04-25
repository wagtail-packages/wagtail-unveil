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
            self.assertIsInstance(url_entry[1], str)  # type (list, edit, etc.)
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