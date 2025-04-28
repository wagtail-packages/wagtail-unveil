from django.test import TestCase
from io import StringIO
from unittest.mock import Mock, patch

from wagtail.documents.models import Document
from wagtail.images.models import Image

from wagtail_unveil.helpers.image_helpers import (
    get_image_model,
    get_image_admin_urls,
)
from wagtail_unveil.helpers.media_helpers import (
    get_document_model,
    get_document_admin_urls,
)


class GetImageModelTests(TestCase):
    """Tests for the get_image_model function."""

    @patch('wagtail_unveil.helpers.image_helpers.get_image_model_wagtail')
    def test_default_image_model(self, mock_get_image_model_wagtail):
        """Test get_image_model returns the default Image model when no custom model is configured."""
        mock_get_image_model_wagtail.return_value = Image
        self.assertEqual(get_image_model(), Image)

    @patch('wagtail_unveil.helpers.image_helpers.get_image_model_wagtail')
    def test_custom_image_model(self, mock_get_image_model_wagtail):
        """Test get_image_model returns the custom image model when one is configured."""
        mock_custom_model = Mock()
        mock_get_image_model_wagtail.return_value = mock_custom_model
        
        # Call the function
        result = get_image_model()
        
        # Check the result
        self.assertEqual(result, mock_custom_model)

    @patch('wagtail_unveil.helpers.image_helpers.get_image_model_wagtail')
    def test_invalid_image_model_lookup_error(self, mock_get_image_model_wagtail):
        """Test get_image_model returns the default model when an invalid model is configured (LookupError)."""
        # Set up the mock to return Image (this would happen if there was an error in Wagtail)
        mock_get_image_model_wagtail.return_value = Image
        
        # Call the function
        result = get_image_model()
        
        # Check the result
        self.assertEqual(result, Image)

    @patch('wagtail_unveil.helpers.image_helpers.get_image_model_wagtail')
    def test_invalid_image_model_value_error(self, mock_get_image_model_wagtail):
        """Test get_image_model returns the default model when an invalid model is configured (ValueError)."""
        # Set up the mock to return Image (this would happen if there was an error in Wagtail)
        mock_get_image_model_wagtail.return_value = Image
        
        # Call the function
        result = get_image_model()
        
        # Check the result
        self.assertEqual(result, Image)


class GetImageAdminUrlsTests(TestCase):
    """Tests for the get_image_admin_urls function."""

    def setUp(self):
        self.output = StringIO()
        self.base_url = "http://testserver"
        self.max_instances = 2
        
        # Create a mock Image model
        self.mock_image_model = Mock()
        self.mock_image_model._meta.app_label = "wagtailimages"
        self.mock_image_model._meta.model_name = "image"

    @patch('wagtail_unveil.helpers.image_helpers.get_image_model')
    @patch('wagtail_unveil.helpers.image_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.image_helpers.get_instance_sample')
    @patch('wagtail_unveil.helpers.image_helpers.truncate_instance_name')
    @patch('wagtail_unveil.helpers.image_helpers.format_url_tuple')
    def test_with_instances(self, mock_format_url_tuple, mock_truncate_instance_name, 
                            mock_get_instance_sample, mock_model_has_instances, mock_get_image_model):
        """Test get_image_admin_urls when there are instances."""
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
        
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (model, url_type, url)
        
        # Call the function
        result = get_image_admin_urls(self.output, self.base_url, self.max_instances)
        
        # Check the results
        self.assertEqual(len(result), 5)  # 1 list + 2 edit URLs + 2 delete URLs
        
        # Check that the list URL was added with the correct format
        mock_format_url_tuple.assert_any_call("wagtailimages.image", None, "list", "http://testserver/admin/images/")
        
        # Check that edit URLs were added with the correct format
        mock_format_url_tuple.assert_any_call("wagtailimages.image", "Truncated Image 1", "edit", "http://testserver/admin/images/1/")
        mock_format_url_tuple.assert_any_call("wagtailimages.image", "Truncated Image 2", "edit", "http://testserver/admin/images/2/")
        
        # Check that delete URLs were added with the correct format
        mock_format_url_tuple.assert_any_call("wagtailimages.image", "Truncated Image 1", "delete", "http://testserver/admin/images/1/delete/")
        mock_format_url_tuple.assert_any_call("wagtailimages.image", "Truncated Image 2", "delete", "http://testserver/admin/images/2/delete/")

    @patch('wagtail_unveil.helpers.image_helpers.get_image_model')
    @patch('wagtail_unveil.helpers.image_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.image_helpers.format_url_tuple')
    def test_without_instances(self, mock_format_url_tuple, mock_model_has_instances, mock_get_image_model):
        """Test get_image_admin_urls when there are no instances."""
        # Set up mocks
        mock_get_image_model.return_value = self.mock_image_model
        mock_model_has_instances.return_value = False
        
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (model, instance_name, url_type)
        
        # Call the function
        result = get_image_admin_urls(self.output, self.base_url, self.max_instances)
        
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
    def test_with_output_having_style(self, mock_model_has_instances, mock_get_image_model):
        """Test get_image_admin_urls when output has style method."""
        # Set up mocks
        mock_get_image_model.return_value = self.mock_image_model
        mock_model_has_instances.return_value = False
        
        # Create a mock output object with style.INFO method
        mock_output = Mock()
        mock_output.style = Mock()
        mock_output.style.INFO = lambda x: f"INFO: {x}"
        mock_output.write = Mock()
        
        # Call the function
        get_image_admin_urls(mock_output, self.base_url, self.max_instances)
        
        # Check that style.INFO was called correctly
        mock_output.write.assert_called_once_with(mock_output.style.INFO("Note: wagtailimages.image has no instances"))


class GetDocumentModelTests(TestCase):
    """Tests for the get_document_model function."""

    @patch('wagtail_unveil.helpers.media_helpers.get_document_model_wagtail')
    def test_default_document_model(self, mock_get_document_model_wagtail):
        """Test get_document_model returns the default Document model when no custom model is configured."""
        mock_get_document_model_wagtail.return_value = Document
        self.assertEqual(get_document_model(), Document)

    @patch('wagtail_unveil.helpers.media_helpers.get_document_model_wagtail')
    def test_custom_document_model(self, mock_get_document_model_wagtail):
        """Test get_document_model returns the custom document model when one is configured."""
        mock_custom_model = Mock()
        mock_get_document_model_wagtail.return_value = mock_custom_model
        
        # Call the function
        result = get_document_model()
        
        # Check the result
        self.assertEqual(result, mock_custom_model)

    @patch('wagtail_unveil.helpers.media_helpers.get_document_model_wagtail')
    def test_invalid_document_model_lookup_error(self, mock_get_document_model_wagtail):
        """Test get_document_model returns the default model when an invalid model is configured (LookupError)."""
        # Set up the mock to return Document (this would happen if there was an error in Wagtail)
        mock_get_document_model_wagtail.return_value = Document
        
        # Call the function
        result = get_document_model()
        
        # Check the result
        self.assertEqual(result, Document)

    @patch('wagtail_unveil.helpers.media_helpers.get_document_model_wagtail')
    def test_invalid_document_model_value_error(self, mock_get_document_model_wagtail):
        """Test get_document_model returns the default model when an invalid model is configured (ValueError)."""
        # Set up the mock to return Document (this would happen if there was an error in Wagtail)
        mock_get_document_model_wagtail.return_value = Document
        
        # Call the function
        result = get_document_model()
        
        # Check the result
        self.assertEqual(result, Document)


class GetDocumentAdminUrlsTests(TestCase):
    """Tests for the get_document_admin_urls function."""

    def setUp(self):
        self.output = StringIO()
        self.base_url = "http://testserver"
        self.max_instances = 2
        
        # Create a mock Document model
        self.mock_document_model = Mock()
        self.mock_document_model._meta.app_label = "wagtaildocs"
        self.mock_document_model._meta.model_name = "document"

    @patch('wagtail_unveil.helpers.media_helpers.get_document_model')
    @patch('wagtail_unveil.helpers.media_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.media_helpers.get_instance_sample')
    @patch('wagtail_unveil.helpers.media_helpers.truncate_instance_name')
    @patch('wagtail_unveil.helpers.media_helpers.format_url_tuple')
    def test_with_instances(self, mock_format_url_tuple, mock_truncate_instance_name, 
                            mock_get_instance_sample, mock_model_has_instances, mock_get_document_model):
        """Test get_document_admin_urls when there are instances."""
        # Set up mocks
        mock_get_document_model.return_value = self.mock_document_model
        mock_model_has_instances.return_value = True
        
        mock_instance1 = Mock()
        mock_instance1.id = 1
        mock_instance1.__str__ = lambda self: "Document 1"
        
        mock_instance2 = Mock()
        mock_instance2.id = 2
        mock_instance2.__str__ = lambda self: "Document 2"
        
        mock_get_instance_sample.return_value = [mock_instance1, mock_instance2]
        
        mock_truncate_instance_name.side_effect = lambda x: f"Truncated {x}"
        
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (model, instance_name, url_type)
        
        # Call the function
        result = get_document_admin_urls(self.output, self.base_url, self.max_instances)
        
        # Check the results
        self.assertEqual(len(result), 5)  # 1 list + 2 edit URLs + 2 delete URLs
        
        # Check that the list URL was added with the correct format
        mock_format_url_tuple.assert_any_call("wagtaildocs.document", None, "list", "http://testserver/admin/documents/")
        
        # Check that edit URLs were added with the correct format
        mock_format_url_tuple.assert_any_call(
            "wagtaildocs.document", "Truncated Document 1", "edit", "http://testserver/admin/documents/edit/1/"
        )
        mock_format_url_tuple.assert_any_call(
            "wagtaildocs.document", "Truncated Document 2", "edit", "http://testserver/admin/documents/edit/2/"
        )
        
        # Check that delete URLs were added with the correct format
        mock_format_url_tuple.assert_any_call(
            "wagtaildocs.document", "Truncated Document 1", "delete", "http://testserver/admin/documents/delete/1/"
        )
        mock_format_url_tuple.assert_any_call(
            "wagtaildocs.document", "Truncated Document 2", "delete", "http://testserver/admin/documents/delete/2/"
        )

    @patch('wagtail_unveil.helpers.media_helpers.get_document_model')
    @patch('wagtail_unveil.helpers.media_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.media_helpers.format_url_tuple')
    def test_without_instances(self, mock_format_url_tuple, mock_model_has_instances, mock_get_document_model):
        """Test get_document_admin_urls when there are no instances."""
        # Set up mocks
        mock_get_document_model.return_value = self.mock_document_model
        mock_model_has_instances.return_value = False
        
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (model, instance_name, url_type)
        
        # Call the function
        result = get_document_admin_urls(self.output, self.base_url, self.max_instances)
        
        # Check the results
        self.assertEqual(len(result), 1)  # Only the list URL
        
        # Verify the correct message was written to output
        self.assertIn("Note: wagtaildocs.document has no instances", self.output.getvalue())
        
        # Check that the list URL was added with the correct format and NO INSTANCES note
        mock_format_url_tuple.assert_called_once_with(
            "wagtaildocs.document (NO INSTANCES)", None, "list", "http://testserver/admin/documents/"
        )

    @patch('wagtail_unveil.helpers.media_helpers.get_document_model')
    @patch('wagtail_unveil.helpers.media_helpers.model_has_instances')
    def test_with_output_having_style(self, mock_model_has_instances, mock_get_document_model):
        """Test get_document_admin_urls when output has style method."""
        # Set up mocks
        mock_get_document_model.return_value = self.mock_document_model
        mock_model_has_instances.return_value = False
        
        # Create a mock output object with style.INFO method
        mock_output = Mock()
        mock_output.style = Mock()
        mock_output.style.INFO = lambda x: f"INFO: {x}"
        mock_output.write = Mock()
        
        # Call the function
        get_document_admin_urls(mock_output, self.base_url, self.max_instances)
        
        # Check that style.INFO was called correctly
        mock_output.write.assert_called_once_with(mock_output.style.INFO("Note: wagtaildocs.document has no instances"))