from django.core.management.base import BaseCommand, CommandError
from core.models import Student
from fest.models import FestRegistrstion
import json
from datetime import datetime


class Command(BaseCommand):

    help = 'load fest regs from a json file into the database'

    def handle(self, *args, **options):
        file = 'fest_regs.json'
        reg_objects = []
        regs = json.load(open(file))
        total = len(regs)
        self.stdout.write(self.style.SUCCESS(
            f'Loaded {total} fest regs from {file}'))
        i = 0
        for reg in regs:
            try:
                student = Student.objects.get(email=reg['email'])
                reg_objects.append(
                    FestRegistrstion(
                        student=student,
                        arrival_date=datetime.strptime(
                            reg['arrival_date'], '%Y-%m-%d'),
                        departure_date=datetime.strptime(
                            reg['departure_date'], '%Y-%m-%d'),
                        likelihood=reg['likelihood'],

                    )
                )
                i += 1
                print(f'Loaded {i}/{total} fest regs', end='\r')
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Error: {e} with {reg["email"]}'))
        FestRegistrstion.objects.bulk_create(reg_objects)
        self.stdout.write(self.style.SUCCESS('Successfully loaded fest regs'))
