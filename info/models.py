from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from . import scripts

class Vendor(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

class SwitchModel(models.Model):
    vendor = models.ForeignKey(Vendor, null=True)
    model = models.CharField(max_length=50, unique=True)
    ports = models.PositiveIntegerField()

    def __str__(self):
        return self.model

class District(models.Model):
    name = models.CharField(max_length=15, unique=True)

    class Meta():
        ordering = ['name']

    def __str__(self):
        return self.name

class Quarter(models.Model):
    number = models.PositiveIntegerField(unique=True)

    class Meta():
        ordering = ['number']

    def __str__(self):
        return str(self.number)

class HomeNumber(models.Model):
    number = models.CharField(max_length=4, unique=True)

    class Meta():
        ordering = ['number']

    def __str__(self):
        return str(self.number)

class ApartmentNumber(models.Model):
    number = models.PositiveIntegerField(unique=True)

    class Meta():
        ordering = ['number']

    def __str__(self):
       return str(self.number)

class Address(models.Model):
    district = models.ForeignKey(District)
    quarter = models.ForeignKey(Quarter)
    home = models.ForeignKey(HomeNumber)
    apartment = models.ForeignKey(ApartmentNumber, blank=True, null=True)
    description = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ('district', 'quarter', 'home', 'apartment')
        ordering = ['district', 'quarter', 'home', 'apartment']

    def __str__(self):
        if self.apartment == None:
            result = "%s-%s дом:%s" % (self.district.name, self.quarter.number, self.home.number)
        else:
            result = "%s-%s дом:%s кв:%s" % (self.district.name, self.quarter.number, self.home.number, self.apartment.number)
        return result

class SnmpCommunity(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class OidBase(models.Model):
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.value

class Switch(models.Model):
    ip_add = models.GenericIPAddressField(unique=True)
    model = models.ForeignKey(SwitchModel, null=True, on_delete=models.SET_NULL)
    address = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return str(self.ip_add)

class Network(models.Model):
    ip_add = models.GenericIPAddressField()
    mask = models.GenericIPAddressField()
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Vlaninfo(models.Model):
    name = models.CharField(max_length=50)
    tag = models.PositiveIntegerField()
    networks = models.ForeignKey(Network, blank=True, null=True)

    def __str__(self):
        return self.name

class Providerinfo(models.Model):
    name = models.CharField(max_length=50, unique=True)
    vlan = models.ManyToManyField(Vlaninfo)
    networks = models.ManyToManyField(Network, blank=True)

    def __str__(self):
        return self.name

class PortsInfo(models.Model):
    switch = models.ForeignKey(Switch, on_delete=models.CASCADE)
    number = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(28), MinValueValidator(1)])
    description = models.CharField(max_length=50, blank=True)
    select = models.BooleanField(default=False, verbose_name=(u'Используется'))

    class Meta:
        unique_together = ('switch', 'number')
        ordering = ['switch', 'number']

    def __str__(self):
        sw = str(self.switch)
        num = str(self.number)
        return sw+':'+num

    def is_up(self):
        switch = str(self.switch)
        port = str(self.number)
        oid = str(OidBase.objects.get(name='Статус порта'))
        comm = str(SnmpCommunity.objects.get(pk=1))
        oidport = oid + port
        status = scripts.GetPortStatus(switch, comm, oidport)
        if status == '1':
            return True
        else:
            return False

    def get_absolute_url(self):
        return reverse('info:ports_edit', kwargs={'pk': self.pk})

class Subscriber(models.Model):
    name = models.CharField(max_length=50)
    provider = models.ForeignKey(Providerinfo)
    address = models.ForeignKey(Address,on_delete=models.SET_NULL, null=True)
    port = models.OneToOneField(PortsInfo, null=True, on_delete=models.DO_NOTHING, related_name='subscriber', blank=True)
    login = models.CharField(max_length=20, null=True)
    date = models.DateField(default=timezone.now)
    telephone = models.CharField(max_length=13, null=True)
    bill_url = models.URLField(null=True, blank=True, default="#")
    comment = models.CharField(max_length=50, blank=True)


    class Meta:
        unique_together = ('name', 'address')

    def __str__(self):
        return self.name

