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
        ("Locales","locales"),
        ("Search promotions", "searchpicks"),
    ]

    for name, path in settings_sections:
        section_url = f"{base}/admin/{path}/"
        # Add special debug message for locales section
        if path == "locales":
            output.write(f"Using correct PLURAL URL for locales: {section_url}")
        urls.append(format_url_tuple(f"Settings > {name}", None, "list", section_url))

    # # Users management - try to get an admin user for edit URL
    # admins = safe_import(
    #     output,
    #     get_admin_user,
    #     fallback_value=[],
    #     error_msg="Error getting user instances",
    # )

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

    # Locales - try to get locales for edit URL
    # Try different import paths depending on Wagtail version
    locale_found = False
    Locale = None

    for import_path in [
        lambda: __import__("wagtail.models", fromlist=["Locale"]).Locale,
        lambda: __import__("wagtail.locales.models", fromlist=["Locale"]).Locale,
    ]:
        Locale = safe_import(output, import_path, error_msg=None)
        if Locale:
            locale_found = True
            break

    if locale_found:
        # Try to get locales
        locales = get_instance_sample(output, Locale, max_instances=max_instances)
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
            # Add an example edit URL even if we don't have a locale instance
            locale_edit_url = f"{base}/admin/locales/edit/1/"
            urls.append(
                format_url_tuple(
                    "Settings > Locales > Example", None, "edit", locale_edit_url
                )
            )
    elif "wagtail.i18n" in apps.settings.INSTALLED_APPS:
        # Fall back to older Wagtail versions
        locale_edit_url = f"{base}/admin/locales/edit/1/"
        urls.append(
            format_url_tuple(
                "Settings > Locales > Example", None, "edit", locale_edit_url
            )
        )
    else:
        # Add example URL for documentation purposes
        locale_edit_url = f"{base}/admin/locales/edit/1/"
        urls.append(
            format_url_tuple(
                "Settings > Locales > Example", None, "edit", locale_edit_url
            )
        )

    # Search promotions - try to get a search promotion for edit URL
    if apps.is_installed("wagtail.contrib.search_promotions"):
        promotions = safe_import(
            output,
            get_search_promotions,
            fallback_value=[],
            error_msg="Error getting search promotion instances",
        )

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
            # Add an example URL if no instances found
            promotion_edit_url = f"{base}/admin/searchpicks/1/"
            urls.append(
                format_url_tuple(
                    "Settings > Search promotions > Example",
                    None,
                    "edit",
                    promotion_edit_url,
                )
            )
    else:
        # Add an example URL even when module not installed
        promotion_edit_url = f"{base}/admin/searchpicks/1/"
        urls.append(
            format_url_tuple(
                "Settings > Search promotions > Example",
                None,
                "edit",
                promotion_edit_url,
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
