import json
import googlemaps
from celery import shared_task
from django.conf import settings

from .models import Address
from contratista_be.celery_app import app

@app.task(bind=True, default_retry_delay=60,
            retry_kwargs={'max_retries': 5})
def enqueue_address(self, instance_id):
    gmaps = googlemaps.Client(key=settings.GOOGLEMAPS_SECRET_KEY)
    try:
        query = Address.objects.filter(pk=instance_id)
        address_obj = query.get(pk=instance_id)
        geocode_result = gmaps.geocode(address_obj.formatted_name)
        latlng = json.dumps(geocode_result[0]['geometry']['location'])
        query.update(latlng=latlng)
    except:
        self.retry()
