import inspect
from dataclasses import dataclass, field
from importlib import import_module
from typing import Any, List, Optional, Tuple

from django.apps import apps

from .base import (
    format_url_tuple,
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)


@dataclass
class ModelViewSetHelper:
    """
    A dataclass that encapsulates ModelViewSet helper functionality.
    Developers can inherit from this class to extend its functionality.
    """
    output: Any
    base_url: str
    max_instances: int
    urls: List[Tuple[str, Optional[str], str, str]] = field(default_factory=list)
    
    def __post_init__(self):
        self.base = self.base_url.rstrip("/")
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
        modelviewset_models = get_modelviewset_models()
        
        for model in modelviewset_models:
            model_name = f"{model._meta.app_label}.{model._meta.model_name}"
            
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
                self.urls.append(format_url_tuple(model_name, None, "list", list_url))
                
                # Add edit URLs for actual instances
                instances = get_instance_sample(self.output, model, self.max_instances)
                for instance in instances:
                    instance_name = truncate_instance_name(str(instance))
                    
                    # Add edit URL
                    edit_url = self.get_edit_url(model, instance.id)
                    self.urls.append(
                        format_url_tuple(model_name, instance_name, "edit", edit_url)
                    )
                    
                    # Add delete URL
                    delete_url = self.get_delete_url(model, instance.id)
                    self.urls.append(
                        format_url_tuple(model_name, instance_name, "delete", delete_url)
                    )
            else:
                # For models with no instances, always show the list URL with a note
                if hasattr(self.output, "style"):
                    self.output.write(
                        self.output.style.INFO(f"Note: {model_name} has no instances")
                    )
                else:
                    self.output.write(f"Note: {model_name} has no instances")
                self.urls.append(
                    format_url_tuple(f"{model_name} (NO INSTANCES)", None, "list", list_url)
                )
        
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