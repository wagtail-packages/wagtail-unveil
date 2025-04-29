from wagtail.admin.views.reports import ReportView
from collections import namedtuple
from io import StringIO
from wagtail.admin.widgets.button import HeaderButton
from django.conf import settings

from .helpers.page_helpers import PageHelper
from .helpers.snippet_helpers import SnippetHelper
from .helpers.modelviewset_helpers import ModelViewSetHelper
# from .helpers.modeladmin_helpers import ModelAdminHelper
from .helpers.settings_helpers import get_settings_admin_urls
from .helpers.image_helpers import ImageHelper
from .helpers.document_helpers import DocumentHelper


class UnveilReportView(ReportView):
    index_url_name = "unveil_report"
    index_results_url_name = "unveil_report_results"
    header_icon = "tasks"
    template_name = "wagtail_unveil/unveil_report.html"
    results_template_name = "wagtail_unveil/unveil_report_results.html"
    page_title = "Unveil URL's"
    list_export = [
        "id",
        "model_name",
        "url_type",
        "url",
    ]
    export_headings = {
        "id": "ID",
        "model_name": "Model Name",
        "url_type": "URL Type",
        "url": "URL",
    }
    paginate_by = None
    
    def get_header_buttons(self):
         return [
            HeaderButton(
                label="Run Checks",
                icon_name="link",
                attrs={
                    "data-action": "check-urls",
                },
            ),
        ]

    def get_filterset_kwargs(self):
        # Get the base queryset and pass it to the filterset
        kwargs = super().get_filterset_kwargs()
        kwargs["queryset"] = self.get_queryset()
        return kwargs
    
    def get_base_queryset(self):
        # Return the base queryset for the report
        return self.get_queryset()

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
        # Get max_instances from settings with a default of 1
        max_instances = getattr(settings, 'WAGTAIL_UNVEIL_MAX_INSTANCES', 1)
        base_url = "http://localhost:8000"  # Default base URL
        
        # Collect page URLs
        page_helper = PageHelper(output, base_url, max_instances)
        page_urls = page_helper.page_urls()
        for display_name, instance_name, url_type, url in page_urls:
            all_urls.append(UrlEntry(counter, display_name, url_type, url))
            counter += 1
        
        # Get snippet models and collect snippet URLs
        snippet_helper = SnippetHelper(output, base_url, max_instances)
        snippet_urls = snippet_helper.snippet_urls()
        for display_name, instance_name, url_type, url in snippet_urls:
            all_urls.append(UrlEntry(counter, display_name, url_type, url))
            counter += 1
        
        # Get ModelViewSet URLs using the ModelViewSetHelper class
        modelviewset_helper = ModelViewSetHelper(output, base_url, max_instances)
        modelviewset_urls = modelviewset_helper.modelviewset_urls()
        for display_name, instance_name, url_type, url in modelviewset_urls:
            all_urls.append(UrlEntry(counter, display_name, url_type, url))
            counter += 1
        
        # # Get modeladmin models and collect modeladmin URLs
        # modeladmin_helper = ModelAdminHelper(output, base_url, max_instances)
        # modeladmin_urls = modeladmin_helper.modeladmin_urls()
        # for display_name, instance_name, url_type, url in modeladmin_urls:
        #     all_urls.append(UrlEntry(counter, display_name, url_type, url))
        #     counter += 1
        
        # Collect settings URLs
        settings_urls = get_settings_admin_urls(output, base_url)
        for display_name, instance_name, url_type, url in settings_urls:
            all_urls.append(UrlEntry(counter, display_name, url_type, url))
            counter += 1
        
        # Get image URLs
        image_helper = ImageHelper(output, base_url, max_instances)
        image_urls = image_helper.image_urls()
        for display_name, instance_name, url_type, url in image_urls:
            all_urls.append(UrlEntry(counter, display_name, url_type, url))
            counter += 1
            
        # Get document URLs
        document_helper = DocumentHelper(output, base_url, max_instances)
        document_urls = document_helper.document_urls()
        for display_name, instance_name, url_type, url in document_urls:
            all_urls.append(UrlEntry(counter, display_name, url_type, url))
            counter += 1
            
        return all_urls
