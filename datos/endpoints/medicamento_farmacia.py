from django.http.response import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import MedicamentoFarmacia, Medicamento, Farmacia, MedicamentoRecetado, Actividad, Paciente, Consulta
from ..serializers import MedicamentoFarmaciaSerializer
import json
from django.db import IntegrityError
from rest_framework import status
from django.db import transaction
from django.contrib.auth.models import User, Group
from django.db.models import Q
import random, string
from psycopg2._psycopg import ProgrammingError
from django.db.models import Sum, Count
from operator import itemgetter


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_medicamento_by_farmacia(request):
    payload = json.loads(request.body)
    id_farmacia = payload["id_farmacia"]
    tipo = MedicamentoFarmacia.objects.filter(sucursal=id_farmacia).order_by('id')
    tipoSerializer = MedicamentoFarmaciaSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_medicamento_by_farmacia_nombre(request):
    payload = json.loads(request.body)
    id_farmacia = payload["id_farmacia"]
    medicamentoFarmacia = []
    for medFarmacia_temp in MedicamentoFarmacia.objects.filter(farmacia=id_farmacia).order_by('id'):
        medicamentoFarmacia_ele = {}
        medicamentoFarmacia_ele["id"] = medFarmacia_temp.id
        medicamentoFarmacia_ele["medicamento_id"] = medFarmacia_temp.medicamento.id
        medicamentoFarmacia_ele["nombre_generico"] = medFarmacia_temp.medicamento.nombre_generico
        medicamentoFarmacia_ele["nombre_comercial"] = medFarmacia_temp.medicamento.nombre_comercial
        medicamentoFarmacia_ele["tipo_especifico"] = medFarmacia_temp.medicamento.tipo_especifico
        medicamentoFarmacia_ele["precio"] = medFarmacia_temp.precio
        medicamentoFarmacia_ele["descripcion"] = medFarmacia_temp.descripcion
        medicamentoFarmacia_ele["farmacia"] = medFarmacia_temp.farmacia.id
        medicamentoFarmacia.append(medicamentoFarmacia_ele)
    return JsonResponse(medicamentoFarmacia, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_medicamento_farmacia(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_farmacia = payload["id_farmacia"]
        medicamentos_activos = json.loads(payload["medicamentos_activos"])
        medicamentos_no_activos = json.loads(payload["medicamentos_no_activos"])

        # try:
        with transaction.atomic():
            # borra los medicamento que no estan activos
            for medicamento in medicamentos_no_activos:
                if MedicamentoFarmacia.objects.filter(medicamento=medicamento, farmacia=id_farmacia).count() > 0:
                    medicamentoFarmacia_delete = MedicamentoFarmacia.objects.get(medicamento=medicamento, farmacia=id_farmacia)
                    medicamentoFarmacia_delete.delete()

            # inserta los examenes que estan activos
            for medicamento in medicamentos_activos:
                if MedicamentoFarmacia.objects.filter(medicamento=medicamento, farmacia=id_farmacia).count() == 0:
                    medicamentoFarmacia_add = MedicamentoFarmacia()
                    medicamentoFarmacia_add.medicamento = Medicamento.objects.get(id=medicamento)
                    medicamentoFarmacia_add.farmacia = Farmacia.objects.get(id=id_farmacia)
                    medicamentoFarmacia_add.save()

            medicamentoFarmacia = []
            for medFarmacia_temp in MedicamentoFarmacia.objects.filter(farmacia=id_farmacia).order_by('id'):
                medicamentoFarmacia_ele = {}
                medicamentoFarmacia_ele["id"] = medFarmacia_temp.id
                medicamentoFarmacia_ele["medicamento_id"] = medFarmacia_temp.medicamento.id
                medicamentoFarmacia_ele["nombre_generico"] = medFarmacia_temp.medicamento.nombre_generico
                medicamentoFarmacia_ele["nombre_comercial"] = medFarmacia_temp.medicamento.nombre_comercial
                medicamentoFarmacia_ele["tipo_especifico"] = medFarmacia_temp.medicamento.tipo_especifico
                medicamentoFarmacia_ele["precio"] = medFarmacia_temp.precio
                medicamentoFarmacia_ele["descripcion"] = medFarmacia_temp.descripcion
                medicamentoFarmacia_ele["farmacia"] = medFarmacia_temp.farmacia.id
                medicamentoFarmacia.append(medicamentoFarmacia_ele)
            return JsonResponse(medicamentoFarmacia, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_medicamento_farmacia_detalles(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id = payload["id"]
        id_farmacia = payload["id_farmacia"]
        precio = payload["precio"]
        descripcion = payload["descripcion"]


        medicamentoFarmacia = MedicamentoFarmacia.objects.get(id=id)
        medicamentoFarmacia.precio = precio
        medicamentoFarmacia.descripcion = descripcion
        medicamentoFarmacia.save()

        medicamentoFarmacia = []
        for medFarmacia_temp in MedicamentoFarmacia.objects.filter(farmacia=id_farmacia).order_by('id'):
            medicamentoFarmacia_ele = {}
            medicamentoFarmacia_ele["id"] = medFarmacia_temp.id
            medicamentoFarmacia_ele["medicamento_id"] = medFarmacia_temp.medicamento.id
            medicamentoFarmacia_ele["nombre_generico"] = medFarmacia_temp.medicamento.nombre_generico
            medicamentoFarmacia_ele["nombre_comercial"] = medFarmacia_temp.medicamento.nombre_comercial
            medicamentoFarmacia_ele["tipo_especifico"] = medFarmacia_temp.medicamento.tipo_especifico
            medicamentoFarmacia_ele["precio"] = medFarmacia_temp.precio
            medicamentoFarmacia_ele["descripcion"] = medFarmacia_temp.descripcion
            medicamentoFarmacia_ele["farmacia"] = medFarmacia_temp.farmacia.id
            medicamentoFarmacia.append(medicamentoFarmacia_ele)
        return JsonResponse(medicamentoFarmacia, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_farmacias_con_medicamento(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_medicamento = payload["id_medicamento"]

        farmaciaMedicamento = []
        for medFarmacia_temp in MedicamentoFarmacia.objects.filter(medicamento=id_medicamento).order_by('precio'):
            farmaciaMedicamento_ele = {}
            farmaciaMedicamento_ele["id"] = medFarmacia_temp.id
            farmaciaMedicamento_ele["farmacia_id"] = medFarmacia_temp.farmacia.id
            farmaciaMedicamento_ele["nombre_comercial"] = medFarmacia_temp.farmacia.nombre_comercial
            farmaciaMedicamento_ele["direccion"] = medFarmacia_temp.farmacia.direccion
            farmaciaMedicamento_ele["referencia_direccion"] = medFarmacia_temp.farmacia.referencia_direccion
            provincia = ""
            if medFarmacia_temp.farmacia.provincia is not None:
                provincia = medFarmacia_temp.farmacia.provincia.provincia
            farmaciaMedicamento_ele["provincia"] = provincia
            canton = ""
            if medFarmacia_temp.farmacia.canton is not None:
                canton = medFarmacia_temp.farmacia.canton.canton
            farmaciaMedicamento_ele["canton"] = canton
            parroquia = ""
            if medFarmacia_temp.farmacia.parroquia is not None:
                parroquia = medFarmacia_temp.farmacia.parroquia.parroquia
            farmaciaMedicamento_ele["parroquia"] = parroquia
            farmaciaMedicamento_ele["telefono"] = medFarmacia_temp.farmacia.telefono
            farmaciaMedicamento_ele["lat"] = medFarmacia_temp.farmacia.lat
            farmaciaMedicamento_ele["lon"] = medFarmacia_temp.farmacia.lon
            farmaciaMedicamento_ele["precio"] = medFarmacia_temp.precio

            farmaciaMedicamento.append(farmaciaMedicamento_ele)
        return JsonResponse(farmaciaMedicamento, safe=False)

    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_farmacias_todos_medicamentos(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        print("<payload>",payload)
        id_consulta = payload["id_consulta"]
        idMedicamentos = []
        for medRecetadoTemp in MedicamentoRecetado.objects.filter(consulta=id_consulta):
                idMedicamentos.append(medRecetadoTemp.medicamento.id)
        cantidadMedConsulta = len(idMedicamentos)
        # print(MedicamentoFarmacia.objects.filter(medicamento__in =idMedicamentos).values('farmacia').order_by('farmacia').annotate(precio=Sum('precio')).annotate(cantidad=Count('id')))
        farmaciaMedicamento = []
        for medFarmacia_temp in MedicamentoFarmacia.objects.filter(medicamento__in =idMedicamentos).values('farmacia').order_by('farmacia').annotate(precio=Sum('precio')).annotate(cantidad=Count('id')):
            if medFarmacia_temp["cantidad"] == cantidadMedConsulta:
                # print (medFarmacia_temp)
                farmaciatemp = Farmacia.objects.get(pk=medFarmacia_temp["farmacia"])
                # print(farmaciatemp.nombre_comercial)
                farmaciaMedicamento_ele = {}
                # farmaciaMedicamento_ele["id"] = farmaciatemp["id"]
                farmaciaMedicamento_ele["farmacia_id"] = farmaciatemp.id
                farmaciaMedicamento_ele["nombre_comercial"] = farmaciatemp.nombre_comercial
                farmaciaMedicamento_ele["direccion"] = farmaciatemp.direccion
                farmaciaMedicamento_ele["referencia_direccion"] = farmaciatemp.referencia_direccion
                farmaciaMedicamento_ele["tipo"] = "farmacia"

                provincia = ""
                idProvincia = 0
                if farmaciatemp.provincia is not None:
                    provincia = farmaciatemp.provincia.provincia
                    idProvincia = farmaciatemp.provincia.id
                farmaciaMedicamento_ele["provincia"] = provincia
                farmaciaMedicamento_ele["id_provincia"] = idProvincia

                canton = ""
                idCanton = 0
                if farmaciatemp.canton is not None:
                    canton = farmaciatemp.canton.canton
                    idCanton = farmaciatemp.canton.id
                farmaciaMedicamento_ele["canton"] = canton
                farmaciaMedicamento_ele["id_canton"] = idCanton

                parroquia = ""
                idParroquia = 0
                if farmaciatemp.parroquia is not None:
                    parroquia = farmaciatemp.parroquia.parroquia
                    idParroquia = farmaciatemp.parroquia.id
                farmaciaMedicamento_ele["parroquia"] = parroquia
                farmaciaMedicamento_ele["id_parroquia"] = idParroquia

                farmaciaMedicamento_ele["telefono"] = farmaciatemp.telefono
                farmaciaMedicamento_ele["lat"] = farmaciatemp.lat
                farmaciaMedicamento_ele["lon"] = farmaciatemp.lon
                if medFarmacia_temp["precio"] is None:
                    medFarmacia_temp["precio"] = 0
                farmaciaMedicamento_ele["precio_total"] = float(format(medFarmacia_temp["precio"], '.2f'))

                farmaciaMedicamento.append(farmaciaMedicamento_ele)

        # print(farmaciaMedicamento)
        resultado = sorted(farmaciaMedicamento, key=itemgetter('precio_total'))
        return JsonResponse(resultado, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def medicamentos_solicitados_farmacia(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_consulta = payload["id_consulta"]
        id_farmacia = payload["id_farmacia"]
        precio_total = payload["precio_total"]
        for medFarmaciaTemp in MedicamentoRecetado.objects.filter(consulta=id_consulta):
            medFarmaciaTemp.farmacia = Farmacia.objects.get(pk=id_farmacia)
            medFarmaciaTemp.precio_total = precio_total
            medFarmaciaTemp.save()
        # adiciona las actividades
        actividad = Actividad()
        actividad.paciente = Paciente.objects.get(pk=payload["id_paciente"])
        actividad.consulta = Consulta.objects.get(pk=id_consulta)
        actividad.tipoActividad = "SELECCION_FARMACIA"
        actividad.tipoEntidad = "FARMACIA"
        actividad.entidad = id_farmacia
        actividad.nombreEntidad = Farmacia.objects.get(pk=id_farmacia).nombre_comercial
        actividad.save()
        return JsonResponse({ "msg": "ok" }, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)