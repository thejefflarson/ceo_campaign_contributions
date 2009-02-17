
from nyt import settings
from django.core.management import setup_environ
setup_environ(settings)
import django
from nyt.nytfinance.models import *

zip_objs = Zip.objects.filter(poly=None)
for zip in zip_objs:
    zip.delete()
