from django.test import TestCase
from io import StringIO
from unittest.mock import Mock, patch


from wagtail_unveil.helpers.page_helpers import (
    PageHelper,
)


class PageHelperTests(TestCase):
    """Tests for the PageHelper class."""
    
    def setUp(self):
        self.output = StringIO()
        self.base_url = "http://testserver"
        self.max_instances = 2
        
        # Create mock page instances
        self.mock_page1 = Mock()
        self.mock_page1.id = 1
        self.mock_page1.title = "Test Page 1"
        self.mock_page1.url = "/test-page-1/"
        
        self.mock_page2 = Mock()
        self.mock_page2.id = 2
        self.mock_page2.title = "Test Page 2"
        self.mock_page2.url = "http://external-site.com/test-page-2/"
        
        self.mock_page3 = Mock()
        self.mock_page3.id = 3
        self.mock_page3.title = "Test Page 3"
        self.mock_page3.url = None
        
        # Create a mock Page model
        self.mock_page_model = Mock()
        self.mock_page_model._meta.app_label = "wagtailcore"
        self.mock_page_model._meta.model_name = "page"

    def test_initialization(self):
        """Test PageHelper initialization sets up the correct attributes."""
        helper = PageHelper(self.output, self.base_url, self.max_instances)
        self.assertEqual(helper.base, self.base_url.rstrip('/'))
        
    def test_get_edit_url(self):
        """Test get_edit_url returns correct URL format."""
        helper = PageHelper(self.output, self.base_url, self.max_instances)
        self.assertEqual(helper.get_edit_url(123), "http://testserver/admin/pages/123/edit/")
    
    def test_get_delete_url(self):
        """Test get_delete_url returns correct URL format."""
        helper = PageHelper(self.output, self.base_url, self.max_instances)
        self.assertEqual(helper.get_delete_url(456), "http://testserver/admin/pages/456/delete/")
    
    def test_get_list_url(self):
        """Test get_list_url returns correct URL format."""
        helper = PageHelper(self.output, self.base_url, self.max_instances)
        self.assertEqual(helper.get_list_url(), "http://testserver/admin/pages/")
    
    def test_get_frontend_url_with_relative_url(self):
        """Test get_frontend_url with a relative URL."""
        helper = PageHelper(self.output, self.base_url, self.max_instances)
        self.assertEqual(helper.get_frontend_url(self.mock_page1), 
                         "http://testserver/test-page-1/")
    
    def test_get_frontend_url_with_absolute_url(self):
        """Test get_frontend_url with an absolute URL."""
        helper = PageHelper(self.output, self.base_url, self.max_instances)
        self.assertEqual(helper.get_frontend_url(self.mock_page2), 
                         "http://external-site.com/test-page-2/")
    
    def test_get_frontend_url_with_no_url(self):
        """Test get_frontend_url when page has no URL."""
        helper = PageHelper(self.output, self.base_url, self.max_instances)
        self.assertIsNone(helper.get_frontend_url(self.mock_page3))

    @patch('wagtail_unveil.helpers.page_helpers.get_page_models')
    @patch('wagtail_unveil.helpers.page_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.page_helpers.get_instance_sample')
    @patch('wagtail_unveil.helpers.page_helpers.truncate_instance_name')
    @patch('wagtail_unveil.helpers.page_helpers.format_url_tuple')
    def test_collect_urls_with_instances(self, mock_format_url_tuple, mock_truncate_instance_name, 
                                       mock_get_instance_sample, mock_model_has_instances, 
                                       mock_get_page_models):
        """Test collect_urls method when there are page instances."""
        # Set up mocks
        mock_get_page_models.return_value = [self.mock_page_model]
        mock_model_has_instances.return_value = True
        mock_get_instance_sample.return_value = [self.mock_page1, self.mock_page2]
        mock_truncate_instance_name.side_effect = lambda x: f"Truncated {x}"
        
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (
            model, instance_name, url_type, url)
        
        # Create helper and collect URLs
        helper = PageHelper(self.output, self.base_url, self.max_instances)
        result = helper.collect_urls()
        
        # Check the results - should have edit, delete, and frontend URL for each instance
        # 2 instances x 3 URLs (edit, delete, frontend) = 6 URLs
        self.assertEqual(len(result), 6)
        
        # Check edit URLs
        mock_format_url_tuple.assert_any_call(
            "wagtailcore.page", "Truncated Test Page 1", "edit", 
            "http://testserver/admin/pages/1/edit/"
        )
        mock_format_url_tuple.assert_any_call(
            "wagtailcore.page", "Truncated Test Page 2", "edit", 
            "http://testserver/admin/pages/2/edit/"
        )
        
        # Check delete URLs
        mock_format_url_tuple.assert_any_call(
            "wagtailcore.page", "Truncated Test Page 1", "delete", 
            "http://testserver/admin/pages/1/delete/"
        )
        mock_format_url_tuple.assert_any_call(
            "wagtailcore.page", "Truncated Test Page 2", "delete", 
            "http://testserver/admin/pages/2/delete/"
        )
        
        # Check frontend URLs
        mock_format_url_tuple.assert_any_call(
            "wagtailcore.page", "Truncated Test Page 1", "frontend", 
            "http://testserver/test-page-1/"
        )
        mock_format_url_tuple.assert_any_call(
            "wagtailcore.page", "Truncated Test Page 2", "frontend", 
            "http://external-site.com/test-page-2/"
        )

    @patch('wagtail_unveil.helpers.page_helpers.get_page_models')
    @patch('wagtail_unveil.helpers.page_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.page_helpers.format_url_tuple')
    def test_collect_urls_without_instances(self, mock_format_url_tuple, 
                                          mock_model_has_instances, mock_get_page_models):
        """Test collect_urls method when there are no page instances."""
        # Set up mocks
        mock_get_page_models.return_value = [self.mock_page_model]
        mock_model_has_instances.return_value = False
        
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (
            model, instance_name, url_type, url)
        
        # Create helper and collect URLs
        helper = PageHelper(self.output, self.base_url, self.max_instances)
        result = helper.collect_urls()
        
        # Check the results
        self.assertEqual(len(result), 1)  # Only the list URL
        
        # Verify the correct message was written to output
        self.assertIn("Note: wagtailcore.page has no instances", self.output.getvalue())
        
        # Check that the list URL was added with the correct format and NO INSTANCES note
        mock_format_url_tuple.assert_called_once_with(
            "wagtailcore.page (NO INSTANCES)", None, "list", "http://testserver/admin/pages/"
        )

    @patch('wagtail_unveil.helpers.page_helpers.get_page_models')
    @patch('wagtail_unveil.helpers.page_helpers.model_has_instances')
    def test_collect_urls_with_styled_output(self, mock_model_has_instances, mock_get_page_models):
        """Test collect_urls method when output has style method."""
        # Set up mocks
        mock_get_page_models.return_value = [self.mock_page_model]
        mock_model_has_instances.return_value = False
        
        # Create a mock output object with style.INFO method
        mock_output = Mock()
        mock_output.style = Mock()
        mock_output.style.INFO = lambda x: f"INFO: {x}"
        mock_output.write = Mock()
        
        # Create helper and collect URLs
        helper = PageHelper(mock_output, self.base_url, self.max_instances)
        helper.collect_urls()
        
        # Check that style.INFO was called correctly
        mock_output.write.assert_called_once_with(mock_output.style.INFO("Note: wagtailcore.page has no instances"))

    def test_page_urls_calls_collect_urls(self):
        """Test page_urls method calls collect_urls."""
        helper = PageHelper(self.output, self.base_url, self.max_instances)
        # Mock the collect_urls method
        helper.collect_urls = Mock(return_value=["url1", "url2"])
        
        result = helper.page_urls()
        
        # Verify collect_urls was called
        helper.collect_urls.assert_called_once()
        self.assertEqual(result, ["url1", "url2"])