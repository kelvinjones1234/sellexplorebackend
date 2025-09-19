import json
from rest_framework import serializers
from .models import OptionsNote, Product, ProductImage, ProductOptions, Category
from django.db import transaction

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "is_thumbnail"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")
        if request and representation.get("image"):
            if not representation["image"].startswith(("http://", "https://")):
                representation["image"] = request.build_absolute_uri(
                    representation["image"]
                )
        return representation

class ProductOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOptions
        fields = [
            "id",
            "template_name",
            "note",
            "options",
            "as_template",
        ]

class ListCreateProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    options = serializers.ListField(required=False, allow_empty=True)

    def validate_options(self, value):
        print(f"Validating options: {value}")
        return value

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

    def to_internal_value(self, data):
        print(f"📥 INCOMING DATA: {data}")
        
        restructured_data = {}
        images_dict = {}
        options_list = []

        for key, value in data.items():
            if key.startswith("images["):
                parts = key.replace("]", "").split("[")
                index = int(parts[1])
                field_name = parts[2]

                if index not in images_dict:
                    images_dict[index] = {}
                images_dict[index][field_name] = value

            elif key == "options":
                print(f"🔍 FOUND OPTIONS KEY: {key} = {value}")
                try:
                    # Handle case where value is a JSON string or a list
                    parsed = (
                        json.loads(value)
                        if isinstance(value, str)
                        else value
                    )
                    print(f"✅ PARSED OPTIONS: {parsed}")
                    options_list = parsed if isinstance(parsed, list) else [parsed]
                except Exception as e:
                    print(f"❌ Failed to parse options: {e}")
                    options_list = []  # Default to empty list if parsing fails

            else:
                restructured_data[key] = value

        restructured_data["images"] = [
            images_dict[i] for i in sorted(images_dict.keys())
        ]
        restructured_data["options"] = options_list
        
        print(f"📤 RESTRUCTURED DATA: {restructured_data}")
        
        result = super().to_internal_value(restructured_data)
        print(f"🎯 FINAL VALIDATED DATA: {result}")
        
        return result

    @transaction.atomic
    def create(self, validated_data):
        print(f"🏗️ CREATE METHOD - VALIDATED DATA: {validated_data}")
        
        images_data = validated_data.pop("images", [])
        options_data = validated_data.pop("options", [])
        
        print(f"📷 IMAGES DATA: {images_data}")
        print(f"⚙️ OPTIONS DATA: {options_data}")

        owner = self.context["request"].user
        product = Product.objects.create(owner=owner, **validated_data)
        print(f"✅ PRODUCT CREATED: {product.id}")

        if images_data:
            ProductImage.objects.bulk_create(
                [ProductImage(product=product, **img) for img in images_data]
            )
            print(f"📷 IMAGES CREATED: {len(images_data)}")

        for opt_data in options_data:
            note_instance = None
            if opt_data.get("note"):
                note_instance = OptionsNote.objects.create(note=opt_data["note"])
                print(f"📝 NOTE CREATED: {note_instance.id}")

            option_instance = ProductOptions.objects.create(
                product=product,
                note=note_instance,
                options=opt_data.get("options", []),
                as_template=opt_data.get("as_template", False),
                template_name=opt_data.get("template_name"),
            )
            print(f"⚙️ PRODUCT OPTION CREATED: {option_instance.id}")

        return product

class UpdateProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    options = ProductOptionsSerializer(many=True, required=False)

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

class ProductSummarySerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "images"]

    def get_images(self, obj):
        image = obj.images.filter(is_thumbnail=True).first() or obj.images.first()
        if image:
            return ProductImageSerializer(image).data
        return None

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "image", "slug", "product_count"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


