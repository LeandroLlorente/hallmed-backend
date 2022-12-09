from django.http.response import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import GrupoExamen, Examen, UnidadMedica
from ..serializers import GrupoExamenSerializer
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
def list_examen_by_grupo(request):
    payload = json.loads(request.body)
    id_grupo = payload["id_grupo"]
    tipo = GrupoExamen.objects.filter(grupo=id_grupo).order_by('id')
    tipoSerializer = GrupoExamenSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_examen_by_grupo_nombre(request):
    payload = json.loads(request.body)
    id_grupo = payload["id_grupo"]
    examenesGrupo = []
    for examGrupo_temp in GrupoExamen.objects.filter(grupo=id_grupo).order_by('id'):
        examenesGrupo_ele = {}
        examenesGrupo_ele["id"] = examGrupo_temp.id
        examenesGrupo_ele["examen_id"] = examGrupo_temp.examen.id
        examenesGrupo_ele["examen"] = examGrupo_temp.examen.examen
        examenesGrupo_ele["grupo"] = examGrupo_temp.grupo.id
        examenesGrupo_ele["precio"] = examGrupo_temp.precio
        examenesGrupo_ele["preparacion"] = examGrupo_temp.preparacion
        examenesGrupo_ele["entrega"] = examGrupo_temp.entrega
        examenesGrupo_ele["referencia"] = examGrupo_temp.referencia
        examenesGrupo.append(examenesGrupo_ele)
    return JsonResponse(examenesGrupo, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def listexamen_grupo(request):
    payload = json.loads(request.body)
    # id_grupo = payload["id_grupo"]
    id_grupo = request.user.id
    examenesGrupo = []
    for examGrupo_temp in GrupoExamen.objects.filter(grupo=id_grupo).order_by('id'):
        examenesGrupo_ele = {}
        examenesGrupo_ele["id"] = examGrupo_temp.id
        examenesGrupo_ele["examen_id"] = examGrupo_temp.examen.id
        examenesGrupo_ele["examen"] = examGrupo_temp.examen.examen
        examenesGrupo_ele["grupo"] = examGrupo_temp.grupo.id
        examenesGrupo_ele["precio"] = examGrupo_temp.precio
        examenesGrupo_ele["preparacion"] = examGrupo_temp.preparacion
        examenesGrupo_ele["entrega"] = examGrupo_temp.entrega
        examenesGrupo_ele["referencia"] = examGrupo_temp.referencia
        examenesGrupo.append(examenesGrupo_ele)
    return JsonResponse(examenesGrupo, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_examen_grupo(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_grupo = payload["id_grupo"]
        examenes_activos = json.loads(payload["examenes_activos"])
        examenes_no_activos = json.loads(payload["examenes_no_activos"])

        # try:
        with transaction.atomic():
            # borra los examenes que no estan activos
            for examen in examenes_no_activos:
                if GrupoExamen.objects.filter(examen=examen, grupo=id_grupo).count() > 0:
                    grupoExamen_delete = GrupoExamen.objects.get(examen=examen, grupo=id_grupo)
                    grupoExamen_delete.delete()

            # inserta los examenes que estan activos
            for examen in examenes_activos:
                if GrupoExamen.objects.filter(examen=examen, grupo=id_grupo).count() == 0:
                    grupoExamen_add = GrupoExamen()
                    grupoExamen_add.examen = Examen.objects.get(id=examen)
                    grupoExamen_add.grupo = UnidadMedica.objects.get(id=id_grupo)
                    grupoExamen_add.save()

            tipo = GrupoExamen.objects.filter(grupo=id_grupo).order_by('id')
            tipoSerializer = GrupoExamenSerializer(tipo, many=True)
            return JsonResponse(tipoSerializer.data, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_examen_grupo_detalles(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id = payload["id"]
        precio = payload["precio"]
        preparacion = payload["preparacion"]
        entrega = payload["entrega"]
        referencia = payload["referencia"]

        examenGrupo = GrupoExamen.objects.get(id=id)
        examenGrupo.precio = precio
        examenGrupo.preparacion = preparacion
        examenGrupo.entrega = entrega
        examenGrupo.referencia = referencia
        examenGrupo.save()

        examenesGrupo = []
        for examGrupo_temp in GrupoExamen.objects.filter(grupo=examenGrupo.grupo.id).order_by('id'):
            examenesGrupo_ele = {}
            examenesGrupo_ele["id"] = examGrupo_temp.id
            examenesGrupo_ele["examen_id"] = examGrupo_temp.examen.id
            examenesGrupo_ele["examen"] = examGrupo_temp.examen.examen
            examenesGrupo_ele["grupo"] = examGrupo_temp.grupo.id
            examenesGrupo_ele["precio"] = examGrupo_temp.precio
            examenesGrupo_ele["preparacion"] = examGrupo_temp.preparacion
            examenesGrupo_ele["entrega"] = examGrupo_temp.entrega
            examenesGrupo_ele["referencia"] = examGrupo_temp.referencia
            examenesGrupo.append(examenesGrupo_ele)
        return JsonResponse(examenesGrupo, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


