from django import forms

class LoginForm(forms.Form):
    subscriber_id = forms.CharField(label='Введите свой ID', max_length=9)
    tel_number = forms.CharField(label='Введите свой номер мобильного телефона (с кодом)', max_length=13)