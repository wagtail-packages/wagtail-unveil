from django.test import TestCase
from io import StringIO
from unittest.mock import Mock, patch

from wagtail_unveil.helpers.snippet_helpers import SnippetHelper


class SnippetHelperTests(TestCase):
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
        self.mock_instance1.__str__ = Mock(return_value="Instance 1")
        
        self.mock_instance2 = Mock()
        self.mock_instance2.id = 2
        self.mock_instance2.__str__ = Mock(return_value="Instance 2")
        
        self.snippet_models = [self.mock_model1, self.mock_model2]
        self.base_url = "http://testserver"
        self.max_instances = 5

    @patch('wagtail_unveil.helpers.snippet_helpers.get_snippet_models')
    @patch('wagtail_unveil.helpers.snippet_helpers.ContentType.objects.get_for_model')
    @patch('wagtail_unveil.helpers.snippet_helpers.model_has_instances')
    @patch('wagtail_unveil.helpers.snippet_helpers.get_instance_sample')
    def test_snippet_urls_with_instances(self, mock_get_instance_sample, mock_model_has_instances, mock_get_for_model, mock_get_snippet_models):
        """Test snippet_urls with models that have instances."""
        # Set up the snippet models mock
        mock_get_snippet_models.return_value = self.snippet_models
        
        # Set up the content type mock
        mock_content_type1 = Mock()
        mock_content_type1.app_label = "app1"
        mock_content_type1.model = "model1"
        
        mock_content_type2 = Mock()
        mock_content_type2.app_label = "app2"
        mock_content_type2.model = "model2"
        
        mock_get_for_model.side_effect = [mock_content_type1, mock_content_type2]
        
        # Set up the model_has_instances mock to return True for the first model, False for the second
        mock_model_has_instances.side_effect = [True, False]
        
        # Set up the get_instance_sample mock to return instances for the first model
        mock_get_instance_sample.return_value = [self.mock_instance1, self.mock_instance2]
        
        # Create the helper and call snippet_urls
        helper = SnippetHelper(self.output, self.base_url, self.max_instances)
        result = helper.snippet_urls()
        
        # Check that we get the expected URLs
        # 1 list URL + 2 edit URLs + 2 delete URLs for the model with instances + 1 list URL for the model without instances
        self.assertEqual(len(result), 6)
        
        # Check list URL for the model with instances
        self.assertIn(("app1.model1", "list", "http://testserver/admin/snippets/app1/model1/"), result)
        
        # Check edit URLs for instances
        self.assertIn(("app1.model1 (Instance 1)", "edit", "http://testserver/admin/snippets/app1/model1/1/"), result)
        self.assertIn(("app1.model1 (Instance 2)", "edit", "http://testserver/admin/snippets/app1/model1/2/"), result)
        
        # Check delete URLs for instances
        self.assertIn(("app1.model1 (Instance 1)", "delete", "http://testserver/admin/snippets/app1/model1/1/delete/"), result)
        self.assertIn(("app1.model1 (Instance 2)", "delete", "http://testserver/admin/snippets/app1/model1/2/delete/"), result)
        
        # Check list URL for the model without instances
        self.assertIn(("app2.model2 (NO INSTANCES)", "list", "http://testserver/admin/snippets/app2/model2/"), result)
        
        # Check the output message for models with no instances
        self.assertIn("Note: app2.model2 has no instances", self.output.getvalue())

    @patch('wagtail_unveil.helpers.snippet_helpers.get_snippet_models')
    @patch('wagtail_unveil.helpers.snippet_helpers.ContentType.objects.get_for_model')
    @patch('wagtail_unveil.helpers.snippet_helpers.model_has_instances')
    def test_snippet_urls_without_instances(self, mock_model_has_instances, mock_get_for_model, mock_get_snippet_models):
        """Test snippet_urls with models that have no instances."""
        # Set up the snippet models mock
        mock_get_snippet_models.return_value = self.snippet_models
        
        # Set up the content type mock
        mock_content_type1 = Mock()
        mock_content_type1.app_label = "app1"
        mock_content_type1.model = "model1"
        
        mock_content_type2 = Mock()
        mock_content_type2.app_label = "app2"
        mock_content_type2.model = "model2"
        
        mock_get_for_model.side_effect = [mock_content_type1, mock_content_type2]
        
        # Set up the model_has_instances mock to return False for both models
        mock_model_has_instances.side_effect = [False, False]
        
        # Create the helper and call snippet_urls
        helper = SnippetHelper(self.output, self.base_url, self.max_instances)
        result = helper.snippet_urls()
        
        # Check that we get the expected URLs
        self.assertEqual(len(result), 2)  # 2 list URLs for models with no instances
        
        # Check list URLs for models with no instances
        self.assertIn(("app1.model1 (NO INSTANCES)", "list", "http://testserver/admin/snippets/app1/model1/"), result)
        self.assertIn(("app2.model2 (NO INSTANCES)", "list", "http://testserver/admin/snippets/app2/model2/"), result)
        
        # Check the output messages for models with no instances
        self.assertIn("Note: app1.model1 has no instances", self.output.getvalue())
        self.assertIn("Note: app2.model2 has no instances", self.output.getvalue())

    @patch('wagtail_unveil.helpers.snippet_helpers.get_snippet_models')
    @patch('wagtail_unveil.helpers.snippet_helpers.ContentType.objects.get_for_model')
    @patch('wagtail_unveil.helpers.snippet_helpers.model_has_instances')
    def test_snippet_urls_with_styled_output(self, mock_model_has_instances, mock_get_for_model, mock_get_snippet_models):
        """Test snippet_urls with styled output."""
        # Create a mock output with style
        output_with_style = Mock()
        output_with_style.style = Mock()
        output_with_style.style.INFO = lambda x: f"INFO: {x}"
        output_with_style.write = Mock()
        
        # Set up the snippet models mock
        mock_get_snippet_models.return_value = [self.mock_model1]
        
        # Set up the content type mock
        mock_content_type = Mock()
        mock_content_type.app_label = "app1"
        mock_content_type.model = "model1"
        mock_get_for_model.return_value = mock_content_type
        
        # Set up other mocks
        mock_model_has_instances.return_value = False
        
        # Create the helper and call snippet_urls
        helper = SnippetHelper(output_with_style, self.base_url, self.max_instances)
        helper.snippet_urls()
        
        # Check that the style.INFO method was used for the output
        output_with_style.write.assert_called_once()
        call_args = output_with_style.write.call_args[0][0]
        self.assertTrue(call_args.startswith("INFO:"))