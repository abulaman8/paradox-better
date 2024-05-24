from django.core.management.base import BaseCommand, CommandError
from core.models import Student
from fest.models import FestRegistrstion


class Command(BaseCommand):

    help = 'get state wise student count'

    def handle(self, *args, **options):
        regs = FestRegistrstion.objects.prefetch_related('student').all()
        students = [f.student for f in regs]
        total = len(students)
        state_count = {}
        i = 0
        for student in students:
            if student.state in state_count:
                state_count[student.state] += 1
                i += 1
                print(f"{i}/{total} processed", end='\r', flush=True)
            else:
                state_count[student.state] = 1
                i += 1
                print(f"{i}/{total} processed", end='\r', flush=True)
        keys = ['State', 'Count']

        with open('state_count.csv', 'w') as f:
            f.write(','.join(keys) + '\n')
            for state, count in state_count.items():
                f.write(f'{state},{count}\n')
        self.stdout.write(self.style.SUCCESS(
            'Successfully created "state_count.csv'))
