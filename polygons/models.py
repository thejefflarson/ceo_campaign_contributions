from django.contrib.gis.db import models
from django.contrib.localflavor.us.models import USStateField

# Create your models here.
class Zip(models.Model):
    code = models.CharField(max_length=5) # not unique due to discontiguous zip codes
    poly = models.MultiPolygonField(srid='4326', null=True) #mfing uspa, and census don't line up
    objects = models.GeoManager()
    def __unicode__(self):
        return "%s" % self.code

class State(models.Model):
    state = USStateField()
    fips = models.IntegerField(primary_key=True)
    objects = models.GeoManager()

class CongressionalDistrict(models.Model):
    state = models.ForeignKey(State)
    district = models.IntegerField(unique=True)
    poly = models.MultiPolygonField(srid='4326')
    objects = models.GeoManager()
