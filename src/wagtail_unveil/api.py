from io import StringIO
from django.http import JsonResponse
from django.views import View

from .helpers.page_helpers import get_page_urls
from .helpers.snippet_helpers import get_snippet_urls, get_modelviewset_urls
from .helpers.modeladmin_helpers import get_modeladmin_urls
from .helpers.settings_helpers import get_settings_admin_urls
from .helpers.media_helpers import get_image_admin_urls, get_document_admin_urls


class UnveilApiView(View):
    """API view that returns a JSON representation of all URLs in the Wagtail admin."""
    
    def get(self, request, *args, **kwargs):
        # Create a StringIO object to capture any output/errors
        output = StringIO()
        
        # Parameters
        max_instances = int(request.GET.get('max_instances', 1))
        base_url = request.GET.get('base_url', "http://localhost:8000")
        
        # Collect all URLs
        urls_data = []
        
        # Collect page URLs
        page_urls = get_page_urls(output, base_url, max_instances)
        for model_name, url_type, url in page_urls:
            urls_data.append({
                'model_name': model_name,
                'url_type': url_type,
                'url': url
            })
        
        # Get snippet models and collect snippet URLs
        snippet_urls = get_snippet_urls(output, base_url, max_instances)
        for model_name, url_type, url in snippet_urls:
            urls_data.append({
                'model_name': model_name,
                'url_type': url_type,
                'url': url
            })
        
        # Create an empty dictionary for URL paths since we no longer get it from get_modelviewset_models()
        modelviewset_urls = get_modelviewset_urls(output, base_url, max_instances)
        for model_name, url_type, url in modelviewset_urls:
            urls_data.append({
                'model_name': model_name,
                'url_type': url_type,
                'url': url
            })
        
        # Get modeladmin models and collect modeladmin URLs
        modeladmin_urls = get_modeladmin_urls(output, base_url, max_instances)
        for model_name, url_type, url in modeladmin_urls:
            urls_data.append({
                'model_name': model_name,
                'url_type': url_type,
                'url': url
            })
        
        # Collect settings URLs
        settings_urls = get_settings_admin_urls(output, base_url)
        for model_name, url_type, url in settings_urls:
            urls_data.append({
                'model_name': model_name,
                'url_type': url_type,
                'url': url
            })
        
        # Get image URLs
        image_urls = get_image_admin_urls(output, base_url, max_instances)
        for model_name, url_type, url in image_urls:
            urls_data.append({
                'model_name': model_name,
                'url_type': url_type,
                'url': url
            })
            
        # Get document URLs
        document_urls = get_document_admin_urls(output, base_url, max_instances)
        for model_name, url_type, url in document_urls:
            urls_data.append({
                'model_name': model_name,
                'url_type': url_type,
                'url': url
            })
        
        # Group by backend/frontend
        group_by = request.GET.get('group_by', '').lower()
        
        if group_by == 'interface':
            # Group URLs into backend (admin) and frontend categories
            backend_urls = []
            frontend_urls = []
            
            for item in urls_data:
                url_type = item['url_type']
                url = item['url']
                
                # URLs with 'frontend' type are frontend, URLs with '/admin/' are backend,
                # all other URLs need to be categorized based on their characteristics
                if url_type == 'frontend':
                    frontend_urls.append(item)
                elif '/admin/' in url or url_type in ['admin', 'edit', 'list']:
                    backend_urls.append(item)
                else:
                    # If we can't determine, default to frontend
                    frontend_urls.append(item)
            
            grouped_data = {
                'backend': backend_urls,
                'frontend': frontend_urls
            }
            
            return JsonResponse({'urls': grouped_data})
        elif group_by == 'type':
            # Keep the original type grouping for backward compatibility
            grouped_data = {}
            for item in urls_data:
                url_type = item['url_type']
                if url_type not in grouped_data:
                    grouped_data[url_type] = []
                grouped_data[url_type].append(item)
            return JsonResponse({'urls': grouped_data})
            
        # No grouping, return flat list
        return JsonResponse({'urls': urls_data})