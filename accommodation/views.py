from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import Student, QrCode
from utils.decorators import has_perms, authed
from .models import Accommadation, Supply, OTP, AccomVolunteer
from datetime import datetime, timedelta
import random


@api_view(['GET'])
@authed()
def get_all_supplies(request):
    supplies = Supply.objects.all()
    return Response([{
        'Item Name': supply.name,
        'Item ID': supply.id
    } for supply in supplies])


@api_view(['GET'])
@authed()
def get_user_accommodation(request, id):
    try:
        student = Student.objects.get(id=id)
        accommadation = Accommadation.objects.prefetch_related(
            'hostel', 'mess').filter(student=student).first()
        if not accommadation:
            return Response({'message': 'No Accommodation found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            'Hostel Info': {
                'Name': accommadation.hostel.name,
                'Room Number': accommadation.room
            },
            'Mess Info': {
                'Name': accommadation.mess.name,
                'Floor': accommadation.mess.floor,
                'Caterer': accommadation.mess.caterer
            }
        })
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@has_perms(['change_accommadation'])
def check_in(request, id):
    try:
        student = Student.objects.get(id=id)
        accommadation = Accommadation.objects.filter(student=student).first()
        if not accommadation:
            return Response({'message': 'No Accommodation found'}, status=status.HTTP_404_NOT_FOUND)
        accommadation.check_in = datetime.now()
        accommadation.save()
        return Response({'message': 'Checked In'}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@has_perms(['change_accommadation'])
def check_out(request, id):
    try:
        student = Student.objects.get(id=id)
        accommadation = Accommadation.objects.filter(student=student).first()
        if not accommadation:
            return Response({'message': 'No Accommodation found'}, status=status.HTTP_404_NOT_FOUND)
        accommadation.check_out = datetime.now()
        accommadation.save()
        return Response({'message': 'Checked Out'}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authed()
def request_supply_give_otp(request, id):
    try:
        student = Student.objects.get(id=id)
        accommadation = Accommadation.objects.prefetch_related(
            'supplies_given').filter(student=student).first()
        if not accommadation:
            return Response({'message': 'No Accommodation found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        supply_ids = data.get('Item IDs')
        supply_objects = Supply.objects.filter(id__in=supply_ids).all()
        for supply in supply_objects:
            if supply in accommadation.supplies_given.all():
                return Response({'message': f'{supply.name} already given'}, status=status.HTTP_400_BAD_REQUEST)
        otp = OTP.objects.create(
            student=student,
            otp=''.join([str(random.randint(0, 9)) for _ in range(6)]),
            expires_at=datetime.now() + timedelta(minutes=60)
        )
        otp.supplies.add(*supply_objects)
        otp.save()
        # email otp to student
        try:
            send_mail(
                subject='Supplies OTP',
                message=f"Your OTP to collect supplies is {otp.otp}",
                recipient_list=[student.email],
                from_email=settings.EMAIL_HOST_USER,
                fail_silently=True
            )
        except Exception as e:
            return Response({'message': e}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response({'message': 'otp sent'}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authed()
def submit_supply_give_otp(request, id):
    try:
        student = Student.objects.get(id=id)
        accommadation = Accommadation.objects.filter(student=student).first()
        if not accommadation:
            return Response({'message': 'No Accommodation found'}, status=status.HTTP_404_NOT_FOUND)
        otp = OTP.objects.filter(student=student).order_by('-id').first()
        if not otp:
            return Response({'message': 'No OTP found'}, status=status.HTTP_404_NOT_FOUND)
        if int(otp.otp) != request.data.get('otp'):
            return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        if otp.expires_at < timezone.now():
            return Response({'message': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        supplies = otp.supplies.all()
        accommadation.supplies_given.add(*supplies)
        accommadation.save()
        otp.delete()
        return Response({'message': 'OTP verified'}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authed()
def request_supply_return_otp(request, id):
    try:
        student = Student.objects.get(id=id)
        accommadation = Accommadation.objects.filter(student=student).first()
        if not accommadation:
            return Response({'message': 'No Accommodation found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        supply_ids = data.get('Item IDs')
        supply_objects = Supply.objects.filter(id__in=supply_ids).all()
        otp = OTP.objects.create(
            student=student,
            otp=''.join([str(random.randint(0, 9)) for _ in range(6)]),
            expires_at=datetime.now() + timedelta(minutes=60)
        )
        otp.supplies.add(*supply_objects)
        otp.save()
        # email otp to student
        try:
            send_mail(
                subject='Supplies OTP',
                message=f"Your OTP to return supplies is {otp.otp}",
                recipient_list=[student.email],
                from_email=settings.EMAIL_HOST_USER,
                fail_silently=True
            )
        except Exception as e:
            return Response({'message': e}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({'message': 'otp sent'}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authed()
def submit_supply_return_otp(request, id):
    try:
        student = Student.objects.get(id=id)
        accommadation = Accommadation.objects.filter(student=student).first()
        if not accommadation:
            return Response({'message': 'No Accommodation found'}, status=status.HTTP_404_NOT_FOUND)
        otp = OTP.objects.filter(student=student).order_by('-id').first()
        if not otp:
            return Response({'message': 'No OTP found'}, status=status.HTTP_404_NOT_FOUND)
        print(otp.otp, type(otp.otp))
        print(request.data.get('otp'), type(request.data.get('otp')))
        if int(otp.otp) != request.data.get('otp'):
            return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        if otp.expires_at < timezone.now():
            return Response({'message': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        supplies = otp.supplies.all()
        accommadation.supplies_returned.add(*supplies)
        accommadation.save()
        otp.delete()
        return Response({'message': 'OTP verified'}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authed()
def get_profile(request, code):
    try:
        qr = QrCode.objects.get(code=code)
        student = qr.student
        user = User.objects.filter(email=student.email).first()
        if not user:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'name': user.last_name if user.first_name[0] == '2' else user.first_name + ' ' + user.last_name,
            'email': user.email,
            'id': student.id

        }, status=status.HTTP_200_OK)
    except QrCode.DoesNotExist:
        return Response({'message': 'Invalid QR code'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authed()
def get_checkin_status(request, id):
    try:
        student = Student.objects.get(id=id)
        accommadation = Accommadation.objects.filter(student=student).first()
        if not accommadation:
            return Response({'message': 'No Accommodation found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            'CheckIn': True if accommadation.check_in else False,
            'CheckOut': True if accommadation.check_out else False,
            'CheckIn Time': accommadation.check_in.timestamp() * 1000 if accommadation.check_in else None,
            'CheckOut Time': accommadation.check_out.timestamp() * 1000 if accommadation.check_out else None
        })
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authed()
def get_student_supplies(request, id):
    try:
        student = Student.objects.get(id=id)
        accommadation = Accommadation.objects.prefetch_related(
            'supplies_given', 'supplies_returned').filter(student=student).first()
        if not accommadation:
            return Response({'message': 'No Accommodation found'}, status=status.HTTP_404_NOT_FOUND)
        supplies = Supply.objects.all()
        return Response([
            {
                'Item Name': supply.name,
                'Item ID': supply.id,
                'isProvided': True if supply in accommadation.supplies_given.all() else False,
                'isReturned': True if supply in accommadation.supplies_returned.all() else False
            } for supply in supplies
        ])
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authed()
def get_volunteer_info(request):
    user = request.user
    print(user)
    volunteer = AccomVolunteer.objects.filter(user=user).first()
    if not volunteer:
        return Response({'message': 'No volunteer found'}, status=status.HTTP_404_NOT_FOUND)
    return Response({
        "name": f"{user.first_name} {user.last_name}",
        "email": user.email,
        "hostels": [hostel.name for hostel in volunteer.hostels.all()]
    })
