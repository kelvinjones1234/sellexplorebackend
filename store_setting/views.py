from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .models import Cover, Logo, StoreConfigurations
from .serializers import ConfigurationsSerializer, CoverSerializer, LogoSerializer
from rest_framework import status, permissions


# for updating configurations and displaying configurations
class ConfigurationsView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get the current user's configurations
        """
        config = StoreConfigurations.objects.filter(user=request.user).first()
        if not config:
            return Response(
                {"detail": "No configurations found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ConfigurationsSerializer(config, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Update existing configurations for the current user
        """
        config = get_object_or_404(StoreConfigurations, user=request.user)
        print(request.data)
        serializer = ConfigurationsSerializer(config, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# For public use
class PublicConfigurationsView(APIView):
    """
    Public endpoint to fetch a store's configuration by store_name
    """

    def get(self, request, store_name):
        config = get_object_or_404(
            StoreConfigurations, user__store_name__iexact=store_name
        )
        serializer = ConfigurationsSerializer(config, context={"request": request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class CoverView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # ✅ allow file upload

    def get(self, request):
        user_profile = request.user.profile
        obj, _ = Cover.objects.get_or_create(user=user_profile)
        serializer = CoverSerializer(obj, context={"request": request})
        return Response(serializer.data)

    def put(self, request):
        user_profile = request.user.profile
        obj, _ = Cover.objects.get_or_create(user=user_profile)
        serializer = CoverSerializer(
            obj, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # ✅ allow file upload

    def get(self, request):
        user_profile = request.user.profile
        obj, _ = Logo.objects.get_or_create(user=user_profile)
        serializer = LogoSerializer(obj, context={"request": request})
        return Response(serializer.data)

    def put(self, request):
        user_profile = request.user.profile
        obj, _ = Logo.objects.get_or_create(user=user_profile)
        serializer = LogoSerializer(
            obj, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
