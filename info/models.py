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
    number = models.CharField(unique=True, max_length=5)

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
            result = "%s-%s дом:%s" % (self.district.name, self.quarter.number, self.home)
        else:
            result = "%s-%s дом:%s кв:%s" % (self.district.name, self.quarter.number, self.home, self.apartment.number)
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
    document = models.CharField(max_length=20, unique=True, null=True)
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
        return '%s-%s-%s | %s | %s' % (
            self.address.quarter,
            self.address.home,
            self.address.apartment,
            self.port,
            self.name
        )

class MediaconverterModel(models.Model):
    model = models.CharField(max_length=20, unique=True, verbose_name="Модель")

    def __str__(self):
        return self.model

class Action(models.Model):
    name = models.CharField(max_length=20, verbose_name="Название Акции")
    description = models.CharField(max_length=200, verbose_name="Описание")
    date_start = models.DateField(auto_now=True, verbose_name="Дата начала")
    date_end = models.DateField(auto_now=True, verbose_name="Дата окончания")

    def __str__(self):
        return self.name

class WiFiRouterModel(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, verbose_name="Производитель")
    model = models.CharField(max_length=20, unique=True, verbose_name="Модель")

    def __str__(self):
        return "%s / %s" % (self.vendor, self.model)

class Mediaconverter(models.Model):
    model = models.ForeignKey(MediaconverterModel, on_delete=models.CASCADE, verbose_name="Модель")
    serial_number = models.CharField(max_length=20, unique=True, verbose_name="серийный номер")

    def __str__(self):
        return "%s(%s)" % (self.model, self.serial_number)

class ExpendableMaterial(models.Model):
    subscriber = models.OneToOneField(Subscriber, on_delete=models.PROTECT, verbose_name="Абонент")
    action = models.ForeignKey(Action, default=None, null=True, blank=True)

    sleeve = models.PositiveSmallIntegerField(default=1, verbose_name="Гильза (шт.)")
    sleeve_exp = models.BooleanField(default=False, verbose_name="Гильза расход")

    fast_connector = models.PositiveSmallIntegerField(default=1, verbose_name="Фаст-коннектор (шт.)")
    fc_exp = models.BooleanField(default=False, verbose_name="ФК расход")

    optic_cable = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, verbose_name="Оптический кабель (м.)")
    optiс_exp = models.BooleanField(default=False, verbose_name="Оптика расход")

    sfp_module = models.SmallIntegerField(default=1, verbose_name="SFP-модуль (шт.)")
    sfp_exp = models.BooleanField(default=False, verbose_name="SFP расход")

    plastic_box = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, verbose_name="Короб ПВХ (м.)")
    plastic_exp = models.BooleanField(default=False, verbose_name="Короб расход")

    electric_cable = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, verbose_name="Эл. кабель (м.)")
    ec_exp = models.BooleanField(default=False, verbose_name="Эл.кабель расход")

    rj45_connector = models.SmallIntegerField(default=1, verbose_name="RJ-45 коннектор (шт.)")
    rj45_exp = models.BooleanField(default=False, verbose_name="RJ45 расход")

    utp_cable = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, verbose_name="UTP кабель (м.)")
    utp_exp = models.BooleanField(default=False, verbose_name="UTP расход")

    wifi_router = models.ForeignKey(WiFiRouterModel, verbose_name="Wi-Fi роутер", null=True, blank=True)
    wifi_exp = models.BooleanField(default=True, verbose_name="Wi-Fi расход")

    socket = models.PositiveSmallIntegerField(default=1, verbose_name="Розетка (шт.)")
    socket_exp = models.BooleanField(default=False, verbose_name="Розетка расход")

    socket_plug = models.PositiveSmallIntegerField(default=1, verbose_name="Вилка (шт.)")
    plug_exp = models.BooleanField(default=False, verbose_name="Вилка расход")

    mediaconverter = models.OneToOneField(Mediaconverter, on_delete=models.DO_NOTHING, verbose_name="Медиаконвертер", null=True, blank=True)
    mediaconverter_exp = models.BooleanField(default=False, verbose_name="Медиаконвертер расход")

    def __str__(self):
        return "%s" % (self.subscriber)

class Contract(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.PROTECT, verbose_name="Абонент")
    provider = models.ForeignKey(Providerinfo, verbose_name="Провайдер")
    contract_person = models.CharField(max_length=50, verbose_name="Договор ФИО")
    contract_number = models.CharField(max_length=20, verbose_name="Договор №")
    contract_date = models.DateField(auto_now=True, verbose_name="Договор дата")
    login = models.CharField(max_length=20, verbose_name="Логин")
    bill_url = models.URLField(default=None, null=True, blank=True, verbose_name="Адрес в биллинге")

    class Meta:
        unique_together = ['subscriber', 'provider']

    def __str__(self):
        return "%s [%s]" % (self.subscriber, self.provider)





