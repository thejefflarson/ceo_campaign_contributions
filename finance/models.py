from django.contrib.gis.db import models
from django.db.models import Sum, Q
import datetime


# Create your models here.

class Zip(models.Model):
    code = models.CharField(max_length=5) # not unique due to discontiguous zip codes
    poly = models.MultiPolygonField(srid=4269, null=True) #mfing uspa, and census don't line up
    objects = models.GeoManager()
    def __unicode__(self):
        return "%s" % self.code

class Party(models.Model):
    name = models.CharField(max_length=24, unique=True)
    def _total_donations(self):
        candidates = self.candidate_set.all()
        total_donations = 0
        for candidate in candidates:
            total_donations += candidate.total_donations
        return total_donations
    total_donations = property(_total_donations)

    def __unicode__(self):
        return "%s" % self.name

class Candidate(models.Model):
    name = models.CharField(max_length=63, unique=True)
    party = models.ForeignKey(Party)
    
    def _total_donations(self):
        return self.donation_set.live().aggregate(Sum('donation_amount'))['donation_amount__sum']
    total_donations = property(_total_donations)

    class Meta:
        ordering = ['-party', 'name']

    @models.permalink
    def get_absolute_url(self):
        return ('candidate_detail', [str(self.id)])


class Address(models.Model):
    address = models.TextField()
    address2 = models.TextField(null=True)
    state = models.CharField(max_length=2)
    city = models.CharField(max_length=63)
    zip = models.ForeignKey(Zip)
    point = models.PointField(srid='4326', null=True)
    objects = models.GeoManager()
    class Meta:
        unique_together = ('address', 'address2', 'city', 'state', 'zip')


class Industry(models.Model):
    name = models.CharField(max_length=63)

    @property   
    def total_donations(self):
        return sum([c.total_donations for c in self.ceo_set.all().select_related()])
    
    @property
    def total_donations_by_party(self):
        ceos = self.ceo_set.all()
        total_donations = {}
        for ceo in ceos:
            donations = ceo.donation_set.live().select_related()
            for donation in donations:
                if donation.party_name in total_donations:
                    total_donations[donation.party_name] += donation.donation_amount 
                else:
                    total_donations[donation.party_name] = donation.donation_amount
        return total_donations
    
    class Meta:
        ordering = ["name"]
    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('industry_detail', [str(self.id)])

class CeoManager(models.GeoManager):
    @property
    def total_donations(self):
        return sum([c.total_donations for c in super(CeoManager, self).get_query_set().all()])

    
    def live(self):
        return super(CeoManager, self).get_query_set().filter(donor__isnull=False).distinct()

class Ceo(models.Model):
#add slug field with first name last name
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)
    website = models.URLField()
    industry = models.ForeignKey(Industry, null=True)
    company_name = models.CharField(max_length=63, unique=False)
    company_address = models.ForeignKey(Address)
    ctime = models.DateTimeField(auto_now_add=True)
    mtime = models.DateTimeField(auto_now=True)
    objects = models.GeoManager()
    donated = CeoManager()

    def __unicode__(self):
        return self.first_name + " " + self.last_name
    
    def total_donations_by_candidate(self, candidate):
        return self.donation_set.live().filter(candidate_name=candidate.name).aggregate(Sum('donation_amount'))['donation_amount__sum']
    
    @property
    def total_donations(self):
        donors = self.donor_set.all().select_related()
        total_donations = 0
        for donor in donors:
            total_donations += donor.total_donations
        return total_donations
    
    @property
    def total_donations_by_party(self):
        parties = Party.objects.all()
        party_dict = {}
        for party in parties:
            total_donations = self.donation_set.live().filter(party_name = party.name).aggregate(Sum('donation_amount'))['donation_amount__sum']
            try:
                party_dict[party.name] += total_donations
            except KeyError:
                if total_donations == None:
                    party_dict[party.name] = 0
                else:
                    party_dict[party.name] = total_donations
        return party_dict 
    
    @property
    def leans(self):
        return max(self.total_donations_by_party, key = lambda a: self.total_donations_by_party.get(a))

    class Meta:
        #unique_together = ('company_name', 'last_name')
        ordering = ['last_name']

    @models.permalink
    def get_absolute_url(self):
        return ('ceo_detail', [str(self.id)])

    @models.permalink
    def get_edit_url(self):
        return ('edit_ceo', [str(self.id)])

class DonorManager(models.GeoManager):
    def live(self):
        return self.filter(Q(approved=True, operation='A') | Q(approved=False, operation='D'))

class Donor (models.Model):
    choices = ( ('A', 'add'), ('D', 'delete') )
    operation = models.CharField(max_length=1, choices=choices, default='A')
    approved = models.BooleanField(default=False)
    ceo = models.ForeignKey(Ceo)
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)
    donor_address = models.ForeignKey(Address)
    ctime = models.DateTimeField(auto_now_add=True)
    mtime = models.DateTimeField(auto_now=True)
    objects = DonorManager()
    
    @property
    def total_donations(self):
        return self.donation_set.live().aggregate(Sum('donation_amount'))['donation_amount__sum']

    class Meta:
        unique_together = ('donor_address','first_name', 'last_name')

    def save_and_approve(self):
        self.operation = 'A'
        self.approved = True
        for donation in self.donation_set.all():
            donation.save_and_approve()
        self.save()

    def delete_soft(self):
        self.operation = 'D'
        self.approved = False
        for donation in self.donation_set.live():
            donation.delete_soft()
        self.save()

class DonationManager(models.GeoManager):
    use_for_related_fields = True
    def live(self):
        return self.filter(Q(approved=True, operation='A')  | Q(approved=False, operation='D'))
    
    @property
    def total_donations_by_party(self):
        parties=Party.objects.all()
        party_dict={}
        for party in parties:
            try:
                party_dict[party.name] += Donation.objects.live().filter(party_name=party.name).aggregate(Sum('donation_amount'))['donation_amount__sum']
            except KeyError:
                party_dict[party.name] = Donation.objects.live().filter(party_name=party.name).aggregate(Sum('donation_amount'))['donation_amount__sum']
        return party_dict
    
    @property
    def total_donations(self):
        return Donation.objects.live().aggregate(Sum('donation_amount'))['donation_amount__sum'] 
                    


class Donation(models.Model):
    ##### Crowd Sourcing!!!! ##########
    choices = ( ('A', 'Added'), ('D', 'Deleted') )
    operation = models.CharField(max_length=1, choices=choices, default='A')
    approved = models.BooleanField(default=False)
    candidate = models.ForeignKey(Candidate)
    donor = models.ForeignKey(Donor)
    ceo = models.ForeignKey(Ceo)
    candidate_name = models.CharField(max_length=63, null=True)
    party_name = models.CharField(max_length=24, null=True)
    donation_amount = models.IntegerField()
    donation_date = models.DateField()
    ctime = models.DateTimeField(auto_now_add=True)
    mtime = models.DateTimeField(auto_now=True)
    objects = DonationManager()

    class Meta:
        unique_together = ('candidate', 'donor', 'donation_amount', 'donation_date')
        ordering = ['-donation_date']

    def __unicode__(self):
        return "Donation to %s for %s" % (self.candidate_name,self.ceo)

    @models.permalink
    def get_delete_url(self):
        return ('delete_donation', [str(donation.id)])

    def save(self, force_insert=False, force_update=False):
        # denormalization
        self.ceo = self.donor.ceo
        self.candidate_name = self.candidate.name
        self.party_name = self.candidate.party.name
        super(Donation, self).save(force_insert, force_update)
    
    def save_and_approve(self):
        self.operation = 'A'
        self.approved = True
        self.save()

    def delete_soft(self):
        self.operation = 'D'
        self.approved = False
        self.save()


###########################
#      Rate Limiter       #
###########################

class RequestRateManager(models.Manager):
	def clean_expired(self):
		"""Purges old entries from database.

		If you use max_value's greater than 600 (seconds, ten minutes),
		change the following line."""
		l_time = datetime.datetime.now() - datetime.timedelta(seconds = 600)
		self.get_query_set().filter(last_update__lt=l_time).delete()

class RequestRate(models.Model):
	"""Implements a rate limit per IP.

	value is increased at every request by the amount the request specifies,
	which is meant to be the average number of seconds until the same
	request could be made again.

	value decreases at a rate of 1 per second until it is a 0.
	"""
	name = models.CharField(max_length=20)
	ipaddr = models.IPAddressField(blank=True, null=True)
	last_update = models.DateTimeField(auto_now_add=True)
	value = models.FloatField()

	objects = RequestRateManager()

	def update(self):
		this_update = datetime.datetime.now()
		td = this_update - self.last_update
		time_delta_sec = (float(td.days) * 3600.0 * 60.0 + float(td.seconds) +
			float(td.microseconds) / 1000000.0)
		self.value -= time_delta_sec
		if self.value < 0:
			self.value = 0
		self.last_update = this_update
	def request(self, seconds, max_value):
		self.update()
		if self.value + seconds < max_value:
			self.value += seconds
			self.save()
			return True
		else:
			self.save()
			return False

