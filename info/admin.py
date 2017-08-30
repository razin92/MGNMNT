from django.contrib import admin
from .models import (
    Address, ApartmentNumber, District, Network, PortsInfo, Providerinfo, Switch, SwitchModel,  Subscriber, HomeNumber,
    Quarter, Vlaninfo, Vendor, OidBase, SnmpCommunity
)

admin.site.register(Address)
admin.site.register(ApartmentNumber)
admin.site.register(District)
admin.site.register(Network)
admin.site.register(PortsInfo)
admin.site.register(Providerinfo)
admin.site.register(Switch)
admin.site.register(SwitchModel)
admin.site.register(Subscriber)
admin.site.register(HomeNumber)
admin.site.register(Quarter)
admin.site.register(Vlaninfo)
admin.site.register(Vendor)
admin.site.register(OidBase)
admin.site.register(SnmpCommunity)