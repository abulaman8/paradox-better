from datetime import datetime, timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.template import Template, Context
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from emp.models import RegData
from fest.serializers import FestEventSerializer
from forms.models import Block, Element
from utils.templates import fest_reg_template, event_reg_conf_template
from utils.decorators import authed
from core.models import Student, Event, Department, Announcement, QrCode
from forms.serializers import FormSerializer
from forms.types import FormType, BlockType, ElementType, InputType, SelectType, RadioGroupType, CheckboxGroupType
from .models import FestRegistrstion, AccomodationRegistration
from typing import List
import uuid


@api_view(['GET'])
def get_all_announcements(request):
    announcements = Announcement.objects.prefetch_related(
        'author').all().order_by('-created_at')
    return Response(
        [{
            'id': a.id,
            'title': a.title,
            'body': a.body,
            'created_at': a.created_at.strftime("%d-%m-%Y"),
            'created_by': a.created_by,
            'author': a.author.username
        } for a in announcements], status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authed()
def check_user(request):
    data = request.GET
    email = data.get('email')
    try:
        user = User.objects.get(email=email)
        return Response({'exists': True}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'exists': False}, status=status.HTTP_200_OK)


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

    except Exception as e:
        print(e)
        return Response(
            {"message": e}, status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


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
            return Response({
                'message': 'You have already registered for fest'
            }, status=status.HTTP_200_OK)
        fest_registration = FestRegistrstion.objects.create(
            student=student,
            arrival_date=arrival_date,
            departure_date=departure_date,
            likelihood=likelihood
        )
        QrCode.objects.get_or_create(
            student=student,
            code=uuid.uuid4()
        )
        try:

            headers = {'Reply-To': "support@iitmparadox.org"}
            template = Template(fest_reg_template)
            context = Context({
                'student_name': user.last_name if user.first_name[0] == '2' else user.first_name + ' ' + user.last_name,
            })
            subject = "Get Ready for Paradox'24 - Exciting Updates Await!"
            from_email = f"Paradox'24 <{settings.EMAIL_HOST_USER}>"
            to = student.email
            rendered = template.render(context)
            email = EmailMultiAlternatives(
                subject, rendered, from_email, [to], headers=headers)
            email.attach_alternative(rendered, "text/html")
            email.send()
        except Exception as e:
            print(e)
            pass
        return Response({
            'message': 'Fest registration successful'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(e)
        return Response(
            {'message': e},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['GET'])
@authed()
def check_accom(request):
    user = request.user
    email = user.email
    try:
        student = Student.objects.get(email=email)
        accom = AccomodationRegistration.objects.filter(
            student=student).first()
        if accom and accom.payment_status and not accom.arrival_date:
            return Response(
                {
                    'registered': False,
                    'paid': True,
                    'pwd': accom.pwd,
                    'jain_food': accom.jain_food,
                    'outside_india': accom.outside_india,
                    'arrival_date': accom.arrival_date.timestamp()*1000 if accom.arrival_date else None,
                    'departure_date': accom.departure_date.timestamp()*1000 if accom.departure_date else None,
                    'medical_issues': accom.medical_issues,
                    'emergency_contact': accom.emergency_contact,
                    'emergency_contact_name': accom.emergency_contact_name,
                    'emergency_contact_relation': accom.emergency_contact_relation

                }, status=status.HTTP_200_OK)
        if accom and accom.payment_status:
            return Response(
                {
                    'registered': True,
                    'paid': True,
                    'pwd': accom.pwd,
                    'jain_food': accom.jain_food,
                    'outside_india': accom.outside_india,
                    'arrival_date': accom.arrival_date.timestamp()*1000 if accom.arrival_date else None,
                    'departure_date': accom.departure_date.timestamp()*1000 if accom.departure_date else None,
                    'medical_issues': accom.medical_issues,
                    'emergency_contact': accom.emergency_contact,
                    'emergency_contact_name': accom.emergency_contact_name,
                    'emergency_contact_relation': accom.emergency_contact_relation
                }, status=status.HTTP_200_OK)
        return Response({
            'paid': False,
            'registered': False
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response(
            {'message': e},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['POST'])
@authed()
def accomodation_registration(request):
    data = request.data
    user = request.user
    email = user.email
    files = request.FILES
    pwd = True if data.get('pwd') == 'true' else False
    print("pwd", pwd)
    pwd_cert = files.get('pwd_certificate')
    outside_india = True if data.get('outside_india') == 'true' else False
    print("outside_india", outside_india)
    passport = files.get('passport')
    print("pwd_cert", pwd_cert)
    arrival_date = datetime.fromtimestamp(int(data.get(
        'arrival_date'))//1000).replace(tzinfo=timezone.utc)
    print("arrival_date", arrival_date)
    departure_date = datetime.fromtimestamp(int(data.get(
        'departure_date'))//1000).replace(tzinfo=timezone.utc)
    print("departure_date", departure_date)
    jain_food = True if data.get('jain_food') == 'true' else False
    print("jain_food", jain_food)
    medical_issues = data.get('medical_issues')
    print("medical_issues", medical_issues)
    emergency_contact = data.get('emergency_contact')
    print("emergency_contact", emergency_contact)
    emergency_contact_name = data.get('emergency_contact_name')
    print("emergency_contact_name", emergency_contact_name)
    emergency_contact_relation = data.get('emergency_contact_relation')
    print("emergency_contact_relation", emergency_contact_relation)
    try:
        student = Student.objects.get(email=email)
        print("student", student)
        fest_registration = FestRegistrstion.objects.filter(
            student=student).exists()
        print("fest_registration", fest_registration)
        if not fest_registration:
            return Response(
                {'message': 'Please register for fest first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        accom = AccomodationRegistration.objects.filter(
            student=student).first()
        print("accomodation_registration", accom)
        if accom:
            accom.arrival_date = arrival_date
            accom.departure_date = departure_date
            accom.jain_food = jain_food
            accom.medical_issues = medical_issues
            accom.emergency_contact = emergency_contact
            accom.emergency_contact_name = emergency_contact_name
            accom.emergency_contact_relation = emergency_contact_relation
            accom.pwd = pwd
            accom.pwd_certificate = pwd_cert
            accom.outside_india = outside_india
            accom.passport = passport
            accom.save()
            try:
                with open('accommodation_2.html', 'r') as f:
                    accom_reg_template = f.read()

                headers = {'Reply-To': "support@iitmparadox.org"}
                template = Template(accom_reg_template)
                context = Context({

                })
                subject = "Accommodation Registration - Paradox'24"
                from_email = f"Paradox'24 <{settings.EMAIL_HOST_USER}>"
                to = student.email
                rendered = template.render(context)
                email = EmailMultiAlternatives(
                    subject, rendered, from_email, [to], headers=headers)
                email.attach_alternative(rendered, "text/html")
                email.send()
            except Exception as e:
                print(e)
                pass
            return Response({
                'message': 'Accomodation registration updated'
            }, status=status.HTTP_200_OK)
        try:
            accom = AccomodationRegistration.objects.create(
                student=student,
                arrival_date=arrival_date,
                departure_date=departure_date,
                jain_food=jain_food,
                medical_issues=medical_issues,
                emergency_contact=emergency_contact,
                emergency_contact_name=emergency_contact_name,
                emergency_contact_relation=emergency_contact_relation,
                pwd=pwd,
                pwd_certificate=pwd_cert,
                outside_india=outside_india,
                passport=passport
            )
            try:
                with open('accommodation_2.html', 'r') as f:
                    accom_reg_template = f.read()

                headers = {'Reply-To': "support@iitmparadox.org"}
                template = Template(accom_reg_template)
                context = Context({

                })
                subject = "Accommodation Registration - Paradox'24"
                from_email = f"Paradox'24 <{settings.EMAIL_HOST_USER}>"
                to = student.email
                rendered = template.render(context)
                email = EmailMultiAlternatives(
                    subject, rendered, from_email, [to], headers=headers)
                email.attach_alternative(rendered, "text/html")
                email.send()
            except Exception as e:
                print(e)
                pass

        except Exception as e:
            print(e)
            return Response(
                {'message': e},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        print("accomodation_registration", accom)
        return Response({
            'message': 'Accomodation registration successful'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'message': e},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['GET'])
def get_all_accom_data(request):
    accom = AccomodationRegistration.objects.prefetch_related(
        'student', 'student__email').all()
    data = []
    for a in accom:
        data.append({
            'student': a.student.email,
            'pwd': a.pwd,
            'timestamp': a.created_at.timestamp() if a.created_at else "",
        })
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
# @authed()
def get_events(request):
    data = request.GET
    dept_id = data.get('dept_id')
    if dept_id:
        try:
            dept = Department.objects.get(id=dept_id)
            events = Event.objects.prefetch_related(
                'department').filter(
                department=dept,
                is_approved=True
            ).all()
            if not dept.event_based:
                return Response(
                    {'message': 'Department not found'}, status=status.HTTP_404_NOT_FOUND
                )
        except Department.DoesNotExist:
            return Response(
                {'message': 'Department not found'}, status=status.HTTP_404_NOT_FOUND
            )
    else:
        all_events_cache = cache.get('all_events', None)
        # print("all_events_cache", all_events_cache)
        if all_events_cache:
            print("from cache")
            return Response(all_events_cache, status=status.HTTP_200_OK)
        # events = Event.objects.prefetch_related('department').all()
        events = Event.objects.prefetch_related(
            'department').filter(is_approved=True, flagship=False).all().order_by('registration_end_date')

    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'name': event.name,
            'header_image': event.header_image,
            'department': event.department.name
        })
    cache.set('all_events', events_data, None)
    return Response(events_data, status=status.HTTP_200_OK)


@api_view(['GET'])
# @authed()
def get_event_by_id(request):
    data = request.GET
    event_id = data.get('event_id')
    if event_id:
        try:
            event = Event.objects.get(id=event_id)
            if not event.is_approved:
                return Response(
                    {'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND
                )
            event_cache = cache.get(f'event_{event_id}', None)
            if event_cache:
                print("from cache")
                return Response(event_cache, status=status.HTTP_200_OK)
            serializer = FestEventSerializer(event)
            cache.set(f'event_{event_id}', serializer.data, None)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response(
                {'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@authed()
def get_event_form(request):
    data = request.GET
    event_id = data.get('event_id')
    user = request.user
    student = Student.objects.get(email=user.email)
    if event_id:
        try:
            event = Event.objects.get(id=event_id)
            if not event.is_approved:
                return Response(
                    {'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND
                )
            if event.registration_start_date.date() > datetime.now().date():
                return Response(
                    {'message': 'Registration not started yet'}, status=status.HTTP_400_BAD_REQUEST
                )
            if event.registration_end_date.date() < datetime.now().date():
                return Response(
                    {'message': 'Registration closed'}, status=status.HTTP_400_BAD_REQUEST
                )
            check_reg = RegData.objects.filter(student=student, event=event).first() or RegData.objects.filter(
                students__in=[student], event=event).first()
            if check_reg:
                return Response(
                    {'message': 'You have already registered for this event. You can edit the registration from your profile'}, status=status.HTTP_400_BAD_REQUEST
                )
            form_cache = cache.get(f'form_{event_id}', None)
            if form_cache:
                print("from cache")
                # cache.delete(f'form_{event_id}')
                return Response(form_cache, status=status.HTTP_200_OK)
            form = event.form
            serializer = FormSerializer(form)
            cache.set(f'form_{event_id}', serializer.data, None)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response(
                {'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND
            )


@api_view(['POST'])
@authed()
def register_for_event(request):
    user = request.user
    email = user.email
    data = request.data
    event_id = data.get('event_id')
    try:
        user_form = FormType.from_dict(data.get('form'))
    except Exception as e:
        return Response(
            {'message': e}, status=status.HTTP_400_BAD_REQUEST
        )
    if not event_id:
        return Response(
            {'message': 'Event id not found'}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        event = Event.objects.get(id=event_id)
        student = Student.objects.get(email=email)
        if not FestRegistrstion.objects.filter(student=student).exists():
            return Response(
                {'message': 'You have not registered for the fest'}, status=status.HTTP_400_BAD_REQUEST
            )
        event_form = event.form
        if not event.is_approved:
            return Response(
                {'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND
            )
        if not event_form:
            return Response(
                {'message': 'Form not found'}, status=status.HTTP_404_NOT_FOUND
            )
        check_reg = RegData.objects.filter(
            student=student, event=event).first()
        if check_reg:
            return Response(
                {'message': 'You have already registered'}, status=status.HTTP_400_BAD_REQUEST
            )
        event_elements = []
        user_elements = []
        email_list = []
        event_blocks = Block.objects.filter(form=event_form)
        for blk in event_blocks:
            elements = Element.objects.filter(block=blk)
            for el in elements:
                event_elements.append(el.label)
        user_blocks = user_form.blocks
        for blk in user_blocks:
            elements = blk.elements
            for el in elements:
                user_elements.append(el.label)
        for el in user_elements:
            if el not in event_elements:
                return Response(
                    {'message': 'Form not valid'}, status=status.HTTP_400_BAD_REQUEST
                )
        user_inputs: List[ElementType] = []
        final_data = {}
        user_blocks = user_form.blocks
        for blk in user_blocks:
            elements = blk.elements
            for el in elements:
                user_inputs.append(el)
        for i, el in enumerate(user_inputs):
            vel = el.element
            it = el.inputType
            if it == 'email':
                val = vel["value"]  # type: ignore
                if val is not None and len(val) > 0:
                    email_list.append(val)
            final_data[i] = {
                'id': el.id,
                'label': el.label,
                'value': ','.join(
                    map(str, vel["values"]  # type: ignore
                        ))if it == 'checkbox' else vel["value"]  # type: ignore
            }
        for email in email_list:
            if not User.objects.filter(email=email).exists():
                return Response(
                    {'message': f'User with {email} not found'}, status=status.HTTP_404_NOT_FOUND
                )
        students = Student.objects.filter(email__in=email_list).all()
        for stu in students:
            if RegData.objects.filter(students__in=[stu], event=event).exists():
                return Response(
                    {'message': f'user with email {stu.email} already registered'}, status=status.HTTP_400_BAD_REQUEST
                )
        for stu in students:
            if not FestRegistrstion.objects.filter(student=stu).exists():
                return Response(
                    {'message': f'user with email {stu.email} not registered for fest'}, status=status.HTTP_400_BAD_REQUEST
                )

        reg_data = RegData.objects.create(
            student=student,
            event=event,
            data=final_data,
            form=data.get('form')
        )
        reg_data.students.set(students)
        reg_data.save()
        try:
            print(f"email_list {email_list}")
            print("user_email", user.email)
            recipients = list(set(email_list + [user.email]))
            print(recipients)
            subject = f"Paradox'24 - Registration for {event.name}"
            headers = {'Reply-To': "support@iitmparadox.org"}
            template = Template(event_reg_conf_template)
            context = Context({
                'student_name': user.last_name if user.first_name[0] == '2' else user.first_name + ' ' + user.last_name,
                'event_name': event.name,
            })
            from_email = f"Paradox'24 <{settings.EMAIL_HOST_USER}>"
            rendered = template.render(context)
            email = EmailMultiAlternatives(
                subject, rendered, from_email, recipients, headers=headers)
            email.attach_alternative(rendered, "text/html")
            email.send()

        except Exception as e:
            print(e)
            pass

        return Response({'message': 'Registered successfully'}, status=status.HTTP_200_OK)

    except Event.DoesNotExist:
        return Response(
            {'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND
        )
    except Student.DoesNotExist:
        return Response(
            {'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@authed()
def edit_event_registration(request):
    user = request.user
    email = user.email
    data = request.data
    event_id = data.get('event_id')
    try:
        user_form = FormType.from_dict(data.get('form'))
    except Exception as e:
        return Response(
            {'message': e}, status=status.HTTP_400_BAD_REQUEST
        )
    if not event_id:
        return Response(
            {'message': 'Event id not found'}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        event = Event.objects.get(id=event_id)
        student = Student.objects.get(email=email)
        if not FestRegistrstion.objects.filter(student=student).exists():
            return Response(
                {'message': 'You have not registered for the fest'}, status=status.HTTP_400_BAD_REQUEST
            )
        check_reg = RegData.objects.filter(
            student=student, event=event).first()
        if not check_reg:
            return Response(
                {'message': 'No registration found'}, status=status.HTTP_404_NOT_FOUND
            )
        if check_reg.student != student:
            return Response(
                {'message': 'You are not allowed to edit the registration, only the team leader can edit this, if you think this is a mistake, contact support'}, status=status.HTTP_401_UNAUTHORIZED
            )
        event_form = event.form
        if not event.is_approved:
            return Response(
                {'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND
            )
        if not event_form:
            return Response(
                {'message': 'Form not found'}, status=status.HTTP_404_NOT_FOUND
            )
        event_elements = []
        user_elements = []
        email_list = []
        event_blocks = Block.objects.filter(form=event_form)
        for blk in event_blocks:
            elements = Element.objects.filter(block=blk)
            for el in elements:
                event_elements.append(el.label)
        user_blocks = user_form.blocks
        for blk in user_blocks:
            elements = blk.elements
            for el in elements:
                user_elements.append(el.label)
        for el in user_elements:
            if el not in event_elements:
                return Response(
                    {'message': 'Form not valid'}, status=status.HTTP_400_BAD_REQUEST
                )
        user_inputs: List[ElementType] = []
        final_data = {}
        user_blocks = user_form.blocks
        for blk in user_blocks:
            elements = blk.elements
            for el in elements:
                user_inputs.append(el)
        for i, el in enumerate(user_inputs):
            vel = el.element
            it = el.inputType
            if it == 'email':
                val = vel["value"]  # type: ignore
                if val is not None and len(val) > 0:
                    email_list.append(val)
            final_data[i] = {
                'id': el.id,
                'label': el.label,
                'value': ','.join(
                    map(str, vel["values"]  # type: ignore
                        ))if it == 'checkbox' else vel["value"]  # type: ignore
            }
        for email in email_list:
            if not User.objects.filter(email=email).exists():
                return Response(
                    {'message': f'User with {email} not found'}, status=status.HTTP_404_NOT_FOUND
                )
        students = Student.objects.filter(email__in=email_list).all()
        for stu in students:
            if not FestRegistrstion.objects.filter(student=stu).exists():
                return Response(
                    {'message': f'user with email {stu.email} not registered for fest'}, status=status.HTTP_404_NOT_FOUND
                )

        old_members = check_reg.students.all()
        new_members = [stu for stu in students if stu not in old_members]
        for nm in new_members:
            dup_reg = RegData.objects.filter(
                students__in=[nm], event=event).first() or RegData.objects.filter(
                    student=nm, event=event).first()
            if dup_reg:
                return Response(
                    {'message': f'user with email {nm.email} already registered in another team'}, status=status.HTTP_400_BAD_REQUEST
                )

        check_reg.data = final_data
        check_reg.form = data.get('form')
        check_reg.students.set(students)
        check_reg.save()
        return Response({'message': 'Registration updated successfully'}, status=status.HTTP_200_OK)

    except Event.DoesNotExist:
        return Response(
            {'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND
        )
    except Student.DoesNotExist:
        return Response(
            {'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@authed()
def get_registered_events(request):
    user = request.user
    student = Student.objects.get(email=user.email)
    reg_data = RegData.objects.filter(student=student).union(
        RegData.objects.filter(students__in=[student])).all()
    events = [rd.event for rd in reg_data]
    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'name': event.name,
            'header_image': event.header_image,
        })
    return Response(events_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authed()
def get_event_reg(request, event_id):
    user = request.user
    student = Student.objects.get(email=user.email)
    reg_data = RegData.objects.filter(
        student=student, event_id=event_id).first()
    if not reg_data:
        return Response(
            {'message': 'No registration found'}, status=status.HTTP_404_NOT_FOUND
        )
    data = {
        "user": reg_data.student.email,
        "form": reg_data.form,
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authed()
def delete_reg(request, event_id):
    user = request.user
    student = Student.objects.get(email=user.email)
    reg_data = RegData.objects.filter(
        student=student, event_id=event_id).first()
    if not reg_data:
        return Response(
            {'message': 'No registration found'}, status=status.HTTP_404_NOT_FOUND
        )
    reg_data.delete()
    return Response({'message': 'Registration deleted successfully'}, status=status.HTTP_200_OK)
