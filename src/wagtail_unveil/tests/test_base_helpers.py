from django.test import TestCase
from io import StringIO
from unittest.mock import Mock

from wagtail_unveil.helpers.base import (
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)


class GetInstanceSampleTests(TestCase):
    def setUp(self):
        self.output = StringIO()
        self.mock_model = Mock()
        self.mock_model._meta = Mock()
        self.mock_model._meta.app_label = "test_app"
        self.mock_model._meta.model_name = "test_model"

    def test_get_instance_sample_with_max_instances(self):
        """Test get_instance_sample with a positive max_instances value."""
        # Setup mock objects
        self.mock_model.objects = Mock()
        all_queryset = Mock()
        self.mock_model.objects.all = Mock(return_value=all_queryset)
        all_queryset.__getitem__ = Mock(return_value=["instance1", "instance2"])
        
        result = get_instance_sample(self.output, self.mock_model, max_instances=2)
        
        self.assertEqual(result, ["instance1", "instance2"])
        self.mock_model.objects.all.assert_called_once()
        all_queryset.__getitem__.assert_called_once_with(slice(None, 2))

    def test_get_instance_sample_with_zero_max_instances(self):
        """Test get_instance_sample with max_instances=0 (get all instances)."""
        # Setup mock objects
        self.mock_model.objects = Mock()
        all_queryset = ["instance1", "instance2", "instance3"]
        self.mock_model.objects.all = Mock(return_value=all_queryset)
        
        result = get_instance_sample(self.output, self.mock_model, max_instances=0)
        
        self.assertEqual(result, ["instance1", "instance2", "instance3"])
        self.mock_model.objects.all.assert_called_once()

    def test_get_instance_sample_with_none_max_instances(self):
        """Test get_instance_sample with max_instances=None (get all instances)."""
        # Setup mock objects
        self.mock_model.objects = Mock()
        all_queryset = ["instance1", "instance2", "instance3"]
        self.mock_model.objects.all = Mock(return_value=all_queryset)
        
        result = get_instance_sample(self.output, self.mock_model, max_instances=None)
        
        self.assertEqual(result, ["instance1", "instance2", "instance3"])
        self.mock_model.objects.all.assert_called_once()

    def test_get_instance_sample_with_error(self):
        """Test get_instance_sample when an error occurs."""
        # Setup mock objects to raise an exception
        self.mock_model.objects = Mock()
        self.mock_model.objects.all = Mock(side_effect=AttributeError("Test error"))
        
        result = get_instance_sample(self.output, self.mock_model)
        
        self.assertEqual(result, [])
        self.assertIn("Error getting instances for test_app.test_model", self.output.getvalue())
        self.assertIn("Test error", self.output.getvalue())


class ModelHasInstancesTests(TestCase):
    def setUp(self):
        self.output = StringIO()
        self.mock_model = Mock()
        self.mock_model._meta = Mock()
        self.mock_model._meta.app_label = "test_app"
        self.mock_model._meta.model_name = "test_model"

    def test_model_has_instances_true(self):
        """Test model_has_instances when the model has instances."""
        # Setup mock objects
        self.mock_model.objects = Mock()
        self.mock_model.objects.exists = Mock(return_value=True)
        
        result = model_has_instances(self.output, self.mock_model)
        
        self.assertTrue(result)
        self.mock_model.objects.exists.assert_called_once()

    def test_model_has_instances_false(self):
        """Test model_has_instances when the model has no instances."""
        # Setup mock objects
        self.mock_model.objects = Mock()
        self.mock_model.objects.exists = Mock(return_value=False)
        
        result = model_has_instances(self.output, self.mock_model)
        
        self.assertFalse(result)
        self.mock_model.objects.exists.assert_called_once()

    def test_model_has_instances_with_error(self):
        """Test model_has_instances when an error occurs."""
        # Setup mock objects to raise an exception
        self.mock_model.objects = Mock()
        self.mock_model.objects.exists = Mock(side_effect=AttributeError("Test error"))
        
        result = model_has_instances(self.output, self.mock_model)
        
        self.assertFalse(result)
        self.assertIn("Error checking if test_app.test_model has instances", self.output.getvalue())
        self.assertIn("Test error", self.output.getvalue())


class TruncateInstanceNameTests(TestCase):
    def test_truncate_instance_name_short(self):
        """Test truncate_instance_name with a short name that doesn't need truncation."""
        result = truncate_instance_name("Short Name", max_length=50)
        self.assertEqual(result, "Short Name")

    def test_truncate_instance_name_long(self):
        """Test truncate_instance_name with a long name that needs truncation."""
        long_name = "This is a very long instance name that exceeds the maximum length"
        result = truncate_instance_name(long_name, max_length=30)
        self.assertEqual(result, "This is a very long instanc...")
        self.assertEqual(len(result), 30)

    def test_truncate_instance_name_custom_max_length(self):
        """Test truncate_instance_name with a custom max_length."""
        name = "This will be truncated at 20 characters"
        result = truncate_instance_name(name, max_length=20)
        self.assertEqual(result, "This will be trun...")
        self.assertEqual(len(result), 20)

    def test_truncate_instance_name_exact_length(self):
        """Test truncate_instance_name with a name that is exactly max_length."""
        exact_name = "This is exactly 25 chars."
        result = truncate_instance_name(exact_name, max_length=25)
        self.assertEqual(result, exact_name)
        self.assertEqual(len(result), 25)