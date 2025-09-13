from rest_framework import serializers
from .models import StoreConfigurations, Cover, Logo


class ConfigurationsSerializer(serializers.ModelSerializer):
    background_image_one = serializers.SerializerMethodField()
    background_image_two = serializers.SerializerMethodField()
    background_image_three = serializers.SerializerMethodField()

    class Meta:
        model = StoreConfigurations
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def get_background_image_one(self, obj):
        request = self.context.get("request")
        if obj.background_image_one and hasattr(obj.background_image_one, "url"):
            return request.build_absolute_uri(obj.background_image_one.url)
        return None

    def get_background_image_two(self, obj):
        request = self.context.get("request")
        if obj.background_image_two and hasattr(obj.background_image_two, "url"):
            return request.build_absolute_uri(obj.background_image_two.url)
        return None

    def get_background_image_three(self, obj):
        request = self.context.get("request")
        if obj.background_image_three and hasattr(obj.background_image_three, "url"):
            return request.build_absolute_uri(obj.background_image_three.url)
        return None





class CoverSerializer(serializers.ModelSerializer):
    cover_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Cover
        fields = ["cover_image"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get("request")
        if instance.cover_image:
            rep["cover_image"] = request.build_absolute_uri(instance.cover_image.url)
        return rep


class LogoSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Logo
        fields = ["logo"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get("request")
        if instance.logo:
            rep["logo"] = request.build_absolute_uri(instance.logo.url)
        return rep
