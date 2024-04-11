from django import forms

from Admin.address_master.models import stateModel


class stateForm(forms.ModelForm):
    class Meta:
        model = stateModel
        fields = '__all__'
