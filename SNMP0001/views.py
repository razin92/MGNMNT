from django.shortcuts import render, HttpResponseRedirect,reverse, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from info.models import Subscriber, Switch, Providerinfo
from django.utils import timezone

def my_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
    else:
        return render(request, 'index.html', {
            'error_message': "Неправильный логин или пароль"
        })

@login_required
def index(request):
    switch = Switch.objects.all()
    provider_set = Providerinfo.objects.all().order_by('name')
    subscribers = Subscriber.objects.all()
    subscribers_now = Subscriber.objects.filter(date__month=timezone.now().month)
    result = ["%s: { %s }" % (provider.name, Subscriber.objects.filter(provider=provider).count()) for provider in provider_set]
    result_now = ["%s: { %s }" % (provider.name, Subscriber.objects.filter(
        provider=provider,
        date__month=timezone.now().month,
        date__year=timezone.now().year).count())
                  for provider in provider_set]
    return render_to_response("index.html", {
        'switch': switch,
        'subscribers': subscribers,
        'result': result,
        'subscribers_now': subscribers_now,
        'result_now': result_now,
	    'user': User
    })

def logout_view(request):
    logout_view(request)
