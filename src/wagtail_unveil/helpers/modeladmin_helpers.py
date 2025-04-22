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
    # Dictionary to store custom base URL paths for models
    modeladmin_url_paths = {}

    # Look for apps with wagtail_hooks module
    for app_config in apps.get_app_configs():
        try:
            hooks_module = import_module(f"{app_config.name}.wagtail_hooks")
            # Look for ModelAdmin classes
            for name, obj in inspect.getmembers(hooks_module):
                if inspect.isclass(obj) and hasattr(obj, "model"):
                    # Check if this looks like a ModelAdmin - old or new style
                    # For classic wagtail.contrib.modeladmin.options.ModelAdmin
                    if (
                        hasattr(obj, "get_admin_urls_for_registration")
                        and obj.model is not None
                    ):
                        modeladmin_models.append(obj.model)
                        # Store custom base_url_path if it exists
                        if hasattr(obj, "base_url_path") and obj.base_url_path:
                            modeladmin_url_paths[obj.model] = obj.base_url_path
                    # For the newer wagtail_modeladmin.options.ModelAdmin
                    elif hasattr(obj, "get_admin_urls") and obj.model is not None:
                        modeladmin_models.append(obj.model)
                        # Store custom base_url_path if it exists
                        if hasattr(obj, "base_url_path") and obj.base_url_path:
                            modeladmin_url_paths[obj.model] = obj.base_url_path
        except (ImportError, ModuleNotFoundError):
            # App doesn't have wagtail_hooks module
            pass

    # Check if any objects have been registered directly via modeladmin_register
    try:
        # For the new wagtail_modeladmin package
        from wagtail_modeladmin.options import ModelAdminRegistry

        registry = ModelAdminRegistry()
        for modeladmin in registry._registry:
            if hasattr(modeladmin, "model") and modeladmin.model is not None:
                modeladmin_models.append(modeladmin.model)
                # Store custom base_url_path if it exists
                if hasattr(modeladmin, "base_url_path") and modeladmin.base_url_path:
                    modeladmin_url_paths[modeladmin.model] = modeladmin.base_url_path
    except (ImportError, ModuleNotFoundError):
        # The new wagtail_modeladmin package might not be installed
        pass

    try:
        # For classic wagtail.contrib.modeladmin
        from wagtail.contrib.modeladmin.options import ModelAdminRegistry

        registry = ModelAdminRegistry()
        for modeladmin in registry._registry:
            if hasattr(modeladmin, "model") and modeladmin.model is not None:
                modeladmin_models.append(modeladmin.model)
                # Store custom base_url_path if it exists
                if hasattr(modeladmin, "base_url_path") and modeladmin.base_url_path:
                    modeladmin_url_paths[modeladmin.model] = modeladmin.base_url_path
    except (ImportError, ModuleNotFoundError):
        # The classic wagtail.contrib.modeladmin package might not be installed
        pass

    return modeladmin_models, modeladmin_url_paths


def get_modeladmin_urls(
    output, modeladmin_models, modeladmin_url_paths, base_url, max_instances
):
    """Get admin URLs for modeladmin models"""
    urls = []
    # Strip trailing slash from base_url to avoid double slashes
    base = base_url.rstrip("/")

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
                else:
                    # Use the default modeladmin URL pattern for edit URLs
                    # TODO: depending on how the model is registered, this might not be correct
                    # Other testing suggest using
                    # edit_url = f"{base}/admin/{model._meta.app_label}/{model._meta.model_name}/edit/{instance.id}/"
                    edit_url = f"{base}/admin/modeladmin/{model._meta.app_label}/{model._meta.model_name}/edit/{instance.id}/"

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
