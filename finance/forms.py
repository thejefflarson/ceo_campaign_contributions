from django.forms.models import ModelForm
from django.forms.fields import Field

class DonationDeleteForm(ModelForm):
    class Meta:
        model=Donation
        fields=None
