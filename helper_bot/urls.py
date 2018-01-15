from django.conf.urls import url, include
from . import views


app_name = 'helper_bot'

urlpatterns = [
    url(r'^helper_bot/start/$', views.run_bot, name='start_bot'),
    url(r'^helper_bot/fast_start/$', views.fast_start, name='fast_start')

]