import math

from django.db.models import Q
from django.http.response import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from ..models import Examen, Orden, Sucursal, UnidadMedica, Resultados, Consulta, Actividad, Paciente, SucursalExamen, \
    GrupoExamen
from ..serializers import OrdenSerializer
import json
from django.db import IntegrityError
from rest_framework import status
from django.db import transaction

#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_examen_consulta(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_consulta = payload["id_consulta"]
        estado = Consulta.objects.get(pk=id_consulta).estado
        examenesConsulta = {}
        examenesConsulta["estado"] = estado
        if estado == "RESULTADOS":
            examenesConsulta["resultado"] = str(Resultados.objects.get(consulta=id_consulta).resultadosFile)
        else:
            examenesConsulta["resultado"] = ""
        examenes = []
        for orden in Orden.objects.filter(consulta=id_consulta).order_by('id'):
            examenes_ele = {}
            examenes_ele["id"] = orden.examen.id
            examenes_ele["examen"] = orden.examen.examen
            examenes.append(examenes_ele)
        examenesConsulta["examenes"] = examenes
        return JsonResponse(examenesConsulta, safe=False, status=status.HTTP_201_CREATED)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    tipoSerializer = OrdenSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def unidad_solicitada(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_consulta = payload["id_consulta"]
        id_paciente = payload["id_paciente"]
        tipo = payload["tipo"]
        id = payload["id"]
        precio_total = payload["precio_total"]
        for consulta in Orden.objects.filter(consulta=id_consulta):
            if tipo == "sucursal":
                consulta.tipo = "SUCURSAL"
                consulta.sucursal= Sucursal.objects.get(pk=id)
                precio_unitario=SucursalExamen.objects.filter(sucursal=id, examen=consulta.examen)[0].precio
                print(precio_unitario)
                # bucar en la sucursal el precio del examen por el id examen
            if tipo == "grupo":
                consulta.tipo= "GRUPO"
                consulta.grupo = UnidadMedica.objects.get(pk=id)
                precio_unitario = GrupoExamen.objects.filter(grupo=id, examen=consulta.examen)[0].precio
                print(precio_unitario)
            consulta.precio_unitario = precio_unitario
            consulta.precio_total = precio_total
            consulta.save()

        # adiciona las actividades
        actividad = Actividad()
        actividad.paciente = Paciente.objects.get(pk=payload["id_paciente"])
        actividad.consulta = Consulta.objects.get(pk=id_consulta)
        actividad.tipoActividad = "SELECCION_UM"
        if tipo == "sucursal":
            actividad.tipoEntidad = "SUCURSAL"
            actividad.entidad = id
            actividad.nombreEntidad = Sucursal.objects.get(pk=id).nombre
        if tipo == "grupo":
            actividad.tipoEntidad = "GRUPO"
            actividad.entidad = id
            actividad.nombreEntidad = UnidadMedica.objects.get(pk=id).nombre_comercial
        actividad.save()

        return JsonResponse({"msg": "ok"}, safe=False, status=status.HTTP_200_OK)

    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def ordenes_sucursal(request):
    if request.method == 'POST':
        cantRegistros = 5
        payload = json.loads(request.body)
        id_sucursal = payload["id_sucursal"]
        paginaActual = payload["pagina"]
        if paginaActual < 1:
            return JsonResponse([], safe=False)
        limiteIni= (paginaActual-1) * cantRegistros
        limiteSup = (paginaActual * cantRegistros)
        print("Ini:"+str(limiteIni)+" "+"Sup:"+str(limiteSup))
        ordenes = []
        idConsulta = -1
        cantTotal = len(Orden.objects.filter(sucursal=id_sucursal).distinct('consulta'))
        cantPaginas = math.ceil(cantTotal / cantRegistros)
        ordenTemp = {}
        for orden in Orden.objects.filter(sucursal=id_sucursal).order_by('-id'):
            examenesTemp = {}
            if idConsulta != orden.consulta.id:
                if ordenTemp != {}:
                    ordenes.append(ordenTemp)
                    ordenTemp = {}

                fecha = orden.consulta.fecha
                arrFecha = str(fecha).split("-")
                ordenTemp["fecha"] = arrFecha[2] + "/" + arrFecha[1] + "/" + arrFecha[0]
                ordenTemp["id_consulta"] = orden.consulta.id
                ordenTemp["id_sucursal"] = id_sucursal
                ordenTemp["estado"] = orden.consulta.estado
                ordenTemp["resultado"] = ""
                if len(Resultados.objects.filter(consulta=orden.consulta.id)) > 0:
                    ordenTemp["resultado"] = str(Resultados.objects.filter(consulta=orden.consulta.id)[0].resultadosFile)
                ordenTemp["id_medico"] = orden.consulta.medico.id
                ordenTemp["medico"] = orden.consulta.medico.nombre + " " + orden.consulta.medico.apellidos
                ordenTemp["medico_cedula"] = orden.consulta.medico.cedula
                ordenTemp["medico_codigo"] = orden.consulta.medico.codigo
                ordenTemp["id_paciente"] = orden.consulta.paciente.id
                ordenTemp["paciente"] = orden.consulta.paciente.nombre + " " + orden.consulta.paciente.apellidos
                ordenTemp["examenes"] = []
                # adiciona examenes
                examenesTemp["id"] = orden.id  # id de la orden
                examenesTemp["nombre"] = orden.examen.examen
                ordenTemp["examenes"].append(examenesTemp)
                idConsulta = orden.consulta.id
            else:
                # adiciona examenes
                examenesTemp["id"] = orden.id
                examenesTemp["nombre"] = orden.examen.examen
                ordenTemp["examenes"].append(examenesTemp)
            if limiteSup >= cantTotal - 1:
                ultimaPagina = True
            else:
                ultimaPagina = False
            ordenTemp["ultima_pagina"] = ultimaPagina
            ordenTemp["cant_paginas"] = cantPaginas

        if ordenTemp != {}:
            ordenes.append(ordenTemp)

        return JsonResponse(ordenes[limiteIni:limiteSup], safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def ordenes_grupo(request):
    if request.method == 'POST':
        cantRegistros = 5
        payload = json.loads(request.body)
        id_grupo = payload["id_grupo"]
        paginaActual = payload["pagina"]
        if paginaActual < 1:
            return JsonResponse([], safe=False)
        limiteIni= (paginaActual-1) * cantRegistros
        limiteSup = (paginaActual * cantRegistros)
        print("Ini:"+str(limiteIni)+" "+"Sup:"+str(limiteSup))
        ordenes = []
        idConsulta = -1
        cantTotal = len(Orden.objects.filter(grupo=id_grupo).distinct('consulta'))
        cantPaginas = math.ceil(cantTotal / cantRegistros)
        ordenTemp = {}

        for orden in Orden.objects.filter(grupo=id_grupo).order_by('-id'):
            examenesTemp = {}
            if idConsulta != orden.consulta.id:
                if ordenTemp != {}:
                    ordenes.append(ordenTemp)
                    ordenTemp = {}

                fecha = orden.consulta.fecha
                arrFecha = str(fecha).split("-")
                ordenTemp["fecha"] = arrFecha[2] + "/" + arrFecha[1] + "/" + arrFecha[0]
                ordenTemp["id_consulta"] = orden.consulta.id
                ordenTemp["id_grupo"] = id_grupo
                ordenTemp["estado"] = orden.consulta.estado
                ordenTemp["resultado"] = ""
                if len(Resultados.objects.filter(consulta=orden.consulta.id)) > 0:
                    ordenTemp["resultado"] = str(Resultados.objects.filter(consulta=orden.consulta.id)[0].resultadosFile)
                ordenTemp["id_medico"] = orden.consulta.medico.id
                ordenTemp["medico"] = orden.consulta.medico.nombre + " " + orden.consulta.medico.apellidos
                ordenTemp["medico_cedula"] = orden.consulta.medico.cedula
                ordenTemp["medico_codigo"] = orden.consulta.medico.codigo
                ordenTemp["id_paciente"] = orden.consulta.paciente.id
                ordenTemp["paciente"] = orden.consulta.paciente.nombre + " " + orden.consulta.paciente.apellidos
                ordenTemp["examenes"] = []
                # adiciona examenes
                examenesTemp["id"] = orden.id  # id de la orden
                examenesTemp["nombre"] = orden.examen.examen
                ordenTemp["examenes"].append(examenesTemp)
                idConsulta = orden.consulta.id
            else:
                # adiciona examenes
                examenesTemp["id"] = orden.id
                examenesTemp["nombre"] = orden.examen.examen
                ordenTemp["examenes"].append(examenesTemp)
            if limiteSup >= cantTotal - 1:
                ultimaPagina = True
            else:
                ultimaPagina = False
            ordenTemp["ultima_pagina"] = ultimaPagina
            ordenTemp["cant_paginas"] = cantPaginas

        if ordenTemp != {}:
            ordenes.append(ordenTemp)

        return JsonResponse(ordenes[limiteIni:limiteSup], safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def filtrar_ordenes_grupo(request):
    if request.method == 'POST':
        cantRegistros = 5
        payload = json.loads(request.body)
        id_grupo = payload["id_grupo"]
        paginaActual = payload["pagina"]
        if paginaActual < 1:
            return JsonResponse([], safe=False)
        limiteIni= (paginaActual-1) * cantRegistros
        limiteSup = (paginaActual * cantRegistros)
        print("Ini:"+str(limiteIni)+" "+"Sup:"+str(limiteSup))
        ordenes = []
        idConsulta = -1

        ordenTemp = {}

        # los filtros
        filtrosAplicar = []
        filtrosAplicar.append(Q(grupo=id_grupo))
        paciente = payload["paciente"]
        if paciente is not None and paciente != "":
            filtrosAplicar.append(Q(consulta__paciente__id=paciente))
        medico = payload["medico"]
        if medico is not None and medico != "":
            filtrosAplicar.append(Q(consulta__medico__id=medico))
        fecha = payload["fecha"]
        if fecha is not None and fecha != "":
            filtrosAplicar.append(Q(consulta__fecha=fecha))

        cantTotal = len(Orden.objects.filter(*filtrosAplicar).distinct('consulta'))
        cantPaginas = math.ceil(cantTotal / cantRegistros)

        for orden in Orden.objects.filter(*filtrosAplicar).order_by('-id'):
            examenesTemp = {}
            if idConsulta != orden.consulta.id:
                if ordenTemp != {}:
                    ordenes.append(ordenTemp)
                    ordenTemp = {}

                fecha = orden.consulta.fecha
                arrFecha = str(fecha).split("-")
                ordenTemp["fecha"] = arrFecha[2] + "/" + arrFecha[1] + "/" + arrFecha[0]
                ordenTemp["id_consulta"] = orden.consulta.id
                ordenTemp["id_grupo"] = id_grupo
                ordenTemp["estado"] = orden.consulta.estado
                ordenTemp["resultado"] = ""
                if len(Resultados.objects.filter(consulta=orden.consulta.id)) > 0:
                    ordenTemp["resultado"] = str(Resultados.objects.filter(consulta=orden.consulta.id)[0].resultadosFile)
                ordenTemp["id_medico"] = orden.consulta.medico.id
                ordenTemp["medico"] = orden.consulta.medico.nombre + " " + orden.consulta.medico.apellidos
                ordenTemp["medico_cedula"] = orden.consulta.medico.cedula
                ordenTemp["medico_codigo"] = orden.consulta.medico.codigo
                ordenTemp["id_paciente"] = orden.consulta.paciente.id
                ordenTemp["paciente"] = orden.consulta.paciente.nombre + " " + orden.consulta.paciente.apellidos
                ordenTemp["examenes"] = []
                # adiciona examenes
                examenesTemp["id"] = orden.id  # id de la orden
                examenesTemp["nombre"] = orden.examen.examen
                ordenTemp["examenes"].append(examenesTemp)
                idConsulta = orden.consulta.id
            else:
                # adiciona examenes
                examenesTemp["id"] = orden.id
                examenesTemp["nombre"] = orden.examen.examen
                ordenTemp["examenes"].append(examenesTemp)
            if limiteSup >= cantTotal - 1:
                ultimaPagina = True
            else:
                ultimaPagina = False
            ordenTemp["ultima_pagina"] = ultimaPagina
            ordenTemp["cant_paginas"] = cantPaginas

        if ordenTemp != {}:
            ordenes.append(ordenTemp)

        return JsonResponse(ordenes[limiteIni:limiteSup], safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def filtrar_ordenes_sucursal(request):
    if request.method == 'POST':
        cantRegistros = 5
        payload = json.loads(request.body)
        id_sucursal = payload["id_sucursal"]
        paginaActual = payload["pagina"]
        if paginaActual < 1:
            return JsonResponse([], safe=False)
        limiteIni= (paginaActual-1) * cantRegistros
        limiteSup = (paginaActual * cantRegistros)
        print("Ini:"+str(limiteIni)+" "+"Sup:"+str(limiteSup))
        ordenes = []
        idConsulta = -1

        ordenTemp = {}

        # los filtros
        filtrosAplicar = []
        filtrosAplicar.append(Q(sucursal=id_sucursal))
        paciente = payload["paciente"]
        if paciente is not None and paciente != "":
            filtrosAplicar.append(Q(consulta__paciente__id=paciente))
        medico = payload["medico"]
        if medico is not None and medico != "":
            filtrosAplicar.append(Q(consulta__medico__id=medico))
        fecha = payload["fecha"]
        if fecha is not None and fecha != "":
            filtrosAplicar.append(Q(consulta__fecha=fecha))

        cantTotal = len(Orden.objects.filter(*filtrosAplicar).distinct('consulta'))
        cantPaginas = math.ceil(cantTotal / cantRegistros)

        for orden in Orden.objects.filter(*filtrosAplicar).order_by('-id'):
            examenesTemp = {}
            if idConsulta != orden.consulta.id:
                if ordenTemp != {}:
                    ordenes.append(ordenTemp)
                    ordenTemp = {}

                fecha = orden.consulta.fecha
                arrFecha = str(fecha).split("-")
                ordenTemp["fecha"] = arrFecha[2] + "/" + arrFecha[1] + "/" + arrFecha[0]
                ordenTemp["id_consulta"] = orden.consulta.id
                ordenTemp["id_sucursal"] = id_sucursal
                ordenTemp["estado"] = orden.consulta.estado
                ordenTemp["resultado"] = ""
                if len(Resultados.objects.filter(consulta=orden.consulta.id)) > 0:
                    ordenTemp["resultado"] = str(Resultados.objects.filter(consulta=orden.consulta.id)[0].resultadosFile)
                ordenTemp["id_medico"] = orden.consulta.medico.id
                ordenTemp["medico"] = orden.consulta.medico.nombre + " " + orden.consulta.medico.apellidos
                ordenTemp["medico_cedula"] = orden.consulta.medico.cedula
                ordenTemp["medico_codigo"] = orden.consulta.medico.codigo
                ordenTemp["id_paciente"] = orden.consulta.paciente.id
                ordenTemp["paciente"] = orden.consulta.paciente.nombre + " " + orden.consulta.paciente.apellidos
                ordenTemp["examenes"] = []
                # adiciona examenes
                examenesTemp["id"] = orden.id  # id de la orden
                examenesTemp["nombre"] = orden.examen.examen
                ordenTemp["examenes"].append(examenesTemp)
                idConsulta = orden.consulta.id
            else:
                # adiciona examenes
                examenesTemp["id"] = orden.id
                examenesTemp["nombre"] = orden.examen.examen
                ordenTemp["examenes"].append(examenesTemp)
            if limiteSup >= cantTotal - 1:
                ultimaPagina = True
            else:
                ultimaPagina = False
            ordenTemp["ultima_pagina"] = ultimaPagina
            ordenTemp["cant_paginas"] = cantPaginas

        if ordenTemp != {}:
            ordenes.append(ordenTemp)

        return JsonResponse(ordenes[limiteIni:limiteSup], safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)