from django.db.models import Q
from django.http.response import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import Resultados, Orden, Consulta, Actividad, Sucursal, UnidadMedica
from ..serializers import MedicamentoSerializer
import json
from django.db import IntegrityError
from rest_framework import status
from django.db import transaction
import math

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_actividades_consultas(request):
    if request.method == 'POST':
        payload = json.loads(request.body)

        cantRegistros = 5
        paginaActual = payload["pagina"]
        if paginaActual < 1:
            return JsonResponse([], safe=False)
        limiteIni = (paginaActual - 1) * cantRegistros
        limiteSup = (paginaActual * cantRegistros)
        print("I:"+str(limiteIni)+" S:"+str(limiteSup))

        # los filtros
        filtrosAplicar = []
        id_medico = payload["id_medico"]
        filtrosAplicar.append(Q(medico=id_medico))

        paciente = payload["paciente"]
        if paciente is not None and paciente != "":
            filtrosAplicar.append(Q(paciente=paciente))

        cantTotal = len(Consulta.objects.filter(*filtrosAplicar))
        cantPaginas = math.ceil(cantTotal / cantRegistros)
        print("cant:"+str(cantTotal)+" "+"cantPag:"+str(cantPaginas))
        actividades = []
        for consulta in Consulta.objects.filter(*filtrosAplicar).order_by('-id')[limiteIni:limiteSup]:
            actividad_temp = {}
            actividad_temp["id_consulta"] = consulta.id
            actividad_temp["fecha_consulta"] = consulta.fecha.strftime("%d/%m/%Y")
            actividad_temp["paciente"] = consulta.paciente.nombre + " " +consulta.paciente.apellidos
            actividad_temp["diagnostico"] = consulta.diagnostico.cie
            actividad_temp["cant_paginas"] = cantPaginas

            lista_actividades = []

            for actividad in Actividad.objects.filter(consulta=consulta.id).order_by('id'):
                actividad_ele = {}
                actividad_ele["tipo_actividad"] = actividad.tipoActividad
                actividad_ele["nombre_entidad"] = actividad.nombreEntidad
                actividad_ele["fecha_hora"] = actividad.fechaHora.strftime("%H:%M - %d/%m/%Y")
                lista_actividades.append(actividad_ele)
            actividad_temp["lista_actividades"] = lista_actividades

            actividades.append(actividad_temp)
        return JsonResponse(actividades, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_actividades(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        cantRegistros = 5
        paginaActual = payload["pagina"]
        if paginaActual < 1:
            return JsonResponse([], safe=False)
        limiteIni = (paginaActual - 1) * cantRegistros
        limiteSup = (paginaActual * cantRegistros)

        # los filtros
        filtrosAplicar = []
        id_medico = payload["id_medico"]
        filtrosAplicar.append(Q(consulta__medico=id_medico))

        fecha = payload["fecha"]
        if fecha is not None and fecha != "":
            filtrosAplicar.append(Q(consulta__fecha=fecha))

        cantTotal = len(Actividad.objects.filter(*filtrosAplicar))
        cantPaginas = math.ceil(cantTotal / cantRegistros)

        actividades = []
        for actividad in Actividad.objects.filter(*filtrosAplicar).order_by('id')[limiteIni:limiteSup]:
            actividad_ele = {}
            actividad_ele["tipo_actividad"] = actividad.tipoActividad
            actividad_ele["nombre_entidad"] = actividad.nombreEntidad
            actividad_ele["fecha_hora"] = actividad.fechaHora.strftime("%H:%M - %d/%m/%Y")
            actividad_ele["paciente"] = actividad.paciente.nombre + " " + actividad.paciente.apellidos
            actividad_ele["paciente_foto"] = str(actividad.paciente.foto)
            actividad_ele["genero"] = actividad.paciente.genero
            actividad_ele["diagnostico"] = actividad.consulta.diagnostico.cie
            actividad_ele["cant_paginas"] = cantPaginas

            actividades.append(actividad_ele)
        return JsonResponse(actividades, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)