from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, OperationalError
from wagtail.models import Page, Site
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set

from .base import BaseHelper, format_url_tuple


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
        self.urls.append(
            format_url_tuple("All Pages Listing", None, "list", pages_listing_url)
        )
    
    def add_search_urls(self):
        """Add the search URLs - one with no results, one with results"""
        # Add URL with no results
        empty_search_url = f"{self.base}/admin/pages/search/?q=xyznonexistentsearchterm123"
        self.urls.append(
            format_url_tuple("Page Search (No Results)", None, "list", empty_search_url)
        )
        
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
        
        self.urls.append(
            format_url_tuple(result_description, None, "list", result_search_url)
        )
    
    def add_site_urls(self, site: Site):
        """Add URLs for a specific site"""
        # Get the root page for this site
        root_page = site.root_page
        
        # Add frontend URL - use base URL directly for the homepage
        site_url = f"{self.base}/"
        
        # Only add the frontend URL if we haven't added it yet
        if site_url not in self.added_frontend_urls:
            self.urls.append(
                format_url_tuple("Site default page", None, "frontend", site_url)
            )
            self.added_frontend_urls.add(site_url)
        
        # Always add admin edit URL for the root page
        admin_url = f"{self.base}/admin/pages/{root_page.id}/edit/"
        self.urls.append(
            format_url_tuple(
                "Site default page", root_page.title, "edit", admin_url
            )
        )
        
        # Add delete URL for the root page
        delete_url = f"{self.base}/admin/pages/{root_page.id}/delete/"
        self.urls.append(
            format_url_tuple(
                "Site default page", root_page.title, "delete", delete_url
            )
        )
        
        # Add the specific page explorer URL for the root page
        explorer_url = f"{self.base}/admin/pages/{root_page.id}/"
        self.urls.append(
            format_url_tuple(
                "Site default page explorer", root_page.title, "list", explorer_url
            )
        )
        
        # If this is the default site, also add the admin dashboard URL
        if site.is_default_site:
            dashboard_url = f"{self.base}/admin/"
            self.urls.append(
                format_url_tuple("Admin dashboard", None, "admin", dashboard_url)
            )
    
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


# Keep the original function for backward compatibility
def get_site_urls(output, base_url):
    """Get URLs for site default pages"""
    helper = SiteHelper(output=output, base_url=base_url, max_instances=1)
    return helper.collect_urls()