import sys, os
project = os.path.dirname(os.path.abspath(__file__)) + '/../../..' 
sys.path.append(project)
from django.core.management import setup_environ
from beckett import settings
setup_environ(settings)
import django
from beckett.finance.models import *
from django.db import connection
import datetime



def grab_donation_graph():

    url =  'http://chart.apis.google.com/chart?cht=ls&chs=100x16&chco=812526,265283&chd=t:'
    cursor = connection.cursor()
    y_by_party =[]
    max_d = 0
    for party in Party.objects.all():
        startdate = datetime.date(2006,10,1)
        enddate = datetime.date(2008,10,1)
        months = {} 
        while startdate < enddate:
            startdate += datetime.timedelta(30)
            print startdate.strftime("%m")
            months[startdate.strftime('%y %m')] = 0
        cursor.execute("""
        select sum(donation_amount), to_char(donation_date, 'YY MM') as d 
        from finance_donation where party_name='%s' group by d order by d;
        """ % (party.name))
        data_points =  cursor.fetchall()
        series = ''
        for d in data_points:
            if months.has_key(d[1]) and d[0] > 0:
                months[d[1]] = d[0]/1000.0
        keys = months.keys()
        keys.sort()
        points = [months[key] for key in keys]
        m = max(points)
        max_d = max_d > m and max_d or m
        series = ",".join([str(point) for point in points])
        y_by_party.append(series)
        print party.name
    url += "|".join(y_by_party)
    print url 
    print max_d






if __name__ == "__main__":
    grab_donation_graph()
