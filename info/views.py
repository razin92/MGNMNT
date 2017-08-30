from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, render_to_response
from django.http import HttpResponse
from django.urls import reverse_lazy, reverse
from django.views import generic
from .models import Switch, PortsInfo, OidBase, SnmpCommunity, Subscriber, Quarter, HomeNumber, ApartmentNumber
from .  import scripts, decorators
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


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

class PortsInfoDetail(generic.DetailView):
    model = PortsInfo
    template_name = 'info/ports_detail.html'

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

@login_required
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

@login_required
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

@login_required
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

def search_subscribers_result(request):
    error = 'Ничего не найдено, попробуйте указать другие данные'
    subscriber = request.GET['subscriber']
    quarter = request.GET['quarter']
    home = request.GET['home']
    apartment = request.GET['apartment']
    date = request.GET['date']
    subscribers = 'subscriber'
    quarters = 'quarter'
    homes = 'home'
    dates = 'date'	
    apartments = 'apartment'
    # ----------------- ВСЕ 4 совпадения
    if (subscribers and quarters and homes and apartments in request.GET and
        subscriber and quarter and home and apartment):
        result = Subscriber.objects.filter(
            name__icontains=subscriber,
            address__quarter__number=quarter,
            address__home__number=home,
            address__apartment__number=apartment
        )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})
    # ----------------- 3 совпадения
    elif (subscribers and quarters and homes in request.GET and
        subscriber and quarter and home):
        result = Subscriber.objects.filter(
            name__icontains=subscriber,
            address__quarter__number=quarter,
            address__home__number=home
        )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})

    elif (subscribers and quarters and apartments in request.GET and
        subscriber and quarter and apartment):
        result = Subscriber.objects.filter(
            name__icontains=subscriber,
            address__quarter__number=quarter,
            address__apartment__number=apartment
        )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})

    elif (subscribers and homes and apartments in request.GET and
        subscriber and home and apartment):
        result = Subscriber.objects.filter(
            name__icontains=subscriber,
            address__home__number=home,
            address__apartment__number=apartment
        )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})

    elif (quarters and homes and apartments in request.GET and
        quarter and home and apartment):
        result = Subscriber.objects.filter(
            address__quarter__number=quarter,
            address__home__number=home,
            address__apartment__number=apartment
        )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})

    # ---------------------- 2 совпадения
    elif ('subscriber' and 'quarter' in request.GET and
        request.GET['subscriber'] and request.GET['quarter']):
        result = Subscriber.objects.filter(
            name__icontains=subscriber,
            address__quarter__number=quarter
        )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})

    elif ('subscriber' and 'home'in request.GET and
        request.GET['subscriber'] and request.GET['home']):
        result = Subscriber.objects.filter(
            name__icontains=subscriber,
            address__home__number=home
        )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})

    elif ('subscriber' and 'apartment' in request.GET and
        request.GET['subscriber'] and request.GET['apartment']):
        result = Subscriber.objects.filter(
            name__icontains=subscriber,
            address__apartment__number=apartment
        )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})

    elif ('quarter' and 'home' in request.GET and
        request.GET['quarter'] and request.GET['home']):
        result = Subscriber.objects.filter(
            address__quarter__number=quarter,
            address__home__number=home,
          )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})

    elif ('quarter' and 'apartment' in request.GET and
        request.GET['quarter'] and request.GET['apartment']):
        result = Subscriber.objects.filter(
            address__quarter__number=quarter,
            address__apartment__number=apartment
        )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})

    elif ('home' and 'apartment' in request.GET and
        request.GET['home'] and request.GET['apartment']):
        result = Subscriber.objects.filter(
            address__home__number=home,
            address__apartment__number=apartment
        )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})

    # ---------------------- одно совпадение
    elif ('subscriber' in request.GET and
        request.GET['subscriber']):
        result = Subscriber.objects.filter(
            name__icontains=subscriber
        )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})

    elif ('home' in request.GET and
        request.GET['home']):
        result = Subscriber.objects.filter(
            address__home__number=home
        )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})

    elif ('quarter' in request.GET and
        request.GET['quarter']):
        result = Subscriber.objects.filter(
            address__quarter__number=quarter,
        )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})

    elif ('apartment' in request.GET and
        request.GET['apartment']):
        result = Subscriber.objects.filter(
            address__apartment__number=apartment
        )
        return render_to_response('info/search_subscribers_result.html', {'subscriber': result, 'error': error, 'user': User})

    elif 'date' in request.GET:
        result = Subscriber.objects.filter(date=date)
        return render_to_response('info/search_subscribers_result.html',
                                  {'subscriber': result, 'error': error, 'user': User})

    # -------------- Сообщение об ошибке
    else:
        error = 'Ничего не найдено, попробуйте указать другие данные'
        return render_to_response('info/search_subscribers_result.html', {'error': error, 'user': User})


