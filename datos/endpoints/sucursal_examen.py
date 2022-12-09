from django.http.response import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import SucursalExamen, Examen, Sucursal
from ..serializers import SucursalExamenSerializer
import json
from django.db import IntegrityError
from rest_framework import status
from django.db import transaction
from django.contrib.auth.models import User, Group
from django.db.models import Q
import random, string
from psycopg2._psycopg import ProgrammingError


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_examen_by_sucursal(request):
    payload = json.loads(request.body)
    id_sucursal = payload["id_sucursal"]
    tipo = SucursalExamen.objects.filter(sucursal=id_sucursal).order_by('id')
    tipoSerializer = SucursalExamenSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_examen_by_sucursal_nombre(request):
    payload = json.loads(request.body)
    id_sucursal = payload["id_sucursal"]
    examenesSucursal = []
    for examSucursal_temp in SucursalExamen.objects.filter(sucursal=id_sucursal).order_by('id'):
        examenesSucursal_ele = {}
        examenesSucursal_ele["id"] = examSucursal_temp.id
        examenesSucursal_ele["examen_id"] = examSucursal_temp.examen.id
        examenesSucursal_ele["examen"] = examSucursal_temp.examen.examen
        examenesSucursal_ele["sucursal"] = examSucursal_temp.sucursal.id
        examenesSucursal_ele["precio"] = examSucursal_temp.precio
        examenesSucursal_ele["preparacion"] = examSucursal_temp.preparacion
        examenesSucursal_ele["entrega"] = examSucursal_temp.entrega
        examenesSucursal_ele["referencia"] = examSucursal_temp.referencia
        examenesSucursal.append(examenesSucursal_ele)
    return JsonResponse(examenesSucursal, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_examen_sucursal(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_sucursal = payload["id_sucursal"]
        examenes_activos = json.loads(payload["examenes_activos"])
        examenes_no_activos = json.loads(payload["examenes_no_activos"])

        # try:
        with transaction.atomic():
            # borra los examenes que no estan activos
            for examen in examenes_no_activos:
                if SucursalExamen.objects.filter(examen=examen, sucursal=id_sucursal).count() > 0:
                    sucuralExamen_delete = SucursalExamen.objects.get(examen=examen, sucursal=id_sucursal)
                    sucuralExamen_delete.delete()

            # inserta los examenes que estan activos
            for examen in examenes_activos:
                if SucursalExamen.objects.filter(examen=examen, sucursal=id_sucursal).count() == 0:
                    sucuralExamen_add = SucursalExamen()
                    sucuralExamen_add.examen = Examen.objects.get(id=examen)
                    sucuralExamen_add.sucursal = Sucursal.objects.get(id=id_sucursal)
                    sucuralExamen_add.save()

            tipo = SucursalExamen.objects.filter(sucursal=id_sucursal).order_by('id')
            tipoSerializer = SucursalExamenSerializer(tipo, many=True)
            return JsonResponse(tipoSerializer.data, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_examen_sucursal_detalles(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id = payload["id"]
        precio = payload["precio"]
        preparacion = payload["preparacion"]
        entrega = payload["entrega"]
        referencia = payload["referencia"]

        examenSucursal = SucursalExamen.objects.get(id=id)
        examenSucursal.precio = precio
        examenSucursal.preparacion = preparacion
        examenSucursal.entrega = entrega
        examenSucursal.referencia = referencia
        examenSucursal.save()

        examenesSucursal = []
        for examSucursal_temp in SucursalExamen.objects.filter(sucursal=examenSucursal.sucursal.id).order_by('id'):
            examenesSucursal_ele = {}
            examenesSucursal_ele["id"] = examSucursal_temp.id
            examenesSucursal_ele["examen_id"] = examSucursal_temp.examen.id
            examenesSucursal_ele["examen"] = examSucursal_temp.examen.examen
            examenesSucursal_ele["sucursal"] = examSucursal_temp.sucursal.id
            examenesSucursal_ele["precio"] = examSucursal_temp.precio
            examenesSucursal_ele["preparacion"] = examSucursal_temp.preparacion
            examenesSucursal_ele["entrega"] = examSucursal_temp.entrega
            examenesSucursal_ele["referencia"] = examSucursal_temp.referencia
            examenesSucursal.append(examenesSucursal_ele)
        return JsonResponse(examenesSucursal, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


