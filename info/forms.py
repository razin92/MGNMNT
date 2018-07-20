from django import forms
from django.forms import widgets
from .models import \
    Switch, Contract, ExpendableMaterial, Action, \
    Subscriber, Quarter, HomeNumber, ApartmentNumber, \
    Providerinfo, SwitchModel, Address, PortsInfo

class FilterForm(forms.Form):
    subscriber = forms.CharField(help_text='Ф.И.О', max_length=15)

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['contract_number', 'contract_person']

class SwitchFilterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SwitchFilterForm, self).__init__(*args, **kwargs)
        self.fields['address'] = forms.ModelChoiceField(
            queryset=Address.objects.filter(
                apartment__isnull=True).exclude(
                switch__isnull=True).order_by('quarter'),
            label='Фильтр по узлу'
        )

    class Meta:
        model = Switch
        fields = ['address']

class SwitchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SwitchForm, self).__init__(*args, **kwargs)
        self.fields['address'] = forms.ModelChoiceField(
            queryset=Address.objects.all().exclude(
                apartment__isnull=False).order_by('quarter'),
            label='Адрес узла'
        )

    class Meta:
        model = Switch
        fields = ['model', 'ip_add', 'address', 'description']

class AddressSearchForm(forms.ModelForm):

    def __init__(self, data):
        super(AddressSearchForm, self).__init__(data)
        self.fields['quarter'].widget.attrs = {'id': 'typehead'}

    class Meta:
        model = Address
        fields = ['district', 'quarter', 'home', 'apartment']

class SubscriberForm(forms.ModelForm):

    def __init__(self, address, *args, **kwargs):
        super(SubscriberForm, self).__init__(*args, **kwargs)
        self.fields['port'] = forms.ModelChoiceField(
            queryset=PortsInfo.objects.filter(
                switch__address__quarter=address.quarter,
                number__range=(1, 24),
                subscriber__isnull=True
            )
        )
        self.fields['address'] = forms.ModelChoiceField(
            queryset=Address.objects.filter(id=address.id),
            initial=address,
        )

    class Meta:
        model = Subscriber
        fields = ['address', 'name', 'document','provider', 'port',
                  'login', 'date', 'telephone', 'bill_url', 'comment']



