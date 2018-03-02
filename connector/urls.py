from django.conf.urls import url, include
from . import views


app_name = 'connector'

urlpatterns = [
    #Поисковик
    url(r'^ssh/$', views.SSH_connection, name='ssh'),

]