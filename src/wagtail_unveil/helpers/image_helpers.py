from typing import List, Optional, Tuple

from wagtail.images import get_image_model

from .base import (
    BaseHelper,
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)


class ImageHelper(BaseHelper):
    """
    A dataclass that encapsulates image helper functionality.
    Developers can inherit from this class to extend its functionality.
    """
    
    def __post_init__(self):
        super().__post_init__()
        self.image_model = get_image_model()
        self.model_name = self.get_model_name(self.image_model)
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
            self.add_list_url(self.model_name, list_url)
            
            # Add edit and delete URLs for actual instances
            instances = get_instance_sample(self.output, self.image_model, self.max_instances)
            for instance in instances:
                instance_name = truncate_instance_name(str(instance))
                edit_url = self.get_edit_url(instance.id)
                self.add_edit_url(self.model_name, instance_name, edit_url)
                
                delete_url = self.get_delete_url(instance.id)
                self.add_delete_url(self.model_name, instance_name, delete_url)
        else:
            # For models with no instances, show the list URL with a note
            self.write_no_instances_message(self.model_name)
            self.add_url_for_model_with_no_instances(self.model_name, list_url)
        
        return self.urls
    
    def image_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        return self.collect_urls()
