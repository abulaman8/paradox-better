from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from core.models import Student
from fest.models import AccomodationRegistration


class Command(BaseCommand):

    help = 'create accomodation registration for students in emails and set payment_status to True'

    def handle(self, *args, **options):
        with open('temp', 'r') as f:
            emails = f.read().splitlines()
        i = 0
        for email in emails:
            try:
                student = Student.objects.get_or_create(email=email)[0]
                accom = AccomodationRegistration.objects.get_or_create(student=student)[
                    0]
                accom.payment_status = True
                accom.save()
                i += 1
                print(
                    f"{i}/{len(emails)} accommodations opened.",
                    end='\r'
                )
            except Exception as e:
                print(f"{e} at {email}")
                continue
