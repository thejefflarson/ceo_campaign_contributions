from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from beckett.sitemaps import *
admin.autodiscover()

sitemaps = {
    'ceos': CeoSitemap,
    'industries': IndustriesSitemap,
    'candidates': CandidatesSitemap,
}
urlpatterns = patterns('',
    # Example:
    # (r'^beckett/', include('beckett.foo.urls')),

     (r'^', include('finance.urls')),
     (r'^better_represent/', include('better_represent.urls')),
     (r'^feedback/', 'feedback.views.feedback'),
     (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
     (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
