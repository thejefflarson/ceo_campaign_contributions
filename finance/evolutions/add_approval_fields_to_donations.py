from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Donation', 'approved', models.BooleanField, initial=True),
    AddField('Donation', 'operation', models.CharField, initial='A', max_length=1),
    DeleteModel('DonationQueue')
]

