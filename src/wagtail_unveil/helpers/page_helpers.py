from wagtail.models import get_page_models as get_page_models_wagtail

from .base import format_url_tuple, get_instance_sample, model_has_instances


def get_page_models():
    """
    This currently returns the core get_page_models function from Wagtail.
    Not sure yet if this need to be overridden in some way.
    """
    return get_page_models_wagtail()


def get_page_urls(output, base_url, max_instances):
    """Get admin URLs for page models"""
    urls = []
    # Strip trailing slash from base_url to avoid double slashes
    base = base_url.rstrip("/")

    for model in get_page_models():
        model_name = f"{model._meta.app_label}.{model._meta.model_name}"

        # Check if model has any instances
        has_instances = model_has_instances(output, model)

        # Get instances using our safe query helper
        instances = (
            get_instance_sample(output, model, max_instances) if has_instances else []
        )

        if instances:
            # Add edit and frontend URLs for each instance
            for instance in instances:
                # Add admin edit URL
                edit_url = f"{base}/admin/pages/{instance.id}/edit/"
                urls.append(
                    format_url_tuple(model_name, instance.title, "edit", edit_url)
                )

                # Add delete URL for each page
                delete_url = f"{base}/admin/pages/{instance.id}/delete/"
                urls.append(
                    format_url_tuple(model_name, instance.title, "delete", delete_url)
                )

                # Add frontend URL if the page has one
                if hasattr(instance, "url") and instance.url:
                    # Check if already a full URL
                    if instance.url.startswith("http"):
                        frontend_url = instance.url
                    else:
                        # Ensure clean joining of URLs
                        page_url = instance.url
                        if page_url.startswith("/"):
                            frontend_url = f"{base}{page_url}"
                        else:
                            frontend_url = f"{base}/{page_url}"

                    urls.append(
                        format_url_tuple(
                            model_name, instance.title, "frontend", frontend_url
                        )
                    )
        else:
            # For models with no instances, always show the list URL with a note
            if hasattr(output, "style"):
                output.write(output.style.INFO(f"Note: {model_name} has no instances"))
            else:
                output.write(f"Note: {model_name} has no instances")
            urls.append(
                format_url_tuple(
                    f"{model_name} (NO INSTANCES)", None, "list", f"{base}/admin/pages/"
                )
            )

    return urls
