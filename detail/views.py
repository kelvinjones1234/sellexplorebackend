from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Store, StoreFAQ
from .serializers import StoreSerializer, StoreFAQSerializer


class StoreView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Fetch or create the store for the logged-in profile"""
        profile = request.user.profile
        store, _ = Store.objects.get_or_create(user=profile)
        serializer = StoreSerializer(store, context={"request": request})
        return Response(serializer.data)

    def put(self, request):
        """Update store details"""
        profile = request.user.profile
        store, _ = Store.objects.get_or_create(user=profile)
        serializer = StoreSerializer(
            store, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class StoreFAQListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """List FAQs for the logged-in store"""
        profile = request.user.profile
        store = get_object_or_404(Store, user=profile)
        faqs = store.faqs.all()
        serializer = StoreFAQSerializer(faqs, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Add new FAQ to store"""
        profile = request.user.profile
        store = get_object_or_404(Store, user=profile)
        serializer = StoreFAQSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(store=store)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoreFAQDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        profile = request.user.profile
        store = get_object_or_404(Store, user=profile)
        return get_object_or_404(StoreFAQ, pk=pk, store=store)

    def put(self, request, pk):
        faq = self.get_object(request, pk)
        serializer = StoreFAQSerializer(faq, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        faq = self.get_object(request, pk)
        faq.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
