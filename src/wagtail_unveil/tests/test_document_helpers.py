from django.test import TestCase
from io import StringIO
from unittest.mock import Mock, patch


from wagtail_unveil.helpers.document_helpers import DocumentHelper


class DocumentHelperTests(TestCase):
    """Tests for the DocumentHelper class."""
    
    def setUp(self):
        self.output = StringIO()
        self.base_url = "http://testserver"
        self.max_instances = 2
        
        # Create a mock Document model
        self.mock_document_model = Mock()
        self.mock_document_model._meta.app_label = "wagtaildocs"
        self.mock_document_model._meta.model_name = "document"

    @patch('wagtail_unveil.helpers.document_helpers.get_document_model')
    def test_initialization(self, mock_get_document_model):
        """Test DocumentHelper initialization sets up the correct attributes."""
        mock_get_document_model.return_value = self.mock_document_model
        
        helper = DocumentHelper(self.output, self.base_url, self.max_instances)
        
        self.assertEqual(helper.base, self.base_url.rstrip('/'))
        self.assertEqual(helper.document_model, self.mock_document_model)
        self.assertEqual(helper.model_name, "wagtaildocs.document")
        
    @patch('wagtail_unveil.helpers.document_helpers.get_document_model')
    def test_url_methods(self, mock_get_document_model):
        """Test URL generation methods return correct URLs."""
        mock_get_document_model.return_value = self.mock_document_model
        
        helper = DocumentHelper(self.output, self.base_url, self.max_instances)
        
        self.assertEqual(helper.get_list_url(), "http://testserver/admin/documents/")
        self.assertEqual(helper.get_edit_url(123), "http://testserver/admin/documents/edit/123/")
        self.assertEqual(helper.get_delete_url(456), "http://testserver/admin/documents/delete/456/")

    @patch('wagtail_unveil.helpers.document_helpers.get_document_model')
    @patch('wagtail_unveil.helpers.document_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.document_helpers.get_instance_sample')
    @patch('wagtail_unveil.helpers.document_helpers.truncate_instance_name')
    def test_collect_urls_with_instances(self, mock_truncate_instance_name, 
                                       mock_get_instance_sample, mock_model_has_instances, mock_get_document_model):
        """Test collect_urls method when there are document instances."""
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
        
        # Create helper and collect URLs, with proper method mocks
        helper = DocumentHelper(self.output, self.base_url, self.max_instances)
        helper.add_list_url = Mock()
        helper.add_edit_url = Mock()
        helper.add_delete_url = Mock()
        
        helper.collect_urls()
        
        # Check that the helper methods were called correctly
        helper.add_list_url.assert_called_once_with("wagtaildocs.document", "http://testserver/admin/documents/")
        
        # Check that edit URLs were added with the correct format
        helper.add_edit_url.assert_any_call(
            "wagtaildocs.document", "Truncated Document 1", "http://testserver/admin/documents/edit/1/"
        )
        helper.add_edit_url.assert_any_call(
            "wagtaildocs.document", "Truncated Document 2", "http://testserver/admin/documents/edit/2/"
        )
        
        # Check that delete URLs were added with the correct format
        helper.add_delete_url.assert_any_call(
            "wagtaildocs.document", "Truncated Document 1", "http://testserver/admin/documents/delete/1/"
        )
        helper.add_delete_url.assert_any_call(
            "wagtaildocs.document", "Truncated Document 2", "http://testserver/admin/documents/delete/2/"
        )

    @patch('wagtail_unveil.helpers.document_helpers.get_document_model')
    @patch('wagtail_unveil.helpers.document_helpers.model_has_instances')
    def test_collect_urls_without_instances(self, mock_model_has_instances, mock_get_document_model):
        """Test collect_urls method when there are no document instances."""
        # Set up mocks
        mock_get_document_model.return_value = self.mock_document_model
        mock_model_has_instances.return_value = False
        
        # Create helper and collect URLs, with proper method mocks
        helper = DocumentHelper(self.output, self.base_url, self.max_instances)
        helper.write_no_instances_message = Mock()
        helper.add_url_for_model_with_no_instances = Mock()
        
        helper.collect_urls()
        
        # Verify write_no_instances_message was called
        helper.write_no_instances_message.assert_called_once_with("wagtaildocs.document")
        
        # Check that add_url_for_model_with_no_instances was called with the correct arguments
        helper.add_url_for_model_with_no_instances.assert_called_once_with(
            "wagtaildocs.document", "http://testserver/admin/documents/"
        )

    @patch('wagtail_unveil.helpers.document_helpers.get_document_model')
    @patch('wagtail_unveil.helpers.document_helpers.model_has_instances')
    def test_collect_urls_with_styled_output(self, mock_model_has_instances, mock_get_document_model):
        """Test collect_urls method when output has style method."""
        # Set up mocks
        mock_get_document_model.return_value = self.mock_document_model
        mock_model_has_instances.return_value = False
        
        # Create a mock output object with style.INFO method
        mock_output = Mock()
        mock_output.style = Mock()
        mock_output.style.INFO = lambda x: f"INFO: {x}"
        mock_output.write = Mock()
        
        # Create helper and collect URLs
        helper = DocumentHelper(mock_output, self.base_url, self.max_instances)
        helper.add_url_for_model_with_no_instances = Mock()
        helper.collect_urls()
        
        # Check that style.INFO was called correctly
        mock_output.write.assert_called_once_with(mock_output.style.INFO("Note: wagtaildocs.document has no instances"))

    @patch('wagtail_unveil.helpers.document_helpers.get_document_model')
    def test_document_urls_calls_collect_urls(self, mock_get_document_model):
        """Test document_urls method calls collect_urls."""
        mock_get_document_model.return_value = self.mock_document_model
        
        helper = DocumentHelper(self.output, self.base_url, self.max_instances)
        # Mock the collect_urls method
        helper.collect_urls = Mock(return_value=["url1", "url2"])
        
        result = helper.document_urls()
        
        # Verify collect_urls was called
        helper.collect_urls.assert_called_once()
        self.assertEqual(result, ["url1", "url2"])