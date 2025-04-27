import inspect
from importlib import import_module

from django.apps import apps

from .base import (
    format_url_tuple,
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)


def get_modeladmin_models():
    """
    Find models registered with ModelAdmin
    This is a bit more complex since we need to inspect the wagtail_hooks modules
    """
    modeladmin_models = []

    # Look for apps with wagtail_hooks module
    for app_config in apps.get_app_configs():
        try:
            hooks_module = import_module(f"{app_config.name}.wagtail_hooks")
            # Look for ModelAdmin classes
            for name, obj in inspect.getmembers(hooks_module):
                # Check if this object has a model attribute (which is a key indicator of ModelAdmin)
                if hasattr(obj, "model") and obj.model is not None:
                    # Check if this looks like a ModelAdmin - old or new style
                    # For classic wagtail.contrib.modeladmin.options.ModelAdmin
                    if hasattr(obj, "get_admin_urls_for_registration"):
                        modeladmin_models.append(obj.model)
                    # For the newer wagtail_modeladmin.options.ModelAdmin
                    elif hasattr(obj, "get_admin_urls"):
                        modeladmin_models.append(obj.model)
        except (ImportError, ModuleNotFoundError):
            # App doesn't have wagtail_hooks module
            pass

    return modeladmin_models


def get_modeladmin_urls(
    output, base_url, max_instances
):
    """Get admin URLs for modeladmin models"""
    urls = []
    # Strip trailing slash from base_url to avoid double slashes
    base = base_url.rstrip("/")

    # Get modeladmin models
    modeladmin_models = get_modeladmin_models()
    
    # Dictionary to store custom base URL paths for models
    modeladmin_url_paths = {}
    
    # Find custom URL paths for models by re-inspecting wagtail_hooks
    for app_config in apps.get_app_configs():
        try:
            hooks_module = import_module(f"{app_config.name}.wagtail_hooks")
            for name, obj in inspect.getmembers(hooks_module):
                if hasattr(obj, "model") and obj.model is not None:
                    if hasattr(obj, "base_url_path") and obj.base_url_path:
                        modeladmin_url_paths[obj.model] = obj.base_url_path
        except (ImportError, ModuleNotFoundError):
            pass

    for model in modeladmin_models:
        model_name = f"{model._meta.app_label}.{model._meta.model_name}"

        # Check if model has any instances
        has_instances = model_has_instances(output, model)

        # Check if this model has a custom base URL path
        custom_url_path = modeladmin_url_paths.get(model)

        if custom_url_path:
            # Use the custom URL path
            list_url = f"{base}/admin/{custom_url_path}/"
        else:
            # Use the default modeladmin URL pattern
            # TODO: depending on how the model is registered, this might not be correct
            # Other testing suggest using
            # list_url = f"{base}/admin/{model._meta.app_label}/{model._meta.model_name}/"
            list_url = f"{base}/admin/modeladmin/{model._meta.app_label}/{model._meta.model_name}/"

        if has_instances:
            urls.append(format_url_tuple(model_name, None, "list", list_url))

            # Add edit URLs for actual instances
            instances = get_instance_sample(output, model, max_instances)
            for instance in instances:
                instance_name = truncate_instance_name(str(instance))

                if custom_url_path:
                    # Use the custom URL path for edit URLs
                    edit_url = f"{base}/admin/{custom_url_path}/edit/{instance.id}/"
                    # Add delete URL with custom path
                    delete_url = f"{base}/admin/{custom_url_path}/delete/{instance.id}/"
                else:
                    # Use the default modeladmin URL pattern for edit URLs
                    # TODO: depending on how the model is registered, this might not be correct
                    # Other testing suggest using
                    # edit_url = f"{base}/admin/{model._meta.app_label}/{model._meta.model_name}/edit/{instance.id}/"
                    edit_url = f"{base}/admin/modeladmin/{model._meta.app_label}/{model._meta.model_name}/edit/{instance.id}/"
                    # Add delete URL with default pattern
                    delete_url = f"{base}/admin/modeladmin/{model._meta.app_label}/{model._meta.model_name}/delete/{instance.id}/"

                urls.append(
                    format_url_tuple(model_name, instance_name, "edit", edit_url)
                )
                # Add delete URL for each instance
                urls.append(
                    format_url_tuple(model_name, instance_name, "delete", delete_url)
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
