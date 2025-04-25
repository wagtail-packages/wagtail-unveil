from django.test import TestCase
from io import StringIO
from unittest.mock import Mock, patch

from wagtail_unveil.helpers.modeladmin_helpers import (
    get_modeladmin_models,
    get_modeladmin_urls,
)


class GetModeladminModelsTests(TestCase):
    """Tests for the get_modeladmin_models function."""

    @patch('wagtail_unveil.helpers.modeladmin_helpers.apps.get_app_configs')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.import_module')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.inspect.getmembers')
    def test_classic_modeladmin(self, mock_getmembers, mock_import_module, mock_get_app_configs):
        """Test finding models registered with classic wagtail.contrib.modeladmin.options.ModelAdmin."""
        # Set up app configurations
        mock_app_config = Mock()
        mock_app_config.name = 'testapp'
        mock_get_app_configs.return_value = [mock_app_config]
        
        # Set up hook module
        mock_hooks_module = Mock()
        mock_import_module.return_value = mock_hooks_module
        
        # Mock model
        mock_model = Mock()
        
        # Create a mock ModelAdmin class that uses the classic pattern
        mock_modeladmin = Mock()
        mock_modeladmin.model = mock_model
        mock_modeladmin.get_admin_urls_for_registration = Mock()  # Classic ModelAdmin attribute
        mock_modeladmin.base_url_path = 'custom_url_path'
        
        # Set up inspect.getmembers to return our mock ModelAdmin
        mock_getmembers.return_value = [('TestModelAdmin', mock_modeladmin)]
        
        # Call the function
        models, url_paths = get_modeladmin_models()
        
        # Check the results
        self.assertEqual(models, [mock_model])
        self.assertEqual(url_paths, {mock_model: 'custom_url_path'})
        
        # Verify import_module was called with the correct path
        mock_import_module.assert_called_once_with('testapp.wagtail_hooks')

    @patch('wagtail_unveil.helpers.modeladmin_helpers.apps.get_app_configs')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.import_module')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.inspect.getmembers')
    def test_newer_modeladmin(self, mock_getmembers, mock_import_module, mock_get_app_configs):
        """Test finding models registered with newer wagtail_modeladmin.options.ModelAdmin."""
        # Set up app configurations
        mock_app_config = Mock()
        mock_app_config.name = 'testapp'
        mock_get_app_configs.return_value = [mock_app_config]
        
        # Set up hook module
        mock_hooks_module = Mock()
        mock_import_module.return_value = mock_hooks_module
        
        # Mock model
        mock_model = Mock()
        
        # Create a mock ModelAdmin class that uses the newer pattern
        mock_modeladmin = Mock()
        mock_modeladmin.model = mock_model
        mock_modeladmin.get_admin_urls = Mock()  # Newer ModelAdmin attribute
        mock_modeladmin.base_url_path = 'newer_custom_path'
        
        # Set up inspect.getmembers to return our mock ModelAdmin
        mock_getmembers.return_value = [('TestModelAdmin', mock_modeladmin)]
        
        # Call the function
        models, url_paths = get_modeladmin_models()
        
        # Check the results
        self.assertEqual(models, [mock_model])
        self.assertEqual(url_paths, {mock_model: 'newer_custom_path'})

    @patch('wagtail_unveil.helpers.modeladmin_helpers.apps.get_app_configs')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.import_module')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.inspect.getmembers')
    def test_no_base_url_path(self, mock_getmembers, mock_import_module, mock_get_app_configs):
        """Test ModelAdmin without a base_url_path."""
        # Set up app configurations
        mock_app_config = Mock()
        mock_app_config.name = 'testapp'
        mock_get_app_configs.return_value = [mock_app_config]
        
        # Set up hook module
        mock_hooks_module = Mock()
        mock_import_module.return_value = mock_hooks_module
        
        # Mock model
        mock_model = Mock()
        
        # Create a mock ModelAdmin class with no base_url_path
        mock_modeladmin = Mock(spec=['model', 'get_admin_urls_for_registration'])
        mock_modeladmin.model = mock_model
        # base_url_path is not in the spec, so it won't be found
        
        # Set up inspect.getmembers to return our mock ModelAdmin
        mock_getmembers.return_value = [('TestModelAdmin', mock_modeladmin)]
        
        # Call the function
        models, url_paths = get_modeladmin_models()
        
        # Check the results
        self.assertEqual(models, [mock_model])
        self.assertEqual(url_paths, {})  # No URL paths should be found

    @patch('wagtail_unveil.helpers.modeladmin_helpers.apps.get_app_configs')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.import_module')
    def test_import_error(self, mock_import_module, mock_get_app_configs):
        """Test handling of ImportError when trying to import wagtail_hooks."""
        # Set up app configurations
        mock_app_config = Mock()
        mock_app_config.name = 'testapp'
        mock_get_app_configs.return_value = [mock_app_config]
        
        # Simulate ImportError when importing wagtail_hooks
        mock_import_module.side_effect = ImportError("No module named 'testapp.wagtail_hooks'")
        
        # Call the function
        models, url_paths = get_modeladmin_models()
        
        # Check the results - should be empty since we couldn't import any hooks
        self.assertEqual(models, [])
        self.assertEqual(url_paths, {})

    @patch('wagtail_unveil.helpers.modeladmin_helpers.apps.get_app_configs')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.import_module')
    def test_module_not_found_error(self, mock_import_module, mock_get_app_configs):
        """Test handling of ModuleNotFoundError when trying to import wagtail_hooks."""
        # Set up app configurations
        mock_app_config = Mock()
        mock_app_config.name = 'testapp'
        mock_get_app_configs.return_value = [mock_app_config]
        
        # Simulate ModuleNotFoundError when importing wagtail_hooks
        mock_import_module.side_effect = ModuleNotFoundError("No module named 'testapp.wagtail_hooks'")
        
        # Call the function
        models, url_paths = get_modeladmin_models()
        
        # Check the results - should be empty since we couldn't import any hooks
        self.assertEqual(models, [])
        self.assertEqual(url_paths, {})

    @patch('wagtail_unveil.helpers.modeladmin_helpers.apps.get_app_configs')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.import_module')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.inspect.getmembers')
    def test_multiple_modeladmins(self, mock_getmembers, mock_import_module, mock_get_app_configs):
        """Test finding multiple ModelAdmin classes across different apps."""
        # Set up app configurations
        mock_app_config1 = Mock()
        mock_app_config1.name = 'app1'
        mock_app_config2 = Mock()
        mock_app_config2.name = 'app2'
        mock_get_app_configs.return_value = [mock_app_config1, mock_app_config2]
        
        # Mock models
        mock_model1 = Mock()
        mock_model2 = Mock()
        
        # Create mock ModelAdmin classes
        mock_modeladmin1 = Mock()
        mock_modeladmin1.model = mock_model1
        mock_modeladmin1.get_admin_urls_for_registration = Mock()
        mock_modeladmin1.base_url_path = 'custom_path1'
        
        mock_modeladmin2 = Mock()
        mock_modeladmin2.model = mock_model2
        mock_modeladmin2.get_admin_urls = Mock()
        mock_modeladmin2.base_url_path = 'custom_path2'
        
        # Set up import_module to return different hook modules for each app
        mock_hooks_module1 = Mock()
        mock_hooks_module2 = Mock()
        mock_import_module.side_effect = lambda path: {
            'app1.wagtail_hooks': mock_hooks_module1,
            'app2.wagtail_hooks': mock_hooks_module2
        }[path]
        
        # Set up inspect.getmembers to return different ModelAdmin classes for each module
        mock_getmembers.side_effect = lambda module: {
            mock_hooks_module1: [('TestModelAdmin1', mock_modeladmin1)],
            mock_hooks_module2: [('TestModelAdmin2', mock_modeladmin2)]
        }[module]
        
        # Call the function
        models, url_paths = get_modeladmin_models()
        
        # Check the results - should have both models and both URL paths
        self.assertEqual(set(models), {mock_model1, mock_model2})
        self.assertEqual(url_paths, {mock_model1: 'custom_path1', mock_model2: 'custom_path2'})

    @patch('wagtail_unveil.helpers.modeladmin_helpers.apps.get_app_configs')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.import_module')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.inspect.getmembers')
    def test_class_without_model(self, mock_getmembers, mock_import_module, mock_get_app_configs):
        """Test class that has attributes like ModelAdmin but no model attribute."""
        # Set up app configurations
        mock_app_config = Mock()
        mock_app_config.name = 'testapp'
        mock_get_app_configs.return_value = [mock_app_config]
        
        # Set up hook module
        mock_hooks_module = Mock()
        mock_import_module.return_value = mock_hooks_module
        
        # Create a mock class that looks like ModelAdmin but has no model
        mock_class = Mock(spec=['get_admin_urls_for_registration'])
        # No model attribute
        
        # Set up inspect.getmembers to return our mock class
        mock_getmembers.return_value = [('TestClass', mock_class)]
        
        # Call the function
        models, url_paths = get_modeladmin_models()
        
        # Check the results - should be empty since the class has no model
        self.assertEqual(models, [])
        self.assertEqual(url_paths, {})

    @patch('wagtail_unveil.helpers.modeladmin_helpers.apps.get_app_configs')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.import_module')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.inspect.getmembers')
    def test_class_with_none_model(self, mock_getmembers, mock_import_module, mock_get_app_configs):
        """Test ModelAdmin class with model=None."""
        # Set up app configurations
        mock_app_config = Mock()
        mock_app_config.name = 'testapp'
        mock_get_app_configs.return_value = [mock_app_config]
        
        # Set up hook module
        mock_hooks_module = Mock()
        mock_import_module.return_value = mock_hooks_module
        
        # Create a mock ModelAdmin class with model=None
        mock_modeladmin = Mock()
        mock_modeladmin.model = None
        mock_modeladmin.get_admin_urls_for_registration = Mock()
        
        # Set up inspect.getmembers to return our mock ModelAdmin
        mock_getmembers.return_value = [('TestModelAdmin', mock_modeladmin)]
        
        # Call the function
        models, url_paths = get_modeladmin_models()
        
        # Check the results - should be empty since model is None
        self.assertEqual(models, [])
        self.assertEqual(url_paths, {})


class GetModeladminUrlsTests(TestCase):
    """Tests for the get_modeladmin_urls function."""

    def setUp(self):
        self.output = StringIO()
        self.base_url = "http://testserver"
        self.max_instances = 2
        
        # Create mock models
        self.mock_model = Mock()
        self.mock_model._meta = Mock()
        self.mock_model._meta.app_label = "testapp"
        self.mock_model._meta.model_name = "testmodel"

    @patch('wagtail_unveil.helpers.modeladmin_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.get_instance_sample')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.truncate_instance_name')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.format_url_tuple')
    def test_with_instances_default_url(self, mock_format_url_tuple, mock_truncate_instance_name, 
                               mock_get_instance_sample, mock_model_has_instances):
        """Test get_modeladmin_urls when there are instances and using default URL pattern."""
        # Set up mocks
        mock_model_has_instances.return_value = True
        
        mock_instance1 = Mock()
        mock_instance1.id = 1
        mock_instance1.__str__ = lambda self: "Instance 1"
        
        mock_instance2 = Mock()
        mock_instance2.id = 2
        mock_instance2.__str__ = lambda self: "Instance 2"
        
        mock_get_instance_sample.return_value = [mock_instance1, mock_instance2]
        
        mock_truncate_instance_name.side_effect = lambda x: f"Truncated {x}"
        
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (model, url_type, url)
        
        # Empty modeladmin_url_paths dict (using default URLs)
        modeladmin_url_paths = {}
        
        # Call the function
        result = get_modeladmin_urls(
            self.output, [self.mock_model], modeladmin_url_paths, self.base_url, self.max_instances
        )
        
        # Check the results
        self.assertEqual(len(result), 3)  # 1 list + 2 edit URLs
        
        # Check that the list URL was added with the correct format
        mock_format_url_tuple.assert_any_call(
            "testapp.testmodel", None, "list", 
            "http://testserver/admin/modeladmin/testapp/testmodel/"
        )
        
        # Check that edit URLs were added with the correct format
        mock_format_url_tuple.assert_any_call(
            "testapp.testmodel", "Truncated Instance 1", "edit", 
            "http://testserver/admin/modeladmin/testapp/testmodel/edit/1/"
        )
        mock_format_url_tuple.assert_any_call(
            "testapp.testmodel", "Truncated Instance 2", "edit", 
            "http://testserver/admin/modeladmin/testapp/testmodel/edit/2/"
        )

    @patch('wagtail_unveil.helpers.modeladmin_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.get_instance_sample')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.truncate_instance_name')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.format_url_tuple')
    def test_with_instances_custom_url(self, mock_format_url_tuple, mock_truncate_instance_name, 
                              mock_get_instance_sample, mock_model_has_instances):
        """Test get_modeladmin_urls when there are instances and using custom URL pattern."""
        # Set up mocks
        mock_model_has_instances.return_value = True
        
        mock_instance1 = Mock()
        mock_instance1.id = 1
        mock_instance1.__str__ = lambda self: "Instance 1"
        
        mock_instance2 = Mock()
        mock_instance2.id = 2
        mock_instance2.__str__ = lambda self: "Instance 2"
        
        mock_get_instance_sample.return_value = [mock_instance1, mock_instance2]
        
        mock_truncate_instance_name.side_effect = lambda x: f"Truncated {x}"
        
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (model, url_type, url)
        
        # Custom modeladmin_url_paths dict
        modeladmin_url_paths = {self.mock_model: 'custom/path'}
        
        # Call the function
        result = get_modeladmin_urls(
            self.output, [self.mock_model], modeladmin_url_paths, self.base_url, self.max_instances
        )
        
        # Check the results
        self.assertEqual(len(result), 3)  # 1 list + 2 edit URLs
        
        # Check that the list URL was added with the correct format
        mock_format_url_tuple.assert_any_call(
            "testapp.testmodel", None, "list", 
            "http://testserver/admin/custom/path/"
        )
        
        # Check that edit URLs were added with the correct format
        mock_format_url_tuple.assert_any_call(
            "testapp.testmodel", "Truncated Instance 1", "edit", 
            "http://testserver/admin/custom/path/edit/1/"
        )
        mock_format_url_tuple.assert_any_call(
            "testapp.testmodel", "Truncated Instance 2", "edit", 
            "http://testserver/admin/custom/path/edit/2/"
        )

    @patch('wagtail_unveil.helpers.modeladmin_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.format_url_tuple')
    def test_without_instances(self, mock_format_url_tuple, mock_model_has_instances):
        """Test get_modeladmin_urls when there are no instances."""
        # Set up mocks
        mock_model_has_instances.return_value = False
        
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (model, url_type, url)
        
        # Empty modeladmin_url_paths dict (using default URLs)
        modeladmin_url_paths = {}
        
        # Call the function
        result = get_modeladmin_urls(
            self.output, [self.mock_model], modeladmin_url_paths, self.base_url, self.max_instances
        )
        
        # Check the results
        self.assertEqual(len(result), 1)  # Only the list URL
        
        # Verify the correct message was written to output
        self.assertIn("Note: testapp.testmodel has no instances", self.output.getvalue())
        
        # Check that the list URL was added with the correct format and NO INSTANCES note
        mock_format_url_tuple.assert_called_once_with(
            "testapp.testmodel (NO INSTANCES)", None, "list", 
            "http://testserver/admin/modeladmin/testapp/testmodel/"
        )

    @patch('wagtail_unveil.helpers.modeladmin_helpers.model_has_instances')
    def test_with_output_having_style(self, mock_model_has_instances):
        """Test get_modeladmin_urls when output has style method."""
        # Set up mocks
        mock_model_has_instances.return_value = False
        
        # Create a mock output object with style.INFO method
        mock_output = Mock()
        mock_output.style = Mock()
        mock_output.style.INFO = lambda x: f"INFO: {x}"
        mock_output.write = Mock()
        
        # Empty modeladmin_url_paths dict
        modeladmin_url_paths = {}
        
        # Call the function
        get_modeladmin_urls(
            mock_output, [self.mock_model], modeladmin_url_paths, self.base_url, self.max_instances
        )
        
        # Check that style.INFO was called correctly
        mock_output.write.assert_called_once_with(mock_output.style.INFO("Note: testapp.testmodel has no instances"))

    @patch('wagtail_unveil.helpers.modeladmin_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.format_url_tuple')
    def test_with_trailing_slash_in_base_url(self, mock_format_url_tuple, mock_model_has_instances):
        """Test get_modeladmin_urls when base_url has a trailing slash."""
        # Set up mocks
        mock_model_has_instances.return_value = False
        
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (model, url_type, url)
        
        # Empty modeladmin_url_paths dict
        modeladmin_url_paths = {}
        
        # Base URL with trailing slash
        base_url_with_slash = "http://testserver/"
        
        # Call the function
        get_modeladmin_urls(
            self.output, [self.mock_model], modeladmin_url_paths, base_url_with_slash, self.max_instances
        )
        
        # Check that the trailing slash was removed to avoid double slashes
        mock_format_url_tuple.assert_called_once_with(
            "testapp.testmodel (NO INSTANCES)", None, "list", 
            "http://testserver/admin/modeladmin/testapp/testmodel/"
        )

    def test_empty_models_list(self):
        """Test get_modeladmin_urls with an empty models list."""
        # Call the function with an empty models list
        result = get_modeladmin_urls(
            self.output, [], {}, self.base_url, self.max_instances
        )
        
        # Check the results
        self.assertEqual(result, [])  # Should return an empty list

    @patch('wagtail_unveil.helpers.modeladmin_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.format_url_tuple')
    def test_multiple_models(self, mock_format_url_tuple, mock_model_has_instances):
        """Test get_modeladmin_urls with multiple models."""
        # Set up mocks
        mock_model_has_instances.return_value = False
        
        mock_format_url_tuple.side_effect = lambda model, instance_name, url_type, url: (model, url_type, url)
        
        # Create a second mock model
        mock_model2 = Mock()
        mock_model2._meta = Mock()
        mock_model2._meta.app_label = "testapp"
        mock_model2._meta.model_name = "secondmodel"
        
        # Empty modeladmin_url_paths dict
        modeladmin_url_paths = {}
        
        # Call the function with multiple models
        result = get_modeladmin_urls(
            self.output, [self.mock_model, mock_model2], modeladmin_url_paths, self.base_url, self.max_instances
        )
        
        # Check the results
        self.assertEqual(len(result), 2)  # Should have a list URL for each model
        
        # Verify both models have URLs with the correct format
        mock_format_url_tuple.assert_any_call(
            "testapp.testmodel (NO INSTANCES)", None, "list", 
            "http://testserver/admin/modeladmin/testapp/testmodel/"
        )
        mock_format_url_tuple.assert_any_call(
            "testapp.secondmodel (NO INSTANCES)", None, "list", 
            "http://testserver/admin/modeladmin/testapp/secondmodel/"
        )