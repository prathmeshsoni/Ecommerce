from rest_framework import serializers

from Admin.product.models import productModel


class proSerialize(serializers.ModelSerializer):
    class Meta:
        model = productModel
        fields = '__all__'
