import math, sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../../')
from beckett import settings
from django.core.management import setup_environ
setup_environ(settings)
import django
from django.db.models import Count
import psycopg2
from django.contrib.gis.measure import D, A
from beckett.finance.models import *
from beckett.finance.utils.nyt_finance_getter import get_finance_data_json
from beckett.finance.utils.parser import save_donor
from beckett.finance.utils.geocoder import geo_code




def search_100_miles(ceo):
    json_data = get_finance_data_json(**{
                        'resource_type':'contributions',
                        'query_file': 'donorsearch',
                        'search':{
                            'fname': ceo.first_name,
                            'lname': ceo.last_name,
                        }
                       })
    if 'errors' not in json_data:
        for donor_json in json_data:  
            try:
                zip_obj = Zip.objects.get(code=donor_json['donor_zip5'])
            except Zip.DoesNotExist:
                zip_obj = Zip(code=donor_json['donor_zip5'])
                zip_obj.save()
            except Zip.MultipleObjectsReturned:
                zip_obj = Zip.objects.filter(code=donor_json['donor_zip5'])[0]

            try:
                address = Address.objects.get(**{
                    'address': donor_json['donor_address1'],
                    'address2': donor_json['donor_address1'],
                    'state':donor_json['donor_state'],
                    'city':donor_json['donor_city'],
                    'zip':zip_obj
                })
                return
            except Address.DoesNotExist:
                address = Address(**{
                    'address': donor_json['donor_address1'],
                    'address2': donor_json['donor_address1'],
                    'state':donor_json['donor_state'],
                    'city':donor_json['donor_city'],
                    'zip':zip_obj
                })

            address = geo_code(address)
            if address.point:
                addresses = Address.objects.filter(point__distance_lte=(address.point, D(mi=70)))
                if addresses:
                    for address in addresses:
                        if address == ceo.company_address:
                            print address
                            print donor_json
                            save_donor([donor_json], ceo)
    return json_data


if __name__ == "__main__":
    ceos = Ceo.objects.all()
    ceo_list = []
    for ceo in ceos:
#        try:
            search_100_miles(ceo)
#        except ValueError:
            print 'error %s' % (ceo)
            ceo_list.append(ceo)

    while ceo_list:
        try:
            ceo = ceo_list.pop()
            search_100_miles(ceo)
        except ValueError:
            print 'error %s' % (ceo)
            ceo_list.append(ceo)


