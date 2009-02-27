from django.shortcuts import render_to_response
from django.contrib.sites.models import Site
from django.views.decorators.cache import cache_page
from beckett.finance.models import *
from django.forms.models import modelformset_factory
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseRedirect 
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
import simplejson as json
import random, os
import itertools


def limit(name, seconds, max_value, per_ip=True, limit_exceeded_view=None,
		limit_exceeded_template='connection_limit_exceeded.html'):
	"""Makes a rate-limiting decorator"""
	def default_limit_exceeded_view(*args, **kwargs):
		return render_to_response(limit_exceeded_template)
	limit_exceeded_view = limit_exceeded_view or default_limit_exceeded_view
	def decorator(view):
		def limited_view(request, *args, **kwargs):
			if random.random() < 0.05:
				RequestRate.objects.clean_expired()
			if per_ip:
				ipaddr = request.META['REMOTE_ADDR']
			else:
				ipaddr = None
			(l,tmp) = RequestRate.objects.get_or_create(name=name, ipaddr=ipaddr,
				defaults={'value': 0 })
			if l.request(seconds, max_value):
				return view(request, *args, **kwargs)
			else:
				return limit_exceeded_view(*args, **kwargs)
		return limited_view
	return decorator


def paginate(objects_list, request, num=25):
    paginator = Paginator(objects_list, num) # Show 25 contacts per page
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        return paginator.page(page)
    except (EmptyPage, InvalidPage):
        return paginator.page(paginator.num_pages)

def robots(request):
    return HttpResponse(open(os.path.dirname(os.path.abspath(__file__)) + '/../robots.txt').read(), 'text/plain')

def finance_index(Request):
    donations_by_party = Donation.objects.total_donations_by_party
    donations = Donation.objects.total_donations
    return render_to_response('finance/index.html',{'donations_by_party': donations_by_party,'donations':donations})

def candidate_detail(Request, id_string=None):
    if id_string == None:
       raise Http404
    candidate = get_object_or_404(Candidate, pk=id_string)
    donation_list = Donation.objects.live().filter(candidate=candidate).order_by('ceo__id').select_related()
    ceo_list = paginate([ k for k,v in itertools.groupby(donation_list, lambda v: v.ceo)], Request)
    return render_to_response('finance/candidate_detail.html', {"ceo_list": ceo_list, 'candidate': candidate})

@cache_page(60 * 60)
def ceo_index(Request):
    ceo_list = paginate(Ceo.donated.live().select_related(), Request)
    return render_to_response('finance/ceo_list.html', {"ceo_list": ceo_list})

#           ss   mm   h
@cache_page(60 * 60 * 8)
def industry_index(Request):
    industry_list = Industry.objects.all().select_related()
    return render_to_response('finance/industry_list.html', {'objects': industry_list})

@cache_page(60 * 60 * 8)
def industry_detail(Request, object_id=None):
    object = get_object_or_404(Industry, pk=object_id)
    ceo_list = paginate(object.ceo_set.all(), Request)
    return render_to_response('finance/industry_detail.html',{'object': object, 'ceo_list':ceo_list})
    
@cache_page(60 * 60 * 8)
def ceos_to_json(Request, id_string=None):
    ceo_list = Ceo.donated
    limit = 0
    if id_string==None:
        ceo_list = Ceo.donated.live().select_related()
        limit = 2300
    else:
        ids = id_string.split('-')
        try:
            ids.remove('')
        except ValueError:
            pass
        ceo_list = Ceo.donated.live().filter(id__in=ids)
    places = []
    for ceo in ceo_list:
        if ceo.total_donations > limit:
            place = {
                'icon': ceo.leans,
                'total': ceo.total_donations, 
                'url': ceo.get_absolute_url()
            }
            if ceo.company_address and ceo.company_address.point.x and ceo.company_address.point.y:
                place['pointlong'] = ceo.company_address.point.y
                place['pointlat'] = ceo.company_address.point.x
            places.append(place)
    return HttpResponse(json.dumps(places), mimetype="application/json")

@cache_page(60 * 60)
def zips_to_json(Request, zip_code=None):
    if zip_code == None:
       raise Http404
    zip = Zip.objects.filter(code=zip_code)[0]
    try:
        return HttpResponse(zip.poly.geojson, mimetype="application/json")
    except AttributeError:
       raise Http404

@cache_page(60 * 60 * 8)
def get_zip_data(Request, zip_code=None):
    from beckett.finance.utils.nyt_finance_getter import get_finance_data_json
    if zip_code == None:
        raise Http404
    response = get_finance_data_json(**{'resource_type': 'zips', 'query_file': zip_code})
    if 'errors' in response:
        raise Http404
    party_dict = {}
    for resp in response:
        try:
            party_dict[resp['party']] += resp['total']
        except KeyError:
            party_dict[resp['party']] = resp['total']
    return HttpResponse(max(party_dict, key= lambda a: party_dict.get(a)), mimetype="application/json")

@cache_page(5)
def edit_ceo(Request, id_string=None):
    ceo = get_object_or_404(Ceo, pk=id_string)
    donors = ceo.donor_set.live()
    return render_to_response('finance/edit_ceo.html', {
            'donors': donors,
            'object': ceo
        })

@limit("delete_donor", 2, 60 * 60 * 24 * 7, per_ip=True, limit_exceeded_template="finance/delete_donor_exceeded.html")
@cache_page(0)
def delete_donor(Request, id_string=None):
    current_site = Site.objects.get_current().domain
    donor = get_object_or_404(Donor, pk=id_string)
    if Request.META['HTTP_REFERER'] == "http://%s%s" % (current_site, donor.ceo.get_edit_url()):
        donor.delete_soft()
        return render_to_response('finance/delete_donor.html', { 'ok': 1 })
    return HttpResponseForbidden()

def verify(Request):
    return HttpResponse('verify!')
