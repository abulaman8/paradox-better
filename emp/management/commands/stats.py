
from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType
from emp.models import RegData
from core.models import Event


class Command(BaseCommand):

    help = 'get stats about registrations'

    def handle(self, *args, **options):
        events = Event.objects.all()
        tech = Event.objects.prefetch_related('department').filter(
            department__name="Technicals").all()
        cult = Event.objects.prefetch_related('department').filter(
            department__name="Culturals").all()
        sport = Event.objects.prefetch_related(
            'department').filter(department__name="Sports").all()
        all_reg = RegData.objects.prefetch_related(
            'event', 'student', 'students').all()
        print('all reg fetched', flush=True)
        total_count = len(all_reg)
        tech_reg = all_reg.filter(event__in=tech).all()
        cult_reg = all_reg.filter(event__in=cult).all()
        sport_reg = all_reg.filter(event__in=sport).all()
        tech_count = len(tech_reg)
        cult_count = len(cult_reg)
        sport_count = len(sport_reg)
        event_counts = {}
        for event in events:
            event_counts[event.name] = len(
                all_reg.filter(event=event).all())
        reg_students = set()
        for reg in all_reg:
            reg_students.add(reg.student.email)
            for st in reg.students.all():
                reg_students.add(st.email)
        reg_students_count = len(reg_students)
        self.stdout.write(self.style.SUCCESS(
            f'Total Registrations: {total_count}\n'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Tech Registrations: {tech_count}\n'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Cult Registrations: {cult_count}\n'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Sport Registrations: {sport_count}\n'
        ))
        for e, c in event_counts.items():
            self.stdout.write(self.style.SUCCESS(
                f'{e}: {c}\n'
            ))
        self.stdout.write(self.style.SUCCESS(
            f'Total Students: {reg_students_count}\n'
        ))
