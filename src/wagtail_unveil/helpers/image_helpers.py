from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

from wagtail.images import get_image_model

from .base import (
    format_url_tuple,
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)


@dataclass
class ImageHelper:
    """
    A dataclass that encapsulates image helper functionality.
    Developers can inherit from this class to extend its functionality.
    """
    output: Any
    base_url: str
    max_instances: int
    urls: List[Tuple[str, Optional[str], str, str]] = field(default_factory=list)
    
    def __post_init__(self):
        self.base = self.base_url.rstrip("/")
        self.image_model = get_image_model()
        self.model_name = f"{self.image_model._meta.app_label}.{self.image_model._meta.model_name}"
        self.has_instances = model_has_instances(self.output, self.image_model)
    
    def get_list_url(self) -> str:
        """Get the list URL for images"""
        return f"{self.base}/admin/images/"
    
    def get_edit_url(self, instance_id: int) -> str:
        """Get the edit URL for an image instance"""
        return f"{self.base}/admin/images/{instance_id}/"
    
    def get_delete_url(self, instance_id: int) -> str:
        """Get the delete URL for an image instance"""
        return f"{self.base}/admin/images/{instance_id}/delete/"
    
    def collect_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """Collect all image admin URLs"""
        list_url = self.get_list_url()
        
        if self.has_instances:
            self.urls.append(format_url_tuple(self.model_name, None, "list", list_url))
            
            # Add edit and delete URLs for actual instances
            instances = get_instance_sample(self.output, self.image_model, self.max_instances)
            for instance in instances:
                instance_name = truncate_instance_name(str(instance))
                edit_url = self.get_edit_url(instance.id)
                self.urls.append(format_url_tuple(self.model_name, instance_name, "edit", edit_url))
                
                delete_url = self.get_delete_url(instance.id)
                self.urls.append(format_url_tuple(self.model_name, instance_name, "delete", delete_url))
        else:
            # For models with no instances, show the list URL with a note
            if hasattr(self.output, "style"):
                self.output.write(self.output.style.INFO(f"Note: {self.model_name} has no instances"))
            else:
                self.output.write(f"Note: {self.model_name} has no instances")
            self.urls.append(
                format_url_tuple(f"{self.model_name} (NO INSTANCES)", None, "list", list_url)
            )
        
        return self.urls
    
    def image_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        return self.collect_urls()
