from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Address
from .tasks import enqueue_address

@receiver(post_save, sender=Address)
def start_address_latlong(sender, instance, created, **kwargs):
    print('signal sent, shit is working')
    print(created)
    enqueue_address.apply_async((instance.id,created,))
