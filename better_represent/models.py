import subprocess
import simplejson as json
from math import fabs
from hashlib import md5
from datetime import date, timedelta, datetime
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.query import QuerySet
from django.db.models import Count, Max, Q
from beckett.polygons.models import Zip, CongressionalDistrict, State
from persistent_store.django_tokyo_persistent_store import tyrant_store
# Create your models here.


def address_normalize(address):
    return slugify(address.lower()).replace("-", " ")

class Address(models.Model):
    """
    simple address model, tries to geocode, and if unsuccessful doesn't save and raises AddressPointNotFoundError
    """
    address = models.TextField(unique=True)
    slug = models.SlugField(unique=True)
    zip = models.ForeignKey(Zip, related_name="%(class)s_related")
    point = models.PointField(srid=4326)
    objects = models.GeoManager()
    class Meta:
        unique_together = ('address', 'zip')

    class AddressPointNotFoundError(Exception):
        def __init__(self, address, json):
            self.address = address
            self.json = json
        def __str__(self):
            return "address: %s GeoCoder Returned %s" % (self.address, str(self.json))
    

    def save(self, force_insert=False, force_update=False):
        self.address = address_normalize(self.address)
        self.slug = slugify(self.address)
        try:
            geocoded = json.loads(subprocess.Popen(["/web/geocode_db/query.pl", 
                        "/web/geocode_db/geocoder.db", 
                        self.address], 
                        stdout=subprocess.PIPE).communicate()[0]).pop()
            self.zip, created = Zip.objects.get_or_create(code=geocoded["zip"])
            self.point = Point(float(geocoded["long"]), float(geocoded["lat"]))
        except (KeyError, IndexError):
            raise self.AddressPointNotFoundError(address=self.address, 
                                                    json=subprocess.Popen(["/web/geocode_db/query.pl", 
                                                                            "/web/geocode_db/geocoder.db", 
                                                                            self.address], 
                                                                            stdout=subprocess.PIPE).communicate())
        return super(Address, self).save(force_insert, force_update)

    @models.permalink
    def get_absolute_url(self):
        return ('address_detail', (), {'address_slug':self.slug})

    def __unicode__(self):
        return u'%s' % (self.address)

class Congress(models.Model):
    chamber = models.TextField()
    session = models.IntegerField()
    class Meta:
        unique_together = ('chamber', 'session')
        verbose_name_plural = 'congresses'


class Party(models.Model):
    name = models.CharField(max_length=24, unique=True)


        
class RepManager(models.Manager):
    use_for_related_fields = True
    def get_query_set(self):
        return self.model.QuerySet(self.model)


class GenericRep(models.Model):
    TYPE = (
            ('H', 'Representative'),
            ('S', 'Senator'),
            )
    type = models.CharField(max_length=1, choices=TYPE)
    member_id = models.CharField(max_length=10, unique=True)
    first_name = models.TextField()
    last_name = models.TextField()
    party = models.ForeignKey(Party)
    state = models.ForeignKey(State)
    end_date = models.DateField(null=True)
    congresses = models.ManyToManyField(Congress, through='CongressMembership')
    district = models.ForeignKey(CongressionalDistrict, null=True)
    slug = models.SlugField(max_length=50)
    objects = RepManager()
    
    def save(self, force_insert=False, force_update=False):
        self.slug = slugify("-".join([self.first_name, self.last_name]))
        return super(GenericRep, self).save(force_insert, force_update)
        
    
    @property
    def tyrant_key(self):
        return "rep-%s-items" % self.pk

    def _set_items(self, value):
        tyrant_store.set(self.tyrant_key, value)

    def _get_items(self):
        return tyrant_store.get(self.tyrant_key)
    
    items = property(_get_items, _set_items)
    
    def stats_by_day(self, timeframe=None, start=None):
        if isinstance(timeframe, timedelta) == False:
            timeframe=timedelta(days=30)
        if isinstance(start, date) == False:
            start=date.today()
        raw_days = [n for n in 
                    self.repstat_set.filter(Q(stat__gte=start-timeframe) & Q(stat__lte=start)).values('stat').annotate(num_stats=Count('id')).order_by('-stat')]
        data = {}
        for n in range(timeframe.days):
            data[start-timedelta(days=n)] = 0
        for day in raw_days:
            just_the_date = day['stat']
            data[just_the_date] = day['num_stats']
        data_zipped = [{'date':k, 'num_stats':v} for k,v in zip(data.keys(), data.values())]
        data_zipped.sort(key=lambda x: x['date'])
        return data_zipped
    
    class QuerySet(QuerySet):
        def live(self):
            return self.filter(**{'end_date__gt':date.today()})
        def old(self):
            return self.filter(**{'end_date__lt':date.today()})
        def total_stats(self, timeframe=None, start=None):
            if isinstance(timeframe, timedelta) == False:
                timeframe=timedelta(days=30)
            if isinstance(start, date) == False:
                start=date.today()
            return self.extra(select={'stats__count': 'select coalesce(sum(num_stats), 0) from "better_represent_repstat_max_stat" where "rep_id"="better_represent_genericrep"."id" and "better_represent_repstat_max_stat"."stat" >= \'%s\'' % (start-timeframe)}).order_by('-stats__count')
        def annotate_max_stats(self):
            """ put yr thinkin' hat on"""
            return self.extra(select={'stats__max': 'select coalesce(max(num_stats),0) as max_stats from "better_represent_repstat_max_stat" where "rep_id"="better_represent_genericrep"."id"'})

    class Meta:
        pass
    
    @models.permalink
    def get_absolute_url(self):
        return ('rep_detail', (), {'rep_id':self.pk, 'slug': self.slug})

    def __unicode__(self):
        return "%s %s %s" % ( self.get_type_display(), self.first_name, self.last_name)

    def save(self, force_insert=False, force_update=False):
        if self.district and self.type=='S':
            raise IntegrityError
        return super(GenericRep, self).save(force_insert, force_update)


class CongressMembership(models.Model):
    title = models.CharField(max_length=64)
    congress = models.ForeignKey(Congress)
    rep = models.ForeignKey(GenericRep)
    class Meta:
        pass



class RepStat(models.Model):
    stat = models.DateField()
    hash = models.CharField(max_length=128)
    rep = models.ForeignKey(GenericRep)

    def _encode_hash(self, title):
        return md5(title.encode('utf-8')).hexdigest()

    def set_hash(self, title):
        hash = self._encode_hash(title)
        self.hash = hash

    def check_hash(self, title):
        return self.hash == self._encode_hash(title)

    def __unicode__(self):
        return "%s %s" % (self.stat, self.hash)

    class Meta:
        unique_together=('stat', 'hash', 'rep')
