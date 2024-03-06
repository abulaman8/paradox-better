from django.core.management.base import BaseCommand, CommandError
from core.models import Student


class Command(BaseCommand):

    help = 'set student emails from user emails.'

    def handle(self, *args, **options):
        students = Student.objects.all()
        for student in students:
            student.email = student.user.email
            student.save()
        self.stdout.write(self.style.SUCCESS(
            'Successfully set student emails from user emails.'))
