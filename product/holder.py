from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CategorySerializer, ProductOptionSerializer, ProductSerializer
from .models import Category, Product, ProductOption
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from rest_framework import status
from rest_framework.pagination import PageNumberPagination


class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        products = Product.objects.filter(owner=request.user).order_by("-created_at")
        search = request.GET.get("search")
        if search:
            products = products.filter(name__icontains=search)

        paginator = PageNumberPagination()
        paginator.page_size = request.GET.get("page_size", 10)  # 👈 important

        queryset = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(
            queryset, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                {"message": "Product created successfully", "id": product.id},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        """Retrieve a specific product by ID for the authenticated user"""
        product = get_object_or_404(Product, pk=pk, owner=request.user)
        serializer = ProductSerializer(product, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        """Update a specific product by ID for the authenticated user"""
        product = get_object_or_404(Product, pk=pk, owner=request.user)
        serializer = ProductSerializer(
            product, data=request.data, context={"request": request}, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Product updated successfully", "id": product.id},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """Delete a specific product by ID for the authenticated user"""
        product = get_object_or_404(Product, pk=pk, owner=request.user)
        product.delete()
        return Response(
            {"message": "Product deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class CategoryListCreateView(APIView):
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

    def post(self, request):
        serializer = CategorySerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Views for ProductOption
class ProductOptionListCreateView(APIView):
    def get(self, request):
        options = ProductOption.objects.all()
        serializer = ProductOptionSerializer(options, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductOptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductOptionDetailView(APIView):
    def get(self, request, pk):
        option = get_object_or_404(ProductOption, pk=pk)
        serializer = ProductOptionSerializer(option)
        return Response(serializer.data)

    def put(self, request, pk):
        option = get_object_or_404(ProductOption, pk=pk)
        serializer = ProductOptionSerializer(option, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        option = get_object_or_404(ProductOption, pk=pk)
        option.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
