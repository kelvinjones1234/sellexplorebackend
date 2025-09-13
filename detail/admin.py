from django.contrib import admin
from .models import Store, StoreFAQ


class StoreFAQInline(admin.TabularInline):
    model = StoreFAQ
    extra = 1  # number of empty forms to show
    fields = ("question", "answer")
    show_change_link = True


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "country",
        "state",
        "business_category",
        "created_at",
    )
    search_fields = ("name", "phone", "country", "state", "business_category")
    list_filter = ("country", "state", "business_category", "created_at")
    readonly_fields = ("created_at", "updated_at")
    inlines = [StoreFAQInline]

    fieldsets = (
        ("Basic Information", {"fields": ("user", "name", "phone", "description")}),
        ("Location", {"fields": ("country", "state", "address", "delivery")}),
        ("Business", {"fields": ("business_category", "product_types")}),
        ("About", {"fields": ("story", "image_one", "image_two", "image_three")}),
        (
            "Social Links",
            {"fields": ("twitter", "facebook", "tiktok", "snapchat", "instagram")},
        ),
        ("Extra Info", {"fields": ("delivery_time", "policy")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(StoreFAQ)
class StoreFAQAdmin(admin.ModelAdmin):
    list_display = ("store", "question", "answer")
    search_fields = ("question", "answer", "store__name")
    list_filter = ("store",)
