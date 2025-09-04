from django.urls import path
from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    ProductCreateView,
    # ProductDetailView,
    ProductOptionDetailView,
    ProductOptionListCreateView,
    PaginatedProductCreateView,
    PaginatedCategoryListCreateView
)

urlpatterns = [
    # Category URLs
    path("products-paginated/", PaginatedProductCreateView.as_view(), name="product-create"),
    path("products/", ProductCreateView.as_view(), name="product-create"),
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories-paginated/", PaginatedCategoryListCreateView.as_view(), name="category-list-create"),


    # path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path(
        "categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"
    ),
    # ProductOption URLs
    path(
        "product-options/",
        ProductOptionListCreateView.as_view(),
        name="product-option-list-create",
    ),
    path(
        "product-options/<int:pk>/",
        ProductOptionDetailView.as_view(),
        name="product-option-detail",
    ),
]
