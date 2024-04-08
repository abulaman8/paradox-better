from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Event, Role, Department
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
        print(head_perms)
        event_type = ContentType.objects.get_for_model(Event)
        dept_type = ContentType.objects.get_for_model(Department)
        for event in events:
            dept = event.department
            head_role = Role.objects.get(
                name="head", content_type=event_type, object_id=event.id)
            dept_core_role = Role.objects.get(
                name="coordinator", content_type=dept_type, object_id=dept.id)

            head_role.permissions.add(*head_perms)
            dept_core_role.permissions.add(*head_perms)
            event.permissions.add(*perms)
            head_role.save()
            dept_core_role.save()
            event.save()
            self.stdout.write(self.style.SUCCESS(
                f'Added perms for {event.name}'))
