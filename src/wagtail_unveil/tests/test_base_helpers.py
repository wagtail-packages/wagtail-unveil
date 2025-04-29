from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, OperationalError
from io import StringIO
from unittest.mock import Mock, patch

from wagtail_unveil.helpers.base import (
    safe_query,
    safe_import,
    get_instance_sample,
    model_has_instances,
    format_url_tuple,
    truncate_instance_name,
)


class SafeQueryTests(TestCase):
    def setUp(self):
        self.output = StringIO()

    def test_safe_query_success(self):
        """Test that safe_query returns the result of the query function when successful."""
        def query_func():
            return "success"
        
        result = safe_query(self.output, query_func)
        self.assertEqual(result, "success")

    def test_safe_query_with_attribute_error(self):
        """Test that safe_query handles AttributeError and returns fallback value."""
        def query_func():
            raise AttributeError("Attribute error")
        
        result = safe_query(self.output, query_func, fallback_value="fallback")
        self.assertEqual(result, "fallback")

    def test_safe_query_with_value_error(self):
        """Test that safe_query handles ValueError and returns fallback value."""
        def query_func():
            raise ValueError("Value error")
        
        result = safe_query(self.output, query_func, fallback_value="fallback")
        self.assertEqual(result, "fallback")

    def test_safe_query_with_type_error(self):
        """Test that safe_query handles TypeError and returns fallback value."""
        def query_func():
            raise TypeError("Type error")
        
        result = safe_query(self.output, query_func, fallback_value="fallback")
        self.assertEqual(result, "fallback")

    def test_safe_query_with_object_does_not_exist(self):
        """Test that safe_query handles ObjectDoesNotExist and returns fallback value."""
        def query_func():
            raise ObjectDoesNotExist("Object does not exist")
        
        result = safe_query(self.output, query_func, fallback_value="fallback")
        self.assertEqual(result, "fallback")

    def test_safe_query_with_database_error(self):
        """Test that safe_query handles DatabaseError and returns fallback value."""
        def query_func():
            raise DatabaseError("Database error")
        
        result = safe_query(self.output, query_func, fallback_value="fallback")
        self.assertEqual(result, "fallback")

    def test_safe_query_with_operational_error(self):
        """Test that safe_query handles OperationalError and returns fallback value."""
        def query_func():
            raise OperationalError("Operational error")
        
        result = safe_query(self.output, query_func, fallback_value="fallback")
        self.assertEqual(result, "fallback")

    def test_safe_query_with_model_name(self):
        """Test that safe_query outputs error message with model name."""
        def query_func():
            raise ValueError("Value error")
        
        safe_query(self.output, query_func, model_name="TestModel")
        self.assertIn("Error getting instances for TestModel", self.output.getvalue())

    def test_safe_query_with_custom_error_msg(self):
        """Test that safe_query outputs custom error message."""
        def query_func():
            raise ValueError("Value error")
        
        safe_query(self.output, query_func, error_msg="Custom error message")
        self.assertIn("Custom error message", self.output.getvalue())


class SafeImportTests(TestCase):
    def setUp(self):
        self.output = StringIO()

    def test_safe_import_success(self):
        """Test that safe_import returns the result of the import function when successful."""
        def import_func():
            return "success"
        
        result = safe_import(self.output, import_func)
        self.assertEqual(result, "success")

    def test_safe_import_with_import_error(self):
        """Test that safe_import handles ImportError and returns fallback value."""
        def import_func():
            raise ImportError("Import error")
        
        result = safe_import(self.output, import_func, fallback_value="fallback")
        self.assertEqual(result, "fallback")

    def test_safe_import_with_module_not_found_error(self):
        """Test that safe_import handles ModuleNotFoundError and returns fallback value."""
        def import_func():
            raise ModuleNotFoundError("Module not found error")
        
        result = safe_import(self.output, import_func, fallback_value="fallback")
        self.assertEqual(result, "fallback")

    def test_safe_import_with_attribute_error(self):
        """Test that safe_import handles AttributeError and returns fallback value."""
        def import_func():
            raise AttributeError("Attribute error")
        
        result = safe_import(self.output, import_func, fallback_value="fallback")
        self.assertEqual(result, "fallback")

    def test_safe_import_with_custom_error_msg(self):
        """Test that safe_import outputs custom error message."""
        def import_func():
            raise ImportError("Import error")
        
        safe_import(self.output, import_func, error_msg="Custom error message")
        self.assertIn("Custom error message", self.output.getvalue())


class GetInstanceSampleTests(TestCase):
    def setUp(self):
        self.output = StringIO()
        self.mock_model = Mock()
        self.mock_model._meta = Mock()
        self.mock_model._meta.app_label = "test_app"
        self.mock_model._meta.model_name = "test_model"

    @patch('wagtail_unveil.helpers.base.safe_query')
    def test_get_instance_sample_with_max_instances(self, mock_safe_query):
        """Test get_instance_sample with a positive max_instances value."""
        mock_safe_query.return_value = ["instance1", "instance2"]
        
        result = get_instance_sample(self.output, self.mock_model, max_instances=2)
        
        self.assertEqual(result, ["instance1", "instance2"])
        # Check that safe_query was called with the correct parameters
        mock_safe_query.assert_called_once()
        # Check the first parameter (output)
        self.assertEqual(mock_safe_query.call_args[0][0], self.output)
        # Check the fallback_value and model_name as keyword arguments
        self.assertEqual(mock_safe_query.call_args[1]['fallback_value'], [])
        self.assertEqual(mock_safe_query.call_args[1]['model_name'], "test_app.test_model")

    @patch('wagtail_unveil.helpers.base.safe_query')
    def test_get_instance_sample_with_zero_max_instances(self, mock_safe_query):
        """Test get_instance_sample with max_instances=0 (get all instances)."""
        mock_safe_query.return_value = ["instance1", "instance2", "instance3"]
        
        result = get_instance_sample(self.output, self.mock_model, max_instances=0)
        
        self.assertEqual(result, ["instance1", "instance2", "instance3"])

    @patch('wagtail_unveil.helpers.base.safe_query')
    def test_get_instance_sample_with_none_max_instances(self, mock_safe_query):
        """Test get_instance_sample with max_instances=None (get all instances)."""
        mock_safe_query.return_value = ["instance1", "instance2", "instance3"]
        
        result = get_instance_sample(self.output, self.mock_model, max_instances=None)
        
        self.assertEqual(result, ["instance1", "instance2", "instance3"])


class ModelHasInstancesTests(TestCase):
    def setUp(self):
        self.output = StringIO()
        self.mock_model = Mock()
        self.mock_model._meta = Mock()
        self.mock_model._meta.app_label = "test_app"
        self.mock_model._meta.model_name = "test_model"

    @patch('wagtail_unveil.helpers.base.safe_query')
    def test_model_has_instances_true(self, mock_safe_query):
        """Test model_has_instances when the model has instances."""
        mock_safe_query.return_value = True
        
        result = model_has_instances(self.output, self.mock_model)
        
        self.assertTrue(result)
        # Check that safe_query was called with the correct parameters
        mock_safe_query.assert_called_once()
        # Check the first parameter (output)
        self.assertEqual(mock_safe_query.call_args[0][0], self.output)
        # Check the fallback_value and model_name as keyword arguments
        self.assertEqual(mock_safe_query.call_args[1]['fallback_value'], False)
        self.assertEqual(mock_safe_query.call_args[1]['model_name'], "test_app.test_model")

    @patch('wagtail_unveil.helpers.base.safe_query')
    def test_model_has_instances_false(self, mock_safe_query):
        """Test model_has_instances when the model has no instances."""
        mock_safe_query.return_value = False
        
        result = model_has_instances(self.output, self.mock_model)
        
        self.assertFalse(result)


class FormatUrlTupleTests(TestCase):
    def test_format_url_tuple_without_instance_name(self):
        """Test format_url_tuple without an instance name."""
        result = format_url_tuple("TestModel", url_type="list", url="/admin/test/")
        self.assertEqual(result, ("TestModel", None, "list", "/admin/test/"))

    def test_format_url_tuple_with_instance_name(self):
        """Test format_url_tuple with an instance name."""
        result = format_url_tuple("TestModel", instance_name="Test Instance", url_type="edit", url="/admin/test/1/")
        self.assertEqual(result, ("TestModel (Test Instance)", "Test Instance", "edit", "/admin/test/1/"))


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