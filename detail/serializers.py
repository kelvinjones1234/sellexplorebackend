from rest_framework import serializers
from .models import Store, StoreFAQ


class StoreFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreFAQ
        fields = ["id", "question", "answer"]


class StoreSerializer(serializers.ModelSerializer):
    faqs = StoreFAQSerializer(many=True, read_only=True)

    class Meta:
        model = Store 
        fields = [
            "id",
            "name",
            "phone",
            "description",
            "country",
            "state",
            "address",
            "delivery",
            "business_category",
            "product_types",
            "story",
            "image_one",
            "image_two",
            "image_three",
            "twitter",
            "facebook",
            "tiktok",
            "snapchat",
            "instagram",
            "delivery_time",
            "policy",
            "faqs",
            "created_at",
            "updated_at",
        ]
