from django_evolution.mutations import *
from django.db import models
import datetime

MUTATIONS = [
    AddField('Donation', 'mtime', models.DateTimeField, initial=datetime.datetime.now())
]
