from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Fields to display in the admin list view
    list_display = ("email", "store_name", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "niche")
    search_fields = ("email", "store_name", "full_name")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_login", "slug")

    # Fields for adding and changing users
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {"fields": ("full_name", "store_name", "niche", "location", "slug")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "store_name",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user_email", "phone_number", "email_verified")
    list_filter = ("email_verified",)
    search_fields = ("full_name", "user__email", "phone_number")
    readonly_fields = ("user_email",)

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "User Email"
