from django.test import TestCase
from io import StringIO
from unittest.mock import Mock, patch

from wagtail_unveil.helpers.modeladmin_helpers import (
    get_modeladmin_models,
    ModelAdminHelper,
)


class ModelAdminHelperTests(TestCase):
    """Tests for the ModelAdminHelper class."""
    
    def setUp(self):
        """Set up test environment."""
        self.output = StringIO()
        self.base_url = "http://testserver"
        self.max_instances = 2
        
        # Create mock model
        self.mock_model = Mock()
        self.mock_model._meta.app_label = "testapp"
        self.mock_model._meta.model_name = "testmodel"
        
        # Create mock instances
        self.mock_instance1 = Mock()
        self.mock_instance1.id = 1
        self.mock_instance1.__str__ = Mock(return_value="Test Instance 1")
        
        self.mock_instance2 = Mock()
        self.mock_instance2.id = 2
        self.mock_instance2.__str__ = Mock(return_value="Test Instance 2")

    def test_initialization(self):
        """Test ModelAdminHelper initialization sets up the correct attributes."""
        helper = ModelAdminHelper(self.output, self.base_url, self.max_instances)
        self.assertEqual(helper.output, self.output)
        self.assertEqual(helper.base, "http://testserver")
        self.assertEqual(helper.max_instances, self.max_instances)
        self.assertEqual(helper.urls, [])
    
    def test_get_list_url_default(self):
        """Test get_list_url returns correct URL with default path."""
        helper = ModelAdminHelper(self.output, self.base_url, self.max_instances)
        url = helper.get_list_url(self.mock_model)
        self.assertEqual(url, "http://testserver/admin/modeladmin/testapp/testmodel/")
    
    def test_get_list_url_custom_path(self):
        """Test get_list_url returns correct URL with custom path."""
        helper = ModelAdminHelper(self.output, self.base_url, self.max_instances)
        url = helper.get_list_url(self.mock_model, custom_url_path="custom/path")
        self.assertEqual(url, "http://testserver/admin/custom/path/")
    
    def test_get_edit_url_default(self):
        """Test get_edit_url returns correct URL with default path."""
        helper = ModelAdminHelper(self.output, self.base_url, self.max_instances)
        url = helper.get_edit_url(self.mock_model, 123)
        self.assertEqual(url, "http://testserver/admin/modeladmin/testapp/testmodel/edit/123/")
    
    def test_get_edit_url_custom_path(self):
        """Test get_edit_url returns correct URL with custom path."""
        helper = ModelAdminHelper(self.output, self.base_url, self.max_instances)
        url = helper.get_edit_url(self.mock_model, 123, custom_url_path="custom/path")
        self.assertEqual(url, "http://testserver/admin/custom/path/edit/123/")
    
    def test_get_delete_url_default(self):
        """Test get_delete_url returns correct URL with default path."""
        helper = ModelAdminHelper(self.output, self.base_url, self.max_instances)
        url = helper.get_delete_url(self.mock_model, 123)
        self.assertEqual(url, "http://testserver/admin/modeladmin/testapp/testmodel/delete/123/")
    
    def test_get_delete_url_custom_path(self):
        """Test get_delete_url returns correct URL with custom path."""
        helper = ModelAdminHelper(self.output, self.base_url, self.max_instances)
        url = helper.get_delete_url(self.mock_model, 123, custom_url_path="custom/path")
        self.assertEqual(url, "http://testserver/admin/custom/path/delete/123/")

    @patch('wagtail_unveil.helpers.modeladmin_helpers.import_module')
    def test_get_modeladmin_models(self, mock_import_module):
        """Test get_modeladmin_models returns models registered with ModelAdmin."""
        # Set up mock app configs
        mock_app_config1 = Mock()
        mock_app_config1.name = "app1"
        
        mock_app_config2 = Mock()
        mock_app_config2.name = "app2"
        
        # Create mock hooks modules
        mock_hooks_module1 = Mock()
        mock_hooks_module2 = Mock()
        
        # Create mock ModelAdmin instances
        mock_modeladmin1 = Mock()
        mock_modeladmin1.model = self.mock_model
        mock_modeladmin1.get_admin_urls_for_registration = Mock()  # Classic ModelAdmin
        
        mock_modeladmin2 = Mock()
        mock_modeladmin2.model = Mock()
        mock_modeladmin2.get_admin_urls = Mock()  # Newer ModelAdmin
        
        # Set up the import_module mock to return our hooks modules
        def side_effect(module_path):
            if module_path == "app1.wagtail_hooks":
                return mock_hooks_module1
            elif module_path == "app2.wagtail_hooks":
                return mock_hooks_module2
            raise ImportError(f"No module named '{module_path}'")
        
        mock_import_module.side_effect = side_effect
        
        # Set up inspect.getmembers for each hooks module
        mock_hooks_module1.__dict__ = {"modeladmin1": mock_modeladmin1}
        mock_hooks_module2.__dict__ = {"modeladmin2": mock_modeladmin2}
        
        with patch('wagtail_unveil.helpers.modeladmin_helpers.apps') as mock_apps, \
             patch('wagtail_unveil.helpers.modeladmin_helpers.inspect') as mock_inspect:
            
            # Configure mock_apps
            mock_apps.get_app_configs.return_value = [mock_app_config1, mock_app_config2]
            
            # Configure mock_inspect
            mock_inspect.getmembers.side_effect = lambda obj: [
                ("modeladmin1", mock_modeladmin1) if obj == mock_hooks_module1 else
                ("modeladmin2", mock_modeladmin2)
            ]
            
            # Call method and verify results
            helper = ModelAdminHelper(self.output, self.base_url, self.max_instances)
            result = helper.get_modeladmin_models()
            
            self.assertEqual(len(result), 2)
            self.assertIn(self.mock_model, result)
            self.assertIn(mock_modeladmin2.model, result)

    @patch('wagtail_unveil.helpers.modeladmin_helpers.import_module')
    def test_get_modeladmin_url_paths(self, mock_import_module):
        """Test get_modeladmin_url_paths returns custom paths for models."""
        # Set up mock app configs
        mock_app_config = Mock()
        mock_app_config.name = "app1"
        
        # Create mock hooks module
        mock_hooks_module = Mock()
        
        # Create mock ModelAdmin instance with custom base_url_path
        mock_modeladmin = Mock()
        mock_modeladmin.model = self.mock_model
        mock_modeladmin.base_url_path = "custom/model/path"
        
        # Set up the import_module mock
        mock_import_module.return_value = mock_hooks_module
        
        with patch('wagtail_unveil.helpers.modeladmin_helpers.apps') as mock_apps, \
             patch('wagtail_unveil.helpers.modeladmin_helpers.inspect') as mock_inspect:
            
            # Configure mock_apps
            mock_apps.get_app_configs.return_value = [mock_app_config]
            
            # Configure mock_inspect
            mock_inspect.getmembers.return_value = [("modeladmin", mock_modeladmin)]
            
            # Call method and verify results
            helper = ModelAdminHelper(self.output, self.base_url, self.max_instances)
            result = helper.get_modeladmin_url_paths()
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[self.mock_model], "custom/model/path")

    @patch('wagtail_unveil.helpers.modeladmin_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.get_instance_sample')
    @patch('wagtail_unveil.helpers.modeladmin_helpers.truncate_instance_name')
    def test_collect_urls_with_instances(self, mock_truncate_instance_name,
                                      mock_get_instance_sample, mock_model_has_instances):
        """Test collect_urls method when models have instances."""
        helper = ModelAdminHelper(self.output, self.base_url, self.max_instances)
        
        # Mock methods used by collect_urls
        helper.get_modeladmin_models = Mock(return_value=[self.mock_model])
        helper.get_modeladmin_url_paths = Mock(return_value={})
        
        # Also mock the helper methods that add URLs
        helper.add_list_url = Mock()
        helper.add_edit_url = Mock()
        helper.add_delete_url = Mock()
        
        # Configure other mocks
        mock_model_has_instances.return_value = True
        mock_get_instance_sample.return_value = [self.mock_instance1, self.mock_instance2]
        mock_truncate_instance_name.side_effect = lambda x: f"Truncated {x}"
        
        # Call collect_urls and check results
        helper.collect_urls()
        
        # Verify add_list_url was called correctly
        helper.add_list_url.assert_called_once_with(
            "testapp.testmodel", 
            "http://testserver/admin/modeladmin/testapp/testmodel/"
        )
        
        # Check edit URLs
        helper.add_edit_url.assert_any_call(
            "testapp.testmodel", "Truncated Test Instance 1",
            "http://testserver/admin/modeladmin/testapp/testmodel/edit/1/"
        )
        helper.add_edit_url.assert_any_call(
            "testapp.testmodel", "Truncated Test Instance 2",
            "http://testserver/admin/modeladmin/testapp/testmodel/edit/2/"
        )
        
        # Check delete URLs
        helper.add_delete_url.assert_any_call(
            "testapp.testmodel", "Truncated Test Instance 1",
            "http://testserver/admin/modeladmin/testapp/testmodel/delete/1/"
        )
        helper.add_delete_url.assert_any_call(
            "testapp.testmodel", "Truncated Test Instance 2",
            "http://testserver/admin/modeladmin/testapp/testmodel/delete/2/"
        )

    @patch('wagtail_unveil.helpers.modeladmin_helpers.model_has_instances')
    def test_collect_urls_without_instances(self, mock_model_has_instances):
        """Test collect_urls method when models have no instances."""
        helper = ModelAdminHelper(self.output, self.base_url, self.max_instances)
        
        # Mock methods used by collect_urls
        helper.get_modeladmin_models = Mock(return_value=[self.mock_model])
        helper.get_modeladmin_url_paths = Mock(return_value={})
        
        # Also mock the helper method
        helper.write_no_instances_message = Mock()
        helper.add_url_for_model_with_no_instances = Mock()
        
        # Configure other mocks
        mock_model_has_instances.return_value = False
        
        # Call collect_urls and check results
        helper.collect_urls()
        
        # Check that the appropriate methods were called
        helper.write_no_instances_message.assert_called_once_with("testapp.testmodel")
        helper.add_url_for_model_with_no_instances.assert_called_once_with(
            "testapp.testmodel", 
            "http://testserver/admin/modeladmin/testapp/testmodel/"
        )

    @patch('wagtail_unveil.helpers.modeladmin_helpers.model_has_instances')
    def test_collect_urls_with_styled_output(self, mock_model_has_instances):
        """Test collect_urls method when output has style method."""
        # Create a mock output with style
        mock_output = Mock()
        mock_output.style = Mock()
        mock_output.style.INFO = lambda x: f"INFO: {x}"
        mock_output.write = Mock()
        
        helper = ModelAdminHelper(mock_output, self.base_url, self.max_instances)
        
        # Mock methods used by collect_urls
        helper.get_modeladmin_models = Mock(return_value=[self.mock_model])
        helper.get_modeladmin_url_paths = Mock(return_value={})
        
        # Configure other mocks
        mock_model_has_instances.return_value = False
        
        # Call collect_urls
        helper.collect_urls()
        
        # Check that style.INFO was used for the message
        mock_output.write.assert_called_once_with(
            mock_output.style.INFO("Note: testapp.testmodel has no instances")
        )

    def test_collect_urls_with_custom_url_path(self):
        """Test collect_urls with custom URL paths."""
        helper = ModelAdminHelper(self.output, self.base_url, self.max_instances)
        
        # Mock methods used by collect_urls
        helper.get_modeladmin_models = Mock(return_value=[self.mock_model])
        helper.get_modeladmin_url_paths = Mock(return_value={self.mock_model: "custom/model/path"})
        
        # Also mock the helper methods that add URLs
        helper.add_list_url = Mock()
        helper.add_edit_url = Mock()
        helper.add_delete_url = Mock()
        
        # Mock other helpers
        with patch('wagtail_unveil.helpers.modeladmin_helpers.model_has_instances') as mock_model_has_instances, \
             patch('wagtail_unveil.helpers.modeladmin_helpers.get_instance_sample') as mock_get_instance_sample, \
             patch('wagtail_unveil.helpers.modeladmin_helpers.truncate_instance_name') as mock_truncate_instance_name:
            
            mock_model_has_instances.return_value = True
            mock_get_instance_sample.return_value = [self.mock_instance1]
            mock_truncate_instance_name.side_effect = lambda x: f"Truncated {x}"
            
            # Call collect_urls
            helper.collect_urls()
            
            # Check URLs use custom path
            helper.add_list_url.assert_called_once_with(
                "testapp.testmodel", 
                "http://testserver/admin/custom/model/path/"
            )
            helper.add_edit_url.assert_called_once_with(
                "testapp.testmodel", "Truncated Test Instance 1",
                "http://testserver/admin/custom/model/path/edit/1/"
            )
            helper.add_delete_url.assert_called_once_with(
                "testapp.testmodel", "Truncated Test Instance 1",
                "http://testserver/admin/custom/model/path/delete/1/"
            )

    def test_modeladmin_urls(self):
        """Test modeladmin_urls calls collect_urls."""
        helper = ModelAdminHelper(self.output, self.base_url, self.max_instances)
        
        # Mock collect_urls method
        helper.collect_urls = Mock(return_value=["url1", "url2"])
        
        # Call modeladmin_urls
        result = helper.modeladmin_urls()
        
        # Verify collect_urls was called and result was returned
        helper.collect_urls.assert_called_once()
        self.assertEqual(result, ["url1", "url2"])

    def test_get_modeladmin_models_function(self):
        """Test the standalone get_modeladmin_models function."""
        with patch.object(ModelAdminHelper, 'get_modeladmin_models') as mock_method:
            mock_method.return_value = ["model1", "model2"]
            
            # Call the standalone function
            result = get_modeladmin_models()
            
            # Verify the result
            self.assertEqual(result, ["model1", "model2"])
            mock_method.assert_called_once()