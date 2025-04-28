from wagtail.documents import get_document_model as get_document_model_wagtail

from .base import (
    format_url_tuple,
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)



def get_document_model():
    """
    This currently returns the core get_document_model function from Wagtail.
    Not sure yet if this need to be overridden in some way.
    """
    return get_document_model_wagtail()


def get_document_admin_urls(output, base_url, max_instances):
    """Get admin URLs for documents"""
    urls = []
    base = base_url.rstrip("/")
    DocumentModel = get_document_model()
    model_name = f"{DocumentModel._meta.app_label}.{DocumentModel._meta.model_name}"

    # Check if there are any documents
    has_instances = model_has_instances(output, DocumentModel)

    # Add list URL
    list_url = f"{base}/admin/documents/"

    if has_instances:
        urls.append(format_url_tuple(model_name, None, "list", list_url))

        # Add edit URLs for actual instances using the helper method
        instances = get_instance_sample(output, DocumentModel, max_instances)
        for instance in instances:
            instance_name = truncate_instance_name(str(instance))
            # The correct edit URL pattern for documents
            edit_url = f"{base}/admin/documents/edit/{instance.id}/"
            urls.append(format_url_tuple(model_name, instance_name, "edit", edit_url))
            
            # Add delete URL for each document
            delete_url = f"{base}/admin/documents/delete/{instance.id}/"
            urls.append(format_url_tuple(model_name, instance_name, "delete", delete_url))
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