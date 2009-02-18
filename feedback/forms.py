from django import forms

class FeedBackForm(forms.Form):
    sender = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
