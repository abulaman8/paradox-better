from django.core.management.base import BaseCommand, CommandError
from accommodation.models import AccomVolunteer
import random
import string
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.models import User


class Command(BaseCommand):

    help = 'send accom volunteer creds'

    def handle(self, *args, **options):
        volunteers = AccomVolunteer.objects.prefetch_related('user').all()
        count = 0
        for volunteer in volunteers:
            email = volunteer.user.email
            user = volunteer.user
            if not user:
                continue  # User not found, skip sending credentails to this person

            password = "".join(random.choices(
                string.ascii_uppercase + string.digits, k=8))
            user.set_password(password)
            user.save()
            subject = 'Accomodation Volunteer Credentials'
            from_email = f'Accommodation - Paradox\'24 <{settings.EMAIL_HOST_USER}>'
            message = 'Hi, your username is {} and password is {}'.format(
                user.username, password)
            with open('accom_creds.txt', 'a') as f:
                f.write(f'{email},{password}\n')
            # mail = EmailMessage(
            #     subject=subject,
            #     body=message,
            #     from_email=from_email,
            #     to=[email],
            #     cc=['studentrelations@iitmparadox.org'],
            # )
            # mail.send()
            count += 1
            print(
                f"Sent credentials to {email} ({count}/{len(volunteers)})", end='\r', flush=True)
