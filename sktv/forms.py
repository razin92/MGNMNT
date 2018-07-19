from django import forms
from datetime import datetime
from .models import DeviceType, DeviceModel
from django.core.exceptions import ValidationError

##########################################################################
#Для теста
class LoginForm(forms.Form):
    subscriber_id = forms.CharField(label='Введите свой ID', max_length=9)
    tel_number = forms.CharField(label='Введите свой номер мобильного телефона (с кодом)', max_length=13)

class MakeRequestForm(forms.Form):
    date = forms.DateTimeField(label="Дата(Date)", initial=datetime.now())
    district = forms.CharField(
        label="Район(Район_Key)",
        initial="1f47fc27-5134-11e4-8276-9c2a7053e206",
        max_length=36
    )
    quarter = forms.CharField(
        label="Квартал(КварталМассив_Key)",
        initial="0a9a5424-5138-11e4-8276-9c2a7053e206",
        max_length=36
    )
    building = forms.CharField(
        label="Дом(Дом_Key)",
        initial="4c2fb29d-5139-11e4-8276-9c2a7053e206",
        max_length=36
    )
    apartment = forms.CharField(
        label="Квартира(Квартира_Key)",
        initial="c0cba461-9c02-11e6-80b7-940c6dc95a33",
        max_length=36
    )
    contract = forms.CharField(
        label="Договор(АбонентскийДоговор_Key)",
        initial="1893369f-9c23-11e6-80b7-940c6dc95a33",
        max_length=36
    )
    subscriber = forms.CharField(
        label="Абонент (ФизическоеЛицо_Key)",
        initial="0ffa9bf5-9c23-11e6-80b7-940c6dc95a33",
        max_length=36
    )
    question = forms.CharField(
        label="Вопрос (Вопрос_Key)",
        initial="ce78fa8e-85c0-11e4-9407-001e8cd9ad93",
        max_length=36
    )
    organization = forms.CharField(
        label="Организация (Организация_Key)",
        initial="591ee6f7-5132-11e4-8276-9c2a7053e206",
        max_length=36
    )

######################################################################
#Рабочая область
class DeviceTypeForm(forms.ModelForm):
    class Meta:
        model = DeviceType
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name']

        if DeviceType.objects.filter(name=name).__len__() != 0:
            raise ValidationError("%s уже существует" % name)

        return name

class DeviceModelForm(forms.ModelForm):
    class Meta:
        model = DeviceModel
        fields = ['device_type', 'model']

    def clean_model(self):
        model = self.cleaned_data['model']

        if DeviceType.objects.filter(model=model).__len__() != 0:
            raise ValidationError("%s уже существует" % model)

        return model

class BuildingBaseForm(forms.Form):
    pass

class BuildingForm(forms.Form):
    pass

class DeviceForm(forms.Form):
    pass

class BuildingDeviceGroup(forms.Form):
    pass











