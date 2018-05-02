from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, render_to_response, HttpResponse
from connector.views import SSH_connection
from django.urls import reverse_lazy, reverse
from django.views import generic, View
from .models import Switch, PortsInfo, OidBase, SnmpCommunity, Subscriber, Quarter, HomeNumber, ApartmentNumber
from .  import scripts, decorators
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import FilterForm, ContractForm, AddressSearchForm
import json


class SwitchView(generic.ListView):
    template_name = 'info/switch_list.html'
    context_object_name = 'switch'

    def get_queryset(self):
        return Switch.objects.order_by('ip_add')
    # Поисковик
    def search_switch(request):
        switch = Switch.objects.all()
        return render_to_response('info/search_sw_p.html', {'switch': switch, 'user': User})


class PortsInfoView(generic.ListView):
    template_name = 'info/ports_list.html'
    context_object_name = 'ports'
    paginate_by = 10

    def get_queryset(self):
        return PortsInfo.objects.order_by('switch','number')

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
    model = PortsInfo
    success_url = reverse_lazy('info:ports_list')
    template_name = 'info/ports_edit.html'
    fields = ['description', 'select']

    #def get_success_url(self):
     #   return render_to_response('info/ports_detail.html', {'pk': self.model.id})

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

class CreatePorts(View):

    def get(self, request):
        switch = Switch.objects.all()
        for each in switch:
            for x in range(1, each.model.ports+1):
                PortsInfo.objects.get_or_create(
                    switch=each,
                    number=x
                )
        return HttpResponseRedirect(reverse('info:switch_list'))

@login_required()
def PortReboot(request, switch_id, port_id):
    oid = str(OidBase.objects.get(pk=2))
    comm = str(SnmpCommunity.objects.get(pk=2))
    port = get_object_or_404(PortsInfo, pk=port_id)
    switch = str(get_object_or_404(Switch, pk=switch_id))
    result = oid + str(port.number)
    def shutdown():
        return scripts.SetPortStatus(switch, comm, result, 2)
    @decorators.pause
    def up():
        return scripts.SetPortStatus(switch, comm, result, 1)
    status = str(shutdown()) + '|' + str(up())
    return HttpResponseRedirect(reverse('info:ports_detail', args=(port_id,)))
    #return render_to_response('info/ports_detail.html', {'status': status, 'portsinfo': port, 'user': User})

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

def search_switch_result(request):
    error = 'Ничего не найдено, попробуйте указать другие данные'
    req = request.GET['switch']
    switch = Switch.objects.filter(address__switch__ip_add__icontains=req)

    return render_to_response('info/search_switch_result.html', {'switch': switch, 'user': User, 'error': error})

@login_required()
def search_ports_result(request):
    error = 'Ничего не найдено, попробуйте указать другие данные'
    ports = 'port'
    switches = 'switch'
    switch = request.GET[switches]
    port = request.GET[ports]
    if ports and switches in request.GET and switch and port:
        numbers = PortsInfo.objects.filter(switch__ip_add__icontains=switch, number=port)
        return render_to_response(
            'info/search_ports_result.html', {
                'ports': numbers,
                'error': error,
                'user': User,
            }
        )
    elif ports in request.GET and switch:
        numbers = PortsInfo.objects.filter(switch__ip_add__icontains=switch)
        return render_to_response('info/search_ports_result.html', {'ports': numbers, 'error': error, 'user': User})
    elif ports in request.GET and port:
        numbers = PortsInfo.objects.filter(number=port)
        return render_to_response('info/search_ports_result.html', {'ports': numbers, 'error': error, 'user': User})
    else:
        return render_to_response('info/search_ports_result.html', {'error': error, 'user': User})

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



