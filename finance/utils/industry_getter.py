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

def update_ceo_industry(url):
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
        print ceo_dict
    ceos = list()
    if ceo_dict.has_key('CEO'):
        ceos = [ceo_dict['CEO'].split(" ")]
    elif ceo_dict.has_key('CEOs'):
        cs = ceo_dict['CEOs'].split(", ")
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
            print "No name!"
            return

        ceo  = Ceo.objects.get(**{
            'first_name': search['fname'],
            'last_name': search['lname'],
            'website': ceo_dict['Website'],
            'company_name': ceo_dict['Company'],
        })
        
        ind_box = SoupStrainer('div', {'id': 'industryName'})
        page = urllib.urlopen(url)
        industry_soup = BeautifulSoup(page, parseOnlyThese=ind_box)
        print industry_soup
        industry_link = industry_soup.find('a')
        
        industry = industry_link.contents[0]
        print industry
        industry_obj, created = Industry.objects.get_or_create(**{'name': unicode(industry)})
        ceo.industry = industry_obj
        print ceo.pk, ceo.industry.pk
        ceo.save()
        return  


def get_ceo_urllist_by_letter(letter):
    CNN_BASE = "http://money.cnn.com/magazines/fortune/fortune500/2008/ceos/"
    page = urllib.urlopen(CNN_BASE + letter + ".html")
    tds = SoupStrainer('td', {'class': 'alignLft'})
    soup = BeautifulSoup(page, parseOnlyThese=tds)
    links = soup.findAll('a')
    for link in links:
        #try:
            print(link['href'])
            update_ceo_industry(CNN_BASE + link['href'])
        #except Exception, inst:
            print "error! " + link['href']


if __name__ == "__main__":
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" # ABCDEFGHI
    for letter in letters:
        get_ceo_urllist_by_letter(letter)
    get_ceo_urllist_by_letter('index')
