from wagtail.images import get_image_model as get_image_model_wagtail

from .base import (
    format_url_tuple,
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)


def get_image_model():
    """
    This currently returns the core get_image_model function from Wagtail.
    Not sure yet if this need to be overridden in some way.
    """
    return get_image_model_wagtail()


def get_image_admin_urls(output, base_url, max_instances):
    """Get admin URLs for images"""
    urls = []
    base = base_url.rstrip("/")
    ImageModel = get_image_model()
    model_name = f"{ImageModel._meta.app_label}.{ImageModel._meta.model_name}"

    # Check if there are any images
    has_instances = model_has_instances(output, ImageModel)

    # Add list URL
    list_url = f"{base}/admin/images/"

    if has_instances:
        urls.append(format_url_tuple(model_name, None, "list", list_url))

        # Add edit URLs for actual instances using the helper method
        instances = get_instance_sample(output, ImageModel, max_instances)
        for instance in instances:
            instance_name = truncate_instance_name(str(instance))
            edit_url = f"{base}/admin/images/{instance.id}/"
            urls.append(format_url_tuple(model_name, instance_name, "edit", edit_url))
            
            # Add delete URL for each image
            # In Wagtail, the delete URL format differs from documents
            # It's likely /admin/images/{id}/delete/ instead of /admin/images/delete/{id}/
            delete_url = f"{base}/admin/images/{instance.id}/delete/"
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