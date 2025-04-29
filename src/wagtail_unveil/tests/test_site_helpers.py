from django.test import TestCase
from django.db import DatabaseError
from io import StringIO
from unittest.mock import Mock, patch

from wagtail_unveil.helpers.site_helpers import SiteHelper


class SiteHelperTests(TestCase):
    """Tests for the SiteHelper class."""
    
    def setUp(self):
        self.output = StringIO()
        self.base_url = "http://testserver"
        self.max_instances = 2
        
        # Create mock Site and Page instances
        self.mock_root_page = Mock()
        self.mock_root_page.id = 1
        self.mock_root_page.title = "Root Page"
        
        self.mock_site1 = Mock()
        self.mock_site1.id = 1
        self.mock_site1.root_page = self.mock_root_page
        self.mock_site1.is_default_site = True
        
        self.mock_site2 = Mock()
        self.mock_site2.id = 2
        self.mock_site2.root_page = self.mock_root_page
        self.mock_site2.is_default_site = False

    def test_initialization(self):
        """Test SiteHelper initialization sets up the correct attributes."""
        helper = SiteHelper(self.output, self.base_url, self.max_instances)
        self.assertEqual(helper.base, self.base_url.rstrip('/'))
        self.assertEqual(helper.added_frontend_urls, set())
    
    def test_add_general_pages_listing_url(self):
        """Test add_general_pages_listing_url adds the correct URL."""
        helper = SiteHelper(self.output, self.base_url, self.max_instances)
        helper.add_general_pages_listing_url()
        
        self.assertEqual(len(helper.urls), 1)
        self.assertEqual(helper.urls[0][0], "All Pages Listing")
        self.assertEqual(helper.urls[0][2], "list")
        self.assertEqual(helper.urls[0][3], "http://testserver/admin/pages/")
    
    def test_add_search_urls_with_home_page(self):
        """Test add_search_urls when a home page exists."""
        helper = SiteHelper(self.output, self.base_url, self.max_instances)
        
        with patch('wagtail_unveil.helpers.site_helpers.Page.objects.filter') as mock_filter:
            mock_home_page = Mock()
            mock_home_page.title = "Welcome to Wagtail"
            mock_filter.return_value.first.return_value = mock_home_page
            
            helper.add_search_urls()
            
            # Should have two URLs: one with no results and one with results
            self.assertEqual(len(helper.urls), 2)
            
            # Check URL with no results
            self.assertEqual(helper.urls[0][0], "Page Search (No Results)")
            self.assertEqual(helper.urls[0][3], "http://testserver/admin/pages/search/?q=xyznonexistentsearchterm123")
            
            # Check URL with results
            self.assertEqual(helper.urls[1][0], "Page Search (With Results - 'Welcome')")
            self.assertEqual(helper.urls[1][3], "http://testserver/admin/pages/search/?q=Welcome")
    
    def test_add_search_urls_without_home_page(self):
        """Test add_search_urls when no home page exists."""
        helper = SiteHelper(self.output, self.base_url, self.max_instances)
        
        with patch('wagtail_unveil.helpers.site_helpers.Page.objects.filter') as mock_filter:
            mock_filter.return_value.first.return_value = None
            
            helper.add_search_urls()
            
            # Should have two URLs: one with no results and one with results
            self.assertEqual(len(helper.urls), 2)
            
            # Check URL with no results
            self.assertEqual(helper.urls[0][0], "Page Search (No Results)")
            
            # Check URL with results (fallback to "page")
            self.assertEqual(helper.urls[1][0], "Page Search (With Results - 'page')")
            self.assertEqual(helper.urls[1][3], "http://testserver/admin/pages/search/?q=page")
    
    def test_add_search_urls_with_database_error(self):
        """Test add_search_urls handles database errors gracefully."""
        helper = SiteHelper(self.output, self.base_url, self.max_instances)
        
        with patch('wagtail_unveil.helpers.site_helpers.Page.objects.filter') as mock_filter:
            mock_filter.side_effect = DatabaseError("Database error")
            
            helper.add_search_urls()
            
            # Should have two URLs: one with no results and one with results
            self.assertEqual(len(helper.urls), 2)
            
            # Check URL with results (ultimate fallback to "the")
            self.assertEqual(helper.urls[1][0], "Page Search (With Results - 'the') (Error: Database error)")
            self.assertEqual(helper.urls[1][3], "http://testserver/admin/pages/search/?q=the")
    
    def test_add_site_urls(self):
        """Test add_site_urls for a specific site."""
        helper = SiteHelper(self.output, self.base_url, self.max_instances)
        helper.add_site_urls(self.mock_site1)
        
        # Should have 5 URLs: frontend, edit, delete, explorer, dashboard (since it's the default site)
        self.assertEqual(len(helper.urls), 5)
        
        # Check frontend URL
        self.assertEqual(helper.urls[0][0], "Site default page")
        self.assertEqual(helper.urls[0][2], "frontend")
        self.assertEqual(helper.urls[0][3], "http://testserver/")
        
        # Check edit URL
        self.assertEqual(helper.urls[1][0], "Site default page (Root Page)")
        self.assertEqual(helper.urls[1][1], "Root Page")
        self.assertEqual(helper.urls[1][2], "edit")
        self.assertEqual(helper.urls[1][3], "http://testserver/admin/pages/1/edit/")
        
        # Check delete URL
        self.assertEqual(helper.urls[2][0], "Site default page (Root Page)")
        self.assertEqual(helper.urls[2][1], "Root Page")
        self.assertEqual(helper.urls[2][2], "delete")
        self.assertEqual(helper.urls[2][3], "http://testserver/admin/pages/1/delete/")
        
        # Check explorer URL
        self.assertEqual(helper.urls[3][0], "Site default page explorer (Root Page)")
        self.assertEqual(helper.urls[3][2], "list")
        self.assertEqual(helper.urls[3][3], "http://testserver/admin/pages/1/")
        
        # Check dashboard URL (added for default site)
        self.assertEqual(helper.urls[4][0], "Admin dashboard")
        self.assertEqual(helper.urls[4][2], "admin")
        self.assertEqual(helper.urls[4][3], "http://testserver/admin/")
    
    def test_add_site_urls_for_default_site(self):
        """Test add_site_urls adds dashboard URL for default site."""
        helper = SiteHelper(self.output, self.base_url, self.max_instances)
        helper.add_site_urls(self.mock_site1)  # Default site
        
        # Should have 5 URLs: frontend, edit, delete, explorer, dashboard
        self.assertEqual(len(helper.urls), 5)
        
        # Check dashboard URL
        self.assertEqual(helper.urls[4][0], "Admin dashboard")
        self.assertEqual(helper.urls[4][2], "admin")
        self.assertEqual(helper.urls[4][3], "http://testserver/admin/")
    
    def test_add_site_urls_for_non_default_site(self):
        """Test add_site_urls doesn't add dashboard URL for non-default site."""
        helper = SiteHelper(self.output, self.base_url, self.max_instances)
        helper.add_site_urls(self.mock_site2)  # Non-default site
        
        # Should have 4 URLs: frontend, edit, delete, explorer (no dashboard)
        self.assertEqual(len(helper.urls), 4)
        
        # No dashboard URL should be present
        dashboard_urls = [url for url in helper.urls if url[0] == "Admin dashboard"]
        self.assertEqual(len(dashboard_urls), 0)
    
    def test_add_site_urls_duplicate_frontend_url(self):
        """Test add_site_urls doesn't add duplicate frontend URLs."""
        helper = SiteHelper(self.output, self.base_url, self.max_instances)
        
        # Add site1
        helper.add_site_urls(self.mock_site1)
        
        # Clear all URLs except frontend URL
        frontend_url = helper.urls[0]
        helper.urls = [frontend_url]
        
        # Add site1 again
        helper.add_site_urls(self.mock_site1)
        
        # Should have 5 URLs: 1 frontend + 3 admin URLs + dashboard URL (since it's the default site)
        self.assertEqual(len(helper.urls), 5)
        
        # Count frontend URLs - should be only 1
        frontend_urls = [url for url in helper.urls if url[2] == "frontend"]
        self.assertEqual(len(frontend_urls), 1)
    
    @patch('wagtail_unveil.helpers.site_helpers.Site.objects.all')
    def test_collect_urls(self, mock_site_objects_all):
        """Test collect_urls method gathers all site URLs."""
        mock_site_objects_all.return_value = [self.mock_site1, self.mock_site2]
        
        helper = SiteHelper(self.output, self.base_url, self.max_instances)
        result = helper.collect_urls()
        
        # Verify all the expected URLs were collected
        # 1 general pages listing + 2 search URLs + 
        # 5 URLs for default site + 4 URLs for non-default site
        self.assertEqual(len(result), 11)
    
    @patch('wagtail_unveil.helpers.site_helpers.Site.objects.all')
    def test_collect_urls_with_database_error(self, mock_site_objects_all):
        """Test collect_urls handles database errors gracefully."""
        mock_site_objects_all.side_effect = DatabaseError("Database error")
        
        helper = SiteHelper(self.output, self.base_url, self.max_instances)
        result = helper.collect_urls()
        
        # Should have no URLs
        self.assertEqual(len(result), 0)
        
        # Verify error message was written to output
        self.assertIn("Error getting site URLs: Database error", self.output.getvalue())
    
    def test_site_urls_calls_collect_urls(self):
        """Test site_urls method calls collect_urls."""
        helper = SiteHelper(self.output, self.base_url, self.max_instances)
        # Mock the collect_urls method
        helper.collect_urls = Mock(return_value=["url1", "url2"])
        
        result = helper.site_urls()
        
        # Verify collect_urls was called
        helper.collect_urls.assert_called_once()
        self.assertEqual(result, ["url1", "url2"])