from django import forms

from Admin.filter.models import colourModel


class colourForm(forms.ModelForm):
    class Meta:
        model = colourModel
        fields = '__all__'
