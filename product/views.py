from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    CategorySerializer,
    ProductOptionsSerializer,
    ListCreateProductSerializer,
    UpdateProductSerializer,
    ProductImageSerializer,
)
from .models import Category, Product, ProductOptions, ProductImage
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from rest_framework.pagination import PageNumberPagination
import json
from django.core.files.uploadedfile import UploadedFile


class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """Return a list of all products for the authenticated user"""
        products = Product.objects.filter(owner=request.user).order_by("-created_at")
        serializer = ListCreateProductSerializer(
            products, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        print(request.data)  # Debug the incoming FormData
        serializer = ListCreateProductSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                {"message": "Product created successfully", "id": product.id},
                status=status.HTTP_201_CREATED,
            )
        print(serializer.errors)  # Debug serializer errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    def get(self, request, pk):

        product = get_object_or_404(Product, pk=pk)
        serializer = UpdateProductSerializer(product, context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = UpdateProductSerializer(
            product, data=request.data, partial=True, context={"request": request}
        )

        if serializer.is_valid():

            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductImageUpdateView(APIView):
    """
    Manage product images:
    - POST: Create new images (multiple in one request).
    - PUT: Update an existing image (e.g., change thumbnail).
    """

    def post(self, request, product_pk):
        """
        Create new images for a product.
        One of them will be marked as thumbnail.
        """
        product = get_object_or_404(Product, pk=product_pk)

        # Parse image metadata (JSON array of dicts)
        images_metadata = request.data.get("images")
        if images_metadata:
            try:
                images_data = json.loads(images_metadata)
            except json.JSONDecodeError:
                return Response(
                    {"error": "Invalid images metadata format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            images_data = []

        created_images = []

        # Check if request explicitly sets a thumbnail
        thumbnail_requested = any(img.get("is_thumbnail", False) for img in images_data)

        for i, img_data in enumerate(images_data):
            is_thumbnail = img_data.get("is_thumbnail", False)

            # If no thumbnail requested, make the first uploaded one the thumbnail
            if not thumbnail_requested and i == 0:
                is_thumbnail = True

            file_index = img_data.get("file_index")
            if file_index is not None:
                file_data = request.FILES.get(f"image_files_{file_index}")

                if file_data and isinstance(file_data, UploadedFile):
                    new_image = ProductImage(product=product, is_thumbnail=is_thumbnail)
                    new_image.image.save(file_data.name, file_data, save=True)

                    created_images.append(ProductImageSerializer(new_image).data)

        return Response(created_images, status=status.HTTP_201_CREATED)

    def put(self, request, product_pk, image_pk):
        """
        Update an existing image (e.g., set as thumbnail).
        """
        product = get_object_or_404(Product, pk=product_pk)
        image = get_object_or_404(ProductImage, pk=image_pk, product=product)

        serializer = ProductImageSerializer(
            image, data=request.data, partial=True, context={"request": request}
        )

        if serializer.is_valid():
            updated_image = serializer.save()

            # If this image is now the thumbnail, clear others
            if updated_image.is_thumbnail:
                ProductImage.objects.filter(product=product).exclude(
                    id=updated_image.id
                ).update(is_thumbnail=False)

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, image_id):
        try:
            image_id = int(image_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid image ID format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Attempt to delete the specified image
        try:
            image = ProductImage.objects.get(id=image_id)
            image.delete()

            return Response(
                {"message": "Image deleted successfully"}, status=status.HTTP_200_OK
            )
        except ProductImage.DoesNotExist:
            return Response(
                {"error": "Image not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class PaginatedProductListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        products = Product.objects.filter(owner=request.user).order_by("-created_at")
        search = request.GET.get("search")
        if search:
            products = products.filter(name__icontains=search)

        paginator = PageNumberPagination()
        paginator.page_size = request.GET.get("page_size", 10)  # 👈 important

        queryset = paginator.paginate_queryset(products, request)
        serializer = ListCreateProductSerializer(
            queryset, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)


class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Annotate product_count in the queryset
        categories = Category.objects.annotate(product_count=Count("product"))
        serializer = CategorySerializer(
            categories, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    def get(self, request, pk):

        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):  # Add pk here
        print("poster")
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)

        if serializer.is_valid():

            serializer.save()
            return Response(serializer.data)
        print("Validation errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaginatedCategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Category.objects.annotate(product_count=Count("product"))
        search = request.GET.get("search")
        if search:
            categories = categories.filter(name__icontains=search)

        paginator = PageNumberPagination()
        paginator.page_size = request.GET.get("page_size", 10)  # 👈 important

        queryset = paginator.paginate_queryset(categories, request)
        serializer = CategorySerializer(
            queryset, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)


class ProductOptionsListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        options = ProductOptions.objects.filter(as_template=True)  # ✅ only templates
        serializer = ProductOptionsSerializer(options, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductOptionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductOptionsDetailView(APIView):

    def get(self, request, pk):
        option = get_object_or_404(ProductOptions, pk=pk)
        serializer = ProductOptionsSerializer(option)
        return Response(serializer.data)

    def put(self, request, pk):
        option = get_object_or_404(ProductOptions, pk=pk)
        serializer = ProductOptionsSerializer(option, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        option = get_object_or_404(ProductOptions, pk=pk)
        option.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
