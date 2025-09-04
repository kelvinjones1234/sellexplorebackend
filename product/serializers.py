from rest_framework import serializers
from .models import Product, ProductImage, ProductOption, Category
from django.db import transaction


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "is_thumbnail"]


class ProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        fields = ["id", "name", "image"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    options = ProductOptionSerializer(many=True, required=False)

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
            "extra_info",
            "images",
            "options",
        ]

    def to_internal_value(self, data):
        # This method is needed for multipart/form-data submissions.
        # For JSON APIs, this can often be removed.
        restructured_data = {}
        images_dict = {}
        options_dict = {}

        for key, value in data.items():
            if key.startswith("images["):
                # E.g., 'images[0][is_thumbnail]' -> parts = ['images', '0', 'is_thumbnail']
                parts = key.replace("]", "").split("[")
                index = int(parts[1])
                field_name = parts[2]

                # Group data by index in a dictionary
                if index not in images_dict:
                    images_dict[index] = {}
                images_dict[index][field_name] = value

            elif key.startswith("options["):
                parts = key.replace("]", "").split("[")
                index = int(parts[1])
                field_name = parts[2]

                if index not in options_dict:
                    options_dict[index] = {}
                options_dict[index][field_name] = value

            else:
                restructured_data[key] = value

        # Convert the dictionaries to lists, sorted by index
        restructured_data["images"] = [
            images_dict[i] for i in sorted(images_dict.keys())
        ]
        restructured_data["options"] = [
            options_dict[i] for i in sorted(options_dict.keys())
        ]

        return super().to_internal_value(restructured_data)

    @transaction.atomic  # Ensures the whole operation succeeds or fails together
    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        options_data = validated_data.pop("options", [])

        # 1. Create the main product instance
        owner = self.context["request"].user
        product = Product.objects.create(owner=owner, **validated_data)

        # 2. Prepare image and option objects for bulk creation
        images_to_create = [
            ProductImage(product=product, **img_data) for img_data in images_data
        ]
        options_to_create = [
            ProductOption(product=product, **opt_data) for opt_data in options_data
        ]

        # 3. Create all images and options in just two queries
        if images_to_create:
            ProductImage.objects.bulk_create(images_to_create)

        if options_to_create:
            ProductOption.objects.bulk_create(options_to_create)

        return product


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "image", "slug", "product_count"]


class ProductOptionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = ProductOption
        fields = ["id", "product", "product_name", "name", "image"]
