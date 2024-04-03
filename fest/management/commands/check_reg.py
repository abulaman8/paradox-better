from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from core.models import Student
from fest.models import FestRegistrstion
import sys


email = "23f3001343@ds.study.iitm.ac.in"


class Command(BaseCommand):

    help = 'check if an user has already registered for the fest or not.'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(email=email)
            student = Student.objects.get(user=user)
            fest_reg = FestRegistrstion.objects.filter(student=student).first()
            if fest_reg:
                print(student)
                self.stdout.write(self.style.SUCCESS(
                    'User has already registered for the fest'))
            else:
                self.stdout.write(self.style.ERROR(
                    'User has not registered for the fest'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User does not exist'))
