from django.urls import path

from .views import UnveilApiView

urlpatterns = [
    path(
        "urls/",
        UnveilApiView.as_view(),
        name="unveil_api_urls",
    ),
]