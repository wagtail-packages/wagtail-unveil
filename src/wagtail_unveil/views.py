from wagtail.admin.views.reports import ReportView


class UnveilReportView(ReportView):
    index_url_name = "unveil_report"
    index_results_url_name = "unveil_report_results"
    header_icon = "user"
    results_template_name = "wagtail_unveil/unveil_report_results.html"
    page_title = "Unveil Report"

    def get_queryset(self):
        # Create a basic implementation using all URL listing functionality
        # Get base URL from the default site or use a fallback
        return []