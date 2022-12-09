from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import VENDIDO, Farmacia, Medicamento, MedicamentoRecetado
from django.db.models import Count, Sum
import json
import datetime
from .helpers import ifDo, ifEmptyGet,  handle_error, calc_compensacion, isEmpty


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def ultimos_dias_farmacia(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_farmacia = payload["id_farmacia"]
        hoy = datetime.datetime.now()
        # se le adiciona 1 para que tome la ultima semana ej de sabado a sabado
        ultimos7dias = hoy - datetime.timedelta(days=8)
        ultimos30dias = hoy - datetime.timedelta(days=31)
        ultimos_dias = {}
        # Recetas
        cantHoy = len(MedicamentoRecetado.objects.filter(
            farmacia=id_farmacia, consulta__fecha=hoy))
        cant7dias = len(MedicamentoRecetado.objects.filter(
            farmacia=id_farmacia, consulta__fecha__gt=ultimos7dias))
        cant30dias = len(MedicamentoRecetado.objects.filter(
            farmacia=id_farmacia, consulta__fecha__gt=ultimos30dias))
        medicamentos = {}
        medicamentos["hoy"] = cantHoy
        medicamentos["ultimos7dias"] = cant7dias
        medicamentos["ultimos30dias"] = cant30dias
        ultimos_dias["medicamentos"] = medicamentos
        return JsonResponse(ultimos_dias, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@ authentication_classes([TokenAuthentication])
@ permission_classes([IsAuthenticated])
@ api_view(['POST'])
def cierre_ciclo_farmacia(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_farmacia = payload["id_farmacia"]
        mes = payload["mes"]
        ciclos = {}
        porciento_recetas = 0
        cant_paciente_con_receta = len(
            MedicamentoRecetado.objects.filter(farmacia=id_farmacia))
        if cant_paciente_con_receta != 0:
            cant_pacientes_con_medicamento = len(
                MedicamentoRecetado.objects.filter(farmacia=id_farmacia))
            porciento_recetas = (
                cant_pacientes_con_medicamento * 100) / cant_paciente_con_receta
        ciclos["medicamento"] = porciento_recetas
        return JsonResponse(ciclos, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def medicamentos_frecuentes(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_farmacia = payload["id_farmacia"]
        medicamentos_frecuentes = []
        for resultado in MedicamentoRecetado.objects.filter(farmacia=id_farmacia).values('medicamento').annotate(total=Count('id')).order_by('-total')[:3]:
            elemento = {}
            elemento["medicamento"] = Medicamento.objects.get(
                id=resultado["medicamento"]).nombre_generico
            elemento["cantidad"] = resultado["total"]
            medicamentos_frecuentes.append(elemento)
            # print(orden)
        return JsonResponse(medicamentos_frecuentes, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@ authentication_classes([TokenAuthentication])
@ permission_classes([IsAuthenticated])
@ api_view(['POST'])
def facturacion_farmacia(request):
    if request.method != 'POST':
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    try:
        payload = json.loads(request.body)
        id_farmacia = payload["id_farmacia"]
        mes = payload["mes"]
        ano = payload["ano"]

        farm = Farmacia.objects.get(pk=id_farmacia)

        qs = MedicamentoRecetado.objects.filter(
            farmacia_id=id_farmacia, estado=VENDIDO[0], consulta__fecha__month=mes, consulta__fecha__year=ano)
   
        tabla = []
        for mr in qs.values('medicamento').order_by('medicamento').annotate(precio=Sum('precio_total')):
            elemento_desglose = {}
            # elemento_desglose["id"] = mr["medicamento"]
            elemento_desglose["medicamento"] = Medicamento.objects.get(
                pk=mr["medicamento"]).__str__()
            elemento_desglose["precio"] = mr["precio"]
            elemento_desglose["compensacion"] = calc_compensacion(
                mr["precio"], farm.compensacion)
            tabla.append(elemento_desglose)
            print(elemento_desglose)

        resultados_finales = {}
        resultados_finales["farmacia"] = ifEmptyGet(
            farm.razon_social, farm.nombre_comercial)
        resultados_finales["farmacia_compensacion"] = farm.compensacion
        resultados_finales["precio_total"] = ifDo(
            len(qs) > 0, qs.aggregate(precio=Sum('precio_total'))["precio"], 0)
        resultados_finales["compensacion_total"] = calc_compensacion(
            resultados_finales["precio_total"], resultados_finales["farmacia_compensacion"])
        resultados_finales["tabla"] = tabla

        return JsonResponse(resultados_finales, status=status.HTTP_200_OK)

    except Exception as e:
        return handle_error(e)
