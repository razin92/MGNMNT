from django.shortcuts import render, HttpResponseRedirect,reverse, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from info.models import Subscriber, Switch, Providerinfo
from django.utils import timezone

def my_login(request):
    username = request.POST['username']
    password = request.POST['password']
    if username == 'Android':
        return render(request, 'registration/login.html', {
            'error_message': "Доступ запрещен!"
        })
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
    else:
        return render(request, 'registration/login.html', {
            'error_message': "Неправильный логин или пароль"
        })

@login_required
def index(request):
    switch = Switch.objects.all()
    provider_set = Providerinfo.objects.all().order_by('name')
    subscribers = Subscriber.objects.filter(port__isnull=False)
    subscribers_now = Subscriber.objects.filter(
        date__month=timezone.now().month, date__year=timezone.now().year)

    class SubscribersCounter():
        def __init__(self, name, counter):
            self.name = name
            self.counter = counter

    result = [SubscribersCounter(
        provider.name, Subscriber.objects.filter(
            provider=provider, port__isnull=False).count()) for provider in provider_set]
    result_now = [SubscribersCounter(provider.name, Subscriber.objects.filter(
        provider=provider,
        port__isnull=False,
        date__month=timezone.now().month,
        date__year=timezone.now().year).count())
                  for provider in provider_set]
    last_subscriber = Subscriber.objects.filter(port__isnull=False).last()

    return render_to_response("index.html", {
        'switch': switch,
        'subscribers': subscribers,
        'result': result,
        'subscribers_now': subscribers_now,
        'result_now': result_now,
        'last_subscriber': last_subscriber,
	    'user': User
    })

def logout_view(request):
    logout_view(request)
