from django.test import TestCase
from io import StringIO
from unittest.mock import Mock, patch

from wagtail_unveil.helpers.modelviewset_helpers import (
    get_modelviewset_models,
    get_modelviewset_urls,
)


class GetModelViewsetModelsTests(TestCase):
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


class GetModelViewsetUrlsTests(TestCase):
    def setUp(self):
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

    @patch('wagtail_unveil.helpers.modelviewset_helpers.get_modelviewset_models')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.get_instance_sample')
    def test_get_modelviewset_urls_with_instances(self, mock_get_instance_sample, mock_model_has_instances, mock_get_modelviewset_models):
        """Test get_modelviewset_urls with models that have instances."""
        # Set up the get_modelviewset_models mock to return our test models
        mock_get_modelviewset_models.return_value = self.modelviewset_models
        
        # Set up the model_has_instances mock to return True for both models
        mock_model_has_instances.side_effect = [True, True]
        
        # Set up the get_instance_sample mock to return instances
        mock_get_instance_sample.return_value = [self.mock_instance1, self.mock_instance2]
        
        # Call the function
        result = get_modelviewset_urls(
            self.output, 
            self.base_url, 
            self.max_instances
        )
        
        # Check the output - we should skip the locale model because it's in skip_models
        self.assertIn("Skipping duplicate wagtailcore.locale URLs", self.output.getvalue())
        
        # We should only get URLs for the regular model (locale is skipped)
        # 1 list URL + 2 edit URLs + 2 delete URLs = 5 URLs total
        self.assertEqual(len(result), 5)
        
        # Check list URL for regular model
        self.assertIn(("app1.model1", "list", "http://testserver/admin/model1/"), result)
        
        # Check edit URLs for regular model
        self.assertIn(("app1.model1 (Instance 1)", "edit", "http://testserver/admin/model1/1/"), result)
        self.assertIn(("app1.model1 (Instance 2)", "edit", "http://testserver/admin/model1/2/"), result)
        
        # Check delete URLs for regular model
        self.assertIn(("app1.model1 (Instance 1)", "delete", "http://testserver/admin/model1/1/delete/"), result)
        self.assertIn(("app1.model1 (Instance 2)", "delete", "http://testserver/admin/model1/2/delete/"), result)

    @patch('wagtail_unveil.helpers.modelviewset_helpers.get_modelviewset_models')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.model_has_instances')
    def test_get_modelviewset_urls_without_instances(self, mock_model_has_instances, mock_get_modelviewset_models):
        """Test get_modelviewset_urls with models that have no instances."""
        # Set up the get_modelviewset_models mock to return our test models
        mock_get_modelviewset_models.return_value = self.modelviewset_models
        
        # Set up the model_has_instances mock to return False for both models
        mock_model_has_instances.side_effect = [False, False]
        
        # Call the function
        result = get_modelviewset_urls(
            self.output, 
            self.base_url, 
            self.max_instances
        )
        
        # Check the output - we should skip the locale model because it's in skip_models
        self.assertIn("Skipping duplicate wagtailcore.locale URLs", self.output.getvalue())
        
        # We should only get URLs for the regular model, without instances
        self.assertEqual(len(result), 1)  # 1 list URL for the model without instances (locale is skipped)
        
        # Check list URL for model with no instances
        self.assertIn(("app1.model1 (NO INSTANCES)", "list", "http://testserver/admin/model1/"), result)
        
        # Check the output message for models with no instances
        self.assertIn("Note: app1.model1 has no instances", self.output.getvalue())

    @patch('wagtail_unveil.helpers.modelviewset_helpers.get_modelviewset_models')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.modelviewset_helpers.get_instance_sample')
    def test_get_modelviewset_urls_with_custom_url_paths(self, mock_get_instance_sample, mock_model_has_instances, mock_get_modelviewset_models):
        """Test get_modelviewset_urls with custom URL paths."""
        # Set up the get_modelviewset_models mock to return just model1
        mock_get_modelviewset_models.return_value = [self.mock_model1]
        
        # Set up other mocks
        mock_model_has_instances.return_value = True
        mock_get_instance_sample.return_value = [self.mock_instance1]
        
        # Call the function
        result = get_modelviewset_urls(
            self.output, 
            self.base_url, 
            self.max_instances
        )
        
        # Check that we get the expected URLs with the custom path
        self.assertEqual(len(result), 3)  # 1 list URL + 1 edit URL + 1 delete URL
        
        # The actual implementation doesn't use custom paths
        # It always constructs URLs based on model name
        self.assertIn(("app1.model1", "list", "http://testserver/admin/model1/"), result)
        self.assertIn(("app1.model1 (Instance 1)", "edit", "http://testserver/admin/model1/1/"), result)
        self.assertIn(("app1.model1 (Instance 1)", "delete", "http://testserver/admin/model1/1/delete/"), result)

    @patch('wagtail_unveil.helpers.modelviewset_helpers.get_modelviewset_models')
    def test_get_modelviewset_urls_with_skip_models(self, mock_get_modelviewset_models):
        """Test get_modelviewset_urls skips models that are already covered by settings admin URLs."""
        # Create a mock model that should be skipped
        mock_skip_model = Mock()
        mock_skip_model._meta = Mock()
        mock_skip_model._meta.app_label = "wagtailcore"
        mock_skip_model._meta.model_name = "site"
        
        # Set up the get_modelviewset_models mock to return the skip model
        mock_get_modelviewset_models.return_value = [mock_skip_model]
        
        # Call the function
        result = get_modelviewset_urls(
            self.output, 
            self.base_url, 
            self.max_instances
        )
        
        # Check the output message indicating the model was skipped
        self.assertIn("Skipping duplicate wagtailcore.site URLs", self.output.getvalue())
        
        # Check that we get no URLs because the model was skipped
        self.assertEqual(len(result), 0)