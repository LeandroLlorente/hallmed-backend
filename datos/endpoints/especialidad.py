from django.http.response import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import Especialidad
from ..serializers import EspecialidadSerializer
import json
from django.db import IntegrityError
from rest_framework import status
from django.db import transaction

#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_especialidad(request):
    especialidades = Especialidad.objects.all().order_by('id')
    especialidadSerializer = EspecialidadSerializer(especialidades, many=True)
    return JsonResponse(especialidadSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_especialidad(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            obj = Especialidad()
            obj.especialidad = payload["especialidad"]

            obj.save()
            tabla = Especialidad.objects.filter().order_by('id')
            tabla_serializer = EspecialidadSerializer(tabla, many=True)
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
def update_especialidad(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            obj = Especialidad.objects.get(pk=int(payload["id"]))
            obj.especialidad = payload["especialidad"]

            obj.save()
            tabla = Especialidad.objects.filter().order_by('id')
            tabla_serializer = EspecialidadSerializer(tabla, many=True)
            return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except Especialidad.DoesNotExist as e:
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
def delete_especialidad(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            with transaction.atomic():
                obj = Especialidad.objects.get(pk=int(payload["id"]))
                obj.delete()
                tabla = Especialidad.objects.filter().order_by('id')
                tabla_serializer = EspecialidadSerializer(tabla, many=True)
                return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except Especialidad.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return JsonResponse({'error': 'There is already a record with that data'}, safe=False,
                                status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)