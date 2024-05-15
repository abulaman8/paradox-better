from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import Student, QrCode
from fest.models import AccomodationRegistration
from utils.decorators import authed
from .models import Accommadation, Hostel, Supply, OTP, AccomVolunteer, Mess
from datetime import datetime, timedelta
import random
from .decorators import has_accom_perms
from io import StringIO
import csv


@api_view(['POST'])
@has_accom_perms(['add_hostel'])
def add_hostel(request):
    data = request.data
    name = data.get('name')
    if Hostel.objects.filter(name=name).exists():
        return Response({'message': 'Hostel already exists'}, status=status.HTTP_400_BAD_REQUEST)
    Hostel.objects.create(name=name)
    return Response({'message': 'Hostel created'}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@has_accom_perms(['change_hostel'])
def edit_hostel(request, id):
    data = request.data
    name = data.get('name')
    try:
        Hostel.objects.filter(id=id).update(name=name)
        return Response({'message': 'Hostel edited'}, status=status.HTTP_200_OK)
    except Hostel.DoesNotExist:
        return Response({'message': 'Hostel not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@has_accom_perms(['delete_hostel'])
def delete_hostel(request, id):
    Hostel.objects.filter(id=id).delete()
    return Response({'message': 'Hostel deleted'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@has_accom_perms(['add_supply'])
def add_supply(request):
    data = request.data
    name = data.get('name')
    if Supply.objects.filter(name=name).exists():
        return Response({'message': 'Supply already exists'}, status=status.HTTP_400_BAD_REQUEST)
    Supply.objects.create(name=name)
    return Response({'message': 'Supply created'}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@has_accom_perms(['change_supply'])
def edit_supply(request, id):
    data = request.data
    name = data.get('name')
    try:
        Supply.objects.filter(id=id).update(name=name)
        return Response({'message': 'Supply edited'}, status=status.HTTP_200_OK)
    except Supply.DoesNotExist:
        return Response({'message': 'Supply not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@has_accom_perms(['delete_supply'])
def delete_supply(request, id):
    Supply.objects.filter(id=id).delete()
    return Response({'message': 'Supply deleted'}, status=status.HTTP_200_OK)


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


@api_view(['PUT'])
@has_accom_perms(['change_mess'])
def edit_mess(request, id):
    data = request.data
    name = data.get('name')
    floor = data.get('floor')
    caterer = data.get('caterer')
    try:
        Mess.objects.filter(id=id).update(
            name=name, floor=floor, caterer=caterer)
        return Response({'message': 'Mess edited'}, status=status.HTTP_200_OK)
    except Mess.DoesNotExist:
        return Response({'message': 'Mess not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@has_accom_perms(['delete_mess'])
def delete_mess(request, id):
    Mess.objects.filter(id=id).delete()
    return Response({'message': 'Mess deleted'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@has_accom_perms(['view_mess'])
def get_all_mess(request):
    mess = Mess.objects.all()
    return Response([{
        'id': mess.id,
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
        "hostels": [{"id": hostel.id, "name": hostel.name} for hostel in volunteer.hostels.all()]
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


@api_view(['GET'])
@authed()
def get_hostel_stats(request, id):
    try:
        hostel = Hostel.objects.get(id=id)
    except Hostel.DoesNotExist:
        return Response({'message': 'Hostel not found'}, status=status.HTTP_404_NOT_FOUND)
    accom = Accommadation.objects.prefetch_related('student').filter(
        hostel=hostel).all()
    data = {}
    data["checked_in"] = []
    data["checked_out"] = []
    data["pending"] = []
    for acc in accom:
        if acc.check_out:
            user = User.objects.filter(email=acc.student.email).first()
            if not user:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            data["checked_out"].append({
                'name': user.last_name if user.first_name[0] == '2' else user.first_name + ' ' + user.last_name,
                'email': acc.student.email
            })
        elif acc.check_in:
            user = User.objects.filter(email=acc.student.email).first()
            if not user:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            data["checked_in"].append({
                'name': user.last_name if user.first_name[0] == '2' else user.first_name + ' ' + user.last_name,
                'email': acc.student.email
            })
        else:
            user = User.objects.filter(email=acc.student.email).first()
            if not user:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            data["pending"].append({
                'name': user.last_name if user.first_name[0] == '2' else user.first_name + ' ' + user.last_name,
                'email': acc.student.email
            })
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@has_accom_perms(['add_accommadation'])
def add_accom_entry(request):
    data = request.data
    email = data.get('email')
    hostel_id = data.get('hostel')
    room = data.get('room')
    mess_id = data.get('mess')
    try:
        student = Student.objects.get(email=email)
        if not AccomodationRegistration.objects.filter(student=student).exists():
            return Response({'message': 'Accommodation not found'}, status=status.HTTP_404_NOT_FOUND)
        hostel = Hostel.objects.get(id=hostel_id)
        mess = Mess.objects.get(id=mess_id)
        exists = Accommadation.objects.filter(student=student).exists()
        if exists:
            return Response({'message': 'Accommodation already exists for this student'}, status=status.HTTP_400_BAD_REQUEST)
        accom = Accommadation.objects.create(
            student=student,
            room=room,
            mess=mess,
            hostel=hostel
        )
        return Response({'message': 'Accommodation added'}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    except Hostel.DoesNotExist:
        return Response({'message': 'Hostel not found'}, status=status.HTTP_404_NOT_FOUND)
    except Mess.DoesNotExist:
        return Response({'message': 'Mess not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@has_accom_perms(['change_accommadation'])
def edit_accom_entry(request):
    data = request.data
    email = data.get('email')
    hosel_id = data.get('hostel')
    room = data.get('room')
    mess_id = data.get('mess')
    try:
        student = Student.objects.get(email=email)
        if not AccomodationRegistration.objects.filter(student=student).exists():
            return Response({'message': 'Accommodation not found'}, status=status.HTTP_404_NOT_FOUND)
        accom = Accommadation.objects.filter(student=student).first()
        if not accom:
            return Response({'message': 'Accommodation not found'}, status=status.HTTP_404_NOT_FOUND)
        mess = Mess.objects.get(id=mess_id)
        hostel = Hostel.objects.get(id=hosel_id)

        accom.room = room
        accom.mess = mess
        accom.hostel = hostel
        accom.save()
        return Response({'message': 'Accommodation edited'}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    except Hostel.DoesNotExist:
        return Response({'message': 'Hostel not found'}, status=status.HTTP_404_NOT_FOUND)
    except Mess.DoesNotExist:
        return Response({'message': 'Mess not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@has_accom_perms(['delete_accommadation'])
def delete_accom_entry(request):
    data = request.data
    email = data.get('email')
    try:
        student = Student.objects.get(email=email)
        if not AccomodationRegistration.objects.filter(student=student).exists():
            return Response({'message': 'Accommodation not found'}, status=status.HTTP_404_NOT_FOUND)
        Accommadation.objects.filter(student=student).delete()
        return Response({'message': 'Accommodation deleted'}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@has_accom_perms(['add_accommadation'])
def mass_upload_accom(request):
    csv_file = request.FILES['file'].read().decode('utf-8')
    # columns - email, hostel, room, mess, floor, caterer
    hostel_dict = {}
    mess_dict = {}
    hostels = Hostel.objects.all()
    for host in hostels:
        hostel_dict[host.name] = host
    messes = Mess.objects.all()
    for mess in messes:
        mess_dict[f"{mess.name}{mess.floor}{mess.caterer}"] = mess
    accom_objects = []
    print(hostel_dict)
    print(mess_dict)
    with StringIO(csv_file) as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            try:
                student = Student.objects.get(email=row['email'])
                if not AccomodationRegistration.objects.filter(student=student).exists():
                    print(
                        f"Accommodation for student {row['email']} not found")
                    # continue
                    return Response({'message': f'Accommodation for student {row["email"]} not found'}, status=status.HTTP_404_NOT_FOUND)
                mess = mess_dict.get(
                    f"{row['mess']}{row['floor']}{row['caterer']}"
                )
                if not mess:
                    return Response({'message': f'Mess {row["mess"]} - {row["floor"]} - {row["caterer"]} not found'}, status=status.HTTP_404_NOT_FOUND)
                hostel = hostel_dict.get(row['hostel'])
                if not hostel:
                    return Response({'message': f'Hostel {row["hostel"]} not found'}, status=status.HTTP_404_NOT_FOUND)
                accom = Accommadation.objects.filter(student=student).first()
                if accom:
                    accom.room = row['room']
                    accom.mess = mess
                    accom.hostel = hostel
                    accom.save()
                else:
                    accom = Accommadation(
                        student=student,
                        room=row['room'],
                        mess=mess,
                        hostel=hostel
                    )
                    accom_objects.append(accom)
            except Student.DoesNotExist:
                return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
            except Hostel.DoesNotExist:
                return Response({'message': 'Hostel not found'}, status=status.HTTP_404_NOT_FOUND)
            except Mess.DoesNotExist:
                return Response({'message': 'Mess not found'}, status=status.HTTP_404_NOT_FOUND)
        Accommadation.objects.bulk_create(accom_objects)

    return Response({'message': 'Accommodation added'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@has_accom_perms(['view_accommadation'])
def get_accom_entries(request):
    accoms = Accommadation.objects.prefetch_related(
        'mess',
        'hostel',
        'student',
        'supplies_given',
        'supplies_returned'
    ).all()
    data = []
    for accom in accoms:
        data.append({
            'email': accom.student.email,
            'hostel': accom.hostel.name,
            'room': accom.room,
            'mess': f"{accom.mess.name}-{accom.mess.floor}-{accom.mess.caterer}",
            'check in': accom.check_in.strftime('%d-%m-%Y %H:%M:%S') if accom.check_in else None,
            'check out': accom.check_out.strftime('%d-%m-%Y %H:%M:%S') if accom.check_out else None,
            'supplies provided': ", ".join([supply.name for supply in accom.supplies_given.all()]),
            'supplies returned': ", ".join([supply.name for supply in accom.supplies_returned.all()])
        })
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@has_accom_perms(['add_accomvolunteer'])
def add_accom_volunteer(request):
    data = request.data
    email = data.get('email')
    hostels = data.get('hostels')
    try:
        hostel_objs = [Hostel.objects.get(id=id) for id in hostels]
        student = Student.objects.get(email=email)
        exists = AccomVolunteer.objects.filter(student=student).exists()
        if exists:
            return Response({'message': 'Accommodation volunteer already exists for this student'}, status=status.HTTP_400_BAD_REQUEST)

        accom = AccomVolunteer.objects.create(
            student=student
        )
        accom.hostels.set(hostel_objs)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    except Hostel.DoesNotExist:
        return Response({'message': 'Hostel not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@has_accom_perms(['delete_accomvolunteer'])
def delete_accom_volunteer(request):
    data = request.data
    email = data.get('email')
    try:
        student = Student.objects.get(email=email)
        if not AccomVolunteer.objects.filter(student=student).exists():
            return Response({'message': 'Accommodation volunteer not found'}, status=status.HTTP_404_NOT_FOUND)
        AccomVolunteer.objects.filter(student=student).delete()
        return Response({'message': 'Accommodation volunteer deleted'}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@has_accom_perms(['change_accomvolunteer'])
def edit_accom_volunteer(request):
    data = request.data
    email = data.get('email')
    hostels = data.get('hostels')
    try:
        student = Student.objects.get(email=email)
        if not AccomVolunteer.objects.filter(student=student).exists():
            return Response({'message': 'Accommodation volunteer not found'}, status=status.HTTP_404_NOT_FOUND)
        accom = AccomVolunteer.objects.filter(student=student).first()
        if not accom:
            return Response({'message': 'Accommodation volunteer not found'}, status=status.HTTP_404_NOT_FOUND)
        accom.hostels.set(hostels)
        accom.save()
        return Response({'message': 'Accommodation volunteer edited'}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    except Hostel.DoesNotExist:
        return Response({'message': 'Hostel not found'}, status=status.HTTP_404_NOT_FOUND)
