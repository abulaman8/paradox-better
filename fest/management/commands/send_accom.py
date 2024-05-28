from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
import multiprocessing


def send_email(email):
    try:
        with open('accom_temp.html', 'r') as f:
            accom_open_template = f.read()

        headers = {'Reply-To': "support@iitmparadox.org"}
        template = Template(accom_open_template)
        split_email = email.split(',')
        hostel = split_email[1]
        room = split_email[2]
        name = split_email[4]
        email = split_email[7]
        context = Context({
            "hostel": hostel,
            "room": room,
            "name": name
        })
        subject = "Paradox'24 - Accommodation Confirmation"
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

    help = 'send qr mails'

    def handle(self, *args, **options):
        with open('missed', 'r') as f:
            emails = f.read().splitlines()
        # emails = [
        #     '5,Bhadra,113,24F1001636,Swathi A Menon,29-05-2024,02-06-2024,21f1000506@ds.study.iitm.ac.in',
        # ]
        print(len(emails))
        input("Press Enter to continue...")

        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        pool.map(send_email, emails)
        pool.close()
        pool.join()
