from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from core.models import Student
from emp.models import RegData
from datetime import datetime, timedelta


class Command(BaseCommand):

    help = 'get daily event reg data in csv <email>,<username>,<event>'

    def handle(self, *args, **options):
        yesterday = datetime.now().date() - timedelta(days=1)
        rd = RegData.objects.prefetch_related('student').filter(
            created_at__date=yesterday
        )
        data = []
        count = 0
        for r in rd.all():
            tlstudent = r.student
            tluser = User.objects.filter(email=tlstudent.email).first()
            if not tluser:
                continue
            name = tluser.last_name if tluser.first_name[0] == '2' else tluser.first_name + \
                ' ' + tluser.last_name
            data.append(f"{tlstudent.email},{name},{r.event.name}")
            for stu in r.students.all():
                stuser = User.objects.filter(email=stu.email).first()
                if not stuser:
                    continue
                name = stuser.last_name if stuser.first_name[0] == '2' else stuser.first_name + \
                    ' ' + stuser.last_name
                data.append(f"{stu.email},{name},{r.event.name}")
            count += 1
            print(f"{count}/{rd.count()} processed", end='\r', flush=True)

        with open('daily_reg.csv', 'w') as f:
            f.write('\n'.join(data))
