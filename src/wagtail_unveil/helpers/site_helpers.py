from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, OperationalError
from wagtail.models import Page, Site
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set

from .base import BaseHelper


@dataclass
class SiteHelper(BaseHelper):
    """Helper for collecting site-related admin URLs"""
    added_frontend_urls: Set[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.added_frontend_urls is None:
            self.added_frontend_urls = set()
    
    def add_general_pages_listing_url(self):
        """Add the general pages listing URL"""
        pages_listing_url = f"{self.base}/admin/pages/"
        self.add_list_url("All Pages Listing", pages_listing_url)
    
    def add_search_urls(self):
        """Add the search URLs - one with no results, one with results"""
        # Add URL with no results
        empty_search_url = f"{self.base}/admin/pages/search/?q=xyznonexistentsearchterm123"
        self.add_list_url("Page Search (No Results)", empty_search_url)
        
        # Add URL with results
        try:
            home_page = Page.objects.filter(depth=2).first()
            if home_page:
                # Extract a single word from the title that's likely to match
                title_word = home_page.title.split()[0]
                result_search_url = f"{self.base}/admin/pages/search/?q={title_word}"
                result_description = f"Page Search (With Results - '{title_word}')"
            else:
                # Fallback to a common word that's likely to be in any page
                result_search_url = f"{self.base}/admin/pages/search/?q=page"
                result_description = "Page Search (With Results - 'page')"
        except (
            AttributeError,
            ObjectDoesNotExist,
            DatabaseError,
            OperationalError,
            IndexError,
        ) as e:
            # Ultimate fallback if we can't query the database
            result_search_url = f"{self.base}/admin/pages/search/?q=the"
            result_description = f"Page Search (With Results - 'the') (Error: {str(e)})"
        
        self.add_list_url(result_description, result_search_url)
    
    def add_site_urls(self, site: Site):
        """Add URLs for a specific site"""
        # Get the root page for this site
        root_page = site.root_page
        
        # Add frontend URL - use base URL directly for the homepage
        site_url = f"{self.base}/"
        
        # Only add the frontend URL if we haven't added it yet
        if site_url not in self.added_frontend_urls:
            # Using tuple approach to create a custom frontend URL entry
            # (display_name, instance_name, url_type, url)
            self.urls.append(("Site default page", None, "frontend", site_url))
            self.added_frontend_urls.add(site_url)
        
        # Always add admin edit URL for the root page
        admin_url = f"{self.base}/admin/pages/{root_page.id}/edit/"
        self.add_edit_url("Site default page", root_page.title, admin_url)
        
        # Add delete URL for the root page
        delete_url = f"{self.base}/admin/pages/{root_page.id}/delete/"
        self.add_delete_url("Site default page", root_page.title, delete_url)
        
        # Add the specific page explorer URL for the root page
        explorer_url = f"{self.base}/admin/pages/{root_page.id}/"
        self.add_list_url(f"Site default page explorer ({root_page.title})", explorer_url)
        
        # If this is the default site, also add the admin dashboard URL
        if site.is_default_site:
            dashboard_url = f"{self.base}/admin/"
            # Using tuple approach to create a custom admin URL entry
            # (display_name, instance_name, url_type, url)
            self.urls.append(("Admin dashboard", None, "admin", dashboard_url))
    
    def collect_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """Collect all site-related admin URLs"""
        try:
            # Get all sites configured in Wagtail
            sites = Site.objects.all()
            
            # Add common URLs
            self.add_general_pages_listing_url()
            self.add_search_urls()
            
            # Add URLs for each site
            for site in sites:
                self.add_site_urls(site)
                
        except (
            AttributeError,
            ObjectDoesNotExist,
            DatabaseError,
            OperationalError,
        ) as e:
            if hasattr(self.output, "style"):
                self.output.write(self.output.style.WARNING(f"Error getting site URLs: {str(e)}"))
            else:
                self.output.write(f"Error getting site URLs: {str(e)}")
                
        return self.urls
    
    def site_urls(self) -> List[Tuple[str, Optional[str], str, str]]:
        """
        Get all site-related admin URLs.
        This method is a wrapper around the collect_urls method.
        """
        return self.collect_urls()
