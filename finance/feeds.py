from django.contrib.gis.feeds import Feed, W3CGeoFeed
from beckett.finance.models import *


class AllDonorCeos(Feed):
    title = "All Ceos who donated"
    link = "/finance/ceos/"
    description = "Mapping Ceo Addresses"

    def items(self):
        return Ceo.donated.all()

    def item_geometry(self, item):
        try:
            return item.company_address.point.y, item.company_address.point.x
        except:
            return
