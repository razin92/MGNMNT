from django import forms
from .models import Contract, ExpendableMaterial, Action, Subscriber

class FilterForm(forms.Form):
    subscriber = forms.CharField(help_text='Ф.И.О', max_length=15)

