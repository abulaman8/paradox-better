from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from core.models import Student, Event, Department
from core.serializers import EventSerializer
from .models import Round, SomeDude
from .serializers import RoundSerializer
from utils.decorators import has_perms
from .decorators import has_event_perms
from datetime import datetime


@api_view(['POST'])
@has_event_perms(['add_event'])
def add_event(request):
    user = request.user
    data = request.data
    dept_id = data.get('dept_id')
    event_name = data.get('event_name')
    head_email = data.get('head_email')
    is_team_event = data.get('is_team_event')
    max_team_size = data.get('max_team_size')
    min_team_size = data.get('min_team_size')
    max_participants = data.get('max_participants')
    fee = data.get('fee')
    description = data.get('description')
    location = data.get('location')
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d %H:%M:%S')
    registration_start_date = datetime.strptime(
        data.get('registration_start_date'), '%Y-%m-%d %H:%M:%S')
    registration_end_date = datetime.strptime(
        data.get('registration_end_date'), '%Y-%m-%d %H:%M:%S')
    try:
        user = User.objects.get(email=head_email)
        dept = Department.objects.get(id=dept_id)
        event = Event.objects.create(
            name=event_name,
            head=user,
            department=dept,
            is_team_event=is_team_event,
            max_team_size=max_team_size,
            min_team_size=min_team_size,
            max_participants=max_participants,
            fee=fee if fee else 0,
            description=description,
            location=location,
            start_date=start_date,
            end_date=end_date,
            registration_start_date=registration_start_date,
            registration_end_date=registration_end_date
        )
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except User.DoesNotExist:
        return Response({'message': 'User with the provided email not found'}, status=status.HTTP_400_BAD_REQUEST)
    except Department.DoesNotExist:
        return Response({'message': 'Department with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@has_event_perms(['change_event'])
def edit_event(request, event_id):
    data = request.data
    event = Event.objects.get(id=event_id)
    event_name = data.get('event_name')
    head_email = data.get('head_email')
    is_team_event = data.get('is_team_event')
    max_team_size = data.get('max_team_size')
    min_team_size = data.get('min_team_size')
    max_participants = data.get('max_participants')
    fee = data.get('fee')
    description = data.get('description')
    location = data.get('location')
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d %H:%M:%S')
    registration_start_date = datetime.strptime(
        data.get('registration_start_date'), '%Y-%m-%d %H:%M:%S')
    registration_end_date = datetime.strptime(
        data.get('registration_end_date'), '%Y-%m-%d %H:%M:%S')
    try:
        user = User.objects.get(email=head_email)
        event.name = event_name
        event.head = user
        event.is_team_event = is_team_event
        event.max_team_size = max_team_size
        event.min_team_size = min_team_size
        event.max_participants = max_participants
        event.fee = fee if fee else 0
        event.description = description
        event.location = location
        event.start_date = start_date
        event.end_date = end_date
        event.registration_start_date = registration_start_date
        event.registration_end_date = registration_end_date
        event.is_approved = False
        event.save()
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'message': 'User with the provided email not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@has_event_perms(['delete_event'])
def delete_event(request):
    data = request.data
    event_id = data.get('event_id')
    try:
        event = Event.objects.get(id=event_id)
        event.delete()
        return Response({'message': 'Event deleted successfully'}, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@has_event_perms(['approve_event'])
def approve_event(request):
    data = request.data
    event_id = data.get('event_id')
    try:
        event = Event.objects.get(id=event_id)
        event.is_approved = True
        event.save()
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@has_event_perms(['approve_event'])
def disapprove_event(request):
    data = request.data
    event_id = data.get('event_id')
    try:
        event = Event.objects.get(id=event_id)
        event.is_approved = False
        event.save()
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([OAuth2Authentication])
def view_dept_events(request):
    data = request.GET
    dept_id = data.get('dept_id')
    try:
        dept = Department.objects.get(id=dept_id)
        events = Event.objects.filter(department=dept)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Department.DoesNotExist:
        return Response({'message': 'Department with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([OAuth2Authentication])
def view_all_events(request):
    events = Event.objects.all()
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([OAuth2Authentication])
def view_event(request):
    data = request.GET
    event_id = data.get('event_id')
    try:
        event = Event.objects.get(id=event_id)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@has_perms(['change_event'])
def add_round(request):
    data = request.data
    event_id = data.get('event_id')
    round_name = data.get('round_name')
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d %H:%M:%S')
    location = data.get('location')
    description = data.get('description')
    try:
        event = Event.objects.get(id=event_id)
        round = Round.objects.create(
            event=event,
            name=round_name,
            start_time=start_date,
            end_time=end_date,
            location=location,
            description=description
        )
        serializer = RoundSerializer(round)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@has_perms(['change_event'])
def edit_round(request):
    data = request.data
    event_id = data.get('event_id')
    round_id = data.get('round_id')
    round_name = data.get('round_name')
    start_time = datetime.strptime(data.get('start_date'), '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(data.get('end_date'), '%Y-%m-%d %H:%M:%S')
    location = data.get('location')
    description = data.get('description')
    try:
        round = Round.objects.get(id=round_id)
        round.name = round_name
        round.start_time = start_time
        round.end_time = end_time
        round.location = location
        round.description = description
        round.save()
        serializer = RoundSerializer(round)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Round.DoesNotExist:
        return Response({'message': 'Round with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@has_perms(['change_event'])
def delete_round(request):
    data = request.data
    event_id = data.get('event_id')
    round_id = data.get('round_id')
    try:
        round = Round.objects.get(id=round_id)
        round.delete()
        return Response({'message': 'Round deleted successfully'}, status=status.HTTP_200_OK)
    except Round.DoesNotExist:
        return Response({'message': 'Round with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)
