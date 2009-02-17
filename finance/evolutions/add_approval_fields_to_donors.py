
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Donor', 'approved', models.BooleanField, initial=True),
    AddField('Donor', 'operation', models.CharField, initial='A', max_length=1)
    ]
