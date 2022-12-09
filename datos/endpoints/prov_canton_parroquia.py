from django.http.response import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import Provincia, Canton, Parroquia
from ..serializers import ProvinciaSerializer, CantonSerializer, ParroquiaSerializer

@api_view(['GET'])
def list_provincia(request):
    tipo = Provincia.objects.filter().order_by('id')
    tipoSerializer = ProvinciaSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


@api_view(['GET'])
def list_canton(request):
    tipo = Canton.objects.filter().order_by('id')
    tipoSerializer = CantonSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


@api_view(['GET'])
def list_parroquia(request):
    tipo = Parroquia.objects.filter().order_by('id')
    tipoSerializer = ParroquiaSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)