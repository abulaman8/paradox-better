from django.core.management.base import BaseCommand
from fest.models import FestRegistrstion


class Command(BaseCommand):

    help = 'Get unpaid students'

    def handle(self, *args, **options):
        saf = []
        with open('student_activity_fee_paid.csv', 'r') as f:
            saf = [line for line in f]
        all_fr = FestRegistrstion.objects.prefetch_related('student').all()
        fr_emails = [fr.student.email for fr in all_fr]
        print(len(fr_emails))
        print(len(saf))
        unpaid = [email for email in fr_emails if email not in saf]
        with open('unpaid.csv', 'w') as f:
            f.write('\n'.join(unpaid))
