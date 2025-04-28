from django.test import TestCase
from django.db import DatabaseError
from io import StringIO
from unittest.mock import Mock, patch


from wagtail_unveil.helpers.page_helpers import (
    get_page_models,
    get_page_urls,
)
from wagtail_unveil.helpers.site_helpers import get_site_urls


class GetPageModelsTests(TestCase):
    @patch('wagtail_unveil.helpers.page_helpers.get_page_models_wagtail')
    def test_get_page_models(self, mock_get_page_models_wagtail):
        """Test that get_page_models returns all models that inherit from Page."""
        # Create mock models
        mock_model1 = Mock()
        mock_model2 = Mock()
        
        # Set up the mock to return our test models
        mock_get_page_models_wagtail.return_value = [mock_model1, mock_model2]
        
        # Call the function
        result = get_page_models()
        
        # Check we got the expected models
        self.assertEqual(len(result), 2)
        self.assertIn(mock_model1, result)
        self.assertIn(mock_model2, result)
        
        # Verify the Wagtail function was called
        mock_get_page_models_wagtail.assert_called_once()


class GetPageUrlsTests(TestCase):
    def setUp(self):
        self.output = StringIO()
        
        # Create mock models and instances
        self.mock_model1 = Mock()
        self.mock_model1._meta = Mock()
        self.mock_model1._meta.app_label = "app1"
        self.mock_model1._meta.model_name = "model1"
        
        self.mock_model2 = Mock()
        self.mock_model2._meta = Mock()
        self.mock_model2._meta.app_label = "app2"
        self.mock_model2._meta.model_name = "model2"
        
        self.mock_instance1 = Mock()
        self.mock_instance1.id = 1
        self.mock_instance1.title = "Instance 1"
        self.mock_instance1.url = "/page1/"
        
        self.mock_instance2 = Mock()
        self.mock_instance2.id = 2
        self.mock_instance2.title = "Instance 2"
        self.mock_instance2.url = "http://example.com/page2/"
        
        self.mock_instance3 = Mock()
        self.mock_instance3.id = 3
        self.mock_instance3.title = "Instance 3"
        # This instance doesn't have a URL
        
        self.page_models = [self.mock_model1, self.mock_model2]
        self.base_url = "http://testserver"
        self.max_instances = 5

    @patch('wagtail_unveil.helpers.page_helpers.get_page_models')
    @patch('wagtail_unveil.helpers.page_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.page_helpers.get_instance_sample')
    def test_get_page_urls_with_instances(self, mock_get_instance_sample, mock_model_has_instances, mock_get_page_models):
        """Test get_page_urls with models that have instances."""
        # Set up the get_page_models mock to return our test models
        mock_get_page_models.return_value = self.page_models
        
        # Set up the mocks to return instances for the first model and no instances for the second
        mock_model_has_instances.side_effect = [True, False]
        mock_get_instance_sample.return_value = [self.mock_instance1, self.mock_instance2, self.mock_instance3]
        
        # Call the function with the updated signature
        result = get_page_urls(self.output, self.base_url, self.max_instances)
        
        # Check that we get the expected URLs
        # 3 edit URLs + 3 delete URLs + 3 frontend URLs (for instances with URLs) + 1 listing URL (for model with no instances)
        self.assertEqual(len(result), 10)
        
        # Check edit URLs for instances
        edit_urls = [r for r in result if r[1] == "edit"]
        self.assertEqual(len(edit_urls), 3)
        
        # Check delete URLs for instances
        delete_urls = [r for r in result if r[1] == "delete"]
        self.assertEqual(len(delete_urls), 3)
        
        # Verify delete URLs are formatted correctly
        self.assertIn(("app1.model1 (Instance 1)", "delete", "http://testserver/admin/pages/1/delete/"), result)
        self.assertIn(("app1.model1 (Instance 2)", "delete", "http://testserver/admin/pages/2/delete/"), result)
        self.assertIn(("app1.model1 (Instance 3)", "delete", "http://testserver/admin/pages/3/delete/"), result)
        
        # Check frontend URLs for instances that have them
        frontend_urls = [r for r in result if r[1] == "frontend"]
        self.assertEqual(len(frontend_urls), 3)
        
        # Check one URL with a relative path and one with an absolute URL
        self.assertIn(("app1.model1 (Instance 1)", "frontend", "http://testserver/page1/"), result)
        self.assertIn(("app1.model1 (Instance 2)", "frontend", "http://example.com/page2/"), result)
        
        # Check that models with no instances get a list URL
        list_urls = [r for r in result if r[1] == "list"]
        self.assertEqual(len(list_urls), 1)
        self.assertIn(('app2.model2 (NO INSTANCES)', 'list', 'http://testserver/admin/pages/'), result)
        
        # Check the output message for models with no instances
        self.assertIn("Note: app2.model2 has no instances", self.output.getvalue())

    @patch('wagtail_unveil.helpers.page_helpers.get_page_models')
    @patch('wagtail_unveil.helpers.page_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.page_helpers.get_instance_sample')
    def test_get_page_urls_without_instances(self, mock_get_instance_sample, mock_model_has_instances, mock_get_page_models):
        """Test get_page_urls with models that have no instances."""
        # Set up the get_page_models mock to return our test models
        mock_get_page_models.return_value = self.page_models
        
        # Set up the mocks to return no instances for both models
        mock_model_has_instances.side_effect = [False, False]
        mock_get_instance_sample.return_value = []
        
        # Call the function with the updated signature
        result = get_page_urls(self.output, self.base_url, self.max_instances)
        
        # Check that we get the expected URLs
        self.assertEqual(len(result), 2)  # 2 list URLs
        
        # Check list URLs for models with no instances
        list_urls = [r for r in result if r[1] == "list"]
        self.assertEqual(len(list_urls), 2)
        
        # Check the output messages for models with no instances
        self.assertIn("Note: app1.model1 has no instances", self.output.getvalue())
        self.assertIn("Note: app2.model2 has no instances", self.output.getvalue())
        
    @patch('wagtail_unveil.helpers.page_helpers.get_page_models')
    @patch('wagtail_unveil.helpers.page_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.page_helpers.get_instance_sample')
    def test_get_page_urls_with_trailing_slash_in_base_url(self, mock_get_instance_sample, mock_model_has_instances, mock_get_page_models):
        """Test get_page_urls with a base_url that has a trailing slash."""
        # Set up the get_page_models mock to return only the first model
        mock_get_page_models.return_value = [self.mock_model1]
        
        # Set up the mocks to return instances for the first model
        mock_model_has_instances.return_value = True
        mock_get_instance_sample.return_value = [self.mock_instance1]
        
        # Call the function with a base_url that has a trailing slash
        base_url_with_slash = "http://testserver/"
        result = get_page_urls(self.output, base_url_with_slash, self.max_instances)
        
        # Check that we get the expected URLs without double slashes
        self.assertEqual(len(result), 3)  # 1 edit URL + 1 delete URL + 1 frontend URL
        
        # Check edit URL doesn't have double slashes
        self.assertIn(("app1.model1 (Instance 1)", "edit", "http://testserver/admin/pages/1/edit/"), result)
        
        # Check delete URL doesn't have double slashes
        self.assertIn(("app1.model1 (Instance 1)", "delete", "http://testserver/admin/pages/1/delete/"), result)
        
        # Check frontend URL doesn't have double slashes
        self.assertIn(("app1.model1 (Instance 1)", "frontend", "http://testserver/page1/"), result)


class GetSiteUrlsTests(TestCase):
    def setUp(self):
        self.output = Mock()
        self.output.style = Mock()
        self.output.style.INFO = lambda x: x
        self.output.style.WARNING = lambda x: x
        self.output.write = Mock()
        
        self.base_url = "http://testserver"

    @patch('wagtail_unveil.helpers.site_helpers.Site')
    @patch('wagtail_unveil.helpers.site_helpers.Page')
    def test_get_site_urls_with_sites(self, mock_page, mock_site):
        """Test get_site_urls with sites configured."""
        # Create mock sites and root pages
        mock_root_page1 = Mock()
        mock_root_page1.id = 1
        mock_root_page1.title = "Root Page 1"
        
        mock_root_page2 = Mock()
        mock_root_page2.id = 2
        mock_root_page2.title = "Root Page 2"
        
        mock_site1 = Mock()
        mock_site1.root_page = mock_root_page1
        mock_site1.is_default_site = True
        
        mock_site2 = Mock()
        mock_site2.root_page = mock_root_page2
        mock_site2.is_default_site = False
        
        # Make Site.objects.all() return our mock sites
        mock_site.objects.all.return_value = [mock_site1, mock_site2]
        
        # Set up a mock home page for the search URL example
        mock_home_page = Mock()
        mock_home_page.title = "Welcome to Wagtail"
        mock_page.objects.filter.return_value.first.return_value = mock_home_page
        
        # Call the function
        result = get_site_urls(self.output, self.base_url)
        
        # Check that we get the expected URLs
        self.assertEqual(len(result), 11)  # Expected number of URLs
        
        # Check that we have the general admin pages listing URL
        # Note: the format must match that used in the implementation
        self.assertIn(("All Pages Listing", "list", "http://testserver/admin/pages/"), result)
        
        # Check that we have search URLs
        empty_search_url = "http://testserver/admin/pages/search/?q=xyznonexistentsearchterm123"
        self.assertIn(("Page Search (No Results)", "list", empty_search_url), result)
        
        result_search_url = "http://testserver/admin/pages/search/?q=Welcome"
        search_tuple = ("Page Search (With Results - 'Welcome')", "list", result_search_url)
        self.assertIn(search_tuple, result)
        
        # Check admin edit URLs for root pages (including root page title)
        self.assertIn(("Site default page (Root Page 1)", "edit", "http://testserver/admin/pages/1/edit/"), result)
        self.assertIn(("Site default page (Root Page 2)", "edit", "http://testserver/admin/pages/2/edit/"), result)
        
        # Check admin delete URLs for root pages
        self.assertIn(("Site default page (Root Page 1)", "delete", "http://testserver/admin/pages/1/delete/"), result)
        self.assertIn(("Site default page (Root Page 2)", "delete", "http://testserver/admin/pages/2/delete/"), result)
        
        # Check frontend URL
        self.assertIn(("Site default page", "frontend", "http://testserver/"), result)
        
        # Check explorer URLs for root pages
        self.assertIn(("Site default page explorer (Root Page 1)", "list", "http://testserver/admin/pages/1/"), result)
        self.assertIn(("Site default page explorer (Root Page 2)", "list", "http://testserver/admin/pages/2/"), result)
        
        # Check that we have the admin dashboard URL for the default site
        self.assertIn(("Admin dashboard", "admin", "http://testserver/admin/"), result)

    @patch('wagtail_unveil.helpers.site_helpers.Site')
    def test_get_site_urls_with_database_error(self, mock_site):
        """Test get_site_urls with a database error."""
        # Set up the mock to raise a database error
        mock_site.objects.all.side_effect = DatabaseError("Test database error")
        
        # Call the function
        result = get_site_urls(self.output, self.base_url)
        
        # Check that we get an empty list of URLs
        self.assertEqual(result, [])
        
        # Check that we logged an error
        self.output.write.assert_called_once()
        error_msg = self.output.write.call_args[0][0]
        self.assertIn("Error getting site URLs", error_msg)

    @patch('wagtail_unveil.helpers.site_helpers.Site')
    @patch('wagtail_unveil.helpers.site_helpers.Page')
    def test_get_site_urls_with_no_home_page(self, mock_page, mock_site):
        """Test get_site_urls with no home page available for the search example."""
        # Create mock site and root page
        mock_root_page = Mock()
        mock_root_page.id = 1
        mock_root_page.title = "Root Page"
        
        mock_site1 = Mock()
        mock_site1.root_page = mock_root_page
        mock_site1.is_default_site = True
        
        # Make Site.objects.all() return our mock site
        mock_site.objects.all.return_value = [mock_site1]
        
        # Make Page.objects.filter().first() return None to simulate no home page
        mock_page.objects.filter.return_value.first.return_value = None
        
        # Call the function
        result = get_site_urls(self.output, self.base_url)
        
        # Check that we get the expected URLs
        self.assertGreater(len(result), 0)  # Should still have some URLs
        
        # Check that we have a search URL with the fallback search term 'page'
        result_search_url = "http://testserver/admin/pages/search/?q=page"
        self.assertTrue(any(url[2] == result_search_url for url in result))