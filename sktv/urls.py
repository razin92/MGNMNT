from django.conf.urls import url
from . import views

app_name = 'sktv'

urlpatterns = [
    # Типы устройств
    url(r'device_type/$', views.DeviceTypeView.as_view(), name='device_type'),
    url(r'device_type/edit/(?P<pk>[0-9]+)/$', views.DeviceTypeEdit.as_view(), name='device_type_edit'),
    # Модели устройств
    url(r'device_model/$', views.DeviceModelView.as_view(), name='device_model'),
    url(r'device_model/edit/(?P<pk>[0-9]+)/$', views.DeviceModelEdit.as_view(), name='device_model_edit'),
]