from datetime import datetime
from django.conf import settings
from django.template import Template, Context
from django.core.mail import EmailMultiAlternatives
from django.db.utils import OperationalError, InterfaceError, DatabaseError
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status

from core.models import Student
from .models import FestRegistrstion, AccomodationRegistration


fest_reg_template = '''
<!DOCTYPE html>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paradox'24 Updates</title>
</head>
<body>
    <div>
        <p>Dear {{ student_name }},</p>
        <p>Congratulations for successfully registering for Paradox'24! Get set for an exhilarating experience on our campus from May 30th to June 2nd.</p>
        <p>And guess what?  We've got an electrifying surprise event in store for everyone, and details will be unveiled shortly. Stay tuned to our social media channels for the latest updates and sneak peeks!</p>
        <p>Please note that this email serves as confirmation of your festival registration. As for accommodation, fret not, registration form will soon be rolled out on our website. But bear in mind, accommodation slots are limited and will be allocated on a first-come, first-served basis.</p>
        <p>The check-in desk for accommodation opens its doors on May 29th and remains accessible until June 2nd. Operating hours are from 8:00 AM to 8:00 PM daily. Plan your travel arrangements accordingly to ensure a seamless check-in process.</p>
        <p>Should you have any inquiries or doubts, please don't hesitate to reach out to us at <a href="mailto:support@iitmparadox.org">support@iitmparadox.org</a>.</p>

        <p>Warm Regards,</p>
        <p>Team Paradox</p>
    </div>
</body>
</html>
'''

fest_update_template = '''
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paradox'24 Registration Update</title>
</head>
<body>
    <div>
        <p>Dear {{ student_name }},</p>
        <p>We've received your update/edit for Paradox'24 registration. Your changes have been successfully captured. Thank you for keeping us informed!</p>
        <p>If you have any further questions or concerns, feel free to reach out to us at <a href="mailto:support@iitmparadox.org">support@iitmparadox.org</a>.</p>
        <p>Best Regards,</p>
        <p>Team Paradox</p>
    </div>
</body>
</html>
'''


@api_view(['GET'])
@authentication_classes([OAuth2Authentication])
def check_fest_registration(request):
    user = request.user
    try:
        email = user.email
        student = Student.objects.get(email=email)
        fest_registration = FestRegistrstion.objects.filter(
            student=student).exists()
        if fest_registration:
            return Response({'registered': True}, status=status.HTTP_200_OK)
        return Response({'registered': False}, status=status.HTTP_200_OK)

    except OperationalError:
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except InterfaceError:
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except DatabaseError:
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        print(e)
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
@authentication_classes([OAuth2Authentication])
def fest_registration(request):
    user = request.user
    email = user.email
    data = request.data
    arrival_date = datetime.fromisoformat(data.get('arrival_date')).date()
    departure_date = datetime.fromisoformat(data.get('departure_date')).date()
    likelihood = data.get('likelihood')
    whatsapp = data.get('whatsapp')
    city = data.get('city')
    state = data.get('state')
    country = data.get('country')
    gender = data.get('gender')
    dob = datetime.fromisoformat(data.get('dob')).date()
    try:
        student = Student.objects.get(email=email)
        student.whatsapp = whatsapp
        student.city = city
        student.state = state
        student.country = country
        student.gender = gender
        student.date_of_birth = dob
        student.save()
        fest_registration = FestRegistrstion.objects.filter(
            student=student).first()
        if fest_registration:
            return Response({'message': 'You have already registered for fest, updating registration will be available soon'}, status=status.HTTP_200_OK)
            # fest_registration.arrival_date = arrival_date
            # fest_registration.departure_date = departure_date
            # fest_registration.likelihood = likelihood
            # fest_registration.save()
            # headers = {'Reply-To': "support@iitmparadox.org"}
            # template = Template(fest_update_template)
            # context = Context({
            #     'student_name': student.user.last_name if student.user.first_name[0] == '2' else student.user.first_name + ' ' + student.user.last_name,
            # })
            # subject = "Registration Update Confirmation for Paradox'24"
            # from_email = settings.EMAIL_HOST_USER
            # to = student.user.email
            # rendered = template.render(context)
            # email = EmailMultiAlternatives(
            #     subject, rendered, from_email, [to], headers=headers)
            # email.attach_alternative(rendered, "text/html")
            # email.send()
            # return Response({'message': 'Fest registration updated'}, status=status.HTTP_200_OK)
        fest_registration = FestRegistrstion.objects.create(
            student=student,
            arrival_date=arrival_date,
            departure_date=departure_date,
            likelihood=likelihood
        )
        # Send email
        headers = {'Reply-To': "support@iitmparadox.org"}
        template = Template(fest_reg_template)
        context = Context({
            'student_name': user.last_name if user.first_name[0] == '2' else user.first_name + ' ' + user.last_name,
        })
        subject = "Get Ready for Paradox'24 - Exciting Updates Await!"
        from_email = settings.EMAIL_HOST_USER
        to = student.email
        rendered = template.render(context)
        email = EmailMultiAlternatives(
            subject, rendered, from_email, [to], headers=headers)
        email.attach_alternative(rendered, "text/html")
        email.send()
        return Response({'message': 'Fest registration successful'}, status=status.HTTP_201_CREATED)

    except OperationalError:
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except InterfaceError:
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except DatabaseError:
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        print(e)
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
@authentication_classes([OAuth2Authentication])
def accomodation_registration(request):
    data = request.data
    user = request.user
    email = user.email
    arrival_date = datetime.fromisoformat(data.get('arrival_date')).date()
    departure_date = datetime.fromisoformat(data.get('departure_date')).date()
    jain_food = data.get('jain_food')
    medical_issues = data.get('medical_issues')
    emergency_contact = data.get('emergency_contact')
    emergency_contact_name = data.get('emergency_contact_name')
    emergency_contact_relation = data.get('emergency_contact_relation')
    try:
        student = Student.objects.get(user=request.user)
        fest_registration = FestRegistrstion.objects.filter(
            student=student).exists()
        if not fest_registration:
            return Response({'message': 'Please register for fest first'}, status=status.HTTP_400_BAD_REQUEST)
        accomodation_registration = AccomodationRegistration.objects.filter(
            student=student).first()
        if accomodation_registration:
            accomodation_registration.arrival_date = arrival_date
            accomodation_registration.departure_date = departure_date
            accomodation_registration.jain_food = jain_food
            accomodation_registration.medical_issues = medical_issues
            accomodation_registration.emergency_contact = emergency_contact
            accomodation_registration.emergency_contact_name = emergency_contact_name
            accomodation_registration.emergency_contact_relation = emergency_contact_relation
            accomodation_registration.save()
            return Response({'message': 'Accomodation registration updated'}, status=status.HTTP_200_OK)

        accomodation_registration = AccomodationRegistration.objects.create(
            student=student,
            arrival_date=arrival_date,
            departure_date=departure_date,
            jain_food=jain_food,
            medical_issues=medical_issues,
            emergency_contact=emergency_contact,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_relation=emergency_contact_relation
        )
        return Response({'message': 'Accomodation registration successful'}, status=status.HTTP_201_CREATED)

    except OperationalError:
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except InterfaceError:
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except DatabaseError:
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
