from feedback.forms import FeedBackForm
from django.shortcuts import render_to_response
from django.core.mail import send_mail, BadHeaderError

def feedback(Request):
    form = FeedBackForm() # An unbound form
    msg = ''
    if Request.method == 'POST': 
        form = FeedBackForm(Request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            msg = '<h1>Thanks!</h1>'
            try:
                send_mail(message[:15], message, sender, ['infoatceocontributions@gmail.com'], fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Something\'s fishy. Please try again.')
            form = FeedBackForm()
    return render_to_response('feedback/feedback_base.html', {
        'form': form,
        'message': msg
    })
