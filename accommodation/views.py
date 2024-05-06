from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import Student, QrCode
from utils.decorators import authed
from .models import Accommadation, Hostel, Supply, OTP, AccomVolunteer, Mess
from datetime import datetime, timedelta
import random
from .decorators import has_accom_perms


@api_view(['POST'])
@has_accom_perms(['add_hostel'])
def add_hostel(request):
    data = request.data
    name = data.get('name')
    if Hostel.objects.filter(name=name).exists():
        return Response({'message': 'Hostel already exists'}, status=status.HTTP_400_BAD_REQUEST)
    Hostel.objects.create(name=name)
    return Response({'message': 'Hostel created'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@has_accom_perms(['add_supply'])
def add_supply(request):
    data = request.data
    name = data.get('name')
    if Supply.objects.filter(name=name).exists():
        return Response({'message': 'Supply already exists'}, status=status.HTTP_400_BAD_REQUEST)
    Supply.objects.create(name=name)
    return Response({'message': 'Supply created'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@has_accom_perms(['add_mess'])
def add_mess(request):
    data = request.data
    name = data.get('name')
    floor = data.get('floor')
    caterer = data.get('caterer')
    if Mess.objects.filter(name=name, caterer=caterer, floor=floor).exists():
        return Response({'message': 'Mess already exists'}, status=status.HTTP_400_BAD_REQUEST)
    Mess.objects.create(name=name, floor=floor, caterer=caterer)
    return Response({'message': 'Mess created'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@has_accom_perms(['view_mess'])
def get_all_mess(request):
    mess = Mess.objects.all()
    return Response([{
        'name': mess.name,
        'floor': mess.floor,
        'caterer': mess.caterer
    } for mess in mess], status=status.HTTP_200_OK)


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
def get_all_hostels(request):
    hostels = Hostel.objects.all()
    return Response([{
        'name': hostel.name,
        'id': hostel.id
    } for hostel in hostels])


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
# @has_perms(['change_accommadation'])
@authed()
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
# @has_perms(['change_accommadation'])
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
        old_otps = OTP.objects.filter(student=student).all().delete()
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
        old_otps = OTP.objects.filter(student=student).all().delete()
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
        accommadation.supplies_checked_out = True
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


@api_view(['GET'])
@authed()
def upcoming_students(request, id):
    try:
        hostel = Hostel.objects.get(id=id)
    except Hostel.DoesNotExist:
        return Response({'message': 'Hostel not found'}, status=status.HTTP_404_NOT_FOUND)
    accom = Accommadation.objects.filter(
        check_in__isnull=True, hostel=hostel).all()
    students = []
    for acc in accom:
        student = acc.student
        user = User.objects.filter(email=student.email).first()
        if not user:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        students.append({
            'name': user.last_name if user.first_name[0] == '2' else user.first_name + ' ' + user.last_name,
            'email': user.email,
            'roomNo': acc.room
        })
    return Response(students, status=status.HTTP_200_OK)


@api_view(['GET'])
@authed()
def can_check_out(request, id):
    try:
        student = Student.objects.get(id=id)
        accommadation = Accommadation.objects.filter(student=student).first()
        if not accommadation:
            return Response({'message': 'No Accommodation found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'canCheckOut': accommadation.supplies_checked_out}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
