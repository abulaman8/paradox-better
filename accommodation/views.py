from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from core.models import Student, QrCode
from utils.decorators import has_perms, authed
from .models import Accommadation
from .serializers import AccommodationSerializer


@api_view(['GET'])
@authed()
def get_user_accommodation(request):
    data = request.GET
    code = data.get('code')
    try:
        qr = QrCode.objects.get(code=code)
        student = qr.student
        accommodation = Accommadation.objects.get(student=student)
        serializer = AccommodationSerializer(accommodation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except QrCode.DoesNotExist:
        return Response({'message': 'Invalid QR code'}, status=400)
    except Accommadation.DoesNotExist:
        return Response({'message': 'No accommodation found'}, status=404)


@api_view(['PUT'])
@has_perms(['change_accommadation'])
def check_in(request):
    data = request.data
