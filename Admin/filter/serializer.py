from rest_framework import serializers

from Admin.filter.models import colourModel


class colourSerialize(serializers.ModelSerializer):
    class Meta:
        model = colourModel
        fields = '__all__'
