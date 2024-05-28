from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from core.models import Student, Event
from emp.models import RegData


class Command(BaseCommand):

    help = 'Get all registration data in csv'

    def handle(self, *args, **options):
        data = []
        events = Event.objects.prefetch_related(
            'department',
        ).filter(
            is_approved=True).all()
        for ev in events:
            rd = RegData.objects.prefetch_related(
                'student',
                'students'
            ).filter(event=ev).all()
            count = 0
            self.stdout.write(
                self.style.SUCCESS(
                    f"{ev.name} has {rd.count()} registrations")
            )
            for r in rd.all():
                tlstudent = r.student
                tluser = User.objects.filter(email=tlstudent.email).first()
                if not tluser:
                    continue
                tlname = tluser.last_name if tluser.first_name[0] == '2' else tluser.first_name + \
                    ' ' + tluser.last_name
                data.append(
                    f"{tlname},{tlstudent.email},{tlstudent.whatsapp},{ev.name},{ev.department.name},{ev.start_date.strftime('%d-%m-%Y %H:%M')},{ev.end_date.strftime('%d-%m-%Y %H:%M')}")
                for stu in r.students.all():
                    stuser = User.objects.filter(email=stu.email).first()
                    if not stuser:
                        continue
                    stname = stuser.last_name if stuser.first_name[
                        0] == '2' else stuser.first_name + ' ' + stuser.last_name
                    data.append(
                        f"{stname},{stu.email},{stu.whatsapp},{ev.name},{ev.department.name},{ev.start_date.strftime('%d-%m-%Y %H:%M')},{ev.end_date.strftime('%d-%m-%Y %H:%M')}")
                count += 1
                print(f"{count}/{rd.count()} processed", end='\r', flush=True)

        with open('all_event_reg.csv', 'w') as f:
            f.write('\n'.join(data))
