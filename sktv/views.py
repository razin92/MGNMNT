from django.shortcuts import render, get_object_or_404, reverse, HttpResponseRedirect
from django.views import View
from django.urls import reverse_lazy
from .models import DeviceType, DeviceModel, BuildingBase, Building, Device, BuildingDeviceGroup
from .forms import DeviceTypeForm
from django.contrib import messages
from django.views.generic import UpdateView
from django.core.paginator import Paginator


def get_requested_url(request):
    start = request.META['HTTP_HOST']
    end = request.META['PATH_INFO']
    url = 'http://%s%s' % (start, end)

    return url


class DeviceTypeView(View):
    """
    List of devices and creating form
    """
    form_class = DeviceTypeForm
    template = 'sktv/device_type.html'

    def get(self, request):
        form = self.form_class(None)
        devices = DeviceType.objects.all().order_by('name')
        context = {
            'form': form,
            'devices': devices
        }
        return render(request, self.template, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('sktv:device_type'))
        return render(request, self.template, context={'form': form})

class DeviceTypeEdit(UpdateView):
    model = DeviceType
    fields = ['name']
    template_name = 'sktv/edit_form.html'
    success_url = reverse_lazy('sktv:device_type')
