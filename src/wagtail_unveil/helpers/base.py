from dataclasses import dataclass, field
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, OperationalError
from typing import Any, List, Optional, Tuple


def safe_query(
    output, query_func, fallback_value=None, model_name=None, error_msg=None
):
    """
    Safely execute a database query with standardized error handling.

    Args:
        output: The stdout writer from the command
        query_func: Function that performs the database query
        fallback_value: Value to return if the query fails
        model_name: Name of the model for error reporting
        error_msg: Custom error message

    Returns:
        The result of the query or the fallback value if it fails
    """
    try:
        return query_func()
    except (
        AttributeError,
        ValueError,
        TypeError,
        ObjectDoesNotExist,
        DatabaseError,
        OperationalError,
    ) as e:
        if model_name or error_msg:
            message = error_msg or f"Error getting instances for {model_name}"
            output.write(f"{message}: {str(e)}")
        return fallback_value


def get_instance_sample(output, model, max_instances=1):
    """
    Get a sample of instances from a model with proper error handling.

    Args:
        output: The stdout writer from the command
        model: The model class to query
        max_instances: Maximum number of instances to return (0 for all)

    Returns:
        A queryset of model instances or an empty list if the query fails
    """
    if max_instances is not None and max_instances > 0:

        def query_func():
            return model.objects.all()[:max_instances]

    else:

        def query_func():
            return model.objects.all()

    return safe_query(
        output,
        query_func,
        fallback_value=[],
        model_name=f"{model._meta.app_label}.{model._meta.model_name}",
    )


def model_has_instances(output, model):
    """
    Check if a model has any instances.

    Args:
        output: The stdout writer from the command
        model: The model class to query

    Returns:
        Boolean indicating if the model has any instances
    """

    def query_func():
        try:
            return model.objects.exists()
        except (
            AttributeError,
            ValueError,
            TypeError,
            ObjectDoesNotExist,
            DatabaseError,
            OperationalError,
        ) as e:
            output.write(
                f"Error checking if {model._meta.app_label}.{model._meta.model_name} has instances: {str(e)}"
            )
            return False

    return safe_query(
        output,
        query_func,
        fallback_value=False,
        model_name=f"{model._meta.app_label}.{model._meta.model_name}",
    )


def truncate_instance_name(instance_name, max_length=50):
    """
    Truncate an instance name if it's too long.

    Args:
        instance_name: The instance name to truncate
        max_length: Maximum length before truncation

    Returns:
        Truncated name if needed
    """
    if len(instance_name) > max_length:
        return instance_name[: max_length - 3] + "..."
    return instance_name


@dataclass
class BaseHelper:
    """
    A base dataclass that encapsulates common helper functionality.
    All specific helpers should inherit from this class.
    """
    output: Any
    base_url: str
    max_instances: int
    urls: List[Tuple[str, Optional[str], str, str]] = field(default_factory=list)
    
    def __post_init__(self):
        """Strip trailing slash from base_url"""
        self.base = self.base_url.rstrip("/")
    
    def get_model_name(self, model) -> str:
        """Get the full name of a model"""
        return f"{model._meta.app_label}.{model._meta.model_name}"
    
    def write_no_instances_message(self, model_name: str) -> None:
        """Write a message indicating a model has no instances"""
        if hasattr(self.output, "style"):
            self.output.write(self.output.style.INFO(f"Note: {model_name} has no instances"))
        else:
            self.output.write(f"Note: {model_name} has no instances")
    
    def add_url_for_model_with_no_instances(self, model_name: str, list_url: str) -> None:
        """Add a list URL for a model with no instances"""
        display_name = f"{model_name} (NO INSTANCES)"
        self.urls.append((display_name, None, "list", list_url))
    
    def add_list_url(self, model_name: str, list_url: str) -> None:
        """Add a list URL for a model"""
        self.urls.append((model_name, None, "list", list_url))
    
    def add_edit_url(self, model_name: str, instance_name: str, edit_url: str) -> None:
        """Add an edit URL for a model instance"""
        display_name = model_name
        if instance_name:
            display_name = f"{model_name} ({instance_name})"
        self.urls.append((display_name, instance_name, "edit", edit_url))
    
    def add_delete_url(self, model_name: str, instance_name: str, delete_url: str) -> None:
        """Add a delete URL for a model instance"""
        display_name = model_name
        if instance_name:
            display_name = f"{model_name} ({instance_name})"
        self.urls.append((display_name, instance_name, "delete", delete_url))
    
    def collect_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """
        Abstract method that should be implemented by subclasses.
        Collects all admin URLs relevant to the specific helper.
        """
        raise NotImplementedError("Subclasses must implement collect_urls method")
