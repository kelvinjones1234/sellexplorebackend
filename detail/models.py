from django.db import models
from account.models import UserProfile


class Store(models.Model):
    """
    Main Store profile linked to Profile instead of User
    """

    user = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="store"
    )

    # Basic
    name = models.CharField(max_length=200, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Location
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    delivery = models.CharField(max_length=255, blank=True, null=True)

    # Business
    business_category = models.CharField(max_length=100, blank=True, null=True)
    product_types = models.JSONField(default=list, blank=True)  # array of strings

    # About
    story = models.TextField(blank=True, null=True)
    image_one = models.ImageField(upload_to="", null=True, blank=True)
    image_two = models.ImageField(upload_to="", null=True, blank=True)
    image_three = models.ImageField(upload_to="", null=True, blank=True)

    # Social Links
    twitter = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)
    tiktok = models.CharField(max_length=255, blank=True, null=True)
    snapchat = models.CharField(max_length=255, blank=True, null=True)
    instagram = models.CharField(max_length=255, blank=True, null=True)

    # Extra Info
    delivery_time = models.CharField(max_length=100, blank=True, null=True)
    policy = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class StoreFAQ(models.Model):
    """
    Frequently Asked Questions
    """

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.store.name} - {self.question[:30]}"
