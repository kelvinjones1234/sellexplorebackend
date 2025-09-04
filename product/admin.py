from django.contrib import admin
from .models import Product, ProductImage, ProductOption, ProductOption, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    list_filter = ["name"]




class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # how many empty forms to display
    fields = ("image", "is_thumbnail")
    readonly_fields = ()
    show_change_link = True


class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1
    fields = ("name", "image")
    readonly_fields = ()
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "category",
        "price",
        "discount_price",
        "quantity",
        "availability",
        "created_at",
    )
    list_filter = ("availability", "category", "created_at")
    search_fields = ("name", "description", "extra_info", "owner__username")
    inlines = [ProductImageInline, ProductOptionInline]
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "is_thumbnail")
    list_filter = ("is_thumbnail",)
    search_fields = ("product__name",)


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "name")
    search_fields = ("product__name", "name")
