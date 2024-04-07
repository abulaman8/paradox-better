from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from core.models import Student
from fest.models import AccomodationRegistration
import multiprocessing


def send_email(email):
    try:
        with open('accommodation_2.html', 'r') as f:
            accom_open_template = f.read()

        headers = {'Reply-To': "support@iitmparadox.org"}
        template = Template(accom_open_template)
        context = Context({})
        subject = "Paradox'24 - Accommodation Registration"
        from_email = f"Paradox'24 <{settings.EMAIL_HOST_USER}>"
        rendered = template.render(context)

        # No longer fetching Student and AccomodationRegistration objects here
        # Instead, just using email to create context-specific information
        to = email
        mail = EmailMultiAlternatives(
            subject, rendered, from_email, [to], headers=headers)
        mail.attach_alternative(rendered, "text/html")
        mail.send()
        print(f"Email sent to {email}")
    except Exception as e:
        print(f"Error sending email to {email}: {str(e)}")


class Command(BaseCommand):

    help = 'send accomodation confirmation mails to missed out students'

    def handle(self, *args, **options):
        ar = AccomodationRegistration.objects.prefetch_related('student').all()
        emails = [
            accom.student.email for accom in ar if accom.payment_status and accom.arrival_date]
        # emails = [
        #     '21f3002911@ds.study.iitm.ac.in',
        #     '21f1000506@ds.study.iitm.ac.in',
        #     '23f3000516@ds.study.iitm.ac.in',
        # ]
        print(emails)
        print(len(emails))
        input("Press Enter to continue...")

        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        pool.map(send_email, emails)
        pool.close()
        pool.join()
