from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Address
from .tasks import enqueue_address

@receiver(post_save, sender=Address)
def start_address_latlong(sender, instance, **kwargs):
    print('signal sent, shit is working')
    enqueue_address.delay(instance.id)
