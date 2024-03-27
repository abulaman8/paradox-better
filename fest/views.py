from datetime import datetime
from django.conf import settings
from django.template import Template, Context
from django.core.mail import EmailMultiAlternatives
from django.db.utils import OperationalError, InterfaceError, DatabaseError
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from utils.templates import fest_reg_template, fest_update_template
from utils.decorators import authed
from core.models import Student
from .models import FestRegistrstion, AccomodationRegistration


@api_view(['GET'])
@authed()
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
@authed()
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
@authed()
def accomodation_registration(request):
    data = request.data
    user = request.user
    email = user.email
    files = request.FILES
    pwd = True if data.get('pwd') == 'true' else False
    pwd_cert = files.get('pwd_cert')
    arrival_date = datetime.fromisoformat(data.get('arrival_date')).date()
    departure_date = datetime.fromisoformat(data.get('departure_date')).date()
    jain_food = True if data.get('jain_food') == 'true' else False
    medical_issues = data.get('medical_issues')
    emergency_contact = data.get('emergency_contact')
    emergency_contact_name = data.get('emergency_contact_name')
    emergency_contact_relation = data.get('emergency_contact_relation')
    try:
        student = Student.objects.get(email=email)
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
            accomodation_registration.pwd = pwd
            accomodation_registration.pwd_certificate = pwd_cert
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
            emergency_contact_relation=emergency_contact_relation,
            pwd=pwd,
            pwd_certificate=pwd_cert
        )
        return Response({'message': 'Accomodation registration successful'}, status=status.HTTP_201_CREATED)

    except OperationalError:
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except InterfaceError:
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except DatabaseError:
        return Response({'message': 'We are experiencing heavy traffic, please try again later'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        return Response({'message': e}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
