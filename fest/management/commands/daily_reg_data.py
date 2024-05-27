from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from core.models import Student
from emp.models import RegData
from datetime import datetime, timedelta


class Command(BaseCommand):

    help = 'get daily event reg data in csv <email>,<username>,<event>'

    def handle(self, *args, **options):
        yesterday = datetime.now().date()  # - timedelta(days=1)
        # rd = RegData.objects.prefetch_related('student').filter(
        #     created_at__date=yesterday
        # )
        rd = RegData.objects.all()
        # print(f"{len(rd)} registrations fetched", flush=True)
        self.stdout.write(self.style.SUCCESS(
            f"{len(rd)} registrations fetched"
        ))
        data = []
        count = 0
        for r in rd.all():
            tlstudent = r.student
            data.append(
                f"{tlstudent.email},{tlstudent.whatsapp},{r.event.name}")
            for stu in r.students.all():
                data.append(f"{stu.email},{stu.whatsapp},{r.event.name}")
            count += 1
            print(f"{count}/{rd.count()} processed", end='\r', flush=True)

        with open('daily_reg.csv', 'w') as f:
            f.write('\n'.join(data))
