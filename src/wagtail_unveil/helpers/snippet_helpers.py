from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

from django.contrib.contenttypes.models import ContentType
from wagtail.snippets.models import get_snippet_models

from .base import (
    format_url_tuple,
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)


@dataclass
class SnippetHelper:
    """
    A dataclass that encapsulates snippet helper functionality.
    Developers can inherit from this class to extend its functionality.
    """
    output: Any
    base_url: str
    max_instances: int
    urls: List[Tuple[str, Optional[str], str, str]] = field(default_factory=list)
    
    def __post_init__(self):
        self.base = self.base_url.rstrip("/")
    
    def get_list_url(self, content_type) -> str:
        """Get the list URL for a snippet model"""
        return f"{self.base}/admin/snippets/{content_type.app_label}/{content_type.model}/"
    
    def get_edit_url(self, content_type, instance_id: int) -> str:
        """Get the edit URL for a snippet instance"""
        return f"{self.base}/admin/snippets/{content_type.app_label}/{content_type.model}/{instance_id}/"
    
    def get_delete_url(self, content_type, instance_id: int) -> str:
        """Get the delete URL for a snippet instance"""
        return f"{self.base}/admin/snippets/{content_type.app_label}/{content_type.model}/{instance_id}/delete/"
    
    def collect_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """Collect all snippet admin URLs"""
        for model in get_snippet_models():
            model_name = f"{model._meta.app_label}.{model._meta.model_name}"
            content_type = ContentType.objects.get_for_model(model)
            
            # Check if model has any instances
            has_instances = model_has_instances(self.output, model)
            
            # Add list URL - always include this regardless of whether there are instances
            list_url = self.get_list_url(content_type)
            
            if has_instances:
                self.urls.append(format_url_tuple(model_name, None, "list", list_url))
                
                # Add edit URLs for actual instances
                instances = get_instance_sample(self.output, model, self.max_instances)
                for instance in instances:
                    instance_name = truncate_instance_name(str(instance))
                    edit_url = self.get_edit_url(content_type, instance.id)
                    self.urls.append(format_url_tuple(model_name, instance_name, "edit", edit_url))
                    
                    # Add delete URL for each instance
                    delete_url = self.get_delete_url(content_type, instance.id)
                    self.urls.append(format_url_tuple(model_name, instance_name, "delete", delete_url))
            else:
                # For models with no instances, always show the list URL with a note
                if hasattr(self.output, "style"):
                    self.output.write(self.output.style.INFO(f"Note: {model_name} has no instances"))
                else:
                    self.output.write(f"Note: {model_name} has no instances")
                self.urls.append(
                    format_url_tuple(f"{model_name} (NO INSTANCES)", None, "list", list_url)
                )
        
        return self.urls
    
    def snippet_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """Return all snippet URLs"""
        return self.collect_urls()
