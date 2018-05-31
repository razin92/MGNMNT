from django.conf.urls import url
from . import tg_bot as views


app_name = 'api'

urlpatterns = [
    url(r'^start/$', views.run_bot, name='start_notifier'),
    url(r'^notifier/$', views.Message.as_view(), name='notifier')
]