from rest_framework.serializers import ModelSerializer
from .models import Round, SomeDude


class RoundSerializer(ModelSerializer):
    class Meta:
        model = Round
        fields = '__all__'
