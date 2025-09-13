from rest_framework import serializers
from detail.models import StoreFAQ, Store
from product.models import Product
from product.serializers import (
    CategorySerializer,
    ProductImageSerializer,
    ProductOptionSerializer,
)
from store_setting.models import StoreConfigurations, Cover, Logo


class StoreFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreFAQ
        fields = ["id", "question", "answer"]


class StoreConfigurationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreConfigurations
        fields = "__all__"


class CoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cover
        fields = "__all__"


class LogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logo
        fields = "__all__"


class StoreSerializer(serializers.ModelSerializer):
    faqs = StoreFAQSerializer(many=True, read_only=True)
    configurations = StoreConfigurationsSerializer(
        source="user.user.configurations", read_only=True
    )
    cover = CoverSerializer(source="user.logo", read_only=True)
    logo = LogoSerializer(source="user.background", read_only=True)

    class Meta:
        model = Store
        fields = "__all__"


class FeaturedProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    options = ProductOptionSerializer(many=True, required=False)
    category = CategorySerializer(required=False)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "category",
            "description",
            "price",
            "discount_price",
            "quantity",
            "availability",
            "hot_deal",
            "featured",
            "recent",
            "extra_info",
            "images",
            "options",
        ]
