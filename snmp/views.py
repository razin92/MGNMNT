from django.shortcuts import render, HttpResponseRedirect, reverse
from . import scripts

def PortDown(request):
    scripts.SetPortStatus('192.168.1.3','TESTwr','1.3.6.1.2.2.1.7.2',2)
    return HttpResponseRedirect(reverse('info:switch_list'))
