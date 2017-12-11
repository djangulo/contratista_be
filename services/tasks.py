import json
import googlemaps
from celery import shared_task
from django.conf import settings

from .models import Address
from contratista_be.celery_app import app

@shared_task
def test(param):
    return f'The test task was executed with argument {param}'
    
@app.task(bind=True)
def enqueue_address(self, instance_id, created):
    print(instance_id, created)
    if created:
        gmaps = googlemaps.Client(key=settings.GOOGLEMAPS_SECRET_KEY)
        # try:
        address = Address.objects.get(pk=instance_id)
        geocode_result = gmaps.geocode(address.formatted_name)
        latlng = json.dumps(geocode_result[0]['geometry']['location'])
        address.latlng = latlng
        address.save()
        print('it ran?')
        # except:
    #        print('it failed yo')