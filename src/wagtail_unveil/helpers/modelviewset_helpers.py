import inspect
from importlib import import_module
from typing import List, Optional, Tuple

from django.apps import apps

from .base import (
    BaseHelper,
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)


class ModelViewSetHelper(BaseHelper):
    """
    A dataclass that encapsulates ModelViewSet helper functionality.
    Developers can inherit from this class to extend its functionality.
    """
    
    def __post_init__(self):
        super().__post_init__()
        # Models that should be skipped because they're already included in settings
        self.skip_models = ["wagtailcore.locale", "wagtailcore.site"]
    
    def get_modelviewset_models(self):
        """
        Find models registered with ModelViewSet
        This is a bit more complex since we need to inspect the wagtail_hooks modules
        """
        modelviewset_models = []

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
            except (ImportError, ModuleNotFoundError):
                # App doesn't have wagtail_hooks module
                pass

        return modelviewset_models
    
    def get_list_url(self, model) -> str:
        """Get the list URL for a model"""
        model_name = model._meta.model_name
        
        # Special case for 'wagtailcore.locale' to use plural 'locales' in URL
        if f"{model._meta.app_label}.{model._meta.model_name}" == "wagtailcore.locale":
            return f"{self.base}/admin/locales/"
        
        return f"{self.base}/admin/{model_name}/"
    
    def get_edit_url(self, model, instance_id: int) -> str:
        """Get the edit URL for a model instance"""
        model_name = model._meta.model_name
        
        # Special case for 'wagtailcore.locale' to use plural 'locales' in URL
        if f"{model._meta.app_label}.{model._meta.model_name}" == "wagtailcore.locale":
            return f"{self.base}/admin/locales/{instance_id}/"
        
        return f"{self.base}/admin/{model_name}/{instance_id}/"
    
    def get_delete_url(self, model, instance_id: int) -> str:
        """Get the delete URL for a model instance"""
        model_name = model._meta.model_name
        
        # Special case for 'wagtailcore.locale' to use plural 'locales' in URL
        if f"{model._meta.app_label}.{model._meta.model_name}" == "wagtailcore.locale":
            return f"{self.base}/admin/locales/{instance_id}/delete/"
        
        return f"{self.base}/admin/{model_name}/{instance_id}/delete/"
    
    def collect_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """Get admin URLs for models registered with ModelViewSet"""
        # Get the models
        modelviewset_models = self.get_modelviewset_models()
        
        for model in modelviewset_models:
            model_name = self.get_model_name(model)
            
            # Skip models that are already covered by settings admin URLs
            if model_name in self.skip_models:
                self.output.write(
                    f"Skipping duplicate {model_name} URLs - already included in settings section"
                )
                continue
            
            # Check if model has any instances
            has_instances = model_has_instances(self.output, model)
            
            # Add list URL
            list_url = self.get_list_url(model)
            
            if has_instances:
                self.add_list_url(model_name, list_url)
                
                # Add edit URLs for actual instances
                instances = get_instance_sample(self.output, model, self.max_instances)
                for instance in instances:
                    instance_name = truncate_instance_name(str(instance))
                    
                    # Add edit URL
                    edit_url = self.get_edit_url(model, instance.id)
                    self.add_edit_url(model_name, instance_name, edit_url)
                    
                    # Add delete URL
                    delete_url = self.get_delete_url(model, instance.id)
                    self.add_delete_url(model_name, instance_name, delete_url)
            else:
                # For models with no instances, always show the list URL with a note
                self.write_no_instances_message(model_name)
                self.add_url_for_model_with_no_instances(model_name, list_url)
        
        return self.urls
    
    def modelviewset_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """Return all ModelViewSet URLs"""
        return self.collect_urls()


# Legacy wrapper for backward compatibility
def get_modelviewset_models():
    """
    Legacy wrapper for backward compatibility.
    Find models registered with ModelViewSet.
    """
    helper = ModelViewSetHelper(output=None, base_url="", max_instances=0)
    return helper.get_modelviewset_models()