from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Event, Role
from fest.models import FestRegistrstion
import sys


class Command(BaseCommand):

    help = 'Setup initial perms in for all events'

    def handle(self, *args, **options):
        events = Event.objects.all()
        codenames = [
            'view_event',
            'change_event',
        ]
        head_codenames = [
            'manage_event_member'
        ]
        perms = Permission.objects.filter(codename__in=codenames).all()
        head_perms = Permission.objects.filter(
            codename__in=head_codenames).all()
        event_type = ContentType.objects.get_for_model(Event)
        for event in events:
            head_role = Role.objects.get(
                name="head", content_type=event_type, object_id=event.id)
            head_role.permissions.add(*head_perms)
            event.permissions.add(*perms)
            event.save()
            self.stdout.write(self.style.SUCCESS(
                f'Added perms for {event.name}'))
