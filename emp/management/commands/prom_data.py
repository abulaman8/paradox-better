from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from core.models import Student, Event
from emp.models import RegData
from datetime import datetime, timedelta


class Command(BaseCommand):

    help = 'Get prom data in csv'

    def handle(self, *args, **options):
        prom = Event.objects.get(id=86)
        rd = RegData.objects.prefetch_related('student').filter(event=prom)
        data = []
        count = 0
        for r in rd:
            st = r.student
            us = User.objects.filter(email=st.email).first()
            if not us:
                continue
            name = f"{us.last_name}" if us.first_name[0] == "2" else f"{us.first_name} {us.last_name}"
            dob = st.date_of_birth
            age = datetime.now().year - dob.year if dob else "n/a"
            gender = st.gender
            data.append(f"{name},{st.email},{age},{gender}")
            count += 1
            print(f"{count}/{rd.count()}", flush=True, end='\r')
        with open('prom.csv', 'w') as f:
            f.write('\n'.join(data))
