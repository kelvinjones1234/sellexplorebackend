from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import CategorySerializer, ProductOptionSerializer, ProductSerializer
from .models import Category, Product, ProductOption
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from rest_framework.pagination import PageNumberPagination


class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """Return a list of all products for the authenticated user"""
        products = Product.objects.filter(owner=request.user).order_by("-created_at")
        serializer = ProductSerializer(
            products, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        print(request.data)  # Debug the incoming FormData
        serializer = ProductSerializer(data=request.data, context={"request": request})
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
        serializer = ProductSerializer(product, context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk): 
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True, context={"request": request})
        
        if serializer.is_valid():
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)








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
        serializer = ProductSerializer(
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
