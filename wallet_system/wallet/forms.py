from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email']


class PaymentForm(forms.Form):
    Amount = forms.DecimalField()


class TransferForm(forms.Form):
    account_number = forms.CharField(label='Account Number')
    bank_code = forms.CharField(label='Bank Code')
    account_name = forms.CharField(label='Account Name')
    amount = forms.DecimalField(label='Amount', max_digits=10, decimal_places=2)
    reason = forms.CharField(label='Reason', widget=forms.Textarea)


