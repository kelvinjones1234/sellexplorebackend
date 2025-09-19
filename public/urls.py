from django.urls import path
from .views import (
    ProductGroupView,
    ProductListFilterView,
    PublicStoreDetailView,
    PaginatedProductListView,
    CategoriesAndFeaturedItems,
)

urlpatterns = [
    # general store configurations
    path(
        "stores/<str:store_name>/",
        PublicStoreDetailView.as_view(),
        name="public-store-detail",
    ),
    # for product group
    path(
        "item-group/<str:storename>/",
        ProductGroupView.as_view(),
        name="item-group",
    ),
    # pubilic items list with paginations
    path(
        "items/<str:store_name>/items/",
        PaginatedProductListView.as_view(),
        name="items",
    ),
    # 
    path(
        "items/<str:store_name>/filtered/",
        ProductListFilterView.as_view(),
        name="filter",
    ),
    # For featured products
    path(
        "featured-and-category/<str:store_name>/",
        CategoriesAndFeaturedItems.as_view(),
        name="featured",
    ),
]
