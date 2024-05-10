from django.shortcuts import render
from core.models import Event
from utils.decorators import authed, has_perms
from rest_framework.response import Response
from rest_framework import status
from .models import SrVolunteer
from rest_framework.decorators import api_view


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


@api_view(['POST'])
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
