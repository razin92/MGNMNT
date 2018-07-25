from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from . import views


app_name = 'helper_bot'

urlpatterns = [
    url(r'^helper_bot/start/$', views.run_bot, name='start_bot'),
    url(r'^helper_bot/fast_start/$', views.fast_start, name='fast_start'),
    url(r'^oner/$', csrf_exempt(views.OnerSender.as_view()), name='oner')

]