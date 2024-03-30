from django.core.management.base import BaseCommand, CommandError
from core.models import Student
import json
from datetime import datetime
from django.contrib.auth.models import User
from fest.models import FestRegistrstion


class Command(BaseCommand):

    help = 'Fixes duplicate students in the database by deleting any student without a fest registration'

    def handle(self, *args, **options):
        emails = [student.email for student in Student.objects.all()]
        counts = {}
        for email in emails:
            if email not in counts:
                counts[email] = 0
            counts[email] += 1
        emails = [email for email in counts if counts[email] > 1]
        i = 0
        for email in emails:
            i += 1
            students = Student.objects.filter(email=email).all()
            if len(students) > 1:
                print(f"Found {len(students)} students with email {email}")
                try:
                    fest_registration = FestRegistrstion.objects.get(
                        student__email=email)
                except FestRegistrstion.DoesNotExist:
                    print("Reg not found so deleting the first student")
                    students[0].delete()
                    continue
                for student in students:
                    if fest_registration.student != student:
                        print(f"Deleting student {student}")
                        student.delete()
            print(f"Processed {i}/{len(emails)}", end="\r")
        print("Done")
