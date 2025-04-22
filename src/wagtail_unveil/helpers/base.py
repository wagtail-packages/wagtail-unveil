from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, OperationalError


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


def safe_import(output, import_func, fallback_value=None, error_msg=None):
    """
    Safely import a module with standardized error handling.

    Args:
        output: The stdout writer from the command
        import_func: Function that performs the import
        fallback_value: Value to return if the import fails
        error_msg: Custom error message

    Returns:
        The result of the import or the fallback value if it fails
    """
    try:
        return import_func()
    except (ImportError, ModuleNotFoundError, AttributeError) as e:
        if error_msg:
            output.write(f"{error_msg}: {str(e)}")
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


def format_url_tuple(model_name, instance_name=None, url_type="list", url=None):
    """
    Format a URL tuple consistently for the URL output list.

    Args:
        model_name: The name of the model
        instance_name: Optional instance name
        url_type: Type of URL (list, edit, frontend, etc.)
        url: The actual URL

    Returns:
        A tuple formatted as (display_name, url_type, url)
    """
    display_name = model_name
    if instance_name:
        display_name = f"{model_name} ({instance_name})"

    return (display_name, url_type, url)


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
