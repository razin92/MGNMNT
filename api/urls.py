from django.conf.urls import url
from . import tg_bot as views
from django.contrib.auth.decorators import login_required


app_name = 'api'

urlpatterns = [
    url(r'^start/$', views.run_bot, name='start_notifier'),
    url(r'^notifier/$', login_required(views.Message.as_view()), name='notifier')
]