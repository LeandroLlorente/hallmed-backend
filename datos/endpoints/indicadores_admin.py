from sqlite3 import complete_statement
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.http.response import JsonResponse
from django.db.models import Sum
from django.db import connection
from django.db.models import Min, Max
from datos.serializers import TarifaSerializer
from ..models import Consulta, Farmacia, Orden, MedicamentoRecetado, Resultados, Tarifa, Sucursal, Medicamento, VENDIDO
from .helpers import calc_compensacion, fullname, str2time, ifDo, handle_error
from functools import reduce
import json
import datetime


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def ultimos_dias_admin(request):
    if request.method == 'POST':
        #payload = json.loads(request.body)
        #id_medico = payload["id_medico"]
        hoy = datetime.datetime.now()
        # se le adiciona 1 para que tome la ultima semana ej de sabado a sabado
        ultimos7dias = hoy - datetime.timedelta(days=8)
        ultimos30dias = hoy - datetime.timedelta(days=31)
        ultimos_dias = {}
        # Consultas
        cantHoy = len(Consulta.objects.filter(fecha=hoy))
        cant7dias = len(Consulta.objects.filter(fecha__gt=ultimos7dias))
        cant30dias = len(Consulta.objects.filter(fecha__gt=ultimos30dias))
        consultas = {}
        consultas["hoy"] = cantHoy
        consultas["ultimos7dias"] = cant7dias
        consultas["ultimos30dias"] = cant30dias
        ultimos_dias["consultas"] = consultas
        # Examenes
        cantHoy = len(Orden.objects.filter(consulta__fecha=hoy))
        cant7dias = len(Orden.objects.filter(consulta__fecha__gt=ultimos7dias))
        cant30dias = len(Orden.objects.filter(
            consulta__fecha__gt=ultimos30dias))
        examenes = {}
        examenes["hoy"] = cantHoy
        examenes["ultimos7dias"] = cant7dias
        examenes["ultimos30dias"] = cant30dias
        ultimos_dias["examenes"] = examenes
        # Recetas
        cantHoy = len(MedicamentoRecetado.objects.filter(consulta__fecha=hoy))
        cant7dias = len(MedicamentoRecetado.objects.filter(
            consulta__fecha__gt=ultimos7dias))
        cant30dias = len(MedicamentoRecetado.objects.filter(
            consulta__fecha__gt=ultimos30dias))
        recetas = {}
        recetas["hoy"] = cantHoy
        recetas["ultimos7dias"] = cant7dias
        recetas["ultimos30dias"] = cant30dias
        ultimos_dias["recetas"] = recetas
        return JsonResponse(ultimos_dias, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@ authentication_classes([TokenAuthentication])
@ permission_classes([IsAuthenticated])
@ api_view(['POST'])
def cierre_ciclo_admin(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        #id_medico = payload["id_medico"]
        mes = payload["mes"]
        ano = payload["ano"]
        ciclos = {}
        porciento_examen = 0
        porciento_recetas = 0
        cant_pacientes_examenes = len(Orden.objects.all())
        if cant_pacientes_examenes != 0:
            cant_pacientes_resultados = len(
                Resultados.objects.filter(consulta__fecha__month=mes, consulta__fecha__year=ano))
            porciento_examen = (cant_pacientes_resultados *
                                100) / cant_pacientes_examenes
        cant_paciente_con_receta = len(
            MedicamentoRecetado.objects.filter(farmacia__isnull=False))
        if cant_paciente_con_receta != 0:
            cant_pacientes_con_medicamento = len(
                MedicamentoRecetado.objects.filter(farmacia__isnull=True))
            porciento_recetas = (
                cant_pacientes_con_medicamento * 100) / cant_paciente_con_receta
        ciclos["examen"] = porciento_examen
        ciclos["medicamento"] = porciento_recetas
        return JsonResponse(ciclos, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_sucursal_grupo_admin(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "mes" not in payload.keys() or payload["mes"] is None \
                or payload["mes"] == 'null' \
                or payload["mes"] == '':
            return JsonResponse({'error': 'El campo: mes es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "ano" not in payload.keys() or payload["ano"] is None \
                or payload["ano"] == 'null' \
                or payload["ano"] == '':
            return JsonResponse({'error': 'El campo: ano es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        mes = payload["mes"]
        ano = payload["ano"]
        sql = "select t7.tipo,t7.grupo_id, t7.sucursal_id, t7.nombre_grupo, t8.nombre as nombre_sucursal from (select t5.tipo,t5.grupo_id, t5.sucursal_id, t6.nombre as nombre_grupo from (select t4.tipo,t4.grupo_id, t4.sucursal_id from (select t1.id_consulta from (select id_consulta from resultados r where EXTRACT(MONTH FROM fecha_resultados) = {mes} and EXTRACT(YEAR FROM fecha_resultados) = {ano}) as t1) as t3 inner join (select distinct id_consulta,sucursal_id, tipo,grupo_id from orden) as t4 on t3.id_consulta = t4.id_consulta) as t5 left join (select id,nombre from unidad_medica um ) as t6 on t5.grupo_id=t6.id) as t7 left join (select id, nombre from sucursal s2 ) as t8 on t7.sucursal_id=t8.id".format(
            mes=mes, ano=ano)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            grupos_sucursales = []
            for index in range(cursor.rowcount):
                row = cursor.fetchone()
                grupos_sucursales.append(row)
        return JsonResponse(grupos_sucursales, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_tarifas(request):
    if request.method != 'POST':
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    payload = json.loads(request.body)
    tipoEntidad = payload["tipo_entidad"]
    print(tipoEntidad)
    if tipoEntidad is None:
        lg = Tarifa.objects.values('tipo_entidad').annotate(
            min=Min('porcentaje'), max=Max('porcentaje'))
        l = []
        for tarifa in lg:
            lt = Tarifa.objects.filter(
                tipo_entidad=tarifa['tipo_entidad']).order_by('porcentaje')
            tarifas = TarifaSerializer(lt, many=True)
            l.append({"tipo_entidad": tarifa['tipo_entidad'],
                      "escala_minima": tarifa['min'],
                      "escala_maxima": tarifa['max'],
                      "cantidad": lt.count(),
                      "datos": tarifas.data})
        return JsonResponse(l, safe=False, status=status.HTTP_200_OK)
    else:
        l = []
        for tarifa in Tarifa.objects.filter(tipo_entidad=tipoEntidad).order_by('porcentaje'):
            l.append({"id": tarifa.id, "valor": (
                tarifa.porcentaje*100).__round__()})
        return JsonResponse(l, safe=False, status=status.HTTP_200_OK)


@ authentication_classes([TokenAuthentication])
@ permission_classes([IsAuthenticated])
@ api_view(['POST'])
def creditos(request):
    if request.method != 'POST':
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    payload = json.loads(request.body)
    #id_medico = payload["id_medico"]
    mes = payload["mes"]
    ano = payload["ano"]
    compensaciones = {}
    suma_laboratorio = 0
    suma_imagen = 0
    suma_procedimiento = 0
    resultado_tabla = []
    resultados_finales = {}
    consultas_con_resultados = []
    for resultados_examen in Resultados.objects.filter(consulta__fecha__month=mes, consulta__fecha__year=ano):
        consultas_con_resultados.append(resultados_examen.consulta.id)
    tabla_ele = {}
    id_actual = -1
    for orden in Orden.objects.filter(consulta__in=consultas_con_resultados).order_by('grupo_id').order_by('sucursal_id'):
        # adiona el elemento actual
        elemento_desglose = {}
        elemento_desglose["id"] = orden.id
        elemento_desglose["precio"] = orden.precio_unitario
        elemento_desglose["paciente"] = fullname(orden.consulta.paciente)
        elemento_desglose["examen"] = orden.examen.examen
        elemento_desglose["fecha_inicado"] = str2time(orden.consulta.fecha)

        compensacion = 3

        if orden.tipo == "GRUPO":
            if not orden.grupo is None and id_actual != orden.grupo.id:
                #UM = UnidadMedica.objects.get(pk=orden.grupo.id)
                if not orden.grupo.compensacion is None:
                    compensacion = orden.grupo.compensacion
                if tabla_ele != {}:
                    resultado_tabla.append(tabla_ele)
                tabla_ele = {}
                tabla_ele["id"] = orden.grupo.id
                tabla_ele["unidad_diag"] = orden.grupo.nombre_comercial
                tabla_ele["desglose"] = []
                id_actual = orden.grupo.id

        if orden.tipo == "SUCURSAL":
            if orden.sucursal is not None and id_actual != orden.sucursal.id:
                suc = Sucursal.objects.get(pk=orden.sucursal.id)
                if not suc.compensacion is None:
                    compensacion = suc.compensacion
                if tabla_ele != {}:
                    resultado_tabla.append(tabla_ele)
                tabla_ele = {}
                tabla_ele["id"] = orden.sucursal.id
                tabla_ele["unidad_diag"] = suc.nombre
                tabla_ele["desglose"] = []
                id_actual = orden.sucursal.id

        tabla_ele["desglose"].append(elemento_desglose)
        tabla_ele["precio_total"] = orden.precio_total
        tabla_ele["compensacion_um"] = compensacion.__round__(2)
        compensacionOrden = calc_compensacion(orden.precio_total, compensacion)
        tabla_ele["precio_total_compensado"] = compensacionOrden
        # sumar la cantidad de categoria

        if orden.examen.tipo_examen.categoria == "LABORATORIO":
            suma_laboratorio = suma_laboratorio + compensacionOrden
        if orden.examen.tipo_examen.categoria == "IMAGEN":
            suma_imagen = suma_imagen + compensacionOrden
        if orden.examen.tipo_examen.categoria == "PROCEDIMIENTO":
            suma_procedimiento = suma_procedimiento + compensacionOrden

    if tabla_ele != {}:
        resultado_tabla.append(tabla_ele)

    compensaciones["laboratorio"] = suma_laboratorio.__round__(2)
    compensaciones["imagen"] = suma_imagen.__round__(2)
    compensaciones["procedimiento"] = suma_procedimiento.__round__(2)
    resultados_finales["compesaciones"] = compensaciones
    resultados_finales["tabla"] = resultado_tabla

    return JsonResponse(resultados_finales, safe=False, status=status.HTTP_200_OK)


@ authentication_classes([TokenAuthentication])
@ permission_classes([IsAuthenticated])
@ api_view(['POST'])
def creditos_farmacia(request):
    if request.method != 'POST':
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    try:
        payload = json.loads(request.body)
        mes = payload["mes"]
        ano = payload["ano"]

        qsmr = MedicamentoRecetado.objects.filter(
            estado=VENDIDO[0], consulta__fecha__month=mes, consulta__fecha__year=ano)

        tabla = []
        compensacion = 0
        for f in qsmr.values('farmacia').order_by('farmacia').annotate(precio=Sum('precio_total')):
            farm: Farmacia = Farmacia.objects.get(pk=f["farmacia"])
            desglose = []
            for m in qsmr.filter(farmacia=f['farmacia']).values('medicamento').order_by('medicamento').annotate(precio=Sum('precio_total')):
                med: Medicamento = Medicamento.objects.get(pk=m["medicamento"])
                elemento_desglose = {}
                elemento_desglose["id"] = med.nombre_comercial
                elemento_desglose["medicamento"] = med.nombre_comercial
                elemento_desglose["precio"] = m["precio"]
                elemento_desglose["compensacion"] = calc_compensacion(float(m["precio"]).__round__(2), farm.compensacion)
                desglose.append(elemento_desglose)
            elemento_tabla = {}
            elemento_tabla["id"] = farm.id
            elemento_tabla["farmacia"] = farm.nombre_comercial
            elemento_tabla["precio_total"] = f["precio"]
            elemento_tabla["compensacion"] = farm.compensacion
            elemento_tabla["precio_total_compensado"] = calc_compensacion(
                float(f["precio"]).__round__(2), farm.compensacion)
            elemento_tabla["desglose"] = desglose
            tabla.append(elemento_tabla)
            compensacion += elemento_tabla["precio_total_compensado"]

        resultados_finales = {}
        resultados_finales["precio_total"] = ifDo(
            len(qsmr) > 0, qsmr.aggregate(p=Sum('precio_total'))["p"], 0)
        resultados_finales["compensacion_total"] = compensacion.__round__(2)
        resultados_finales["tabla"] = tabla

        return JsonResponse(resultados_finales, status=status.HTTP_200_OK)

    except Exception as e:
        return handle_error(e)
