from django.contrib import admin
from .models import (
    Address, ApartmentNumber, District, Network, PortsInfo, Providerinfo, Switch, SwitchModel,  Subscriber, HomeNumber,
    Quarter, Vlaninfo, Vendor, OidBase, SnmpCommunity, Action, ExpendableMaterial,
    Contract, Mediaconverter, WiFiRouterModel, MediaconverterModel
)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'address', 'port')

admin.site.register(Address)
admin.site.register(ApartmentNumber)
admin.site.register(District)
admin.site.register(Network)
admin.site.register(PortsInfo)
admin.site.register(Providerinfo)
admin.site.register(Switch)
admin.site.register(SwitchModel)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(HomeNumber)
admin.site.register(Quarter)
admin.site.register(Vlaninfo)
admin.site.register(Vendor)
admin.site.register(OidBase)
admin.site.register(SnmpCommunity)
admin.site.register(Action)
admin.site.register(ExpendableMaterial)
admin.site.register(Contract)
admin.site.register(Mediaconverter)
admin.site.register(MediaconverterModel)
admin.site.register(WiFiRouterModel)




