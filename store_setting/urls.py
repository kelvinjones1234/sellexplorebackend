from django.urls import path

from .views import ConfigurationsView, PublicConfigurationsView, LogoView, CoverView

urlpatterns = [
    path("configurations/", ConfigurationsView.as_view(), name="configurations"),
    path(
        "configurations/<str:store_name>/",
        PublicConfigurationsView.as_view(),
        name="public-configurations",
    ),
    path("logo/", LogoView.as_view(), name="logo"),
    path("cover/", CoverView.as_view(), name="cover"),
]
