import urllib, re, copy, os, pprint
from beckett import settings
from django.core.management import setup_environ
setup_environ(settings)
import django
from django.contrib.gis.geos import Point

from geopy import geocoders
from beckett.finance.models import *

def geo_code(address):
    app_id = "ABQIAAAA6JvOBb2RTumkCsWOAMKcmBRy05bz2Ez3szx9GRUEydtISW_OkxRqGIBjuawVqDpmZxzBW-l_IaKwxg"
    g = geocoders.Google(app_id)
    try:
        res = g.geocode(address.address + "," + address.zip.code + " USA",)
        place, (lat, lng) = res
        if lat and lng:
            address.point = Point((lat, lng), srid=4326)
            address.save()
    except ValueError, e:
        print e
            
    return address
    


if __name__ == "__main__":
    app_id = "ABQIAAAA6JvOBb2RTumkCsWOAMKcmBRy05bz2Ez3szx9GRUEydtISW_OkxRqGIBjuawVqDpmZxzBW-l_IaKwxg"
    g = geocoders.Google(app_id)
    addresses = Address.objects.filter(point=None)
    for address in addresses:
        try:
            place, (lat, lng) = g.geocode(address.address + "," + address.city + ", " + address.state + " " + address.zip.code + " USA")
            address.point = Point((lat, lng), srid=4326)
            address.save()
            print "%s: %.5f, %.5f" % (place, lat, lng)
        except ValueError, e:
            print e
