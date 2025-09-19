from django.urls import path
from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    ProductCreateView,
    ProductDetailView,
    # ProductImageDeleteView,
    ProductImageUpdateView,
    ProductOptionsDetailView,
    ProductOptionsListCreateView,
    PaginatedProductListView,
    PaginatedCategoryListCreateView,
    # ProductOptionsUpdateView,
)

urlpatterns = [
    # for the product page where products are listed
    path(
        "products-paginated/", PaginatedProductListView.as_view(), name="product-create"
    ),
    # create product with details
    path("products/", ProductCreateView.as_view(), name="product-create"),
    # create product images
    path(
        "products/<int:product_pk>/images/update/",
        ProductImageUpdateView.as_view(),
        name="productimage-bulk-update",
    ),
    # product thumbnail update
    path(
        "products/<int:product_pk>/images/<int:image_pk>/",
        ProductImageUpdateView.as_view(),
        name="productimage-bulk-update",
    ),
    # delete product image
    path(
        "products/images/<int:image_id>/",
        ProductImageUpdateView.as_view(),
        name="productimage-bulk-update",
    ),
    # for the categories page where categories are listed
    path(
        "categories-paginated/",
        PaginatedCategoryListCreateView.as_view(),
        name="category-list-create",
    ),
    # update and delete category
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    # list and create categories
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    # update and delete product details
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    # path(
    #     "products/<int:product_pk>/options/update/",
    #     ProductOptionsUpdateView.as_view(),
    #     name="ProductOptions-bulk-update",
    # ),
    path(
        "product-options/<int:pk>/",
        ProductOptionsDetailView.as_view(),
        name="product-option-detail",
    ),
    # ProductOptions URLs
    path(
        "product-options/",
        ProductOptionsListCreateView.as_view(),
        name="product-option-list-create",
    ),
]
