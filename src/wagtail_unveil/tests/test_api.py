from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from unittest.mock import patch
import json

from wagtail_unveil.api import UnveilApiView


class UnveilApiViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = UnveilApiView.as_view()
        
        # Create test data to mock the responses from the helper functions
        self.mock_page_urls = [
            ('Page.Model1', 'edit', 'http://testserver/admin/pages/1/edit/'),
            ('Page.Model1', 'frontend', 'http://testserver/page1/'),
            ('Page.Model2', 'list', 'http://testserver/admin/pages/'),
        ]
        
        self.mock_snippet_urls = [
            ('Snippet.Model1', 'edit', 'http://testserver/admin/snippets/app/model1/1/'),
            ('Snippet.Model1', 'list', 'http://testserver/admin/snippets/app/model1/'),
        ]
        
        self.mock_modelviewset_urls = [
            ('ViewSet.Model1', 'edit', 'http://testserver/admin/viewsets/app/model1/1/'),
            ('ViewSet.Model1', 'list', 'http://testserver/admin/viewsets/app/model1/'),
        ]
        
        self.mock_modeladmin_urls = [
            ('Admin.Model1', 'edit', 'http://testserver/admin/app/model1/1/'),
            ('Admin.Model1', 'list', 'http://testserver/admin/app/model1/'),
        ]
        
        self.mock_settings_urls = [
            ('Settings', 'edit', 'http://testserver/admin/settings/'),
        ]
        
        self.mock_image_urls = [
            ('Image', 'edit', 'http://testserver/admin/images/1/'),
            ('Image', 'list', 'http://testserver/admin/images/'),
        ]
        
        self.mock_document_urls = [
            ('Document', 'edit', 'http://testserver/admin/documents/1/'),
            ('Document', 'list', 'http://testserver/admin/documents/'),
        ]

    @patch('wagtail_unveil.api.get_page_urls')
    @patch('wagtail_unveil.api.get_snippet_urls')
    @patch('wagtail_unveil.api.get_modelviewset_urls')
    @patch('wagtail_unveil.api.get_modeladmin_urls')
    @patch('wagtail_unveil.api.get_settings_admin_urls')
    @patch('wagtail_unveil.api.get_image_admin_urls')
    @patch('wagtail_unveil.api.get_document_admin_urls')
    def test_get_no_grouping(self, mock_doc_urls, mock_img_urls, mock_settings_urls, 
                             mock_admin_urls, mock_viewset_urls, mock_snippet_urls, mock_page_urls):
        """Test the API view with no grouping."""
        # Set up the mocks to return our test data
        mock_page_urls.return_value = self.mock_page_urls
        mock_snippet_urls.return_value = self.mock_snippet_urls
        mock_viewset_urls.return_value = self.mock_modelviewset_urls
        mock_admin_urls.return_value = self.mock_modeladmin_urls
        mock_settings_urls.return_value = self.mock_settings_urls
        mock_img_urls.return_value = self.mock_image_urls
        mock_doc_urls.return_value = self.mock_document_urls
        
        # Create a test request with no grouping
        request = self.factory.get('/api/unveil/')
        
        # Call the view
        response = self.view(request)
        
        # Check response type and status code
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        
        # Parse the response JSON
        response_data = json.loads(response.content)
        
        # Check the response structure
        self.assertIn('meta', response_data)
        self.assertIn('urls', response_data)
        
        # Check that metadata is correct
        self.assertEqual(response_data['meta']['group_by'], 'none')
        self.assertEqual(response_data['meta']['base_url'], 'http://localhost:8000')
        self.assertEqual(response_data['meta']['max_instances'], 1)
        
        # Check counts
        total_test_urls = (len(self.mock_page_urls) + len(self.mock_snippet_urls) +
                          len(self.mock_modelviewset_urls) + len(self.mock_modeladmin_urls) +
                          len(self.mock_settings_urls) + len(self.mock_image_urls) +
                          len(self.mock_document_urls))
        
        self.assertEqual(response_data['meta']['total_urls'], total_test_urls)
        
        # Check that we have the backend and frontend counts
        self.assertIn('backend_count', response_data['meta'])
        self.assertIn('frontend_count', response_data['meta'])
        
        # Check that urls is a flat list
        self.assertIsInstance(response_data['urls'], list)
        self.assertEqual(len(response_data['urls']), total_test_urls)
        
        # Check that each item in the list has the expected structure
        for item in response_data['urls']:
            self.assertIn('model_name', item)
            self.assertIn('url_type', item)
            self.assertIn('url', item)

    @patch('wagtail_unveil.api.get_page_urls')
    @patch('wagtail_unveil.api.get_snippet_urls')
    @patch('wagtail_unveil.api.get_modelviewset_urls')
    @patch('wagtail_unveil.api.get_modeladmin_urls')
    @patch('wagtail_unveil.api.get_settings_admin_urls')
    @patch('wagtail_unveil.api.get_image_admin_urls')
    @patch('wagtail_unveil.api.get_document_admin_urls')
    def test_get_group_by_interface(self, mock_doc_urls, mock_img_urls, mock_settings_urls, 
                                    mock_admin_urls, mock_viewset_urls, mock_snippet_urls, mock_page_urls):
        """Test the API view with grouping by interface."""
        # Set up the mocks to return our test data
        mock_page_urls.return_value = self.mock_page_urls
        mock_snippet_urls.return_value = self.mock_snippet_urls
        mock_viewset_urls.return_value = self.mock_modelviewset_urls
        mock_admin_urls.return_value = self.mock_modeladmin_urls
        mock_settings_urls.return_value = self.mock_settings_urls
        mock_img_urls.return_value = self.mock_image_urls
        mock_doc_urls.return_value = self.mock_document_urls
        
        # Create a test request with interface grouping
        request = self.factory.get('/api/unveil/', {'group_by': 'interface'})
        
        # Call the view
        response = self.view(request)
        
        # Check response type and status code
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        
        # Parse the response JSON
        response_data = json.loads(response.content)
        
        # Check the response structure
        self.assertIn('meta', response_data)
        self.assertIn('urls', response_data)
        
        # Check that metadata is correct
        self.assertEqual(response_data['meta']['group_by'], 'interface')
        
        # Check that counts match our test data
        backend_urls_count = sum(1 for urls in [
            self.mock_page_urls, self.mock_snippet_urls, self.mock_modelviewset_urls,
            self.mock_modeladmin_urls, self.mock_settings_urls, self.mock_image_urls,
            self.mock_document_urls
        ] for model, url_type, url in urls if url_type != 'frontend' and '/admin/' in url or url_type in ['admin', 'edit', 'list'])
        
        frontend_urls_count = sum(1 for urls in [
            self.mock_page_urls, self.mock_snippet_urls, self.mock_modelviewset_urls,
            self.mock_modeladmin_urls, self.mock_settings_urls, self.mock_image_urls,
            self.mock_document_urls
        ] for model, url_type, url in urls if url_type == 'frontend' or ('/admin/' not in url and url_type not in ['admin', 'edit', 'list']))
        
        self.assertEqual(response_data['meta']['backend_count'], backend_urls_count)
        self.assertEqual(response_data['meta']['frontend_count'], frontend_urls_count)
        
        # Check that urls is a dictionary with backend and frontend keys
        self.assertIsInstance(response_data['urls'], dict)
        self.assertIn('backend', response_data['urls'])
        self.assertIn('frontend', response_data['urls'])
        
        # Check that the backend and frontend lists have the correct number of items
        self.assertEqual(len(response_data['urls']['backend']), backend_urls_count)
        self.assertEqual(len(response_data['urls']['frontend']), frontend_urls_count)

    @patch('wagtail_unveil.api.get_page_urls')
    @patch('wagtail_unveil.api.get_snippet_urls')
    @patch('wagtail_unveil.api.get_modelviewset_urls')
    @patch('wagtail_unveil.api.get_modeladmin_urls')
    @patch('wagtail_unveil.api.get_settings_admin_urls')
    @patch('wagtail_unveil.api.get_image_admin_urls')
    @patch('wagtail_unveil.api.get_document_admin_urls')
    def test_get_group_by_type(self, mock_doc_urls, mock_img_urls, mock_settings_urls, 
                               mock_admin_urls, mock_viewset_urls, mock_snippet_urls, mock_page_urls):
        """Test the API view with grouping by type."""
        # Set up the mocks to return our test data
        mock_page_urls.return_value = self.mock_page_urls
        mock_snippet_urls.return_value = self.mock_snippet_urls
        mock_viewset_urls.return_value = self.mock_modelviewset_urls
        mock_admin_urls.return_value = self.mock_modeladmin_urls
        mock_settings_urls.return_value = self.mock_settings_urls
        mock_img_urls.return_value = self.mock_image_urls
        mock_doc_urls.return_value = self.mock_document_urls
        
        # Create a test request with type grouping
        request = self.factory.get('/api/unveil/', {'group_by': 'type'})
        
        # Call the view
        response = self.view(request)
        
        # Check response type and status code
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        
        # Parse the response JSON
        response_data = json.loads(response.content)
        
        # Check the response structure
        self.assertIn('meta', response_data)
        self.assertIn('urls', response_data)
        
        # Check that metadata is correct
        self.assertEqual(response_data['meta']['group_by'], 'type')
        
        # Check that we have type_counts in the metadata
        self.assertIn('type_counts', response_data['meta'])
        
        # Get unique url_types from our test data
        url_types = set()
        for urls in [self.mock_page_urls, self.mock_snippet_urls, self.mock_modelviewset_urls,
                     self.mock_modeladmin_urls, self.mock_settings_urls, self.mock_image_urls,
                     self.mock_document_urls]:
            for _, url_type, _ in urls:
                url_types.add(url_type)
        
        # Check that we have all url_types as keys in the grouped data
        for url_type in url_types:
            self.assertIn(url_type, response_data['urls'])
            
        # Check that the type counts match the number of URLs for each type
        for url_type in url_types:
            count = sum(1 for urls in [
                self.mock_page_urls, self.mock_snippet_urls, self.mock_modelviewset_urls,
                self.mock_modeladmin_urls, self.mock_settings_urls, self.mock_image_urls,
                self.mock_document_urls
            ] for _, t, _ in urls if t == url_type)
            
            self.assertEqual(response_data['meta']['type_counts'][url_type], count)
            self.assertEqual(len(response_data['urls'][url_type]), count)

    @patch('wagtail_unveil.api.get_page_urls')
    @patch('wagtail_unveil.api.get_snippet_urls')
    @patch('wagtail_unveil.api.get_modelviewset_urls')
    @patch('wagtail_unveil.api.get_modeladmin_urls')
    @patch('wagtail_unveil.api.get_settings_admin_urls')
    @patch('wagtail_unveil.api.get_image_admin_urls')
    @patch('wagtail_unveil.api.get_document_admin_urls')
    def test_get_with_custom_parameters(self, mock_doc_urls, mock_img_urls, mock_settings_urls, 
                                        mock_admin_urls, mock_viewset_urls, mock_snippet_urls, mock_page_urls):
        """Test the API view with custom parameters."""
        # Set up the mocks to return our test data
        mock_page_urls.return_value = self.mock_page_urls
        mock_snippet_urls.return_value = self.mock_snippet_urls
        mock_viewset_urls.return_value = self.mock_modelviewset_urls
        mock_admin_urls.return_value = self.mock_modeladmin_urls
        mock_settings_urls.return_value = self.mock_settings_urls
        mock_img_urls.return_value = self.mock_image_urls
        mock_doc_urls.return_value = self.mock_document_urls
        
        # Create a test request with custom parameters
        request = self.factory.get('/api/unveil/', {
            'max_instances': '5',
            'base_url': 'https://example.com',
        })
        
        # Call the view
        response = self.view(request)
        
        # Check response type and status code
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        
        # Parse the response JSON
        response_data = json.loads(response.content)
        
        # Check that the custom parameters were used
        self.assertEqual(response_data['meta']['max_instances'], 5)
        self.assertEqual(response_data['meta']['base_url'], 'https://example.com')
        
        # Verify that the helper functions were called with the custom parameters
        mock_page_urls.assert_called_once()
        self.assertEqual(mock_page_urls.call_args[0][1], 'https://example.com')
        self.assertEqual(mock_page_urls.call_args[0][2], 5)
        
        # Check the same for other helper functions
        for mock_func in [mock_snippet_urls, mock_viewset_urls, mock_admin_urls, 
                          mock_settings_urls, mock_img_urls, mock_doc_urls]:
            mock_func.assert_called_once()
            self.assertEqual(mock_func.call_args[0][1], 'https://example.com')
            self.assertEqual(mock_func.call_args[0][2], 5)