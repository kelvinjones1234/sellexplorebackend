from django.contrib import admin
from .models import OptionsNote, Product, ProductImage, ProductOptions, Category


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


class ProductOptionsInline(admin.TabularInline):
    model = ProductOptions
    extra = 0  # no extra empty form
    fields = ("options", "as_template", "template_name", "note")
    show_change_link = True


@admin.register(OptionsNote)
class OptionsNoteAdmin(admin.ModelAdmin):
    list_display = ("short_note", "created_at", "updated_at")
    search_fields = ("note",)
    readonly_fields = ("created_at", "updated_at")

    def short_note(self, obj):
        return obj.note[:50] + ("..." if len(obj.note) > 50 else "")

    short_note.short_description = "Note"


@admin.register(ProductOptions)
class ProductOptionsAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "note",
        "display_options",
        "as_template",
        "template_name",
        "created_at",
    )
    list_filter = ("as_template", "created_at", "updated_at")
    search_fields = ("product__name", "template_name", "options")
    readonly_fields = ("created_at", "updated_at")

    def display_options(self, obj):
        if isinstance(obj.options, list):
            return ", ".join(map(str, obj.options))
        return obj.options

    display_options.short_description = "Options"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        # "id",
        "name",
        "owner",
        "featured",
        "category",
        "price",
        "discount_price",
        "quantity",
        "availability",
        "updated_at",
    )
    list_filter = ("availability", "category", "updated_at")
    search_fields = ("name", "description", "extra_info", "owner__username")
    inlines = [ProductImageInline, ProductOptionsInline]
    readonly_fields = ("updated_at",)
    ordering = ("-updated_at",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "is_thumbnail")
    list_filter = ("is_thumbnail",)
    search_fields = ("product__name",)





