from rest_framework.serializers import ModelSerializer, SerializerMethodField
from django.contrib.contenttypes.models import ContentType
from core.models import FAQ, Event, Sponsor
from core.serializers import SponsorSerializer, FAQSerializer, LinkSerializer
from .models import Round, SomeDude


class RoundSerializer(ModelSerializer):
    class Meta:
        model = Round
        exclude = ['event']


class SomeDudeSerializer(ModelSerializer):
    class Meta:
        model = SomeDude
        exclude = ['event']


class EventSerializer(ModelSerializer):
    department = SerializerMethodField()
    head = SerializerMethodField()
    sponsors = SerializerMethodField()
    faqs = SerializerMethodField()
    rounds = SerializerMethodField()
    some_dudes = SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id',
            'name',
            'description',
            'header_image',
            'start_date',
            'end_date',
            'registration_start_date',
            'registration_end_date',
            'location',
            'location_link',
            'is_approved',
            'open',
            'is_team_event',
            'max_team_size',
            'min_team_size',
            'max_participants',
            'fee',
            'head',
            'department',
            'sponsors',
            'faqs',
            'rounds',
            'some_dudes'
        ]

    def get_department(self, obj):
        return obj.department.name

    def get_head(self, obj):
        return obj.head.email

    def get_sponsors(self, obj):
        sponsors = Sponsor.objects.filter(
            content_type=ContentType.objects.get_for_model(Event),
            object_id=obj.id
        ).all()
        return SponsorSerializer(sponsors, many=True).data

    def get_faqs(self, obj):
        faqs = FAQ.objects.filter(
            content_type=ContentType.objects.get_for_model(Event),
            object_id=obj.id
        ).all()
        return FAQSerializer(faqs, many=True).data

    def get_rounds(self, obj):
        rounds = Round.objects.filter(
            event=obj
        ).all()
        return RoundSerializer(rounds, many=True).data

    def get_some_dudes(self, obj):
        some_dudes = SomeDude.objects.filter(
            event=obj
        ).all()
        return SomeDudeSerializer(some_dudes, many=True).data
