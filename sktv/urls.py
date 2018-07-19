from django.conf.urls import url
from . import views
from . import views_test

app_name = 'sktv'

urlpatterns = [
    # Типы устройств
    url(r'device_type/$', views.DeviceTypeView.as_view(), name='device_type'),
    url(r'device_type/edit/(?P<pk>[0-9]+)/$', views.DeviceTypeEdit.as_view(), name='device_type_edit'),

]