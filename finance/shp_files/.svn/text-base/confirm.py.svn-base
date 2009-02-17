#! /usr/bin/python
from django.core.management import setup_environ
from nyt import settings 
setup_environ(settings)
import django
from nytfinance.models import Zip
from django.contrib.gis.measure import D
from django.contrib.gis.geos import GEOSGeometry, Point


brooklyn = list(Zip.objects.filter(code="94903").centroid())
print brooklyn[0].centroid

#print Zip.objects.filter(poly__touches=pbrooklyn.poly)
nearby_zips = Zip.objects.filter(poly__dwithin=(brooklyn[0].centroid, .5))
for zip in nearby_zips:
    print zip.code
