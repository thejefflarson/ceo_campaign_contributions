import os
from django.contrib.gis.geos import *
from beckett.finance.models import *
from django.test import TestCase



def initialize_data():
    from django.db.models import get_app, get_apps, get_models
    data_dir = os.path.join(os.path.dirname(__file__), 'wkt')
    def get_file(wkt_file):
        return os.path.join(data_dir, wkt_file)
    zip_obj = Zip.objects.create(code="11238", poly=fromfile(get_file("nz.wkt")))
    party_obj = Party.objects.create(name="Democrat")
    party_obj2 = Party.objects.create(name="Republican")
    candidate_obj = Candidate.objects.create(name="Barack Obama", party=party_obj)
    candidate_obj2 = Candidate.objects.create(name="John McCain", party=party_obj2)
    address_obj = Address.objects.create(address="537 Clinton Ave #4d", state="NY", city="Brooklyn", zip=zip_obj)
    industry_obj = Industry.objects.create(name="Media")
    ceo_obj = Ceo.objects.create(first_name="Jeff", last_name="Larson", website="http://www.thenation.com/", industry=industry_obj, company_name="The Nation", company_address=address_obj)
    donor_obj = Donor.objects.create(ceo=ceo_obj, first_name="Jeff", last_name="Larson", donor_address=address_obj, approved=True, operation='A')
    donation_obj1 = Donation.objects.create(candidate=candidate_obj, donor=donor_obj, donation_amount=100, donation_date="2009-01-03", approved=True, operation='A')
    donation_obj2 = Donation.objects.create(candidate=candidate_obj2, donor=donor_obj, donation_amount=200, donation_date="2009-01-04", approved=True, operation='A')
    donation_obj3 = Donation.objects.create(candidate=candidate_obj, donor=donor_obj, donation_amount=200, donation_date="2009-01-05", approved=False, operation='A')
    donation_obj4 = Donation.objects.create(candidate=candidate_obj2, donor=donor_obj, donation_amount=200, donation_date="2009-01-06", approved=True, operation='D')

class DonorTest(TestCase):
    def setUp(self):
        initialize_data()
        self.donor_obj = Donor.objects.get(first_name="Jeff")
        
    def test_total_donations(self): #must start with the  word test
        """
        Tests the total_donations property on donor objects
        """
        self.failUnlessEqual(self.donor_obj.total_donations, 300)
    
    def test_donor_delete_soft(self):
        self.donor_obj.delete_soft()
        self.failUnlessEqual(self.donor_obj.operation, 'D')
        self.failUnlessEqual(self.donor_obj.approved, False)
        for donation in self.donor_obj.donation_set.live():
            self.failUnlessEqual(donation.operation, 'D')
            self.failUnlessEqual(donation.approved, False)
            

class CeoTotalDonationsTest(TestCase):
    def setUp(self):
        initialize_data()
        self.ceo_obj = Ceo.objects.get(first_name="Jeff")
        self.donations_by_party = { "Democrat": 100, "Republican": 200 }

    def test_ceo_total_donations(self):
        self.failUnlessEqual(self.ceo_obj.total_donations, 300)

    def test_ceo_total_donations_by_candidate(self):
        self.failUnlessEqual(self.ceo_obj.total_donations_by_candidate(Candidate.objects.get(name="Barack Obama")), 100)
        self.failUnlessEqual(self.ceo_obj.total_donations_by_candidate(Candidate.objects.get(name="John McCain")), 200)
    
    def test_total_ceo_donations(self):
        self.failUnlessEqual(Ceo.donated.total_donations, 300)

    def test_industry_total_donations_by_party(self):
        self.failUnlessEqual(self.ceo_obj.total_donations_by_party, self.donations_by_party)

    def test_leans(self):
        self.failUnlessEqual(self.ceo_obj.leans, 'Republican')

class IndustryTotalDonationsTest(TestCase):
    def setUp(self):
        initialize_data()
        self.industry_obj = Industry.objects.get(name="Media")
        self.donations_by_party = { "Democrat": 100, "Republican": 200 }

    def test_industry_total_donations(self):
        self.failUnlessEqual(self.industry_obj.total_donations, 300)

    def test_industry_total_donations_by_party(self):
        self.failUnlessEqual(self.industry_obj.total_donations_by_party, self.donations_by_party)

class DonationsTest(TestCase):
    def setUp(self):
        initialize_data()
        self.donation_obj = Donation.objects.all()[0]
        self.donation_obj.save()
        self.all_donations = Donation.objects

    def test_donations_save(self):
        self.failUnlessEqual(self.donation_obj.party_name, self.donation_obj.candidate.party.name)
        self.failUnlessEqual(self.donation_obj.candidate_name, self.donation_obj.candidate.name)
        self.failUnlessEqual(self.donation_obj.ceo, self.donation_obj.donor.ceo)

    def test_donations_totals(self):
        self.failUnlessEqual(Donation.objects.total_donations_by_party, { "Democrat": 100, "Republican": 200 }) 
        self.failUnlessEqual(self.all_donations.total_donations, 300) 

    def test_donations_delete_soft(self):
        self.donation_obj.delete_soft()
        self.failUnlessEqual(self.donation_obj.operation, 'D')
        self.failUnlessEqual(self.donation_obj.approved, False)
