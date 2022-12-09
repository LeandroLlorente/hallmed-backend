from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import Medico, Seguro
import json
from ..serializers import SeguroSerializer

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_seguro(request):
    tipo = Seguro.objects.all().order_by('id')
    tipoSerializer = SeguroSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)