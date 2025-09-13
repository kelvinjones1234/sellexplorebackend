from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, store_name, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, store_name=store_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, store_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True"))
        return self.create_user(email, store_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    store_name = models.CharField(max_length=255, unique=True)
    niche = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    slug = AutoSlugField(
        max_length=255,
        populate_from="niche",
        unique=True,
        always_update=False,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    is_staff = models.BooleanField(default=False, db_index=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["store_name"]

    def __str__(self):
        return self.email

    class Meta:
        indexes = [
            # A composite index for queries that filter by both niche and active status
            models.Index(fields=["store_name", "is_active"]),
        ]
        ordering = ["-date_joined"]
        verbose_name = "User"
        verbose_name_plural = "Users"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    email = models.EmailField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    vendor = models.TextField(blank=True)
    phone_number = models.CharField(max_length=12)
    email_verified = models.BooleanField(default=False, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["full_name"]),
        ]

    def __str__(self):
        return f"Vendor Profile: {self.full_name} ({self.user.email})"
