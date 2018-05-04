from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, render_to_response, HttpResponse
from connector.views import SSH_connection
from django.urls import reverse, reverse_lazy
from django.views import generic, View
from .models import Switch, PortsInfo, OidBase, SnmpCommunity, Subscriber, Quarter, HomeNumber, ApartmentNumber, Address
from .  import scripts, decorators
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from .forms import FilterForm, ContractForm, AddressSearchForm, SwitchForm, SwitchFilterForm
import json


class SwitchView(View):

    def get(self, request):
        template = 'info/switch_list.html'
        form = SwitchFilterForm
        switches = Switch.objects.all().order_by('address', 'ip_add')
        address = Address.objects.all().exclude(apartment__isnull=False)
        if request.GET.get('address', ''):
            req = request.GET['address']
            switches = Switch.objects.filter(address__id=req)

        context = {
            'switch': switches,
            'address': address,
            'form': form
        }

        return render(request, template, context)

class SwitchDetailView(generic.DetailView):
    model = Switch
    template_name = 'info/switch_detail.html'

    # Инормация о портах
    def get_context_data(self, **kwargs):
        context = super(SwitchDetailView, self).get_context_data(**kwargs)
        context['ports'] = PortsInfo.objects.filter(switch=self.object).order_by('number')
        return context

def PortsInfoDetail(request, pk):
    port = get_object_or_404(PortsInfo, pk=pk)
    template = 'info/ports_detail.html'
    detail = ''
    error_message = ''
    try:
        detail = SSH_connection(port.switch.ip_add, port.number)
    except:
        error_message = 'Ошибка при подключении к коммутатору'

    context = {
        'portsinfo': port,
        'error_message': error_message,
    }
    context.update(detail)

    return render(request, template, context)

class PortsInfoEdit(generic.UpdateView):
    template_name = 'info/ports_edit.html'
    model = PortsInfo
    fields = ['description', 'select']

    def get_success_url(self):
        return reverse('info:switch_detail', args=(self.object.switch.id,))

class SubscribersView(generic.ListView):
    template_name = 'info/subscribers_list.html'
    context_object_name = 'subscriber'
    paginate_by = 25	

    def get_queryset(self):
        return Subscriber.objects.order_by('name', 'address')

    # Поисковик пользователей
    def search_subscribers(request):
        subscriber = Subscriber.objects.all()
        quarter = Quarter.objects.all()
        home = HomeNumber.objects.all()
        apartments = ApartmentNumber.objects.all()
        return render_to_response('info/search_subscribers.html', {
            'subscriber': subscriber,
            'quarter': quarter,
            'home': home,
            'apartments': apartments,
            'user': User
        })

class SubscribersDetail(generic.DetailView):
    model = Subscriber
    template_name = 'info/subscribers_detail.html'

class CreateSwitch(View):
    template = 'info/switch_create.html'

    #Function create switch
    def switch_create(self, data):
        switch = Switch.objects.get_or_create(
            model=data.model,
            ip_add=data.ip_add,
            address=data.address,
            description=data.description
        )
        switch.save()
        return switch

    #Function create ports according on the switch.model.ports q-tty
    def port_create(self, switch):
        for each in range(1, switch.model.ports+1):
            PortsInfo.objects.get_or_create(
                switch=switch,
                number=each,
            )

    def get(self, request):
        form = SwitchForm(None)
        context = {
            'form': form
        }
        return render(request, self.template, context)

    def post(self, request):
        form = SwitchForm(request.POST or None)
        if form.is_valid():
            form.save()
            self.port_create(form.instance)
            return HttpResponseRedirect(reverse('info:switch_list'))
        context = {
            'form': form
        }
        return render(request, self.template, context)

@login_required()
def PortReboot(request, switch_id, port_id):
    import time
    #Data for SNMP request
    oid = str(OidBase.objects.get(pk=2))
    comm = str(SnmpCommunity.objects.get(pk=2))
    port = get_object_or_404(PortsInfo, pk=port_id)
    switch = str(get_object_or_404(Switch, pk=switch_id))
    result = oid + str(port.number)
    #Port shutdown
    scripts.SetPortStatus(switch, comm, result, 2)
    time.sleep(2)
    #Port up
    scripts.SetPortStatus(switch, comm, result, 1)
    time.sleep(1)
    return HttpResponseRedirect(reverse('info:ports_detail', args=(port_id,)))

@login_required()
def PortShutdown(request, switch_id, port_id):
    oid = str(OidBase.objects.get(pk=2))
    comm = str(SnmpCommunity.objects.get(pk=2))
    port = get_object_or_404(PortsInfo, pk=port_id)
    switch = str(get_object_or_404(Switch, pk=switch_id))
    result = oid + str(port.number)

    def shutdown():
        return scripts.SetPortStatus(switch, comm, result, 2)

    status = str(shutdown())

    #return HttpResponseRedirect(reverse('info:ports_detail', args=(port_id,)))
    return render_to_response('info/ports_detail.html', {'status': status, 'portsinfo': port, 'user': User})

@login_required()
def PortUp(request, switch_id, port_id):
    oid = str(OidBase.objects.get(pk=2))
    comm = str(SnmpCommunity.objects.get(pk=2))
    port = get_object_or_404(PortsInfo, pk=port_id)
    switch = get_object_or_404(Switch, pk=switch_id)
    result = oid + str(port.number)

    def up():
        return scripts.SetPortStatus(str(switch), comm, result, 1)
    status = str(up())
    #return HttpResponseRedirect(reverse('info:ports_detail', args=(port_id,)))
    return render_to_response('info/ports_detail.html', {'status': status, 'portsinfo': port, 'user': User})

@login_required()
def search_subscribers_result(request):
    template = 'info/search_subscribers_result.html'
    error = ''
    rqst = request.GET

    #Данные из POST запроса
    subscriber = rqst['subscriber'] or ''
    login = rqst['login'] or ''
    quarter = Quarter.objects.filter(number__icontains=rqst['quarter']).values_list('number')
    home = HomeNumber.objects.filter(number__icontains=rqst['home']).values_list('number')

    filter_result = Subscriber.objects.filter(
        name__icontains=subscriber,
        login__icontains=login,
        address__quarter__number__in=quarter,
        address__home__number__in=home,
    )

    if rqst['date'] and 'date' in rqst:
        date = rqst['date']
        filter_result = Subscriber.objects.filter(date=date)
    elif rqst['apartment'] and 'apartment' in rqst:
        apartment = rqst['apartment']
        filter_result = Subscriber.objects.filter(
            name__icontains=subscriber,
            login__icontains=login,
            address__quarter__number__in=quarter,
            address__home__number__in=home,
            address__apartment__number__icontains=apartment,
        )

    if len(filter_result) == 0:
        error = 'Ничего не найдено, попробуйте указать другие данные'

    context = {
        'subscriber': filter_result,
        'error': error,
        'user': User,
    }

    return render(request, template, context)

class ContractView(View):
    template = 'info/contract_form.html'

    def get(self, request):
        form = AddressSearchForm(None)
        context = {
            'subscriber': ' ',
            'form': form,
        }

        return render(request, self.template, context)

    def post(self, request):
        form = AddressSearchForm(request.POST or None)
        subscriber = ''
        if form.is_valid():
            subscriber = Subscriber.objects.filter(
                address__quarter__number=request.POST['quarter'],
                address__home__number=request.POST['building'],
                address__apartment__number=request.POST['apartment']
            )

        context = {
            'form': form,
            'subscriber': subscriber,
        }

        return render(request, self.template, context)

class ContractViewJson(View):

    def apartment(self, address):
        if address.address.apartment == None:
            return ''
        return '-%s' % address.address.apartment.number

    def get(self, request):
        q = request.GET.get('q', '')
        address_list = []
        address = Subscriber.objects.filter(address__quarter__number__icontains=q)

        for element in address:
            new = {'q': '%s-%s-%s%s' % (
                    element.address.district.name,
                    element.address.quarter.number,
                    element.address.home.number,
                    self.apartment(address=element)
            )
                   }
            address_list.append(new)

        return HttpResponse(json.dumps(address_list, ensure_ascii=False), content_type='application/json')


