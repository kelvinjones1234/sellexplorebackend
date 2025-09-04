from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import UserSerializer, UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User
import logging


logger = logging.getLogger(__name__)


class SignUpView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """

    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        store_name = request.data.get("store_name")

        # Check if email exists
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "An account with this email already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if store_name exists
        if User.objects.filter(store_name=store_name).exists():
            return Response(
                {"error": "This store name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Proceed to serializer if no conflicts
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            {"user": serializer.data, "message": "User registered successfully"},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class SignInView(APIView):
    """
    API endpoint for user login.
    Returns JWT access and refresh tokens upon successful authentication.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = TokenObtainPairSerializer(
            data=request.data
        )  # instantiate manually
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.user

            return Response(
                {
                    "tokens": serializer.validated_data,
                    "user": {
                        "email": user.email,
                        "store_name": getattr(user, "store_name", None),
                        "full_name": getattr(user, "full_name", None),
                        "niche": getattr(user, "niche", None),
                        "vendor_location": getattr(user, "vendor_location", None),
                    },
                    "message": "Login successful",
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class UserProfileAPIView(APIView):
    """User profile management"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = UserProfileSerializer.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfileSerializer.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Profile retrieval error: {str(e)}")
            return Response(
                {"error": "Profile retrieval failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):
        try:
            profile = UserProfileSerializer.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except UserProfileSerializer.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            return Response(
                {"error": "Profile update failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
