
from django.contrib.contenttypes.models import ContentType
from wagtail.snippets.models import get_snippet_models

from .base import (
    format_url_tuple,
    get_instance_sample,
    model_has_instances,
    truncate_instance_name,
)


def get_snippet_urls(output, base_url, max_instances):
    """Get admin URLs for snippet models, including both list and edit URLs"""
    urls = []
    for model in get_snippet_models():
        model_name = f"{model._meta.app_label}.{model._meta.model_name}"
        content_type = ContentType.objects.get_for_model(model)

        # Check if model has any instances
        has_instances = model_has_instances(output, model)

        # Add list URL - always include this regardless of whether there are instances
        list_url = (
            f"{base_url}/admin/snippets/{content_type.app_label}/{content_type.model}/"
        )

        if has_instances:
            urls.append(format_url_tuple(model_name, None, "list", list_url))

            # Add edit URLs for actual instances
            instances = get_instance_sample(output, model, max_instances)
            for instance in instances:
                instance_name = truncate_instance_name(str(instance))
                edit_url = f"{base_url}/admin/snippets/{content_type.app_label}/{content_type.model}/{instance.id}/"
                urls.append(
                    format_url_tuple(model_name, instance_name, "edit", edit_url)
                )
                
                # Add delete URL for each instance
                delete_url = f"{base_url}/admin/snippets/{content_type.app_label}/{content_type.model}/{instance.id}/delete/"
                urls.append(
                    format_url_tuple(model_name, instance_name, "delete", delete_url)
                )
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
