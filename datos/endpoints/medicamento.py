from django.db.models import Q
from django.http.response import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import Medicamento, MedicamentoRecetado, Actividad, Paciente, Consulta, Farmacia
from ..serializers import MedicamentoSerializer
import json
from django.db import IntegrityError
from rest_framework import status
from django.db import transaction
import math

#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_medicamento(request):
    tipo = Medicamento.objects.filter().order_by('id')
    tipoSerializer = MedicamentoSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def medicamento_filtro_comercial(request):
    payload = json.loads(request.body)
    texto = payload["texto"].strip()
    if texto == "":
        tipo = []
    else:
        tipo = Medicamento.objects.filter(nombre_comercial__icontains=texto)[:10]
    tipoSerializer = MedicamentoSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def medicamento_filtro_generico(request):
    payload = json.loads(request.body)
    texto = payload["texto"].strip()
    if texto == "":
        tipo = []
    else:
        tipo = Medicamento.objects.filter(nombre_generico__icontains=texto)[:10]
    tipoSerializer = MedicamentoSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def medicamento_filtro_nombre(request):
    payload = json.loads(request.body)
    texto = payload["texto"].strip()
    if texto == "":
        tipo = []
    else:
        tipo = Medicamento.objects.filter(nombre_generico__icontains=texto)[:10] | \
               Medicamento.objects.filter(nombre_comercial__icontains=texto)[:10]
    tipoSerializer = MedicamentoSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_medicamento(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            obj = Medicamento()
            obj.nombre_generico = payload["nombre_generico"]
            obj.nombre_comercial = payload["nombre_comercial"]
            obj.tipo_especifico = payload["tipo_especifico"]
            obj.tipo_generico = payload["tipo_generico"]
            obj.via_aplicacion = payload["via_aplicacion"]


            obj.save()
            tabla = Medicamento.objects.filter().order_by('id')
            tabla_serializer = MedicamentoSerializer(tabla, many=True)
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
def update_medicamento(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            obj = Medicamento.objects.get(pk=int(payload["id"]))
            obj.nombre_generico = payload["nombre_generico"]
            obj.nombre_comercial = payload["nombre_comercial"]
            obj.tipo_especifico = payload["tipo_especifico"]
            obj.tipo_generico = payload["tipo_generico"]
            obj.via_aplicacion = payload["via_aplicacion"]

            obj.save()
            tabla = Medicamento.objects.filter().order_by('id')
            tabla_serializer = MedicamentoSerializer(tabla, many=True)
            return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except Medicamento.DoesNotExist as e:
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
def delete_medicamento(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            with transaction.atomic():
                obj = Medicamento.objects.get(pk=int(payload["id"]))
                obj.delete()
                tabla = Medicamento.objects.filter().order_by('id')
                tabla_serializer = MedicamentoSerializer(tabla, many=True)
                return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except Medicamento.DoesNotExist as e:
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
def medicamento_generico_inicial(request):
    payload = json.loads(request.body)
    texto = payload["inicial"].strip()
    if texto == "":
        tipo = []
    else:
        tipo = Medicamento.objects.filter(nombre_generico__startswith=texto)[:10]
    tipoSerializer = MedicamentoSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def medicamentos_recetados_farmacia(request):
    if request.method == 'POST':
        cantRegistros = 5
        payload = json.loads(request.body)
        idFarmacia = payload["id_farmacia"]
        paginaActual = payload["pagina"]
        if paginaActual < 1:
            return JsonResponse([], safe=False)
        limiteIni= (paginaActual-1) * cantRegistros
        limiteSup = (paginaActual * cantRegistros)
        print("Ini:"+str(limiteIni)+" "+"Sup:"+str(limiteSup))
        recetas = []
        idConsulta = -1

        cantTotal = len(MedicamentoRecetado.objects.filter(farmacia=idFarmacia).distinct('consulta'))
        cantPaginas = math.ceil(cantTotal / cantRegistros)
        # print(cantTotal)

        for consulta in MedicamentoRecetado.objects.filter(farmacia=idFarmacia).distinct('consulta').order_by('-consulta')[limiteIni:limiteSup]:
            # print(consulta.consulta.id)
            recetaTemp = {}
            fecha = consulta.consulta.fecha.strftime("%d/%m/%Y")
            # print(fecha)
            recetaTemp["fecha"] = consulta.consulta.fecha.strftime("%d/%m/%Y")
            recetaTemp["id_medico"] = consulta.consulta.medico.id
            recetaTemp["medico"] = consulta.consulta.medico.nombre + " " + consulta.consulta.medico.apellidos
            recetaTemp["medico_cedula"] = consulta.consulta.medico.cedula
            recetaTemp["medico_codigo"] = consulta.consulta.medico.codigo
            recetaTemp["id_paciente"] = consulta.consulta.paciente.id
            recetaTemp["id_farmacia"] = idFarmacia
            recetaTemp["paciente"] = consulta.consulta.paciente.nombre + " " + consulta.consulta.paciente.apellidos
            recetaTemp["id_consulta"] = consulta.consulta.id
            print("L:"+str(limiteSup)+" cant:"+str(cantTotal))
            if limiteSup >= cantTotal-1:
                ultimaPagina = True
            else:
                ultimaPagina = False
            recetaTemp["ultima_pagina"] = ultimaPagina
            recetaTemp["cant_paginas"] = cantPaginas
            recetaTemp["medicamentos"] = []
            for receta in MedicamentoRecetado.objects.filter(farmacia=idFarmacia, consulta=consulta.consulta.id).order_by('-id'):
                medicamentosTemp = {}
                # adiciona medicamentos
                medicamentosTemp["id"] = receta.id #receta.medicamento.id
                medicamentosTemp["nombre_comercial"] = receta.medicamento.nombre_comercial
                medicamentosTemp["nombre_generico"] = receta.medicamento.nombre_generico
                medicamentosTemp["presentacion"] = receta.medicamento.tipo_especifico
                medicamentosTemp["estado"] = receta.estado
                recetaTemp["medicamentos"].append(medicamentosTemp)

            recetas.append(recetaTemp)

        return JsonResponse(recetas, safe=False)

    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def filtra_medicamentos_recetados_farmacia(request):
    if request.method == 'POST':
        cantRegistros = 5
        payload = json.loads(request.body)
        idFarmacia = payload["farmacia"]
        paginaActual = payload["pagina"]
        if paginaActual < 1:
            return JsonResponse([], safe=False)
        limiteIni= (paginaActual-1) * cantRegistros
        limiteSup = (paginaActual * cantRegistros) 
        # print("Ini:"+str(limiteIni)+" "+"Sup:"+str(limiteSup))
        recetas = []

        # los filtros
        filtrosAplicar = []
        farmacia = payload["farmacia"]
        filtrosAplicar.append(Q(farmacia=farmacia))
        paciente = payload["paciente"]
        if paciente is not None and paciente != "":
            filtrosAplicar.append(Q(consulta__paciente__id=paciente))
        medico = payload["medico"]
        if medico is not None and medico != "":
            filtrosAplicar.append(Q(consulta__medico__id=medico))
        fecha = payload["fecha"]
        if fecha is not None and fecha != "":
            filtrosAplicar.append(Q(consulta__fecha=fecha))

        cantTotal = len(MedicamentoRecetado.objects.filter(*filtrosAplicar).distinct('consulta'))
        cantPaginas = math.ceil(cantTotal / cantRegistros)

        for consulta in MedicamentoRecetado.objects.filter(*filtrosAplicar).distinct('consulta').order_by('-consulta')[limiteIni:limiteSup]:
            # print(consulta.consulta.id)
            recetaTemp = {}
            recetaTemp["fecha"] = consulta.consulta.fecha.strftime("%d/%m/%Y")
            recetaTemp["id_medico"] = consulta.consulta.medico.id
            recetaTemp["medico"] = consulta.consulta.medico.nombre + " " + consulta.consulta.medico.apellidos
            recetaTemp["medico_cedula"] = consulta.consulta.medico.cedula
            recetaTemp["medico_codigo"] = consulta.consulta.medico.codigo
            recetaTemp["id_paciente"] = consulta.consulta.paciente.id
            recetaTemp["id_farmacia"] = idFarmacia
            recetaTemp["paciente"] = consulta.consulta.paciente.nombre + " " + consulta.consulta.paciente.apellidos
            recetaTemp["id_consulta"] = consulta.consulta.id
            print("L:"+str(limiteSup)+" cant:"+str(cantTotal))
            if limiteSup >= cantTotal-1:
                ultimaPagina = True
            else:
                ultimaPagina = False
            recetaTemp["ultima_pagina"] = ultimaPagina
            recetaTemp["cant_paginas"] = cantPaginas
            recetaTemp["medicamentos"] = []
            for receta in MedicamentoRecetado.objects.filter(farmacia=idFarmacia, consulta=consulta.consulta.id).order_by('-id'):
                medicamentosTemp = {}
                # adiciona medicamentos
                medicamentosTemp["id"] = receta.id #receta.medicamento.id
                medicamentosTemp["nombre_comercial"] = receta.medicamento.nombre_comercial
                medicamentosTemp["nombre_generico"] = receta.medicamento.nombre_generico
                medicamentosTemp["presentacion"] = receta.medicamento.tipo_especifico
                medicamentosTemp["estado"] = receta.estado
                recetaTemp["medicamentos"].append(medicamentosTemp)

            recetas.append(recetaTemp)

        return JsonResponse(recetas, safe=False)

    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
# @api_view(['POST'])
# def filtra_medicamentos_recetados_farmacia(request):
#     if request.method == 'POST':
#         cantRegistros = 5
#         payload = json.loads(request.body)
#         filtrosAplicar = []
#         farmacia = payload["farmacia"]
#         filtrosAplicar.append(Q(farmacia=farmacia))
#         paciente = payload["paciente"]
#         if paciente is not None and paciente != "":
#             filtrosAplicar.append(Q(consulta__paciente__id=paciente) )
#         medico = payload["medico"]
#         if medico is not None and medico != "":
#             filtrosAplicar.append(Q(consulta__medico__id=medico) )
#         fecha = payload["fecha"]
#         if fecha is not None and fecha != "":
#             filtrosAplicar.append(Q(consulta__fecha=fecha) )
#
#         recetas = []
#         idConsulta = -1
#         recetaTemp = {}
#         for receta in MedicamentoRecetado.objects.filter(*filtrosAplicar):
#             medicamentosTemp = {}
#             if idConsulta != receta.consulta.id:
#                 if recetaTemp != {}:
#                     recetas.append(recetaTemp)
#                     recetaTemp = {}
#
#                 recetaTemp["fecha"] = receta.consulta.fecha.strftime("%d/%m/%Y")
#                 recetaTemp["id_medico"] = receta.consulta.medico.id
#                 recetaTemp["medico"] = receta.consulta.medico.nombre + " " + receta.consulta.medico.apellidos
#                 recetaTemp["medico_cedula"] = receta.consulta.medico.cedula
#                 recetaTemp["medico_codigo"] = receta.consulta.medico.codigo
#                 recetaTemp["id_paciente"] = receta.consulta.paciente.id
#                 recetaTemp["id_farmacia"] = farmacia
#                 recetaTemp["paciente"] = receta.consulta.paciente.nombre + " " + receta.consulta.paciente.apellidos
#                 recetaTemp["id_consulta"] = receta.consulta.id
#                 recetaTemp["medicamentos"] = []
#                 # adiciona medicamentos
#                 medicamentosTemp["id"] = receta.id #receta.medicamento.id
#                 medicamentosTemp["nombre_comercial"] = receta.medicamento.nombre_comercial
#                 medicamentosTemp["nombre_generico"] = receta.medicamento.nombre_generico
#                 medicamentosTemp["presentacion"] = receta.medicamento.tipo_especifico
#                 medicamentosTemp["estado"] = receta.estado
#                 recetaTemp["medicamentos"].append(medicamentosTemp)
#                 idConsulta = receta.consulta.id
#             else:
#                 # adiciona medicamentos
#                 medicamentosTemp["id"] = receta.id
#                 medicamentosTemp["nombre_comercial"] = receta.medicamento.nombre_comercial
#                 medicamentosTemp["nombre_generico"] = receta.medicamento.nombre_generico
#                 medicamentosTemp["presentacion"] = receta.medicamento.tipo_especifico
#                 medicamentosTemp["estado"] = receta.estado
#                 recetaTemp["medicamentos"].append(medicamentosTemp)
#
#         if recetaTemp != {}:
#             recetas.append(recetaTemp)
#
#         return JsonResponse(recetas, safe=False)
#     else:
#         return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def medicamentos_venta(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        idMedicamento = payload["id_medicamento_recetado"]
        id_consulta = payload["id_consulta"]
        id_paciente = payload["id_paciente"]
        id_farmacia = payload["id_farmacia"]
        vendido = payload["vendido"]
        med = MedicamentoRecetado.objects.get(pk=idMedicamento)
        if vendido:
            med.estado = "VENDIDO"
        else:
            med.estado = "INDICADO"
        med.save()
        # adiciona las actividades
        if len(Actividad.objects.filter(consulta=id_consulta, tipoActividad="VENTA_MEDICAMENTO")) == 0:
            actividad = Actividad()
            actividad.paciente = Paciente.objects.get(pk=id_paciente)
            actividad.consulta = Consulta.objects.get(pk=id_consulta)
            actividad.tipoActividad = "VENTA_MEDICAMENTO"
            actividad.tipoEntidad = "FARMACIA"
            actividad.entidad = id_farmacia
            actividad.nombreEntidad = Farmacia.objects.get(pk=id_farmacia).nombre_comercial
            actividad.save()
        return JsonResponse({"msg":"ok"}, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
