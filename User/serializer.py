from rest_framework import serializers
from .models import addressModel
from Admin.product.models import productModel

class address_Serialize(serializers.ModelSerializer):

    class Meta:
        model = addressModel
        fields = '__all__'


class prooSerialize(serializers.ModelSerializer):

    class Meta:
        model = productModel
        fields = '__all__'