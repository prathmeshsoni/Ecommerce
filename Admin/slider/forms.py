from django import forms

from Admin.slider.models import GalleryModel


class GalleryForm(forms.ModelForm):
    class Meta:
        model = GalleryModel
        fields = '__all__'
