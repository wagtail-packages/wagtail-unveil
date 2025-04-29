from typing import List, Optional, Tuple

from wagtail.documents import get_document_model

from .base import (
    BaseHelper,
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)


class DocumentHelper(BaseHelper):
    """
    A dataclass that encapsulates document helper functionality.
    Developers can inherit from this class to extend its functionality.
    """
    
    def __post_init__(self):
        super().__post_init__()
        self.document_model = get_document_model()
        self.model_name = self.get_model_name(self.document_model)
        self.has_instances = model_has_instances(self.output, self.document_model)
    
    def get_list_url(self) -> str:
        """Get the list URL for documents"""
        return f"{self.base}/admin/documents/"
    
    def get_edit_url(self, instance_id: int) -> str:
        """Get the edit URL for a document instance"""
        return f"{self.base}/admin/documents/edit/{instance_id}/"
    
    def get_delete_url(self, instance_id: int) -> str:
        """Get the delete URL for a document instance"""
        return f"{self.base}/admin/documents/delete/{instance_id}/"
    
    def collect_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """Collect all document admin URLs"""
        list_url = self.get_list_url()
        
        if self.has_instances:
            self.add_list_url(self.model_name, list_url)
            
            # Add edit and delete URLs for actual instances
            instances = get_instance_sample(self.output, self.document_model, self.max_instances)
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
    
    def document_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        return self.collect_urls()
