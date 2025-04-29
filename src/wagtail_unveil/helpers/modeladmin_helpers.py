import inspect
from importlib import import_module
from typing import Dict, List, Optional, Tuple

from django.apps import apps

from .base import (
    BaseHelper,
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)


class ModelAdminHelper(BaseHelper):
    """
    A dataclass that encapsulates modeladmin helper functionality.
    Developers can inherit from this class to extend its functionality.
    """
    
    def get_modeladmin_models(self):
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
    
    def get_modeladmin_url_paths(self) -> Dict:
        """Find custom URL paths for models by re-inspecting wagtail_hooks"""
        modeladmin_url_paths = {}
        
        for app_config in apps.get_app_configs():
            try:
                hooks_module = import_module(f"{app_config.name}.wagtail_hooks")
                for name, obj in inspect.getmembers(hooks_module):
                    if hasattr(obj, "model") and obj.model is not None:
                        if hasattr(obj, "base_url_path") and obj.base_url_path:
                            modeladmin_url_paths[obj.model] = obj.base_url_path
            except (ImportError, ModuleNotFoundError):
                pass
        
        return modeladmin_url_paths
    
    def get_list_url(self, model, custom_url_path=None) -> str:
        """Get the list URL for a modeladmin model"""
        if custom_url_path:
            # Use the custom URL path
            return f"{self.base}/admin/{custom_url_path}/"
        else:
            # Use the default modeladmin URL pattern
            # TODO: depending on how the model is registered, this might not be correct
            # Other testing suggest using
            # return f"{self.base}/admin/{model._meta.app_label}/{model._meta.model_name}/"
            return f"{self.base}/admin/modeladmin/{model._meta.app_label}/{model._meta.model_name}/"
    
    def get_edit_url(self, model, instance_id, custom_url_path=None) -> str:
        """Get the edit URL for a modeladmin instance"""
        if custom_url_path:
            # Use the custom URL path for edit URLs
            return f"{self.base}/admin/{custom_url_path}/edit/{instance_id}/"
        else:
            # Use the default modeladmin URL pattern for edit URLs
            # TODO: depending on how the model is registered, this might not be correct
            # Other testing suggest using
            # return f"{self.base}/admin/{model._meta.app_label}/{model._meta.model_name}/edit/{instance_id}/"
            return f"{self.base}/admin/modeladmin/{model._meta.app_label}/{model._meta.model_name}/edit/{instance_id}/"
    
    def get_delete_url(self, model, instance_id, custom_url_path=None) -> str:
        """Get the delete URL for a modeladmin instance"""
        if custom_url_path:
            # Use the custom URL path for delete URLs
            return f"{self.base}/admin/{custom_url_path}/delete/{instance_id}/"
        else:
            # Use the default modeladmin URL pattern for delete URLs
            return f"{self.base}/admin/modeladmin/{model._meta.app_label}/{model._meta.model_name}/delete/{instance_id}/"
    
    def collect_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """Collect all modeladmin URLs"""
        try:
            # Get modeladmin models
            modeladmin_models = self.get_modeladmin_models()
            
            # Dictionary to store custom base URL paths for models
            modeladmin_url_paths = self.get_modeladmin_url_paths()
            
            for model in modeladmin_models:
                model_name = self.get_model_name(model)

                # Check if model has any instances
                has_instances = model_has_instances(self.output, model)

                # Check if this model has a custom base URL path
                custom_url_path = modeladmin_url_paths.get(model)

                list_url = self.get_list_url(model, custom_url_path)

                if has_instances:
                    self.add_list_url(model_name, list_url)

                    # Add edit URLs for actual instances
                    instances = get_instance_sample(self.output, model, self.max_instances)
                    
                    # Handle potential coroutine
                    if hasattr(instances, '__await__'):
                        if hasattr(self.output, "style"):
                            self.output.write(self.output.style.WARNING(
                                f"Warning: Async result detected for {model_name}. Skipping instance URLs."
                            ))
                        else:
                            self.output.write(f"Warning: Async result detected for {model_name}. Skipping instance URLs.")
                        continue
                        
                    for instance in instances:
                        instance_name = truncate_instance_name(str(instance))

                        edit_url = self.get_edit_url(model, instance.id, custom_url_path)
                        self.add_edit_url(model_name, instance_name, edit_url)
                        
                        # Add delete URL for each instance
                        delete_url = self.get_delete_url(model, instance.id, custom_url_path)
                        self.add_delete_url(model_name, instance_name, delete_url)
                else:
                    # For models with no instances, always show the list URL with a note
                    self.write_no_instances_message(model_name)
                    self.add_url_for_model_with_no_instances(model_name, list_url)
        except TypeError as e:
            if "coroutine" in str(e):
                if hasattr(self.output, "style"):
                    self.output.write(self.output.style.ERROR(
                        f"Error: Encountered a coroutine object that cannot be iterated. "
                        f"This may be caused by an async function that was not properly awaited. {str(e)}"
                    ))
                else:
                    self.output.write(
                        f"Error: Encountered a coroutine object that cannot be iterated. "
                        f"This may be caused by an async function that was not properly awaited. {str(e)}"
                    )
            else:
                # Re-raise other TypeErrors
                raise
        
        return self.urls
    
    def modeladmin_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """Return all modeladmin URLs"""
        return self.collect_urls()
