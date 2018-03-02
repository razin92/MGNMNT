from django.conf.urls import url, include
from . import views


app_name = 'info'

urlpatterns = [
    #Поисковик
    url(r'^switch/search-result/$', views.search_switch_result, name='search_switch'),
    url(r'^subscribers/search-result/$', views.search_subscribers_result, name='search_subscribers'),
    url(r'^ports/search-result/$', views.search_ports_result, name='search_ports'),
    #СВИЧИ
    url(r'^switch/$', views.SwitchView.as_view(), name='switch_list'),
    url(r'^switch/(?P<pk>[0-9]+)/$', views.SwitchDetailView.as_view(), name='switch_detail'),
    #Порты
    url(r'^ports/$', views.PortsInfoView.as_view(), name='ports_list'),
    url(r'^ports/page/(?P<page>\d+)', views.PortsInfoView.as_view(), name='ports_page'),
    url(r'^ports/(?P<pk>[0-9]+)/$', views.PortsInfoDetail, name='ports_detail'),
    url(r'^ports/edit/(?P<pk>\d+)/$', views.PortsInfoEdit.as_view(), name='ports_edit'),
    url(r'^ports/(?P<switch_id>[0-9]+)/(?P<port_id>[0-9]+)/reboot/$', views.PortReboot, name='port_reboot'),
    url(r'^ports/(?P<switch_id>[0-9]+)/(?P<port_id>[0-9]+)/shutdown/$', views.PortShutdown, name='port_shutdown'),
    url(r'^ports/(?P<switch_id>[0-9]+)/(?P<port_id>[0-9]+)/up/$', views.PortUp, name='port_up'),
    #Пользователи
    url(r'^subscribers/$', views.SubscribersView.as_view(), name='subscribers_list'),
    url(r'^subscribers/(?P<pk>[0-9]+)/$', views.SubscribersDetail.as_view(), name='subscribers_detail'),
    url(r'^subscribers/page/(?P<page>\d+)', views.SubscribersView.as_view(), name='subscribers_page'),

]
