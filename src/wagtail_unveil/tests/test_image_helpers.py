from django.test import TestCase
from io import StringIO
from unittest.mock import Mock, patch

from wagtail_unveil.helpers.image_helpers import ImageHelper


class ImageHelperTests(TestCase):
    """Tests for the ImageHelper class."""

    def setUp(self):
        """Set up common test data."""
        self.output = StringIO()
        self.base_url = "http://testserver"
        self.max_instances = 2
        
        # Create a mock Image model
        self.mock_image_model = Mock()
        self.mock_image_model._meta.app_label = "wagtailimages"
        self.mock_image_model._meta.model_name = "image"

    @patch('wagtail_unveil.helpers.image_helpers.get_image_model')
    def test_initialization(self, mock_get_image_model):
        """Test ImageHelper initialization sets up the correct attributes."""
        mock_get_image_model.return_value = self.mock_image_model
        
        helper = ImageHelper(self.output, self.base_url, self.max_instances)
        
        self.assertEqual(helper.base, self.base_url.rstrip('/'))
        self.assertEqual(helper.image_model, self.mock_image_model)
        self.assertEqual(helper.model_name, "wagtailimages.image")

    @patch('wagtail_unveil.helpers.image_helpers.get_image_model')
    def test_url_methods(self, mock_get_image_model):
        """Test URL generation methods return correct URLs."""
        mock_get_image_model.return_value = self.mock_image_model
        
        helper = ImageHelper(self.output, self.base_url, self.max_instances)
        
        self.assertEqual(helper.get_list_url(), "http://testserver/admin/images/")
        self.assertEqual(helper.get_edit_url(123), "http://testserver/admin/images/123/")
        self.assertEqual(helper.get_delete_url(456), "http://testserver/admin/images/456/delete/")

    @patch('wagtail_unveil.helpers.image_helpers.get_image_model')
    @patch('wagtail_unveil.helpers.image_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.image_helpers.get_instance_sample')
    @patch('wagtail_unveil.helpers.image_helpers.truncate_instance_name')
    @patch('wagtail_unveil.helpers.image_helpers.format_url_tuple')
    def test_collect_urls_with_instances(self, mock_format_url_tuple, mock_truncate_instance_name, 
                                       mock_get_instance_sample, mock_model_has_instances, mock_get_image_model):
        """Test collect_urls method when there are image instances."""
        # Set up mocks
        mock_get_image_model.return_value = self.mock_image_model
        mock_model_has_instances.return_value = True
        
        mock_instance1 = Mock()
        mock_instance1.id = 1
        mock_instance1.__str__ = lambda self: "Image 1"
        
        mock_instance2 = Mock()
        mock_instance2.id = 2
        mock_instance2.__str__ = lambda self: "Image 2"
        
        mock_get_instance_sample.return_value = [mock_instance1, mock_instance2]
        
        mock_truncate_instance_name.side_effect = lambda x: f"Truncated {x}"
        
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (model, instance_name, url_type)
        
        # Create helper and collect URLs
        helper = ImageHelper(self.output, self.base_url, self.max_instances)
        result = helper.collect_urls()
        
        # Check the results
        self.assertEqual(len(result), 5)  # 1 list + 2 edit URLs + 2 delete URLs
        
        # Check that the list URL was added with the correct format
        mock_format_url_tuple.assert_any_call("wagtailimages.image", None, "list", "http://testserver/admin/images/")
        
        # Check that edit URLs were added with the correct format
        mock_format_url_tuple.assert_any_call(
            "wagtailimages.image", "Truncated Image 1", "edit", "http://testserver/admin/images/1/"
        )
        mock_format_url_tuple.assert_any_call(
            "wagtailimages.image", "Truncated Image 2", "edit", "http://testserver/admin/images/2/"
        )
        
        # Check that delete URLs were added with the correct format
        mock_format_url_tuple.assert_any_call(
            "wagtailimages.image", "Truncated Image 1", "delete", "http://testserver/admin/images/1/delete/"
        )
        mock_format_url_tuple.assert_any_call(
            "wagtailimages.image", "Truncated Image 2", "delete", "http://testserver/admin/images/2/delete/"
        )

    @patch('wagtail_unveil.helpers.image_helpers.get_image_model')
    @patch('wagtail_unveil.helpers.image_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.image_helpers.format_url_tuple')
    def test_collect_urls_without_instances(self, mock_format_url_tuple, mock_model_has_instances, mock_get_image_model):
        """Test collect_urls method when there are no image instances."""
        # Set up mocks
        mock_get_image_model.return_value = self.mock_image_model
        mock_model_has_instances.return_value = False
        
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (model, instance_name, url_type)
        
        # Create helper and collect URLs
        helper = ImageHelper(self.output, self.base_url, self.max_instances)
        result = helper.collect_urls()
        
        # Check the results
        self.assertEqual(len(result), 1)  # Only the list URL
        
        # Verify the correct message was written to output
        self.assertIn("Note: wagtailimages.image has no instances", self.output.getvalue())
        
        # Check that the list URL was added with the correct format and NO INSTANCES note
        mock_format_url_tuple.assert_called_once_with(
            "wagtailimages.image (NO INSTANCES)", None, "list", "http://testserver/admin/images/"
        )

    @patch('wagtail_unveil.helpers.image_helpers.get_image_model')
    @patch('wagtail_unveil.helpers.image_helpers.model_has_instances')
    def test_collect_urls_with_styled_output(self, mock_model_has_instances, mock_get_image_model):
        """Test collect_urls method when output has style method."""
        # Set up mocks
        mock_get_image_model.return_value = self.mock_image_model
        mock_model_has_instances.return_value = False
        
        # Create a mock output object with style.INFO method
        mock_output = Mock()
        mock_output.style = Mock()
        mock_output.style.INFO = lambda x: f"INFO: {x}"
        mock_output.write = Mock()
        
        # Create helper and collect URLs
        helper = ImageHelper(mock_output, self.base_url, self.max_instances)
        helper.collect_urls()
        
        # Check that style.INFO was called correctly
        mock_output.write.assert_called_once_with(mock_output.style.INFO("Note: wagtailimages.image has no instances"))

    @patch('wagtail_unveil.helpers.image_helpers.get_image_model')
    def test_image_urls_calls_collect_urls(self, mock_get_image_model):
        """Test image_urls method calls collect_urls."""
        mock_get_image_model.return_value = self.mock_image_model
        
        helper = ImageHelper(self.output, self.base_url, self.max_instances)
        # Mock the collect_urls method
        helper.collect_urls = Mock(return_value=["url1", "url2"])
        
        result = helper.image_urls()
        
        # Verify collect_urls was called
        helper.collect_urls.assert_called_once()
        self.assertEqual(result, ["url1", "url2"])
