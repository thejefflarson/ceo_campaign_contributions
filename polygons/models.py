from django.contrib.gis.db import models

# Create your models here.
class Zip(models.Model):
    code = models.CharField(max_length=5) # not unique due to discontiguous zip codes
    poly = models.MultiPolygonField(srid=4269, null=True) #mfing uspa, and census don't line up
    objects = models.GeoManager()
    def __unicode__(self):
        return "%s" % self.code

class State(models.Model):
    name = models.CharField(max_length=20, unique=True)
    s_name = models.CharField(max_length=2, unique=True)
    objects = models.GeoManager()

class CongressionalDistrict(models.Model):
    district = models.IntegerField(unique=True)
    poly = models.MultiPolygonField(srid=4269)
    objects = models.GeoManager()

