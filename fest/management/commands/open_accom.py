from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from core.models import Student
from fest.models import AccomodationRegistration


class Command(BaseCommand):

    help = 'create accomodation registration for students in emails and set payment_status to True'

    def handle(self, *args, **options):
        with open('emails', 'r') as f:
            emails = f.read().splitlines()
        with open('accommodation_1.html', 'r') as f:
            accom_open_template = f.read()

        headers = {'Reply-To': "support@iitmparadox.org"}
        template = Template(accom_open_template)
        context = Context({
        })
        subject = "Paradox'24 - Accommodation Open"
        from_email = f"Paradox'24 <{settings.EMAIL_HOST_USER}>"
        rendered = template.render(context)
        # emails = ['21f1000506@ds.study.iitm.ac.in',
        #           '21f3002911@ds.study.iitm.ac.in',
        #           ]
        i = 0
        for email in emails:
            try:
                student = Student.objects.get_or_create(email=email)[0]
                accom = AccomodationRegistration.objects.get_or_create(student=student)[
                    0]
                accom.payment_status = True
                accom.save()
                try:
                    to = student.email
                    mail = EmailMultiAlternatives(
                        subject, rendered, from_email, [to], headers=headers)
                    mail.attach_alternative(rendered, "text/html")
                    mail.send()
                    i += 1
                    print(
                        f"{i}/{len(emails)} accommodations opened and mail sent.", end='\r')
                except Exception as e:
                    print(f"{e} at {email}")
                    pass
            except Exception as e:
                print(f"{e} at {email}")
                continue
