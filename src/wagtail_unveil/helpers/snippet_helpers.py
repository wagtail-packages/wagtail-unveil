import inspect
from importlib import import_module

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from wagtail.snippets.models import get_snippet_models

from .base import (
    format_url_tuple,
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)


def get_snippet_urls(output, base_url, max_instances):
    """Get admin URLs for snippet models, including both list and edit URLs"""
    urls = []
    for model in get_snippet_models():
        model_name = f"{model._meta.app_label}.{model._meta.model_name}"
        content_type = ContentType.objects.get_for_model(model)

        # Check if model has any instances
        has_instances = model_has_instances(output, model)

        # Add list URL - always include this regardless of whether there are instances
        list_url = (
            f"{base_url}/admin/snippets/{content_type.app_label}/{content_type.model}/"
        )

        if has_instances:
            urls.append(format_url_tuple(model_name, None, "list", list_url))

            # Add edit URLs for actual instances
            instances = get_instance_sample(output, model, max_instances)
            for instance in instances:
                instance_name = truncate_instance_name(str(instance))
                edit_url = f"{base_url}/admin/snippets/{content_type.app_label}/{content_type.model}/{instance.id}/"
                urls.append(
                    format_url_tuple(model_name, instance_name, "edit", edit_url)
                )
        else:
            # For models with no instances, always show the list URL with a note
            if hasattr(output, "style"):
                output.write(output.style.INFO(f"Note: {model_name} has no instances"))
            else:
                output.write(f"Note: {model_name} has no instances")
            urls.append(
                format_url_tuple(f"{model_name} (NO INSTANCES)", None, "list", list_url)
            )

    return urls


def get_modelviewset_models():
    """
    Find models registered with ModelViewSet
    This is a bit more complex since we need to inspect the wagtail_hooks modules
    """
    modelviewset_models = []
    # Dictionary to store custom base URL paths for models
    modelviewset_url_paths = {}

    # Look for apps with wagtail_hooks module
    for app_config in apps.get_app_configs():
        try:
            hooks_module = import_module(f"{app_config.name}.wagtail_hooks")
            # Look for ModelViewSet classes
            for name, obj in inspect.getmembers(hooks_module):
                if inspect.isclass(obj):
                    # Check if this is a ModelViewSet class
                    if hasattr(obj, "model") and "ModelViewSet" in str(obj.__bases__):
                        # Only add the model if it's not None
                        if obj.model is not None:
                            modelviewset_models.append(obj.model)
                            # Store custom base_url_path if it exists
                            if hasattr(obj, "base_url_path") and obj.base_url_path:
                                modelviewset_url_paths[obj.model] = obj.base_url_path
        except (ImportError, ModuleNotFoundError):
            # App doesn't have wagtail_hooks module
            pass

    return modelviewset_models, modelviewset_url_paths


def get_modelviewset_urls(
    output, modelviewset_models, modelviewset_url_paths, base_url, max_instances
):
    """Get admin URLs for models registered with ModelViewSet"""
    urls = []
    base = base_url.rstrip("/")

    # Models that should be skipped because they're already included in settings
    skip_models = ["wagtailcore.locale", "wagtailcore.site"]

    for model in modelviewset_models:
        model_name = f"{model._meta.app_label}.{model._meta.model_name}"

        # Skip models that are already covered by settings admin URLs
        if model_name in skip_models:
            output.write(
                f"Skipping duplicate {model_name} URLs - already included in settings section"
            )
            continue

        # Check if model has any instances
        has_instances = model_has_instances(output, model)

        # Special case for 'wagtailcore.locale' to use plural 'locales' in URL
        if model_name == "wagtailcore.locale":
            # Add list URL with correct plural form
            list_url = f"{base}/admin/locales/"

            if has_instances:
                urls.append(format_url_tuple(model_name, None, "list", list_url))

                # Add edit URLs for actual instances with correct plural form
                instances = get_instance_sample(output, model, max_instances)
                for instance in instances:
                    instance_name = truncate_instance_name(str(instance))

                    # Use correct plural "locales" for edit URL
                    edit_url = f"{base}/admin/locales/{instance.id}/"
                    urls.append(
                        format_url_tuple(model_name, instance_name, "edit", edit_url)
                    )
            else:
                # For models with no instances, always show the list URL with a note
                if hasattr(output, "style"):
                    output.write(
                        output.style.INFO(f"Note: {model_name} has no instances")
                    )
                else:
                    output.write(f"Note: {model_name} has no instances")
                urls.append(
                    format_url_tuple(
                        f"{model_name} (NO INSTANCES)", None, "list", list_url
                    )
                )

            # Skip the rest of the loop for the locale model since we handled it specially
            continue

        # Normal handling for all other models
        # Add list URL - ModelViewSet URLs use just the model_name, not app_label/model_name
        list_url = f"{base}/admin/{model._meta.model_name}/"

        if has_instances:
            urls.append(format_url_tuple(model_name, None, "list", list_url))

            # Add edit URLs for actual instances
            instances = get_instance_sample(output, model, max_instances)
            for instance in instances:
                instance_name = truncate_instance_name(str(instance))

                # ModelViewSet edit URLs also use just the model_name
                edit_url = f"{base}/admin/{model._meta.model_name}/{instance.id}/"
                urls.append(
                    format_url_tuple(model_name, instance_name, "edit", edit_url)
                )
        else:
            # For models with no instances, always show the list URL with a note
            if hasattr(output, "style"):
                output.write(output.style.INFO(f"Note: {model_name} has no instances"))
            else:
                output.write(f"Note: {model_name} has no instances")
            urls.append(
                format_url_tuple(f"{model_name} (NO INSTANCES)", None, "list", list_url)
            )

    return urls
