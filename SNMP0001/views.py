from django.shortcuts import render, HttpResponseRedirect,reverse, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from info.models import Subscriber, Switch, Providerinfo
from django.utils import timezone

def my_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
    else:
        return render(request, 'index.html', {
            'error_message': "Неправильный логин или пароль"
        })

@login_required
def index(request):
    #return render(request, "index.html")
    subscriber = Subscriber.objects.all()
    switch = Switch.objects.all()
    comnet = subscriber.filter(provider=Providerinfo.objects.get(name="Comnet"))
    istv = subscriber.filter(provider=Providerinfo.objects.get(name="ISTV"))
    time_now = subscriber.filter(date__month=timezone.now().month)
    istv_now = subscriber.filter(provider=Providerinfo.objects.get(name="ISTV"), date__month=timezone.now().month)
    comnet_now = subscriber.filter(provider=Providerinfo.objects.get(name="Comnet"), date__month=timezone.now().month)
    #comnet_now = subscriber.filter(provider=Providerinfo.objects.get(name="Comnet"), date__month=5)
    return render_to_response("index.html", {
        'subscriber': subscriber,
        'switch': switch,
        'comnet': comnet,
        'istv': istv,
        'time': time_now,
        'istvnow': istv_now,
        'comnetnow': comnet_now,
	'user': User
    })

def logout_view(request):
    logout_view(request)
