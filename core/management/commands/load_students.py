from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from core.models import Student
import json
from datetime import datetime


class Command(BaseCommand):

    help = 'load students from a json file into the database'

    def handle(self, *args, **options):
        file = 'students.json'
        student_objects = []
        students = json.load(open(file))
        for student in students:
            try:
                student_objects.append(
                    Student(
                        email=student['email'],
                        gender=student['gender'],
                        whatsapp=student['whatsapp'],
                        city=student['city'],
                        state=student['state'],
                        country=student['country'],
                        date_of_birth=datetime.strptime(
                            student['date_of_birth'], '%Y-%m-%d').date() if student['date_of_birth'] else None,


                    )
                )
            except Exception as e:
                student_objects.append(
                    Student(
                        email=student['email'],
                        gender=student['gender'],
                        whatsapp=student['whatsapp'],
                        city=student['city'],
                        state=student['state'],
                        country=student['country'],
                    )
                )
        try:
            Student.objects.bulk_create(student_objects)
        except IntegrityError:
            for student in student_objects:
                try:
                    student.save()
                except IntegrityError:
                    self.stdout.write(self.style.ERROR(
                        'Student with email %s already exists' % student.email))
        self.stdout.write(self.style.SUCCESS('Successfully loaded students'))
