# views.py

from datetime import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch
from product.models import Product, ProductImage, Category
from utils.caching import CacheHeadersMixin
from rest_framework.pagination import PageNumberPagination
from product.serializers import ListCreateProductSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q
from account.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from detail.models import Store
from .serializers import FeaturedProductSerializer, CategorySerializer, StoreSerializer
from django.utils.timezone import now


# -------------------
# Store detail view and store configurations
# -------------------
class PublicStoreDetailView(CacheHeadersMixin, APIView):
    def get(self, request, store_name):
        # 1. Retrieve the object
        store = (
            Store.objects.select_related(
                "user__user__configurations",
                "user__logo",
                "user__background",
            )
            .prefetch_related("faqs")
            .filter(user__user__store_name__iexact=store_name)
            .first()
        )

        if not store:
            return Response(
                {"detail": "Store not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # 2. Set the target for the cache mixin
        self.object = store

        # 3. Check if the client cache is valid and return 304 if so
        not_modified = self.check_not_modified(request)
        if not_modified:
            return not_modified

        # 4. If cache is invalid, serialize and return the full response
        serializer = StoreSerializer(store, context={"request": request})
        return Response(serializer.data)


# -------------------
# Product group view
# -------------------
class ProductGroupView(CacheHeadersMixin, APIView):
    def get_primary_image_url(self, product, request):
        """Helper to safely get the first image URL for a given product instance."""
        if not product:
            return None
        # Assuming the related name is 'images' and it's pre-fetched and ordered
        primary_image = product.images.first()
        if primary_image and hasattr(primary_image.image, "url"):
            return request.build_absolute_uri(primary_image.image.url)
        return None

    def get(self, request, storename):
        # 1. Define the base queryset for the store
        all_products_queryset = (
            Product.objects.filter(owner__store_name__iexact=storename)
            .select_related("owner")
            .prefetch_related(
                # Crucial prefetch to get images efficiently
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.order_by("-is_thumbnail"),
                    to_attr="ordered_images_list",  # Use a custom attribute to avoid conflicts
                )
            )
        )

        # 2. Set the target for the cache mixin. The ETag will be based on the most
        #    recently updated product in this store.
        self.queryset = all_products_queryset

        # 3. Check if client cache is valid BEFORE doing any more work.
        not_modified = self.check_not_modified(request)
        if not_modified:
            return not_modified

        # 4. If cache is invalid, efficiently get the data from the DB.
        #    This is far more efficient than loading all products into memory.

        # Get counts directly from the database
        total_products_count = all_products_queryset.count()
        featured_products_count = all_products_queryset.filter(featured=True).count()
        # Assuming 'recent' is a flag. If it's based on creation date,
        # you would filter by `created_at` instead.
        recent_products_count = all_products_queryset.filter(recent=True).count()

        # Get the specific products we need for their images
        # We re-use the prefetch for efficiency
        first_product_overall = all_products_queryset.first()
        first_featured_product = all_products_queryset.filter(featured=True).first()
        first_recent_product = all_products_queryset.filter(recent=True).first()

        # 5. Build the response payload
        response_data = {
            "storename": storename,
            "total_products": {
                "count": total_products_count,
                "image": self.get_primary_image_url(first_product_overall, request),
            },
            "featured_products": {
                "count": featured_products_count,
                "image": self.get_primary_image_url(first_featured_product, request),
            },
            "recent_products": {
                "count": recent_products_count,
                "image": self.get_primary_image_url(first_recent_product, request),
            },
        }

        return Response(response_data)


class PaginatedProductListView(APIView):
    """
    Public endpoint to list products by store_name, with optional filters:
    - ?search=<text>
    - ?category=<slug>   (single)
    - ?categories=slug1,slug2 (multiple)
    - ?page_size=20
    """

    permission_classes = [AllowAny]  # ❌ change to IsAuthenticated if private

    def get(self, request, store_name, format=None):
        # 1️⃣ Get store (User)
        store = get_object_or_404(User, store_name__iexact=store_name, is_active=True)

        # 2️⃣ Base queryset → products belonging to that store
        products = Product.objects.filter(owner=store).order_by("-created_at")

        # 3️⃣ Search filter
        search = request.GET.get("search")
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        # 4️⃣ Category filters
        category_slug = request.GET.get("category")
        if category_slug:
            products = products.filter(category__slug=category_slug)

        categories = request.GET.get("categories")
        if categories:
            slug_list = [slug.strip() for slug in categories.split(",") if slug.strip()]
            products = products.filter(category__slug__in=slug_list)

        # 5️⃣ Pagination
        paginator = PageNumberPagination()
        paginator.page_size = int(request.GET.get("page_size", 10))

        queryset = paginator.paginate_queryset(products, request)
        serializer = ListCreateProductSerializer(
            queryset, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)




class CategoriesAndFeaturedItems(CacheHeadersMixin, generics.GenericAPIView):
    serializer_class = FeaturedProductSerializer

    def get(self, request, *args, **kwargs):
        # build the querysets
        featured_qs = Product.objects.filter(
            owner__store_name__iexact=self.kwargs["store_name"],
            featured=True,
        ).order_by("id")[:20]

        categories_qs = Category.objects.all()

        # 👇 Tell the mixin what to use for caching
        # you can combine them in a tuple so ETag/Last-Modified
        # changes if either changes
        self.queryset = (featured_qs, categories_qs)

        # now check client cache
        not_modified = self.check_not_modified(request)
        if not_modified:
            return not_modified

        # serialize
        featured_data = self.get_serializer(
            featured_qs, many=True, context={"request": request}
        ).data
        categories_data = CategorySerializer(
            categories_qs, many=True, context={"request": request}
        ).data

        response = Response({
            "featured_products": featured_data,
            "categories": categories_data,
        })

        return self.finalize_response(request, response)
