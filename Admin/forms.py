from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField


class customerLogin(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True, 'placeholder': 'Enter Username'}))

    password = forms.CharField(label="Password", widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'autocomplete': 'current_password', 'placeholder': 'Enter Password'}))
