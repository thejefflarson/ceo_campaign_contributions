import sys
import os
from django.core.handlers.wsgi import WSGIHandler
from repoze.profile.profiler import AccumulatingProfileMiddleware

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'beckett.settings'

application = WSGIHandler()
#application = AccumulatingProfileMiddleware(
#    application,
#    log_filename=os.path.dirname(os.path.abspath(__file__)) +'/logs/beckettprofile.log',
#    discard_first_request=True,
#    flush_at_shutdown=True,
#    path='/__profile__')


