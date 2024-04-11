from rest_framework import serializers

from Admin.address_master.models import stateModel


class stateSerialize(serializers.ModelSerializer):
    class Meta:
        model = stateModel
        fields = '__all__'
