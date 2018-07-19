from django.db import models
from info.models import Address
# Create your models here.

class DeviceType(models.Model):
    name = models.CharField(max_length=20, verbose_name="Устройство", unique=True)

    def __str__(self):
        return self.name


class DeviceModel(models.Model):
    device_type = models.ForeignKey(
        DeviceType, verbose_name="Тип устройства")
    model = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Модель", unique=True)

    def __str__(self):
        return "%s: %s" % (self.device_type, self.model)


class BuildingBase(models.Model):
    name = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Название типа зданий", unique=True)
    entrance_qty = models.PositiveSmallIntegerField(
        default=1, verbose_name="Кол-во подъездов")
    floor_qty = models.PositiveSmallIntegerField(
        default=5, verbose_name="Кол-во этажей")

    def __str__(self):
        return "%s(%s эт., %s п-ов)" % (
            self.name, self.entrance_qty, self.floor_qty
        )


class Building(models.Model):
    base = models.ForeignKey(BuildingBase, verbose_name="Тип здания")
    address = models.ForeignKey(Address, verbose_name="Адрес")
    comment = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Комментарий")

    class Meta:
        unique_together = ['base', 'address']

    def __str__(self):
        return "%s-%s,%s" % (
            self.address.district.name,
            self.address.quarter.number,
            self.address.home.number
        )


class Device(models.Model):
    model = models.ForeignKey(DeviceModel, verbose_name="Устройство")
    location = models.ForeignKey(Building, verbose_name="Расположение")
    entrance = models.SmallIntegerField(default=1, verbose_name="Подъезд")
    floor = models.SmallIntegerField(default=1, verbose_name="Этаж")
    has_ups = models.BooleanField(default=False, verbose_name="Наличие UPS")
    comment = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Комментарии")

    def __str__(self):
        return "%s (%s)" % (
            self.device_type,
            self.location
        )


class BuildingDeviceGroup(models.Model):
    device = models.ForeignKey(Device)
    buildings = models.ManyToManyField(Building)

    def __str__(self):
        return self.device
