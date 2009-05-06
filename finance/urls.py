from beckett.finance.models import *
from django.conf.urls.defaults import *
from beckett.finance.feeds import AllDonorCeos

urlpatterns = patterns('beckett.finance.views',
     (r'^robots.txt', 'robots'),
     url(r'^$', 'finance_index', name='finance_index'),
     url(r'^industries/$', 'industry_index', name='industry_index'),
     url(r'^ceos/$', 'ceo_index', name="ceo_index"),
     url(r'^ceos/ceos.json$', 'ceos_to_json', name="all_ceos_to_json"),
     url(r'^ceos/(?P<id_string>[\d-]*).json$', 'ceos_to_json', name="ceos_to_json"),
     url(r'^ceos/(?P<id_string>\d+)/edit$', 'edit_ceo', name='edit_ceo'),
     url(r'^donor/(?P<id_string>\d+)/delete$', 'delete_donor', name='delete_donor'),
     url(r'^zips/(?P<zip_code>\d{5}).json$', 'zips_to_json', name='zips_to_json'), 
     url(r'^zips/(?P<zip_code>\d{5})-data.json$', 'get_zip_data', name="zip_data"), 
     url(r'^candidates/(?P<id_string>\d+)/$', 'candidate_detail', name="candidate_detail"),
    url(r'^industries/(?P<object_id>\d+)/$', 'industry_detail', name="industry_detail", ),
)
urlpatterns += patterns('django.views.generic.list_detail',
    url(r'^ceos/(?P<object_id>\d+)/$', 'object_detail',  {'queryset': Ceo.donated.live(), }, "ceo_detail", ),
    url(r'^candidates/$', 'object_list',  {'queryset': Candidate.objects.all(), }, "candidate_index", ),
    url(r'^industries/(?P<object_id>\d+)/$', 'object_detail',  {'queryset': Industry.objects.all(), }, "industry_detail", ),
)


feeds = {
    'ceo_donors_all': AllDonorCeos,
}

urlpatterns += patterns('',
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
          {'feed_dict': feeds}),
)

