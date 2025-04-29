from django.test import TestCase
from io import StringIO
from unittest.mock import Mock, patch

from wagtail_unveil.helpers.modelviewset_helpers import (
    get_modelviewset_models,
    ModelViewSetHelper,
)


class GetModelViewsetModelsTests(TestCase):
    """Tests for the get_modelviewset_models function."""
    
    @patch('wagtail_unveil.helpers.modelviewset_helpers.ModelViewSetHelper.get_modelviewset_models')
    def test_get_modelviewset_models(self, mock_get_modelviewset_models):
        """Test get_modelviewset_models finds models registered with ModelViewSet."""
        # Create mock models
        mock_model1 = Mock()
        mock_model2 = Mock()
        
        # Set up the mock to return our test models
        mock_get_modelviewset_models.return_value = [mock_model1, mock_model2]
        
        # Call the function
        models = get_modelviewset_models()
        
        # Check we get the expected models
        self.assertEqual(len(models), 2)
        self.assertIn(mock_model1, models)
        self.assertIn(mock_model2, models)
        
        # Verify the helper method was called
        mock_get_modelviewset_models.assert_called_once()

    @patch('wagtail_unveil.helpers.modelviewset_helpers.ModelViewSetHelper.get_modelviewset_models')
    def test_get_modelviewset_models_with_import_error(self, mock_get_modelviewset_models):
        """Test get_modelviewset_models handles import errors gracefully."""
        # Set up the mock to return empty list
        mock_get_modelviewset_models.return_value = []
        
        # Call the function
        models = get_modelviewset_models()
        
        # Check we get empty results
        self.assertEqual(models, [])


class ModelViewSetHelperTests(TestCase):
    """Tests for the ModelViewSetHelper class."""
    
    def setUp(self):
        """Set up common test data."""
        self.output = StringIO()
        
        # Create mock models and instances
        self.mock_model1 = Mock()
        self.mock_model1._meta = Mock()
        self.mock_model1._meta.app_label = "app1"
        self.mock_model1._meta.model_name = "model1"
        
        self.mock_model2 = Mock()
        self.mock_model2._meta = Mock()
        self.mock_model2._meta.app_label = "wagtailcore"
        self.mock_model2._meta.model_name = "locale"
        
        self.mock_instance1 = Mock()
        self.mock_instance1.id = 1
        self.mock_instance1.__str__ = Mock(return_value="Instance 1")
        
        self.mock_instance2 = Mock()
        self.mock_instance2.id = 2
        self.mock_instance2.__str__ = Mock(return_value="Instance 2")
        
        self.modelviewset_models = [self.mock_model1, self.mock_model2]
        self.base_url = "http://testserver"
        self.max_instances = 5

    def test_initialization(self):
        """Test ModelViewSetHelper initialization sets up the correct attributes."""
        helper = ModelViewSetHelper(self.output, self.base_url, self.max_instances)
        self.assertEqual(helper.base, self.base_url.rstrip('/'))
        self.assertEqual(helper.skip_models, ["wagtailcore.locale", "wagtailcore.site"])
        
    def test_get_list_url(self):
        """Test get_list_url returns the correct URL format for different models."""
        helper = ModelViewSetHelper(self.output, self.base_url, self.max_instances)
        
        # Test regular model
        self.assertEqual(
            helper.get_list_url(self.mock_model1), 
            "http://testserver/admin/model1/"
        )
        
        # Test locale model (special case)
        self.assertEqual(
            helper.get_list_url(self.mock_model2), 
            "http://testserver/admin/locales/"
        )
    
    def test_get_edit_url(self):
        """Test get_edit_url returns the correct URL format for different models."""
        helper = ModelViewSetHelper(self.output, self.base_url, self.max_instances)
        
        # Test regular model
        self.assertEqual(
            helper.get_edit_url(self.mock_model1, 1), 
            "http://testserver/admin/model1/1/"
        )
        
        # Test locale model (special case)
        self.assertEqual(
            helper.get_edit_url(self.mock_model2, 1), 
            "http://testserver/admin/locales/1/"
        )
    
    def test_get_delete_url(self):
        """Test get_delete_url returns the correct URL format for different models."""
        helper = ModelViewSetHelper(self.output, self.base_url, self.max_instances)
        
        # Test regular model
        self.assertEqual(
            helper.get_delete_url(self.mock_model1, 1), 
            "http://testserver/admin/model1/1/delete/"
        )
        
        # Test locale model (special case)
        self.assertEqual(
            helper.get_delete_url(self.mock_model2, 1), 
            "http://testserver/admin/locales/1/delete/"
        )

    def test_collect_urls_with_instances(self):
        """Test collect_urls method when there are model instances."""
        # Create a new helper with a clean output buffer
        output = StringIO()
        helper = ModelViewSetHelper(output, self.base_url, self.max_instances)
        
        # Replace the get_modelviewset_models method to return just our test model
        helper.get_modelviewset_models = lambda: [self.mock_model1]
        
        # Clear skip_models to prevent the test model from being skipped
        helper.skip_models = []
        
        # Mock the functions that would normally be called
        with patch('wagtail_unveil.helpers.modelviewset_helpers.model_has_instances', return_value=True), \
             patch('wagtail_unveil.helpers.modelviewset_helpers.get_instance_sample', return_value=[self.mock_instance1]), \
             patch('wagtail_unveil.helpers.modelviewset_helpers.truncate_instance_name', side_effect=lambda x: f"Truncated {x}"):
            
            # Call collect_urls to test
            result = helper.collect_urls()
            
            # Check we have the expected number of URLs (1 list URL + 1 edit URL + 1 delete URL = 3)
            self.assertEqual(len(result), 3)
            
            # Check URL types in the correct order
            url_types = [url[2] for url in result]
            self.assertEqual(url_types, ["list", "edit", "delete"])

    def test_collect_urls_without_instances(self):
        """Test collect_urls method when there are no model instances."""
        # Create a new helper with a clean output buffer
        output = StringIO()
        helper = ModelViewSetHelper(output, self.base_url, self.max_instances)
        
        # Replace the get_modelviewset_models method to return just our test model
        helper.get_modelviewset_models = lambda: [self.mock_model1]
        
        # Clear skip_models to prevent the test model from being skipped
        helper.skip_models = []
        
        # Mock the functions that would normally be called
        with patch('wagtail_unveil.helpers.modelviewset_helpers.model_has_instances', return_value=False):
            # Call collect_urls to test
            result = helper.collect_urls()
            
            # Verify the correct message was written to output
            self.assertIn("Note: app1.model1 has no instances", output.getvalue())
            
            # Check that the NO INSTANCES URL was added with the correct format
            self.assertEqual(len(result), 1)
            no_instances_url = result[0]
            self.assertEqual(no_instances_url[0], "app1.model1 (NO INSTANCES)")
            self.assertEqual(no_instances_url[2], "list")
            self.assertEqual(no_instances_url[3], "http://testserver/admin/model1/")

    @patch('wagtail_unveil.helpers.modelviewset_helpers.get_modelviewset_models')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.model_has_instances')
    def test_collect_urls_with_skip_models(self, mock_model_has_instances, mock_get_modelviewset_models):
        """Test that collect_urls skips models that are in the skip_models list."""
        # Create a mock model that should be skipped
        mock_skip_model = Mock()
        mock_skip_model._meta = Mock()
        mock_skip_model._meta.app_label = "wagtailcore"
        mock_skip_model._meta.model_name = "site"
        
        # Set up the get_modelviewset_models mock to return the skip model
        mock_get_modelviewset_models.return_value = [mock_skip_model]
        
        # Create helper and collect URLs
        helper = ModelViewSetHelper(self.output, self.base_url, self.max_instances)
        result = helper.collect_urls()
        
        # Check the output message indicating the model was skipped
        self.assertIn("Skipping duplicate wagtailcore.site URLs", self.output.getvalue())
        
        # Check that we get no URLs because the model was skipped
        self.assertEqual(len(result), 0)

    def test_collect_urls_with_styled_output(self):
        """Test collect_urls method when output has style method."""
        # Create a mock output object with style.INFO method
        mock_output = Mock()
        mock_output.style = Mock()
        mock_output.style.INFO = lambda x: f"INFO: {x}"
        
        # Create helper and collect URLs
        helper = ModelViewSetHelper(mock_output, self.base_url, self.max_instances)
        
        # Replace the get_modelviewset_models method to return just our test model
        helper.get_modelviewset_models = lambda: [self.mock_model1]
        
        # Clear skip_models to prevent the test model from being skipped
        helper.skip_models = []
        
        # Mock the functions that would normally be called
        with patch('wagtail_unveil.helpers.modelviewset_helpers.model_has_instances', return_value=False):
            # Call collect_urls to test
            helper.collect_urls()
            
            # Check that write was called correctly with the styled output
            mock_output.write.assert_any_call("INFO: Note: app1.model1 has no instances")

    def test_modelviewset_urls_calls_collect_urls(self):
        """Test modelviewset_urls method calls collect_urls."""
        helper = ModelViewSetHelper(self.output, self.base_url, self.max_instances)
        
        # Mock the collect_urls method
        helper.collect_urls = Mock(return_value=["url1", "url2"])
        
        result = helper.modelviewset_urls()
        
        # Verify collect_urls was called
        helper.collect_urls.assert_called_once()
        self.assertEqual(result, ["url1", "url2"])