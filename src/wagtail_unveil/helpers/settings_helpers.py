from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import wagtail
from wagtail.models import Collection, Site
from wagtail.contrib.redirects.models import Redirect

from .base import format_url_tuple, get_instance_sample, safe_import

"""This file needs more work"""


# Sites management function
def get_default_site():
    site = Site.objects.filter(is_default_site=True)
    return site.first() if site.exists() else None


# Users management function
def get_admin_user():
    User = get_user_model()
    admins = User.objects.filter(is_superuser=True)
    return admins.first() if admins.exists() else []


# Groups management function
def get_group():
    groups = Group.objects.all()
    return groups.first() if groups.exists() else []


# Collections management function
def get_collections():
    collections = Collection.objects.all().exclude(id=Collection.get_first_root_node().id)[:1]
    return collections if collections.exists() else []


# Redirects management function
def get_redirects():
    redirects = Redirect.objects.all()[:1]
    return redirects if redirects.exists() else []


# Workflows management function
def get_workflows():
    from wagtail.models import Workflow
    workflows = Workflow.objects.all()[:1]
    return workflows if workflows.exists() else []


# Workflow tasks management function
def get_tasks():
    from wagtail.models import Task
    tasks = Task.objects.all()[:1]
    return tasks if tasks.exists() else []


# Search promotions management function
def get_search_promotions():
    from wagtail.contrib.search_promotions.models import SearchPromotion
    promotions = SearchPromotion.objects.all()[:1]
    return promotions if promotions.exists() else []


# Form pages management function
def get_form_pages():
    from wagtail.contrib.forms.models import AbstractEmailForm
    from wagtail.models import Page
    
    form_pages = []
    for page in Page.objects.specific():
        if isinstance(page, AbstractEmailForm):
            form_pages.append(page)
    return form_pages[:5] if form_pages else []  # Limit to 5 to avoid too many URLs


def get_settings_admin_urls(output, base_url, max_instances=1):
    """Get admin URLs for Wagtail settings"""
    urls = []
    base = base_url.rstrip("/")
    
    # Check once for installed apps/features
    locales_app_installed = apps.is_installed("wagtail.locales")
    search_promotions_installed = apps.is_installed("wagtail.contrib.search_promotions")

    # Settings section URLs are added individually - main settings entry is removed

    # Sites settings - wagtail.models.Site is already imported at the top
    sites_url = f"{base}/admin/sites/"
    urls.append(format_url_tuple("Settings > Sites", None, "list", sites_url))

    # Try to get an existing site to create an edit URL
    site = get_default_site()
    if site:
        site_edit_url = f"{base}/admin/sites/{site.id}/"
        urls.append(
            format_url_tuple(
                f"Settings > Sites > {site.hostname}", None, "edit", site_edit_url
            )
        )

    # Add other common settings sections
    settings_sections = [
        ("Collections", "collections"),
        ("Users", "users"),
        ("Groups", "groups"),
        ("Redirects", "redirects"),
        ("Workflows", "workflows/list"),
        ("Workflow tasks","workflows/tasks/index"),
    ]
    
    # Only add Locales to settings_sections if it's explicitly installed in INSTALLED_APPS
    if locales_app_installed:
        settings_sections.append(("Locales", "locales"))

    for name, path in settings_sections:
        section_url = f"{base}/admin/{path}/"
        urls.append(format_url_tuple(f"Settings > {name}", None, "list", section_url))

    admin_user = get_admin_user()
    if admin_user:
        user_edit_url = f"{base}/admin/users/{admin_user.id}/"
        urls.append(
            format_url_tuple(
                f"Settings > Users > {admin_user.username}", None, "edit", user_edit_url
            )
        )

    # Groups management - try to get a group for edit URL
    if apps.is_installed("django.contrib.auth"):
        group = get_group()
        if group:
            group_edit_url = f"{base}/admin/groups/{group.id}/"
            urls.append(
                format_url_tuple(
                    f"Settings > Groups > {group.name}", None, "edit", group_edit_url
                )
            )

    # Collections management - try to get a collection for edit URL
    collections = safe_import(
        output,
        get_collections,
        fallback_value=[],
        error_msg="Error getting collection instances",
    )

    # Apply max_instances limit if more than one collection exists
    if len(collections) > max_instances and max_instances > 0:
        collections = collections[:max_instances]

    for collection in collections:
        collection_edit_url = f"{base}/admin/collections/{collection.id}/"
        urls.append(
            format_url_tuple(
                f"Settings > Collections > {collection.name}",
                None,
                "edit",
                collection_edit_url,
            )
        )

    # Redirects - try to get a redirect for edit URL
    if apps.is_installed("wagtail.contrib.redirects"):
        redirects = safe_import(
            output,
            get_redirects,
            fallback_value=[],
            error_msg="Error getting redirect instances",
        )

        for redirect in redirects:
            redirect_edit_url = f"{base}/admin/redirects/{redirect.id}/"
            urls.append(
                format_url_tuple(
                    f"Settings > Redirects > {redirect.old_path}",
                    None,
                    "edit",
                    redirect_edit_url,
                )
            )

    # Workflows - try to get a workflow for edit URL if the module exists
    if hasattr(wagtail.models, "Workflow"):
        workflows = safe_import(
            output,
            get_workflows,
            fallback_value=[],
            error_msg="Error getting workflow instances",
        )

        for workflow in workflows:
            workflow_edit_url = f"{base}/admin/workflows/edit/{workflow.id}/"
            urls.append(
                format_url_tuple(
                    f"Settings > Workflows > {workflow.name}",
                    None,
                    "edit",
                    workflow_edit_url,
                )
            )

    # Workflow tasks - try to get a workflow task for edit URL if the module exists
    if hasattr(wagtail.models, "Task"):
        tasks = safe_import(
            output,
            get_tasks,
            fallback_value=[],
            error_msg="Error getting workflow task instances",
        )

        for task in tasks:
            task_edit_url = f"{base}/admin/workflows/tasks/edit/{task.id}/"
            urls.append(
                format_url_tuple(
                    f"Settings > Workflow tasks > {task.name}",
                    None,
                    "edit",
                    task_edit_url,
                )
            )

    # Locales - only process if the app is explicitly installed in INSTALLED_APPS
    if locales_app_installed:
        # Use safe_import to import the Locale model
        Locale = safe_import(
            output,
            lambda: __import__("wagtail.models", fromlist=["Locale"]).Locale,
            fallback_value=None,
            error_msg="Error importing Locale model"
        )
        
        if Locale:
            # Try to get locales
            locales = get_instance_sample(output, Locale, max_instances=max_instances)
            if locales:
                # Only add actual locale instances if they exist
                for locale in locales:
                    locale_edit_url = f"{base}/admin/locales/edit/{locale.id}/"
                    urls.append(
                        format_url_tuple(
                            f"Settings > Locales > {locale.language_code}",
                            None,
                            "edit",
                            locale_edit_url,
                        )
                    )
            else:
                # Add an example URL only if no instances found
                # And add NO INSTANCES note to be consistent with other sections
                if hasattr(output, "style"):
                    output.write(output.style.WARNING("Note: Locale has no instances"))
                else:
                    output.write("Note: Locale has no instances")
                
                locale_edit_url = f"{base}/admin/locales/edit/1/"
                urls.append(
                    format_url_tuple(
                        "Settings > Locales > Example (NO INSTANCES)", None, "edit", locale_edit_url
                    )
                )
        else:
            # The Locale model isn't available, even though the app might be installed
            # Log this as an anomaly but don't add URLs
            if hasattr(output, "style"):
                output.write(output.style.WARNING("Note: wagtail.locales is installed but Locale model is not available"))
            else:
                output.write("Note: wagtail.locales is installed but Locale model is not available")
    # No URLs added if wagtail.locales is not in INSTALLED_APPS

    # Search promotions - try to get a search promotion for edit URL
    if search_promotions_installed:
        promotions = safe_import(
            output,
            get_search_promotions,
            fallback_value=[],
            error_msg="Error getting search promotion instances",
        )

        # Add search promotions list URL
        search_promotions_url = f"{base}/admin/searchpicks/"
        
        # Add edit URLs only if we have instances
        if promotions:
            urls.append(format_url_tuple("Settings > Search promotions", None, "list", search_promotions_url))
            
            for promotion in promotions:
                promotion_edit_url = f"{base}/admin/searchpicks/{promotion.id}/"
                # Use the query_string as the identifier
                promo_name = getattr(promotion, "query_string", "Example")
                urls.append(
                    format_url_tuple(
                        f"Settings > Search promotions > {promo_name}",
                        None,
                        "edit",
                        promotion_edit_url,
                    )
                )
        else:
            # For models with no instances, show the list URL with a note
            if hasattr(output, "style"):
                output.write(output.style.WARNING("Note: SearchPromotion has no instances"))
            else:
                output.write("Note: SearchPromotion has no instances")
                
            # Add the list URL with NO INSTANCES note
            urls.append(
                format_url_tuple(
                    "Settings > Search promotions (NO INSTANCES)", 
                    None, 
                    "list", 
                    search_promotions_url
                )
            )
    else:
        # Add search promotions list URL when module not installed (for documentation)
        search_promotions_url = f"{base}/admin/searchpicks/"
        urls.append(
            format_url_tuple(
                "Settings > Search promotions", None, "list", search_promotions_url
            )
        )

    # Try to find other registered settings models
    if apps.is_installed("wagtail.contrib.settings"):
        # Add generic settings URL - these settings are site-wide
        generic_settings_url = f"{base}/admin/settings/base/genericsettings/"
        urls.append(
            format_url_tuple(
                "Settings > GenericSettings", None, "edit", generic_settings_url
            )
        )

        # Add site settings URL - these are per-site
        site = get_default_site()
        if site:
            site_settings_url = f"{base}/admin/settings/base/sitesettings/{site.id}/"
            urls.append(
                format_url_tuple(
                    f"Settings > SiteSettings > {site.hostname}",
                    None,
                    "edit",
                    site_settings_url,
                )
            )
        else:
            # Fallback if no sites found
            site_settings_url = f"{base}/admin/settings/base/sitesettings/1/"
            urls.append(
                format_url_tuple(
                    "Settings > SiteSettings > Example", None, "edit", site_settings_url
                )
            )

    # Forms - Add form pages and submissions URLs if wagtail.contrib.forms is installed
    if apps.is_installed("wagtail.contrib.forms"):
        output.write("Checking for form pages...")

        form_pages = safe_import(
            output,
            get_form_pages,
            fallback_value=[],
            error_msg="Error detecting form pages",
        )

        # Add the main forms listing URL
        forms_list_url = f"{base}/admin/forms/"
        urls.append(format_url_tuple("Forms Listing", None, "list", forms_list_url))

        for form_page in form_pages:
            # Add the form submissions listing URL
            submissions_url = f"{base}/admin/forms/submissions/{form_page.id}/"
            urls.append(
                format_url_tuple(
                    f"Form Submissions > {form_page.title}",
                    None,
                    "list",
                    submissions_url,
                )
            )

    return urls
