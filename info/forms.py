from django import forms
from django.forms import widgets
from .models import \
    Switch, Contract, ExpendableMaterial, Action, \
    Subscriber, Quarter, HomeNumber, ApartmentNumber, \
    Providerinfo, SwitchModel, Address

class FilterForm(forms.Form):
    subscriber = forms.CharField(help_text='Ф.И.О', max_length=15)

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['contract_number', 'contract_person']

class SwitchForm(forms.ModelForm):
    class Meta:
        model = Switch
        fields = ['model', 'ip_add', 'address', 'description']

    def __init__(self, *args, **kwargs):
        super(SwitchForm, self).__init__(*args, **kwargs)
        self.fields['address'].widget.choices = ((x.pk, x) for x in Address.objects.all().exclude(apartment__isnull=False))
        self.fields['address'].valid = True

class AddressSearchForm(forms.Form):
    quarter = forms.ChoiceField(
        choices=((x, x) for x in Quarter.objects.all()),
        label="Квартал"
    )
    building = forms.ChoiceField(
        choices=((x, x) for x in HomeNumber.objects.all()),
        label="Дом"
    )
    apartment = forms.ChoiceField(
        choices=((x, x) for x in ApartmentNumber.objects.all()),
        label="Квартира"
    )

    def __init__(self, data):
        super(AddressSearchForm, self).__init__(data)
        self.fields['quarter'].widget.attrs = {'id': 'typehead'}

class SubscriberForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        label='Ф.И.О'
    )
    document = forms.CharField(
        max_length=20,
        label='Договор №'
    )
    provider = forms.ChoiceField(
        choices=((x.name, x.name) for x in Providerinfo.objects.all()),
        label='Провайдер'
    )
    port = forms.ChoiceField(
        choices=((1,2))
    )


