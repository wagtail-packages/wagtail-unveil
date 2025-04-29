from dataclasses import dataclass
from typing import List, Optional, Tuple

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import wagtail
from wagtail.models import Collection, Page, Site, Task, Workflow
from wagtail.contrib.redirects.models import Redirect
from wagtail.contrib.search_promotions.models import SearchPromotion
from wagtail.contrib.forms.models import AbstractEmailForm

from .base import BaseHelper, get_instance_sample

"""This file needs more work"""


@dataclass
class SettingsHelper(BaseHelper):
    """
    A dataclass that encapsulates Wagtail settings helper functionality.
    Developers can inherit from this class to extend its functionality.
    """
    
    def get_default_site(self):
        """Get the default site"""
        site = Site.objects.filter(is_default_site=True)
        return site.first() if site.exists() else None
    
    def get_admin_user(self):
        """Get an admin user"""
        User = get_user_model()
        admins = User.objects.filter(is_superuser=True)
        return admins.first() if admins.exists() else None
    
    def get_group(self):
        """Get a group"""
        groups = Group.objects.all()
        return groups.first() if groups.exists() else None
    
    def get_collections(self):
        """Get collections"""
        collections = Collection.objects.all().exclude(id=Collection.get_first_root_node().id)[:1]
        return collections if collections.exists() else []
    
    def get_redirects(self):
        """Get redirects"""
        redirects = Redirect.objects.all()[:1]
        return redirects if redirects.exists() else []
    
    def get_workflows(self):
        """Get workflows"""
        workflows = Workflow.objects.all()[:1]
        return workflows if workflows.exists() else []
    
    def get_tasks(self):
        """Get workflow tasks"""
        tasks = Task.objects.all()[:1]
        return tasks if tasks.exists() else []
    
    def get_search_promotions(self):
        """Get search promotions"""
        promotions = SearchPromotion.objects.all()[:1]
        return promotions if promotions.exists() else []
    
    def get_form_pages(self):
        """Get form pages"""
        form_pages = []
        for page in Page.objects.specific():
            if isinstance(page, AbstractEmailForm):
                form_pages.append(page)
        return form_pages[:5] if form_pages else []  # Limit to 5 to avoid too many URLs
    
    def collect_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """Get admin URLs for Wagtail settings"""
        # Check once for installed apps/features
        locales_app_installed = apps.is_installed("wagtail.locales")
        search_promotions_installed = apps.is_installed("wagtail.contrib.search_promotions")
        
        # Sites settings
        sites_url = f"{self.base}/admin/sites/"
        self.add_list_url("Settings > Sites", sites_url)
        
        # Try to get an existing site to create an edit URL
        site = self.get_default_site()
        if site:
            site_edit_url = f"{self.base}/admin/sites/{site.id}/"
            self.add_edit_url("Settings > Sites", site.hostname, site_edit_url)
            
            # Add delete URL for site
            site_delete_url = f"{self.base}/admin/sites/{site.id}/delete/"
            self.add_delete_url("Settings > Sites", site.hostname, site_delete_url)
        
        # Add other common settings sections
        settings_sections = [
            ("Collections", "collections"),
            ("Users", "users"),
            ("Groups", "groups"),
            ("Redirects", "redirects"),
            ("Workflows", "workflows/list"),
            ("Workflow tasks", "workflows/tasks/index"),
        ]
        
        # Only add Locales to settings_sections if it's explicitly installed in INSTALLED_APPS
        if locales_app_installed:
            settings_sections.append(("Locales", "locales"))
        
        for name, path in settings_sections:
            section_url = f"{self.base}/admin/{path}/"
            self.add_list_url(f"Settings > {name}", section_url)
        
        # Users management
        admin_user = self.get_admin_user()
        if admin_user:
            user_edit_url = f"{self.base}/admin/users/{admin_user.id}/"
            self.add_edit_url(
                "Settings > Users", admin_user.username, user_edit_url
            )
            
            # Add delete URL for user
            user_delete_url = f"{self.base}/admin/users/{admin_user.id}/delete/"
            self.add_delete_url(
                "Settings > Users", admin_user.username, user_delete_url
            )
        
        # Groups management
        if apps.is_installed("django.contrib.auth"):
            group = self.get_group()
            if group:
                group_edit_url = f"{self.base}/admin/groups/{group.id}/"
                self.add_edit_url(
                    "Settings > Groups", group.name, group_edit_url
                )
                
                # Add delete URL for group
                group_delete_url = f"{self.base}/admin/groups/{group.id}/delete/"
                self.add_delete_url(
                    "Settings > Groups", group.name, group_delete_url
                )
        
        # Collections management
        collections = self.get_collections()
        
        # Apply max_instances limit if more than one collection exists
        if len(collections) > self.max_instances and self.max_instances > 0:
            collections = collections[:self.max_instances]
        
        for collection in collections:
            collection_edit_url = f"{self.base}/admin/collections/{collection.id}/"
            self.add_edit_url(
                "Settings > Collections", collection.name, collection_edit_url
            )
            
            # Add delete URL for collection
            collection_delete_url = f"{self.base}/admin/collections/{collection.id}/delete/"
            self.add_delete_url(
                "Settings > Collections", collection.name, collection_delete_url
            )
        
        # Redirects
        if apps.is_installed("wagtail.contrib.redirects"):
            redirects = self.get_redirects()
            
            for redirect in redirects:
                redirect_edit_url = f"{self.base}/admin/redirects/{redirect.id}/"
                self.add_edit_url(
                    "Settings > Redirects", redirect.old_path, redirect_edit_url
                )
                
                # Add delete URL for redirect
                redirect_delete_url = f"{self.base}/admin/redirects/{redirect.id}/delete/"
                self.add_delete_url(
                    "Settings > Redirects", redirect.old_path, redirect_delete_url
                )
        
        # Workflows
        if hasattr(wagtail.models, "Workflow"):
            workflows = self.get_workflows()
            
            for workflow in workflows:
                workflow_edit_url = f"{self.base}/admin/workflows/edit/{workflow.id}/"
                self.add_edit_url(
                    "Settings > Workflows", workflow.name, workflow_edit_url
                )
                
                # Use correct URL pattern for workflow disable/delete operation
                workflow_delete_url = f"{self.base}/admin/workflows/disable/{workflow.id}/"
                self.add_delete_url(
                    "Settings > Workflows", workflow.name, workflow_delete_url
                )
        
        # Workflow tasks
        if hasattr(wagtail.models, "Task"):
            tasks = self.get_tasks()
            
            for task in tasks:
                task_edit_url = f"{self.base}/admin/workflows/tasks/edit/{task.id}/"
                self.add_edit_url(
                    "Settings > Workflow tasks", task.name, task_edit_url
                )
                
                # Use correct URL pattern for task disable/delete operation
                task_delete_url = f"{self.base}/admin/workflows/tasks/disable/{task.id}/"
                self.add_delete_url(
                    "Settings > Workflow tasks", task.name, task_delete_url
                )
        
        # Locales
        if locales_app_installed:
            try:
                from wagtail.models import Locale
                
                # Try to get locales
                locales = get_instance_sample(self.output, Locale, max_instances=self.max_instances)
                if locales:
                    # Only add actual locale instances if they exist
                    for locale in locales:
                        locale_edit_url = f"{self.base}/admin/locales/edit/{locale.id}/"
                        self.add_edit_url(
                            "Settings > Locales", locale.language_code, locale_edit_url
                        )
                        
                        # Add delete URL for locale
                        locale_delete_url = f"{self.base}/admin/locales/delete/{locale.id}/"
                        self.add_delete_url(
                            "Settings > Locales", locale.language_code, locale_delete_url
                        )
                else:
                    # Add an example URL only if no instances found
                    self.write_no_instances_message("Locale")
                    
                    locale_edit_url = f"{self.base}/admin/locales/edit/1/"
                    self.add_url_for_model_with_no_instances(
                        "Settings > Locales > Example", locale_edit_url
                    )
            except ImportError:
                # The Locale model isn't available
                if hasattr(self.output, "style"):
                    self.output.write(self.output.style.WARNING("Note: wagtail.locales is installed but Locale model is not available"))
                else:
                    self.output.write("Note: wagtail.locales is installed but Locale model is not available")
        
        # Search promotions
        if search_promotions_installed:
            promotions = self.get_search_promotions()
            
            # Add search promotions list URL
            search_promotions_url = f"{self.base}/admin/searchpicks/"
            
            # Add edit URLs only if we have instances
            if promotions:
                self.add_list_url("Settings > Search promotions", search_promotions_url)
                
                for promotion in promotions:
                    promotion_edit_url = f"{self.base}/admin/searchpicks/{promotion.id}/"
                    # Use the query_string as the identifier
                    promo_name = getattr(promotion, "query_string", "Example")
                    self.add_edit_url(
                        "Settings > Search promotions", promo_name, promotion_edit_url
                    )
                    
                    # Add delete URL for search promotion
                    promotion_delete_url = f"{self.base}/admin/searchpicks/{promotion.id}/delete/"
                    self.add_delete_url(
                        "Settings > Search promotions", promo_name, promotion_delete_url
                    )
            else:
                # For models with no instances, show the list URL with a note
                self.write_no_instances_message("SearchPromotion")
                
                # Add the list URL with NO INSTANCES note
                self.add_url_for_model_with_no_instances(
                    "Settings > Search promotions", search_promotions_url
                )
        else:
            # Add search promotions list URL when module not installed (for documentation)
            search_promotions_url = f"{self.base}/admin/searchpicks/"
            self.add_list_url("Settings > Search promotions", search_promotions_url)
        
        # Try to find other registered settings models
        if apps.is_installed("wagtail.contrib.settings"):
            # Add generic settings URL - these settings are site-wide
            generic_settings_url = f"{self.base}/admin/settings/base/genericsettings/"
            self.add_edit_url(
                "Settings", "GenericSettings", generic_settings_url
            )
            
            # Add site settings URL - these are per-site
            site = self.get_default_site()
            if site:
                site_settings_url = f"{self.base}/admin/settings/base/sitesettings/{site.id}/"
                self.add_edit_url(
                    "Settings > SiteSettings", site.hostname, site_settings_url
                )
            else:
                # Fallback if no sites found
                site_settings_url = f"{self.base}/admin/settings/base/sitesettings/1/"
                self.add_edit_url(
                    "Settings > SiteSettings", "Example", site_settings_url
                )
        
        # Forms - Add form pages and submissions URLs if wagtail.contrib.forms is installed
        if apps.is_installed("wagtail.contrib.forms"):
            self.output.write("Checking for form pages...")
            
            form_pages = self.get_form_pages()
            
            # Add the main forms listing URL
            forms_list_url = f"{self.base}/admin/forms/"
            self.add_list_url("Forms Listing", forms_list_url)
            
            for form_page in form_pages:
                # Add the form submissions listing URL
                submissions_url = f"{self.base}/admin/forms/submissions/{form_page.id}/"
                self.add_list_url(
                    f"Form Submissions > {form_page.title}", submissions_url
                )
        
        return self.urls
    
    def settings_admin_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """Return all settings URLs"""
        return self.collect_urls()


# Legacy wrapper function for backward compatibility
def get_settings_admin_urls(output, base_url, max_instances=1):
    """Get admin URLs for Wagtail settings"""
    helper = SettingsHelper(output, base_url, max_instances)
    return helper.settings_admin_urls()
