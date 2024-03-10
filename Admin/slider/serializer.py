from rest_framework import serializers

from Admin.slider.models import GalleryModel


class sliderSerialize(serializers.ModelSerializer):
    class Meta:
        model = GalleryModel
        fields = '__all__'
