from django.db import models
from account.models import User


class Configurations(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="configurations")
    # Background images (allow null/blank if optional)
    background_image_one = models.ImageField(upload_to="", null=True, blank=True)
    background_image_two = models.ImageField(upload_to="", null=True, blank=True)
    background_image_three = models.ImageField(upload_to="", null=True, blank=True)

    # Branding colors
    brand_color_light = models.CharField(max_length=20, default="#ffffff")
    brand_color_dark = models.CharField(max_length=20, default="#000000")

    # Text customizations
    headline = models.CharField(max_length=255, blank=True, null=True)
    subheading = models.CharField(max_length=500, blank=True, null=True)
    more_button = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    about_button = models.TextField(max_length=100, blank=True, null=True)

    # Layout settings
    position = models.CharField(
        max_length=50,
        choices=[
            ("left", "Left"),
            ("center", "Center"),
            ("right", "Right"),
        ],
        default="center",
    )

    latest_first = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Configurations for {self.user.username}"
