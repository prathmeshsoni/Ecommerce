from django import forms

from .models import *


class brandForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = brandModel
