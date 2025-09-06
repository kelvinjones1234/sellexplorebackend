# from rest_framework import serializers
# from .models import Product, ProductImage, ProductOption, Category
# from django.db import transaction


# class ProductImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductImage
#         fields = ["id", "image", "is_thumbnail"]


# class ProductOptionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductOption
#         fields = ["id", "name", "image"]


# class ProductSerializer(serializers.ModelSerializer):
#     images = ProductImageSerializer(many=True, required=False)
#     options = ProductOptionSerializer(many=True, required=False)

#     class Meta:
#         model = Product
#         fields = [
#             "id",
#             "name",
#             "category",
#             "description",
#             "price",
#             "discount_price",
#             "quantity",
#             "availability",
#             "extra_info",
#             "images",
#             "options",
#         ]

#     def to_internal_value(self, data):
#         # This method is needed for multipart/form-data submissions.
#         # For JSON APIs, this can often be removed.
#         restructured_data = {}
#         images_dict = {}
#         options_dict = {}

#         for key, value in data.items():
#             if key.startswith("images["):
#                 # E.g., 'images[0][is_thumbnail]' -> parts = ['images', '0', 'is_thumbnail']
#                 parts = key.replace("]", "").split("[")
#                 index = int(parts[1])
#                 field_name = parts[2]

#                 # Group data by index in a dictionary
#                 if index not in images_dict:
#                     images_dict[index] = {}
#                 images_dict[index][field_name] = value

#             elif key.startswith("options["):
#                 parts = key.replace("]", "").split("[")
#                 index = int(parts[1])
#                 field_name = parts[2]

#                 if index not in options_dict:
#                     options_dict[index] = {}
#                 options_dict[index][field_name] = value

#             else:
#                 restructured_data[key] = value

#         # Convert the dictionaries to lists, sorted by index
#         restructured_data["images"] = [
#             images_dict[i] for i in sorted(images_dict.keys())
#         ]
#         restructured_data["options"] = [
#             options_dict[i] for i in sorted(options_dict.keys())
#         ]

#         return super().to_internal_value(restructured_data)

#     @transaction.atomic  # Ensures the whole operation succeeds or fails together
#     def create(self, validated_data):
#         images_data = validated_data.pop("images", [])
#         options_data = validated_data.pop("options", [])

#         # 1. Create the main product instance
#         owner = self.context["request"].user
#         product = Product.objects.create(owner=owner, **validated_data)

#         # 2. Prepare image and option objects for bulk creation
#         images_to_create = [
#             ProductImage(product=product, **img_data) for img_data in images_data
#         ]
#         options_to_create = [
#             ProductOption(product=product, **opt_data) for opt_data in options_data
#         ]

#         # 3. Create all images and options in just two queries
#         if images_to_create:
#             ProductImage.objects.bulk_create(images_to_create)

#         if options_to_create:
#             ProductOption.objects.bulk_create(options_to_create)

#         return product


# class CategorySerializer(serializers.ModelSerializer):
#     product_count = serializers.IntegerField(read_only=True)

#     class Meta:
#         model = Category
#         fields = ["id", "name", "image", "slug", "product_count"]


# class ProductOptionSerializer(serializers.ModelSerializer):
#     product_name = serializers.CharField(source="product.name", read_only=True)

#     class Meta:
#         model = ProductOption
#         fields = ["id", "product", "product_name", "name", "image"]








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
        restructured_data = {}
        images_list = []
        options_list = []

        # Handle multipart form data
        for key, value in data.items():
            if key.startswith("images"):
                # Handle cases like images[], images[0], or images[0][field_name]
                if key == "images" or key == "images[]":
                    # Single image file or list of files
                    if isinstance(value, list):
                        images_list.extend([{"image": img} for img in value])
                    else:
                        images_list.append({"image": value})
                elif "[" in key and "]" in key:
                    try:
                        parts = key.replace("]", "").split("[")
                        if len(parts) >= 3:  # Expected: images[0][field_name]
                            index = int(parts[1])
                            field_name = parts[2]
                            while len(images_list) <= index:
                                images_list.append({})
                            images_list[index][field_name] = value
                        elif len(parts) == 2:  # Expected: images[0]
                            index = int(parts[1])
                            while len(images_list) <= index:
                                images_list.append({})
                            images_list[index]["image"] = value
                    except (IndexError, ValueError):
                        # Skip malformed keys
                        continue
            elif key.startswith("options"):
                # Handle options similarly
                if key == "options" or key == "options[]":
                    if isinstance(value, list):
                        options_list.extend([{"name": opt} for opt in value])
                    else:
                        options_list.append({"name": value})
                elif "[" in key and "]" in key:
                    try:
                        parts = key.replace("]", "").split("[")
                        if len(parts) >= 3:  # Expected: options[0][field_name]
                            index = int(parts[1])
                            field_name = parts[2]
                            while len(options_list) <= index:
                                options_list.append({})
                            options_list[index][field_name] = value
                        elif len(parts) == 2:  # Expected: options[0]
                            index = int(parts[1])
                            while len(options_list) <= index:
                                options_list.append({})
                            options_list[index]["name"] = value
                    except (IndexError, ValueError):
                        # Skip malformed keys
                        continue
            else:
                restructured_data[key] = value

        # Add images and options to restructured data
        restructured_data["images"] = [img for img in images_list if img]
        restructured_data["options"] = [opt for opt in options_list if opt]

        return super().to_internal_value(restructured_data)

    @transaction.atomic
    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        options_data = validated_data.pop("options", [])

        # Create the main product instance
        owner = self.context["request"].user
        product = Product.objects.create(owner=owner, **validated_data)

        # Prepare image and option objects for bulk creation
        images_to_create = [
            ProductImage(product=product, **img_data) for img_data in images_data
        ]
        options_to_create = [
            ProductOption(product=product, **opt_data) for opt_data in options_data
        ]

        # Create all images and options in just two queries
        if images_to_create:
            ProductImage.objects.bulk_create(images_to_create)

        if options_to_create:
            ProductOption.objects.bulk_create(options_to_create)

        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        # Pop nested data
        images_data = validated_data.pop("images", [])
        options_data = validated_data.pop("options", [])

        # Update main product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle images: update existing, create new, delete removed
        existing_image_ids = {img.id for img in instance.images.all()}
        submitted_image_ids = {img_data.get("id") for img_data in images_data if img_data.get("id")}
        print("existing_image_ids",existing_image_ids)
        print("submitted_image_ids",submitted_image_ids)

        # Delete images that are no longer in the submitted data
        ProductImage.objects.filter(
            product=instance, id__in=existing_image_ids - submitted_image_ids
        ).delete()

        # Update or create images
        images_to_create = []
        for img_data in images_data:
            img_id = img_data.get("id")
            if img_id:
                # Update existing image
                ProductImage.objects.filter(id=img_id, product=instance).update(**img_data)
            else:
                # Create new image
                images_to_create.append(ProductImage(product=instance, **img_data))

        if images_to_create:
            ProductImage.objects.bulk_create(images_to_create)

        # Handle options: update existing, create new, delete removed
        existing_option_ids = {opt.id for opt in instance.options.all()}
        submitted_option_ids = {opt_data.get("id") for opt_data in options_data if opt_data.get("id")}

        # Delete options that are no longer in the submitted data
        ProductOption.objects.filter(
            product=instance, id__in=existing_option_ids - submitted_option_ids
        ).delete()

        # Update or create options
        options_to_create = []
        for opt_data in options_data:
            opt_id = opt_data.get("id")
            if opt_id:
                # Update existing option
                ProductOption.objects.filter(id=opt_id, product=instance).update(**opt_data)
            else:
                # Create new option
                options_to_create.append(ProductOption(product=instance, **opt_data))

        if options_to_create:
            ProductOption.objects.bulk_create(options_to_create)

        return instance


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