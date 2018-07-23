from django.shortcuts import render, HttpResponseRedirect,reverse, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views import View
from info.models import Subscriber, Switch, Providerinfo, PortsInfo
from django.utils import timezone
from .forms import LoginForm


class Login(View):

    def get(self, request):
        error = ''
        form = LoginForm
        return render(request, "login.html", {'error': error, 'form': form})


    def post(self, request):
        form = LoginForm(request.POST or None)
        username = request.POST['username']
        password = request.POST['password']
        if username == 'Android':
            error = 'Доступ запрещен!'
            context = {
                'error': error,
                'form': form,
            }
            return render(request, "login.html", context)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                error = 'Аккаунт не активирован!'
                context = {
                    'error': error,
                    'form': form,
                }
                return render(request, "login.html", context)

        else:
            error = 'Неправильный логин или пароль'
            context = {
                'error': error,
                'form': form,
            }
            return render(request, "login.html", context)


class Index(View):

    def get(self, request):
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
            'user': User,
            'ports': self.unfilled_ports()
        })

    def unfilled_ports(self):
        result = PortsInfo.objects.filter(
            number__lt=25, subscriber__isnull=True, select=True).order_by('switch__address__quarter')
        return result


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
