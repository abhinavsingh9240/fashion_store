from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from home.models import Cart


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'first_name', 'last_name']


class LoginForm(forms.Form):
    email_phone = forms.CharField(max_length=63)
    password = forms.CharField(max_length=63, widget=forms.PasswordInput)


class NameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)


class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ('quantity', 'size')


class ProductOrder(forms.Form):
    product_id = forms.IntegerField()
    quantity = forms.IntegerField()
    size_id = forms.IntegerField()
