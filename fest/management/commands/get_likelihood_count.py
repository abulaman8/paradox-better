from django.core.management.base import BaseCommand, CommandError
from fest.models import FestRegistrstion


class Command(BaseCommand):

    help = 'get likelihood count of fest registration.'

    def handle(self, *args, **options):
        fest_regs = FestRegistrstion.objects.all()
        most_probably = 0
        unsure = 0
        definitely = 0
        for fest_reg in fest_regs:
            if fest_reg.likelihood == 'Most Probably':
                most_probably += 1
            elif fest_reg.likelihood == 'Unsure':
                unsure += 1
            elif fest_reg.likelihood == 'Definitely':
                definitely += 1
        self.stdout.write(self.style.SUCCESS(
            'Most Probably: %s' % most_probably))
        self.stdout.write(self.style.SUCCESS('Unsure: %s' % unsure))
        self.stdout.write(self.style.SUCCESS('Definitely: %s' % definitely))
