from django.contrib import admin
from .models import StoreConfigurations, Logo, Cover


@admin.register(StoreConfigurations)
class StoreConfigurationsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "brand_color_dark",
        "brand_color_light",
        "position",
        "latest_first",
        "created_at",
        "updated_at",
    )
    list_filter = ("position", "latest_first", "created_at")
    search_fields = ("user__username", "headline", "subheading")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "User",
            {
                "fields": ("user",),
            },
        ),
        (
            "Branding",
            {
                "fields": ("brand_color_dark", "brand_color_light"),
            },
        ),
        (
            "Background Images",
            {
                "fields": (
                    "background_image_one",
                    "background_image_two",
                    "background_image_three",
                ),
            },
        ),
        (
            "Text Customization",
            {
                "fields": ("headline", "subheading", "button_one", "button_two"),
            },
        ),
        (
            "Layout Settings",
            {
                "fields": ("position", "latest_first"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


@admin.register(Logo)
class Logo(admin.ModelAdmin):
    list_display = ("user", "logo")
    search_fields = ("user__user__username",)
    list_filter = ("user",)
    fields = ("user", "logo")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(Cover)
class Cover(admin.ModelAdmin):
    list_display = ("user", "cover_image")
    search_fields = ("user__user__username",)
    list_filter = ("user",)
    fields = ("user", "cover_image")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
