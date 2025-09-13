from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import User
from .models import Store


@receiver(post_save, sender=User)
def create_vendor_profile(sender, instance, created, **kwargs):

    if created:
        Store.objects.create(
            user=instance,
        )



