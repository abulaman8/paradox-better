from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from emp.models import RegData
from core.models import Event


class Command(BaseCommand):

    help = 'send mails to event reg students'

    def handle(self, *args, **options):
        genai = Event.objects.get(name="GenAI")
        emails = set()
        reg = RegData.objects.prefetch_related('student').filter(event=genai)
        for r in reg:
            emails.add(r.student.email)
        emails.add("21f1000506@ds.study.iitm.ac.in")
        body = """Dear student,
Thank you for registering for GenAI. The workshop on genrative AI and vector databases will be held today (31st of June) at 10 am at the New Academic Complex (NAC) room 505.
This workshop is crucial for the hackathon that follows, So we request you to be present on time


Regards,
Team GenAI
        """
        subject = "GenAI Workshop"
        from_email = f" Paradox'24 GenAI <{settings.EMAIL_HOST_USER}>"

        mail = EmailMultiAlternatives(
            subject, body, from_email, list(emails))
        print("number of emails: ", len(emails))
        input("press enter to send mails")
        mail.send()
