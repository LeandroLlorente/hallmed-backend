from django.http.response import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import TipoExamen
from ..serializers import TipoExamenSerializer
import json
from django.db import IntegrityError
from rest_framework import status
from django.db import transaction

#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_tipoexamen(request):
    tipo = TipoExamen.objects.filter().order_by('id')
    tipoSerializer = TipoExamenSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_tipoexamen(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            obj = TipoExamen()
            obj.tipo_examen = payload["tipo_examen"]
            obj.categoria = payload["categoria"]
            obj.save()
            tabla = TipoExamen.objects.filter().order_by('id')
            tabla_serializer = TipoExamenSerializer(tabla, many=True)
            return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return JsonResponse({'error': 'There is already a record with that data'}, safe=False,
                                status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_tipoexamen(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            obj = TipoExamen.objects.get(pk=int(payload["id"]))
            obj.tipo_examen = payload["tipo_examen"]
            obj.categoria = payload["categoria"]

            obj.save()
            tabla = TipoExamen.objects.filter().order_by('id')
            tabla_serializer = TipoExamenSerializer(tabla, many=True)
            return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except TipoExamen.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return JsonResponse({'error': 'There is already a record with that data'}, safe=False,
                                status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def delete_tipoexamen(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            with transaction.atomic():
                obj = TipoExamen.objects.get(pk=int(payload["id"]))
                obj.delete()
                tabla = TipoExamen.objects.filter().order_by('id')
                tabla_serializer = TipoExamenSerializer(tabla, many=True)
                return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except TipoExamen.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return JsonResponse({'error': 'There is already a record with that data'}, safe=False,
                                status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)