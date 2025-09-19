from django.db import models
from account.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="category/images/", blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Generate slug from name if not provided
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure slug uniqueness
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product",
    )
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    quantity = models.PositiveIntegerField(default=0)
    availability = models.BooleanField(default=False)
    hot_deal = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    recent = models.BooleanField(default=False)
    extra_info = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/images/")
    is_thumbnail = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {'Thumbnail' if self.is_thumbnail else 'Image'}"


class OptionsNote(models.Model):

    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.note[:20]


class ProductOptions(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="product_options"
    )
    note = models.ForeignKey(
        OptionsNote,
        on_delete=models.CASCADE,
        related_name="text_options",
        null=True,
        blank=True,
    )

    options = models.JSONField()  # e.g., ["S", "M", "L"]
    as_template = models.BooleanField(default=False)
    template_name = models.CharField(max_length=200, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {'Template: ' + self.template_name if self.as_template else 'Option'}"


