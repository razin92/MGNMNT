from django.shortcuts import render, get_object_or_404, reverse, HttpResponseRedirect
from django.views import View
from django.urls import reverse_lazy
from .models import DeviceType, DeviceModel, BuildingBase, Building, Device, BuildingDeviceGroup
from .forms import DummyForm, DeviceTypeForm, DeviceModelForm
from django.db.models import Model
from django.contrib import messages
from django.views.generic import UpdateView
from django.core.paginator import Paginator


def get_requested_url(request):
    start = request.META['HTTP_HOST']
    end = request.META['PATH_INFO']
    url = 'http://%s%s' % (start, end)

    return url


class DummyModel(Model):
    """
    The class for dynamic configuration of a view
    """
    pass


class BasedView(View):
    """
    Based View class for all models
    """
    template = 'sktv/shared_template.html'
    based_url = ''
    form_class = DummyForm
    model_class = DummyModel
    ordering = ''
    exclude_list = []

    def get(self, request):
        form = self.form_class(None)
        data = self.model_class.objects.all().order_by('%s' % self.ordering)
        headers = [x for x in self.model_class._meta.get_fields() if x.name not in self.exclude_list]
        context = {
            'form': form,
            'data': data,
            'headers': headers
        }
        return render(request, self.template, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('%s' % self.based_url))
        return render(request, self.template, context={'form': form})


# Device Types
class DeviceTypeView(BasedView):
    """
    List of type of devices and creating form
    """
    # template = 'sktv/device_type.html'
    based_url = 'sktv:device_type'
    form_class = DeviceTypeForm
    model_class = DeviceType
    ordering = 'name'
    exclude_list = ['devicemodel']


class DeviceTypeEdit(UpdateView):
    model = DeviceType
    fields = ['name']
    template_name = 'sktv/edit_form.html'
    success_url = reverse_lazy('sktv:device_type')


# Device Models
class DeviceModelView(BasedView):
    """
    List of model of devices and creating form
    """
    #template = 'sktv/device_model.html'
    based_url = 'sktv:device_model'
    form_class = DeviceModelForm
    model_class = DeviceModel
    ordering = 'id'
    exclude_list = ['device']


class DeviceModelEdit(UpdateView):
    model = DeviceModel
    fields = ['device_type', 'model']
    template_name = 'sktv/edit_form.html'
    success_url = reverse_lazy('sktv:device_model')


# Building Base
class BuildingBaseView(View):
    template = ''
    based_url = ''
    form_class = DummyForm
    model_class = DummyModel
    ordering = ''


class BuildingBaseEdit(View):
    model = DeviceModel
    fields = ['device_type', 'model']
    template_name = 'sktv/edit_form.html'
    success_url = reverse_lazy('sktv:device_model')


# Building
class BuildingView(View):
    template = ''
    based_url = ''
    form_class = DummyForm
    model_class = DummyModel
    ordering = ''


class BuildingEdit(View):
    model = DeviceModel
    fields = ['device_type', 'model']
    template_name = 'sktv/edit_form.html'
    success_url = reverse_lazy('sktv:device_model')


# Device
class DeviceView(View):
    template = ''
    based_url = ''
    form_class = DummyForm
    model_class = DummyModel
    ordering = ''


class DeviceEdit(View):
    model = DeviceModel
    fields = ['device_type', 'model']
    template_name = 'sktv/edit_form.html'
    success_url = reverse_lazy('sktv:device_model')


# BuildingDeviceGroup
class BuildingDeviceGroupView(View):
    template = ''
    based_url = ''
    form_class = DummyForm
    model_class = DummyModel
    ordering = ''


class BuildingDeviceGroupEdit(View):
    model = DeviceModel
    fields = ['device_type', 'model']
    template_name = 'sktv/edit_form.html'
    success_url = reverse_lazy('sktv:device_model')


