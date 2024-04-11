from rest_framework import serializers

from Admin.product.models import productModel
from .models import addressModel


class address_Serialize(serializers.ModelSerializer):
    class Meta:
        model = addressModel
        fields = '__all__'


class prooSerialize(serializers.ModelSerializer):
    class Meta:
        model = productModel
        fields = '__all__'
