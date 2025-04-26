from django.urls import path

from .api import UnveilApiView

urlpatterns = [
    path(
        "urls/",
        UnveilApiView.as_view(),
        name="unveil_api_urls",
    ),
]