from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from core.models import Student
from emp.models import RegData
from datetime import datetime, timedelta


class Command(BaseCommand):

    help = 'Get all registration data in csv'

    def handle(self, *args, **options):
        yesterday = datetime.now().date()  # - timedelta(days=1)
        # rd = RegData.objects.prefetch_related('student').filter(
        #     created_at__date=yesterday
        # )
        rd = RegData.objects.prefetch_related(
            'student',
            'event',
            'event__department'
            'students'
        ).all()
        # print(f"{len(rd)} registrations fetched", flush=True)
        self.stdout.write(self.style.SUCCESS(
            f"{len(rd)} registrations fetched"
        ))
        data = []
        count = 0
        for r in rd.all():
            tlstudent = r.student
            tluser = User.objects.filter(email=tlstudent.email).first()
            if not tluser:
                continue
            tlname = tluser.last_name if tluser.first_name[0] == '2' else tluser.first_name + \
                ' ' + tluser.last_name
            data.append(
                f"{tlname},{tlstudent.email},{tlstudent.whatsapp},{r.event.name},{r.event.department.name},{r.event.start_date.strftime('%d-%m-%Y %H:%M')},{r.event.end_date.strftime('%d-%m-%Y %H:%M')}")
            for stu in r.students.all():
                stuser = User.objects.filter(email=stu.email).first()
                if not stuser:
                    continue
                stname = stuser.last_name if stuser.first_name[
                    0] == '2' else stuser.first_name + ' ' + stuser.last_name
                data.append(
                    f"{stname},{stu.email},{stu.whatsapp},{r.event.name}")
            count += 1
            print(f"{count}/{rd.count()} processed", end='\r', flush=True)

        with open('daily_reg.csv', 'w') as f:
            f.write('\n'.join(data))
