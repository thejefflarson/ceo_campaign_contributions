import urllib, re, copy, os, pprint
from datetime import date
from beckett import settings
from django.core.management import setup_environ
setup_environ(settings)
import django
from django.contrib.gis.measure import D, A
from beckett.finance.models import *
from beckett.finance.utils.nyt_finance_getter import get_finance_data_json
from BeautifulSoup import BeautifulSoup, SoupStrainer, MinimalSoup, BeautifulStoneSoup


def save_donor(donor_json, ceo):
    for donation_json in donor_json:
        candidate_name =""
        if donation_json['candidate_full_name'] == "McCain-Palin COMPLIANCE FUND INC.":
            donation_json['candidate_full_name'] = "John McCain" # Cmon NYTIMES!
        candidate_name = donation_json['candidate_full_name'].split(" ")
        candidate_name.reverse()
        query_string = ",".join("%s" % v for v in candidate_name)
        #print query_string
        try:
            candidate_json = get_finance_data_json(**{'resource_type': 'candidates', 'query_file': query_string})
        except:
            return

        for candidate in candidate_json:
            try:
                party, created = Party.objects.get_or_create(**{ 'name': candidate['party'] })
                candidate, created = Candidate.objects.get_or_create(**{ 
                            'name': donation_json['candidate_full_name'], 'party': party })
            except:
                return #compliance fundds argh

        zip_obj = Zip.objects.filter(code=donation_json['donor_zip5'])
        if zip_obj:
            zip_obj = zip_obj[0]
        else:
            zip_obj = Zip(code=donation_json['donor_zip5'])
            zip_obj.save()
        address, created = Address.objects.get_or_create(**{
            'address': donation_json['donor_address1'],
            'address2': donation_json['donor_address1'],
            'state':donation_json['donor_state'],
            'city':donation_json['donor_city'],
            'zip':zip_obj
        })
        donor, created = Donor.objects.get_or_create(**{'ceo': ceo,
                                                            'first_name': donation_json['donor_first_name'],
                                                            'last_name': donation_json['donor_last_name'],
                                                            'donor_address': address})
        year, month, day = donation_json['donation_date'].split("-")
        d = date(int(year), int(month), int(day))
        donation, created = Donation.objects.get_or_create(**{'candidate': candidate,
                                                                'donor': donor,
                                                                'donation_amount': donation_json['donation_amount'],
                                                                'donation_date': d, })

    
def save_ceo(**kwargs):
    ceos = list()
    if kwargs.has_key('CEO'):
        ceos = [kwargs['CEO'].split(" ")]
    elif kwargs.has_key('CEOs'):
        cs = kwargs['CEOs'].split(", ")
        for c in cs:
            a = c.split(" ")
            ceos.append(a)
    for name in ceos:
        search = dict()
        if len(name) > 2:
            search = {
                    'fname': name[0],
                    'lname': name[2],
                }
        elif len(name) == 2:
            search = {
                    'fname': name[0],
                    'lname': name[1],
                }
        else:
            #print "No name!"
            return
        city_state_zip = kwargs['Address1'].split(" ")
        zip = city_state_zip.pop()
        state = city_state_zip.pop()
        city = " ".join(city_state_zip).replace(",", '')
 
        if len(zip) == 5:
            zip_obj = Zip.objects.filter(code=zip)
            if zip_obj:
                zip_obj = zip_obj[0]
            else:
                zip_obj = Zip(code=zip)
                zip_obj.save()
            address, created = Address.objects.get_or_create(**{
                'address': kwargs['Address'],
                'address2': kwargs['Address1'],
                'state':state,
                'city':city,
                'zip':zip_obj
            })
            try:
                ceo, created = Ceo.objects.get_or_create(**{
                'first_name': search['fname'],
                'last_name': search['lname'],
                'website': kwargs['Website'],
                'company_name': kwargs['Company'],
                'company_address':address
                })
            except:
                return #### dynasties
            search['zip'] = zip
            donor_json = get_finance_data_json(**{'resource_type': 'contributions', 
                            'query_file': 'donorsearch',
                            'search': search,
                            })
            if donor_json != 'errors':
                save_donor(donor_json, ceo)
            elif zip_obj.poly:
                #nearby_zips = Zip.objects.filter(poly__dwithin=(zip[0].centroid, .1))[:9]
                nearby_zips = Zip.objects.filter(poly__touches=zip_obj.poly)[:9]
                for zip in nearby_zips:
                    search['zip'] = zip.code
                    donor_json = get_finance_data_json(**{'resource_type': 'contributions', 
                            'query_file': 'donorsearch',
                            'search': search,
                            })
                    if donor_json != 'errors':
                        save_donor(donor_json, ceo)

def get_ceo(url):
    page = urllib.urlopen(url)
    data_boxen = SoupStrainer('div', {'class': 'snapUniqueData'})
    soup = BeautifulSoup(page, parseOnlyThese=data_boxen)
    for tag in soup.findAll():
        tag.hidden = True
    ceo_table = soup.renderContents().decode('utf8')
    ceo_table = re.sub(r'(\t+?|Rank:.*?\))', '', ceo_table).replace(' vs. Top 10', '').replace('Compare tool:', 'Company:')
    ceo_table = re.sub(r'(\n)', '|', ceo_table).replace('||', "")
    ceo_array = ceo_table.split('|')
    ceo_array = [re.sub('^\s', '', field).split(': ') for field in ceo_array]
    ceo_dict = dict()
    for field in ceo_array:
        if field[0]:
            if len(field):
                if 1 < len(field) <= 2:
                    ceo_dict[str(field[0])] = field[1]
                elif len(field) == 1:
                    ceo_dict['Address1'] = field[0]
    if ceo_dict.keys():
        #print ceo_dict
        save_ceo(**ceo_dict)

    
def get_ceo_urllist_by_letter(letter):
    CNN_BASE = "http://money.cnn.com/magazines/fortune/fortune500/2008/ceos/"
    page = urllib.urlopen(CNN_BASE + letter + ".html")
    tds = SoupStrainer('td', {'class': 'alignLft'})
    soup = BeautifulSoup(page, parseOnlyThese=tds)
    links = soup.findAll('a')
    for link in links:
            #print(link['href'])
            get_ceo(CNN_BASE + link['href'])
        #except Exception, inst:
            #print "error! " + link['href']


if __name__ == "__main__":
    letters = "" # ABCDEFGHI
    for letter in letters:
        get_ceo_urllist_by_letter(letter)
    get_ceo_urllist_by_letter('index')
