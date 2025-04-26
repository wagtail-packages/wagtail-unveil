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
        group_by = request.GET.get('group_by', '').lower()
        
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
        settings_urls = get_settings_admin_urls(output, base_url, max_instances)
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
        
        # Count backend and frontend URLs regardless of grouping
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
        
        # Add parameters to response metadata
        response_data = {
            'meta': {
                'max_instances': max_instances,
                'base_url': base_url,
                'group_by': group_by if group_by else 'none',
                'backend_count': len(backend_urls),
                'frontend_count': len(frontend_urls),
                'total_urls': len(urls_data)  # Total URLs collected
            }
        }
        
        # Group by backend/frontend
        if group_by == 'interface':
            grouped_data = {
                'backend': backend_urls,
                'frontend': frontend_urls
            }
            
            response_data['urls'] = grouped_data
            return JsonResponse(response_data)
        elif group_by == 'type':
            # Keep the original type grouping for backward compatibility
            grouped_data = {}
            
            for item in urls_data:
                url_type = item['url_type']
                if url_type not in grouped_data:
                    grouped_data[url_type] = []
                grouped_data[url_type].append(item)
            
            # Update metadata with counts for each type
            response_data['meta']['type_counts'] = {url_type: len(items) for url_type, items in grouped_data.items()}
            
            response_data['urls'] = grouped_data
            return JsonResponse(response_data)
        
        # No grouping, return flat list
        response_data['urls'] = urls_data
        return JsonResponse(response_data)
