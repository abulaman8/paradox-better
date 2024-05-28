from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from core.models import Student, Event
from emp.models import RegData
from datetime import datetime, timedelta


class Command(BaseCommand):

    help = 'Get prom data in csv'

    def handle(self, *args, **options):
        prom = Event.objects.get(id=86)
