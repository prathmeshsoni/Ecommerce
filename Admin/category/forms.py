from django import forms

from .models import categoryModel


class categoryForm(forms.ModelForm):
    class Meta:
        model = categoryModel
        fields = "__all__"
