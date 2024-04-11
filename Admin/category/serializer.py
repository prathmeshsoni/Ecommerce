from rest_framework import serializers

from Admin.category.models import categoryModel


class catSerialize(serializers.ModelSerializer):
    class Meta:
        model = categoryModel
        fields = '__all__'
