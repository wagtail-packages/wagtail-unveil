from wagtail.admin.views.reports import ReportView
from collections import namedtuple
from io import StringIO
from django.http import JsonResponse
from django.views import View

from .helpers.page_helpers import get_page_urls, get_page_models
from .helpers.snippet_helpers import get_snippet_urls, get_modelviewset_urls
from .helpers.modeladmin_helpers import get_modeladmin_urls, get_modeladmin_models
from .helpers.settings_helpers import get_settings_admin_urls
from .helpers.media_helpers import get_image_admin_urls, get_document_admin_urls


class UnveilReportView(ReportView):
    index_url_name = "unveil_report"
    index_results_url_name = "unveil_report_results"
    header_icon = "user"
    results_template_name = "wagtail_unveil/unveil_report_results.html"
    page_title = "Unveil Report"

    def get_queryset(self):
        # Create a StringIO object to capture any output/errors
        output = StringIO()
        
        # Create a named tuple to represent URL entries
        UrlEntry = namedtuple('UrlEntry', ['id', 'model_name', 'url_type', 'url'])
        
        # Collect URLs from different helpers
        all_urls = []
        
        # We'll use a counter for IDs
        counter = 1
        
        # Get URLs from different sources using helper functions
        # Max instances set to 1 for simplicity - can be made configurable later
        max_instances = 1
        base_url = "http://localhost:8000"  # Default base URL
        
        # Collect page URLs
        page_urls = get_page_urls(output, base_url, max_instances)
        for model_name, url_type, url in page_urls:
            all_urls.append(UrlEntry(counter, model_name, url_type, url))
            counter += 1
        
        # Get snippet models and collect snippet URLs
        snippet_urls = get_snippet_urls(output, base_url, max_instances)
        for model_name, url_type, url in snippet_urls:
            all_urls.append(UrlEntry(counter, model_name, url_type, url))
            counter += 1
        
        # Create an empty dictionary for URL paths since we no longer get it from get_modelviewset_models()
        modelviewset_urls = get_modelviewset_urls(output, base_url, max_instances)
        for model_name, url_type, url in modelviewset_urls:
            all_urls.append(UrlEntry(counter, model_name, url_type, url))
            counter += 1
        
        # Get modeladmin models and collect modeladmin URLs
        modeladmin_models, modeladmin_url_paths = get_modeladmin_models()
        modeladmin_urls = get_modeladmin_urls(output, modeladmin_models, modeladmin_url_paths, base_url, max_instances)
        for model_name, url_type, url in modeladmin_urls:
            all_urls.append(UrlEntry(counter, model_name, url_type, url))
            counter += 1
        
        # Collect settings URLs
        settings_urls = get_settings_admin_urls(output, base_url)
        for model_name, url_type, url in settings_urls:
            all_urls.append(UrlEntry(counter, model_name, url_type, url))
            counter += 1
        
        # Get image URLs
        image_urls = get_image_admin_urls(output, base_url, max_instances)
        for model_name, url_type, url in image_urls:
            all_urls.append(UrlEntry(counter, model_name, url_type, url))
            counter += 1
            
        # Get document URLs
        document_urls = get_document_admin_urls(output, base_url, max_instances)
        for model_name, url_type, url in document_urls:
            all_urls.append(UrlEntry(counter, model_name, url_type, url))
            counter += 1
            
        return all_urls


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
        
        # Get page models first
        page_models = get_page_models()
        
        # Collect page URLs
        page_urls = get_page_urls(output, page_models, base_url, max_instances)
        for model_name, url_type, url in page_urls:
            urls_data.append({
                'model_name': model_name,
                'url_type': url_type,
                'url': url
            })
        
        # Get snippet models and collect snippet URLs
        from wagtail.snippets.models import get_snippet_models
        snippet_models = get_snippet_models()
        snippet_urls = get_snippet_urls(output, snippet_models, base_url, max_instances)
        for model_name, url_type, url in snippet_urls:
            urls_data.append({
                'model_name': model_name,
                'url_type': url_type,
                'url': url
            })
        
        # Create an empty dictionary for URL paths since we no longer get it from get_modelviewset_models()
        modelviewset_url_paths = {}
        modelviewset_urls = get_modelviewset_urls(output, modelviewset_url_paths, base_url, max_instances)
        for model_name, url_type, url in modelviewset_urls:
            urls_data.append({
                'model_name': model_name,
                'url_type': url_type,
                'url': url
            })
        
        # Get modeladmin models and collect modeladmin URLs
        modeladmin_models, modeladmin_url_paths = get_modeladmin_models()
        modeladmin_urls = get_modeladmin_urls(output, modeladmin_models, modeladmin_url_paths, base_url, max_instances)
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
        
        # Group by types if requested
        if request.GET.get('group_by_type', 'false').lower() == 'true':
            grouped_data = {}
            for item in urls_data:
                url_type = item['url_type']
                if url_type not in grouped_data:
                    grouped_data[url_type] = []
                grouped_data[url_type].append(item)
            return JsonResponse({'urls': grouped_data})
        
        # Return the JSON response
        return JsonResponse({'urls': urls_data})