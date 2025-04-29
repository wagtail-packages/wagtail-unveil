from typing import List, Optional, Tuple

from django.contrib.contenttypes.models import ContentType
from wagtail.snippets.models import get_snippet_models

from .base import (
    BaseHelper,
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)


class SnippetHelper(BaseHelper):
    """
    A dataclass that encapsulates snippet helper functionality.
    Developers can inherit from this class to extend its functionality.
    """
    
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
            model_name = self.get_model_name(model)
            content_type = ContentType.objects.get_for_model(model)
            
            # Check if model has any instances
            has_instances = model_has_instances(self.output, model)
            
            # Add list URL - always include this regardless of whether there are instances
            list_url = self.get_list_url(content_type)
            
            if has_instances:
                self.add_list_url(model_name, list_url)
                
                # Add edit URLs for actual instances
                instances = get_instance_sample(self.output, model, self.max_instances)
                for instance in instances:
                    instance_name = truncate_instance_name(str(instance))
                    edit_url = self.get_edit_url(content_type, instance.id)
                    self.add_edit_url(model_name, instance_name, edit_url)
                    
                    # Add delete URL for each instance
                    delete_url = self.get_delete_url(content_type, instance.id)
                    self.add_delete_url(model_name, instance_name, delete_url)
            else:
                # For models with no instances, always show the list URL with a note
                self.write_no_instances_message(model_name)
                self.add_url_for_model_with_no_instances(model_name, list_url)
        
        return self.urls
    
    def snippet_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """Return all snippet URLs"""
        return self.collect_urls()
