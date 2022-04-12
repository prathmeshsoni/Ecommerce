from rest_framework import serializers
from .models import addressModel

class address_Serialize(serializers.ModelSerializer):
    
    class Meta:
        model = addressModel
        fields = '__all__'