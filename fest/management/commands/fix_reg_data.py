from django.core.management.base import BaseCommand, CommandError
from emp.models import RegData


class Command(BaseCommand):

    help = 'add element id to reg data\'s data field'

    def handle(self, *args, **options):
        regs = RegData.objects.all()
        for reg in regs:
            data = reg.data
