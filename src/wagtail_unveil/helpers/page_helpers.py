from typing import List, Optional, Tuple

from wagtail.models import get_page_models

from .base import (
    BaseHelper,
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)


class PageHelper(BaseHelper):
    """
    A dataclass that encapsulates page helper functionality.
    Developers can inherit from this class to extend its functionality.
    """
    
    def get_edit_url(self, instance_id: int) -> str:
        """Get the edit URL for a page instance"""
        return f"{self.base}/admin/pages/{instance_id}/edit/"
    
    def get_delete_url(self, instance_id: int) -> str:
        """Get the delete URL for a page instance"""
        return f"{self.base}/admin/pages/{instance_id}/delete/"
    
    def get_frontend_url(self, instance) -> Optional[str]:
        """Get the frontend URL for a page instance if it has one"""
        if not hasattr(instance, "url") or not instance.url:
            return None
            
        # Check if already a full URL
        if instance.url.startswith("http"):
            return instance.url
        
        # Ensure clean joining of URLs
        page_url = instance.url
        if page_url.startswith("/"):
            return f"{self.base}{page_url}"
        else:
            return f"{self.base}/{page_url}"
    
    def get_list_url(self) -> str:
        """Get the list URL for pages"""
        return f"{self.base}/admin/pages/"
    
    def collect_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """Collect all page admin URLs"""
        
        for model in get_page_models():
            model_name = self.get_model_name(model)
            
            # Check if model has any instances
            has_instances = model_has_instances(self.output, model)
            
            # Get instances using our safe query helper
            instances = (
                get_instance_sample(self.output, model, self.max_instances) if has_instances else []
            )
            
            if instances:
                # Add edit and frontend URLs for each instance
                for instance in instances:
                    instance_name = truncate_instance_name(instance.title)
                    
                    # Add admin edit URL
                    edit_url = self.get_edit_url(instance.id)
                    self.add_edit_url(model_name, instance_name, edit_url)
                    
                    # Add delete URL for each page
                    delete_url = self.get_delete_url(instance.id)
                    self.add_delete_url(model_name, instance_name, delete_url)
                    
                    # Add frontend URL if the page has one
                    frontend_url = self.get_frontend_url(instance)
                    if frontend_url:
                        self.urls.append(
                            (f"{model_name} ({instance_name})", instance_name, "frontend", frontend_url)
                        )
            else:
                # For models with no instances, always show the list URL with a note
                self.write_no_instances_message(model_name)
                self.add_url_for_model_with_no_instances(model_name, self.get_list_url())
        
        return self.urls
    
    def page_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """Return all page URLs"""
        return self.collect_urls()

