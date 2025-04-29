from django.test import TestCase
from io import StringIO
from unittest.mock import Mock, patch

from wagtail_unveil.helpers.modelviewset_helpers import (
    get_modelviewset_models,
    ModelViewSetHelper,
)


class GetModelViewsetModelsTests(TestCase):
    """Tests for the get_modelviewset_models function."""
    
    @patch('wagtail_unveil.helpers.modelviewset_helpers.import_module')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.apps')
    def test_get_modelviewset_models(self, mock_apps, mock_import_module):
        """Test get_modelviewset_models finds models registered with ModelViewSet."""
        # Create mock app configs
        mock_app_config1 = Mock()
        mock_app_config1.name = "app1"
        
        mock_app_config2 = Mock()
        mock_app_config2.name = "app2"
        
        mock_apps.get_app_configs.return_value = [mock_app_config1, mock_app_config2]
        
        # Create mock hooks modules with ModelViewSet classes
        mock_hooks_module1 = Mock()
        mock_model1 = Mock()
        mock_modelviewset1 = Mock()
        mock_modelviewset1.__bases__ = ('ModelViewSet',)
        mock_modelviewset1.model = mock_model1
        
        # Add a class that's not a ModelViewSet
        mock_other_class = Mock()
        mock_other_class.__bases__ = ('OtherClass',)
        
        # Add a ModelViewSet with no model
        mock_modelviewset_no_model = Mock()
        mock_modelviewset_no_model.__bases__ = ('ModelViewSet',)
        mock_modelviewset_no_model.model = None
        
        mock_hooks_module1.__dict__ = {
            'ModelViewSet1': mock_modelviewset1,
            'OtherClass': mock_other_class,
            'ModelViewSetNoModel': mock_modelviewset_no_model,
        }
        
        # Create a second hooks module with another ModelViewSet
        mock_hooks_module2 = Mock()
        mock_model2 = Mock()
        mock_modelviewset2 = Mock()
        mock_modelviewset2.__bases__ = ('ModelViewSet',)
        mock_modelviewset2.model = mock_model2
        
        mock_hooks_module2.__dict__ = {
            'ModelViewSet2': mock_modelviewset2,
        }
        
        # Set up import_module to return our mock hooks modules
        def import_module_side_effect(module_path):
            if module_path == "app1.wagtail_hooks":
                return mock_hooks_module1
            elif module_path == "app2.wagtail_hooks":
                return mock_hooks_module2
            raise ImportError(f"No module named '{module_path}'")
        
        mock_import_module.side_effect = import_module_side_effect
        
        # Set up inspect.getmembers for the hooks modules
        with patch('wagtail_unveil.helpers.modelviewset_helpers.inspect.getmembers') as mock_getmembers:
            mock_getmembers.side_effect = [
                [
                    ('ModelViewSet1', mock_modelviewset1), 
                    ('OtherClass', mock_other_class),
                    ('ModelViewSetNoModel', mock_modelviewset_no_model),
                ],
                [
                    ('ModelViewSet2', mock_modelviewset2)
                ],
            ]
            
            with patch('wagtail_unveil.helpers.modelviewset_helpers.inspect.isclass') as mock_isclass:
                mock_isclass.side_effect = lambda obj: obj in [mock_modelviewset1, mock_other_class, mock_modelviewset_no_model, mock_modelviewset2]
                
                # Call the function
                models = get_modelviewset_models()
                
                # Check we get the expected models
                self.assertEqual(len(models), 2)
                self.assertIn(mock_model1, models)
                self.assertIn(mock_model2, models)

    @patch('wagtail_unveil.helpers.modelviewset_helpers.import_module')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.apps')
    def test_get_modelviewset_models_with_import_error(self, mock_apps, mock_import_module):
        """Test get_modelviewset_models handles import errors gracefully."""
        # Create a mock app config
        mock_app_config = Mock()
        mock_app_config.name = "app1"
        mock_apps.get_app_configs.return_value = [mock_app_config]
        
        # Make import_module raise an ImportError
        mock_import_module.side_effect = ImportError("No module named 'app1.wagtail_hooks'")
        
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

    @patch('wagtail_unveil.helpers.modelviewset_helpers.get_modelviewset_models')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.get_instance_sample')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.truncate_instance_name')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.format_url_tuple')
    def test_collect_urls_with_instances(self, mock_format_url_tuple, mock_truncate_instance_name, 
                                       mock_get_instance_sample, mock_model_has_instances, 
                                       mock_get_modelviewset_models):
        """Test collect_urls method when there are model instances."""
        # Set up the get_modelviewset_models mock to return our test models
        mock_get_modelviewset_models.return_value = [self.mock_model1]  # Only include non-skipped model
        
        # Set up the model_has_instances mock to return True
        mock_model_has_instances.return_value = True
        
        # Set up the get_instance_sample mock to return instances
        mock_get_instance_sample.return_value = [self.mock_instance1, self.mock_instance2]
        
        # Set up the truncate_instance_name mock
        mock_truncate_instance_name.side_effect = lambda x: f"Truncated {x}"
        
        # Set up the format_url_tuple mock to return input arguments
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (
            model, instance_name, url_type, url)
        
        # Create helper and collect URLs
        helper = ModelViewSetHelper(self.output, self.base_url, self.max_instances)
        result = helper.collect_urls()
        
        # Check the results - should have list URL, edit URLs, and delete URLs
        # 1 list URL + 2 edit URLs + 2 delete URLs = 5 URLs
        self.assertEqual(len(result), 5)
        
        # Check list URL
        mock_format_url_tuple.assert_any_call(
            "app1.model1", None, "list", "http://testserver/admin/model1/")
        
        # Check edit URLs
        mock_format_url_tuple.assert_any_call(
            "app1.model1", "Truncated Instance 1", "edit", "http://testserver/admin/model1/1/")
        mock_format_url_tuple.assert_any_call(
            "app1.model1", "Truncated Instance 2", "edit", "http://testserver/admin/model1/2/")
        
        # Check delete URLs
        mock_format_url_tuple.assert_any_call(
            "app1.model1", "Truncated Instance 1", "delete", "http://testserver/admin/model1/1/delete/")
        mock_format_url_tuple.assert_any_call(
            "app1.model1", "Truncated Instance 2", "delete", "http://testserver/admin/model1/2/delete/")

    @patch('wagtail_unveil.helpers.modelviewset_helpers.get_modelviewset_models')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.format_url_tuple')
    def test_collect_urls_without_instances(self, mock_format_url_tuple, 
                                         mock_model_has_instances, mock_get_modelviewset_models):
        """Test collect_urls method when there are no model instances."""
        # Set up the get_modelviewset_models mock to return our test models
        mock_get_modelviewset_models.return_value = [self.mock_model1]  # Only include non-skipped model
        
        # Set up the model_has_instances mock to return False
        mock_model_has_instances.return_value = False
        
        # Set up the format_url_tuple mock to return input arguments
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (
            model, instance_name, url_type, url)
        
        # Create helper and collect URLs
        helper = ModelViewSetHelper(self.output, self.base_url, self.max_instances)
        result = helper.collect_urls()
        
        # Check the results - should only have list URL with NO INSTANCES note
        self.assertEqual(len(result), 1)
        
        # Verify the correct message was written to output
        self.assertIn("Note: app1.model1 has no instances", self.output.getvalue())
        
        # Check that the list URL was added with the correct format
        mock_format_url_tuple.assert_called_once_with(
            "app1.model1 (NO INSTANCES)", None, "list", "http://testserver/admin/model1/")

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

    @patch('wagtail_unveil.helpers.modelviewset_helpers.get_modelviewset_models')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.model_has_instances')
    def test_collect_urls_with_styled_output(self, mock_model_has_instances, mock_get_modelviewset_models):
        """Test collect_urls method when output has style method."""
        # Set up the get_modelviewset_models mock to return our test models
        mock_get_modelviewset_models.return_value = [self.mock_model1]
        
        # Set up the model_has_instances mock to return False
        mock_model_has_instances.return_value = False
        
        # Create a mock output object with style.INFO method
        mock_output = Mock()
        mock_output.style = Mock()
        mock_output.style.INFO = lambda x: f"INFO: {x}"
        mock_output.write = Mock()
        
        # Create helper and collect URLs
        helper = ModelViewSetHelper(mock_output, self.base_url, self.max_instances)
        helper.collect_urls()
        
        # Check that style.INFO was called correctly
        mock_output.write.assert_any_call(mock_output.style.INFO("Note: app1.model1 has no instances"))

    def test_modelviewset_urls_calls_collect_urls(self):
        """Test modelviewset_urls method calls collect_urls."""
        helper = ModelViewSetHelper(self.output, self.base_url, self.max_instances)
        
        # Mock the collect_urls method
        helper.collect_urls = Mock(return_value=["url1", "url2"])
        
        result = helper.modelviewset_urls()
        
        # Verify collect_urls was called
        helper.collect_urls.assert_called_once()
        self.assertEqual(result, ["url1", "url2"])