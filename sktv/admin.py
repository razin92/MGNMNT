from django.contrib import admin
from .models import DeviceType, DeviceModel, BuildingBase, Building, Device, BuildingDeviceGroup
# Register your models here.

class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


class DeviceModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'device_type', 'model']
    search_fields = ['model']


class BuildingBaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'entrance_qty', 'floor_qty']
    search_fields = ['name']


class BuildingAdmin(admin.ModelAdmin):
    list_display = ['id', 'base', 'address']
    search_fields = ['address.quarter']


class DeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'model', 'location', 'entrance', 'floor', 'has_ups']
    search_fields = ['location.address.quarter']


class BuildingDeviceGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'device']

admin.site.register(DeviceType, DeviceTypeAdmin)
admin.site.register(DeviceModel, DeviceModelAdmin)
admin.site.register(BuildingBase, BuildingBaseAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(BuildingDeviceGroup, BuildingDeviceGroupAdmin)

