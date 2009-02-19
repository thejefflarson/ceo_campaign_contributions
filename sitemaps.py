from django.contrib.sitemaps import Sitemap
from beckett.finance.models import *

class CeoSitemap(Sitemap):
    def items(self):
        return Ceo.donated.live()
class CandidatesSitemap(Sitemap):
    def items(self):
        return Candidate.objects.all()
class IndustriesSitemap(Sitemap):
    def items(self):
        return Industry.objects.all()
