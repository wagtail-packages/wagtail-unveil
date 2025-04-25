from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, OperationalError
from wagtail.models import Page, Site
from wagtail.models import get_page_models as get_page_models_wagtail

from .base import format_url_tuple, get_instance_sample, model_has_instances


def get_page_models():
    """
    Get all models that inherit from Page
    
    Returns:
        list: A list of page models currently uses the Wagtail
        get_page_models function. It should be good enough...
    """
    return get_page_models_wagtail()


def get_page_urls(output, page_models, base_url, max_instances):
    """Get admin URLs for page models"""
    urls = []
    # Strip trailing slash from base_url to avoid double slashes
    base = base_url.rstrip("/")

    for model in page_models:
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


def get_site_urls(output, base_url):
    """Get URLs for site default pages"""
    urls = []

    try:
        # Get all sites configured in Wagtail
        sites = Site.objects.all()

        # Keep track of URLs we've already added to avoid duplicates
        added_frontend_urls = set()

        # Add the general pages listing URL
        base = base_url.rstrip("/")
        pages_listing_url = f"{base}/admin/pages/"
        urls.append(
            format_url_tuple("All Pages Listing", None, "list", pages_listing_url)
        )

        # Add the search URLs - one with no results, one with results
        empty_search_url = f"{base}/admin/pages/search/?q=xyznonexistentsearchterm123"
        urls.append(
            format_url_tuple("Page Search (No Results)", None, "list", empty_search_url)
        )

        # Get a search term dynamically from the title of any existing page
        # This ensures it will work on any site
        try:
            home_page = Page.objects.filter(depth=2).first()
            if home_page:
                # Extract a single word from the title that's likely to match
                title_word = home_page.title.split()[0]
                result_search_url = f"{base}/admin/pages/search/?q={title_word}"
                result_description = f"Page Search (With Results - '{title_word}')"
            else:
                # Fallback to a common word that's likely to be in any page
                result_search_url = f"{base}/admin/pages/search/?q=page"
                result_description = "Page Search (With Results - 'page')"
        except (
            AttributeError,
            ObjectDoesNotExist,
            DatabaseError,
            OperationalError,
            IndexError,
        ) as e:
            # Ultimate fallback if we can't query the database, with specific exceptions
            result_search_url = f"{base}/admin/pages/search/?q=the"
            result_description = f"Page Search (With Results - 'the') (Error: {str(e)})"

        urls.append(
            format_url_tuple(result_description, None, "list", result_search_url)
        )

        for site in sites:
            # Get the root page for this site
            root_page = site.root_page

            # Add frontend URL - use base URL directly for the homepage
            # Strip trailing slash from base_url to ensure consistent formatting
            base = base_url.rstrip("/")

            # For the root page, just use the base URL as the site URL
            site_url = f"{base}/"

            # Only add the frontend URL if we haven't added it yet
            if site_url not in added_frontend_urls:
                urls.append(
                    format_url_tuple("Site default page", None, "frontend", site_url)
                )
                added_frontend_urls.add(site_url)

            # Always add admin edit URLs for each root page
            admin_url = f"{base}/admin/pages/{root_page.id}/edit/"
            urls.append(
                format_url_tuple(
                    "Site default page", root_page.title, "edit", admin_url
                )
            )

            # Add the specific page explorer URL for the root page
            explorer_url = f"{base}/admin/pages/{root_page.id}/"
            urls.append(
                format_url_tuple(
                    "Site default page explorer", root_page.title, "list", explorer_url
                )
            )

            # If this is the default site, also add the admin dashboard URL
            if site.is_default_site:
                dashboard_url = f"{base}/admin/"
                urls.append(
                    format_url_tuple("Admin dashboard", None, "admin", dashboard_url)
                )
    except (
        AttributeError,
        ObjectDoesNotExist,
        DatabaseError,
        OperationalError,
    ) as e:
        output.write(output.style.WARNING(f"Error getting site URLs: {str(e)}"))

    return urls
