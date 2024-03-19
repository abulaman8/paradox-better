from .models import Supply, Hostel, Mess, Accommadation
from rest_framework import serializers


class SupplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Supply
        fields = '__all__'


class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = '__all__'


class MessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mess
        fields = '__all__'


class AccommodationSerializer(serializers.ModelSerializer):
    mess = MessSerializer()
    hostel = HostelSerializer()
    supplies_given = SupplySerializer(many=True)
    supplies_returned = SupplySerializer(many=True)

    class Meta:
        model = Accommadation
        fields = '__all__'
