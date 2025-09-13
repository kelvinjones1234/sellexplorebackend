from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import User
from .models import StoreConfigurations, Logo, Cover


@receiver(post_save, sender=User)
def create_store_for_new_user(sender, instance, created, **kwargs):
    if created:
        # Automatically create a store for every new user
        StoreConfigurations.objects.create(
            user=instance,
        )


@receiver(post_save, sender=User)
def create_store_for_new_user(sender, instance, created, **kwargs):
    if created:
        # Automatically create a store for every new user
        Logo.objects.create(
            user=instance,
        )



@receiver(post_save, sender=User)
def create_store_for_new_user(sender, instance, created, **kwargs):
    if created:
        # Automatically create a store for every new user
        Cover.objects.create(
            user=instance,
        )
