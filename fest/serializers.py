from django.contrib.contenttypes.models import ContentType
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from core.models import Event, Sponsor, Link, FAQ
from core.serializers import SponsorSerializer, FAQSerializer, LinkSerializer
from emp.models import Round, SomeDude
from emp.serializers import SomeDudeSerializer, RoundSerializer


class FestEventSerializer(ModelSerializer):
    department = SerializerMethodField()
    sponsors = SerializerMethodField()
    faqs = SerializerMethodField()
    rounds = SerializerMethodField()
    some_dudes = SerializerMethodField()
    social_links = SerializerMethodField()
    start_date = SerializerMethodField()
    end_date = SerializerMethodField()
    registration_start_date = SerializerMethodField()
    registration_end_date = SerializerMethodField()
    head = SerializerMethodField()

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
            'is_team_event',
            'max_team_size',
            'min_team_size',
            'max_participants',
            'fee',
            'department',
            'sponsors',
            'faqs',
            'rounds',
            'some_dudes',
            'social_links',
            'rules',
            'head'
        ]

    def get_head(self, obj):
        return obj.head.email

    def get_start_date(self, obj):
        return obj.start_date.timestamp() * 1000 if obj.start_date else None

    def get_end_date(self, obj):
        return obj.end_date.timestamp() * 1000 if obj.end_date else None

    def get_registration_start_date(self, obj):
        return obj.registration_start_date.timestamp() * 1000 if obj.registration_start_date else None

    def get_registration_end_date(self, obj):
        return obj.registration_end_date.timestamp() * 1000 if obj.registration_end_date else None

    def get_department(self, obj):
        return {
            "id": obj.department.id,
            "name": obj.department.name
        }

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

    def get_social_links(self, obj):
        social_links = Link.objects.filter(
            content_type=ContentType.objects.get_for_model(Event),
            object_id=obj.id
        ).all()
        return LinkSerializer(social_links, many=True).data
