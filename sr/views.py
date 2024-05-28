import uuid
from django.core.files.base import ContentFile, File
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Q
from core.models import Event, Member, QrCode, Student
from utils.decorators import authed, has_perms
from utils.fns import generate_qr_code
from rest_framework.response import Response
from rest_framework import status
from emp.models import RegData
from fest.models import FestRegistrstion
from .models import EventCheckin, FestCheckin, SrVolunteer
from rest_framework.decorators import api_view
import csv
from io import StringIO, BytesIO


@api_view(['GET'])
@authed()
def get_volunteer_info(request):
    user = request.user
    print(user)
    volunteer = SrVolunteer.objects.filter(user=user).first()
    if not volunteer:
        return Response({'message': 'No volunteer found'}, status=status.HTTP_404_NOT_FOUND)
    return Response({
        "id": user.id,
        "name": f"{user.first_name} {user.last_name}",
        "email": user.email,
        "isDoingCentralCheckIn": volunteer.can_do_central_checkin,
        "events": [{"id": event.id, "name": event.name} for event in volunteer.events.all()]
    })


@api_view(['GET'])
@authed()
def get_event_info(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
        return Response({
            "id": event.id,
            "name": event.name,
            "starttime": event.start_date.timestamp() * 1000,
            "endtime": event.end_date.timestamp() * 1000
        })
    except Event.DoesNotExist:
        return Response({'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authed()
def get_all_events(request):
    events = Event.objects.all()
    return Response([{
        event.id: event.name
    } for event in events])


@api_view(['GET'])
@authed()
def get_code_by_email(request, email):
    try:
        student = Student.objects.get(email=email)
        code = QrCode.objects.get(student=student)
        return Response({
            'code': code.code
        })
    except User.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authed()
def event_checkin(request, event_id, code):
    try:
        qr = QrCode.objects.get(code=code)
        event = Event.objects.get(id=event_id)
        student = qr.student
        if not FestCheckin.objects.filter(student=student).exists():
            return Response({'message': 'Fest Checkin incomplete'}, status=status.HTTP_404_NOT_FOUND)
        volunteer = SrVolunteer.objects.get(user=request.user)
        if event not in volunteer.events.all():
            return Response({'message': 'Volunteer not authorized'}, status=status.HTTP_404_NOT_FOUND)
        user = User.objects.filter(email=student.email).first()
        if not user:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        reg = RegData.objects.filter(event=event).filter(
            Q(student=student) | Q(students__in=[student])).first()
        if not reg:
            return Response({'message': 'Registration not found'}, status=status.HTTP_404_NOT_FOUND)
        ec, created = EventCheckin.objects.get_or_create(
            student=student,
            event=event
        )
        if created:
            ec.volunteer = volunteer
            ec.save()
            return Response({'message': 'Checkin successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Already checked in'}, status=status.HTTP_400_BAD_REQUEST)

    except QrCode.DoesNotExist:
        return Response({'message': 'Invalid QR code'}, status=status.HTTP_404_NOT_FOUND)
    except Event.DoesNotExist:
        return Response({'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    except SrVolunteer.DoesNotExist:
        return Response({'message': 'Volunteer not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authed()
def fest_checkin(request, code):
    try:
        qr = QrCode.objects.get(code=code)
        student = qr.student
        volunteer = SrVolunteer.objects.get(user=request.user)
        if not volunteer.can_do_central_checkin:
            return Response({'message': 'Volunteer not authorized'}, status=status.HTTP_403_FORBIDDEN)
        reg = FestRegistrstion.objects.filter(student=student).first()
        if not reg:
            return Response({'message': 'Registration not found'}, status=status.HTTP_404_NOT_FOUND)
        ec, created = FestCheckin.objects.get_or_create(
            student=student
        )
        if created:
            ec.volunteer = volunteer
            ec.save()
            return Response({'message': 'Checkin successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Already checked in'}, status=status.HTTP_400_BAD_REQUEST)
    except QrCode.DoesNotExist:
        return Response({'message': 'Invalid QR code'}, status=status.HTTP_404_NOT_FOUND)
    except SrVolunteer.DoesNotExist:
        return Response({'message': 'Volunteer not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authed()
def get_event_participants(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
        reg = RegData.objects.prefetch_related(
            'students').filter(event=event).all()
    except Event.DoesNotExist:
        return Response({'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@has_perms(['add_srvolunteer'])
def add_volunteer(request):
    data = request.data
    email = data.get('email')
    event_ids = data.get('events')
    central_checkin = data.get('central_checkin')
    try:
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        events = Event.objects.filter(id__in=event_ids).all()
        volunteer = SrVolunteer(
            user=user, can_do_central_checkin=central_checkin)
        volunteer.events.set(events)
        volunteer.save()
        return Response({'message': 'Volunteer added'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@has_perms(['change_srvolunteer'])
def update_volunteer(request, id):
    data = request.data
    event_ids = data.get('events')
    central_checkin = data.get('central_checkin')
    try:
        events = Event.objects.filter(id__in=event_ids).all()
        volunteer = SrVolunteer.objects.get(id=id)
        volunteer.can_do_central_checkin = central_checkin
        volunteer.events.set(events)
        volunteer.save()
        return Response({'message': 'Volunteer updated'}, status=status.HTTP_200_OK)
    except SrVolunteer.DoesNotExist:
        return Response({'message': 'Volunteer not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@has_perms(['delete_srvolunteer'])
def delete_volunteer(request, id):
    try:
        volunteer = SrVolunteer.objects.get(id=id)
        volunteer.delete()
        return Response({'message': 'Volunteer deleted'}, status=status.HTTP_200_OK)
    except SrVolunteer.DoesNotExist:
        return Response({'message': 'Volunteer not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
# @has_perms(['change_department'])
def import_dept_members(request, id):
    csv_file = request.FILES.get('csv_file').read().decode('utf-8')
    if not csv_file:
        return Response({'message': 'No CSV file found'}, status=status.HTTP_400_BAD_REQUEST)
    # column names - Name, Roll No, Email, Mobile, Discord Username, Dept/Team Name, Role, Description, Status.
    members = []
    with StringIO(csv_file) as f:
        csv_data = csv.reader(f)
        for row in csv_data:
            name = row[0]
            roll_no = row[1]
            email = row[2]
            mobile = row[3]
            discord_username = row[4]
            dept_name = row[5]
            role = row[6]
            description = row[7]
            member_status = row[8]
            members.append(Member())

    return Response({'message': 'Imported successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def reset_shantanu(request):
    st = Student.objects.get(email="22f3000495@ds.study.iitm.ac.in")
    fc = FestCheckin.objects.filter(student=st).delete()
    ec = EventCheckin.objects.filter(student=st).delete()
    return Response({'message': 'Done'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def generate_qr(request):
    emails = request.data.get('emails')
    students = Student.objects.filter(email__in=emails).all()
    qrs = []
    for student in students:
        code = uuid.uuid4()
        img = generate_qr_code(code)
        img.save('qr.png')
        with open('qr.png', 'rb') as f:
            image = File(f, name='qr.png')
            try:
                qr = QrCode.objects.create(
                    code=code,
                    student=student,
                    image=image
                )
            except Exception as e:
                print(e)
                pass

    return Response({'message': 'Done'}, status=status.HTTP_200_OK)
