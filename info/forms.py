from django import forms

class FilterForm(forms.Form):
    subscriber = forms.CharField(help_text='Ф.И.О', max_length=15)