from django import forms
from .models import DeviceType, DeviceModel
from django.core.exceptions import ValidationError


class DummyForm(forms.Form):
    """
    The form for dynamic configuration of a view
    """
    pass


class DeviceTypeForm(forms.ModelForm):
    class Meta:
        model = DeviceType
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name']

        if self.Meta.model.objects.filter(name=name).__len__() != 0:
            raise ValidationError("%s уже существует" % name)

        return name


class DeviceModelForm(forms.ModelForm):
    class Meta:
        model = DeviceModel
        fields = ['device_type', 'model']

    def clean_model(self):
        model = self.cleaned_data['model']

        if self.Meta.model.objects.filter(model=model).__len__() != 0:
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











