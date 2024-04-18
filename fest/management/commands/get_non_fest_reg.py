from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from core.models import Student
from fest.models import FestRegistrstion
from emp.models import RegData


class Command(BaseCommand):

    help = 'get emails of all students how have registered for an event but not fest'

    def handle(self, *args, **options):
        fest_emails = FestRegistrstion.objects.values_list(
            'student__email', flat=True)
        regs = RegData.objects.prefetch_related(
            'student',
            'students'
        ).all()
        reg_emails = set()
        for reg in regs:
            reg_emails.add(reg.student.email)
            for st in reg.students.all():
                reg_emails.add(st.email)
        for re in reg_emails:
            if re not in fest_emails:
                print(re)
