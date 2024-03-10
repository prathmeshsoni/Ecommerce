from rest_framework import serializers

from Admin.subcategory.models import brandModel


class brandSerializer(serializers.ModelSerializer):
    class Meta:
        model = brandModel
        fields = '__all__'
