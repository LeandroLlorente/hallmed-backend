from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import Consulta, Orden, MedicamentoRecetado, Resultados
import json
import datetime

from .helpers import fullname, calc_compensacion, ifEmptyGet

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def ultimos_dias(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_medico = payload["id_medico"]
        hoy = datetime.datetime.now()
        ultimos7dias = hoy - datetime.timedelta(days=8) # se le adiciona 1 para que tome la ultima semana ej de sabado a sabado
        ultimos30dias = hoy - datetime.timedelta(days=31)
        ultimos_dias = {}
        # Consultas
        cantHoy = len(Consulta.objects.filter(medico=id_medico, fecha=hoy))
        cant7dias = len(Consulta.objects.filter(medico=id_medico, fecha__gt=ultimos7dias))
        cant30dias = len(Consulta.objects.filter(medico=id_medico, fecha__gt=ultimos30dias))
        consultas = {}
        consultas["hoy"] = cantHoy
        consultas["ultimos7dias"] = cant7dias
        consultas["ultimos30dias"] = cant30dias
        ultimos_dias["consultas"] = consultas
        # Examenes
        cantHoy = len(Orden.objects.filter(consulta__medico=id_medico, consulta__fecha=hoy))
        cant7dias = len(Orden.objects.filter(consulta__medico=id_medico, consulta__fecha__gt=ultimos7dias))
        cant30dias = len(Orden.objects.filter(consulta__medico=id_medico, consulta__fecha__gt=ultimos30dias))
        examenes = {}
        examenes["hoy"] = cantHoy
        examenes["ultimos7dias"] = cant7dias
        examenes["ultimos30dias"] = cant30dias
        ultimos_dias["examenes"] = examenes
        # Recetas
        cantHoy = len(MedicamentoRecetado.objects.filter(consulta__medico=id_medico, consulta__fecha=hoy))
        cant7dias = len(MedicamentoRecetado.objects.filter(consulta__medico=id_medico, consulta__fecha__gt=ultimos7dias))
        cant30dias = len(MedicamentoRecetado.objects.filter(consulta__medico=id_medico, consulta__fecha__gt=ultimos30dias))
        recetas = {}
        recetas["hoy"] = cantHoy
        recetas["ultimos7dias"] = cant7dias
        recetas["ultimos30dias"] = cant30dias
        ultimos_dias["recetas"] = recetas
        return JsonResponse(ultimos_dias, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# @ authentication_classes([TokenAuthentication])
# @ permission_classes([IsAuthenticated])
# @ api_view(['POST'])
# def creditos_medico(request):
#     if request.method == 'POST':
#         payload = json.loads(request.body)
#         id_medico = payload["id_medico"]
#         mes = payload["mes"]
#         compensaciones = {}
#         suma_laboratorio = 0
#         suma_imagen = 0
#         suma_procedimiento = 0
#         resultado_tabla = []
#         resultados_finales = {}
#
#         for resultados in Resultados.objects.filter(consulta__medico=id_medico, consulta__fecha__month=mes):
#             resultado_tabla_ele = {}
#             primera = True
#             for orden in Orden.objects.filter(consulta=resultados.consulta.id).order_by('id'):
#
#                 elemento_desglose = {}
#                 if orden.tipo == "GRUPO":
#                     UM = UnidadMedica.objects.get(pk=orden.grupo.id)
#                     compensacion = UM.compensacion
#                     unidad_diag = UM.nombre_comercial
#                     precio_total = orden.precio_total
#                     precio_total_compensado = str((compensacion * precio_total)/100)
#                     if primera:
#                         resultado_tabla_ele["compensacion_um"] = compensacion
#                         resultado_tabla_ele["unidad_diag"] = unidad_diag
#                         resultado_tabla_ele["precio_total"] = precio_total
#                         resultado_tabla_ele["precio_total_compensado"] = precio_total_compensado
#                         resultado_tabla_ele["desglose"] = []
#                         primera = False
#                 else:
#                     suc = Sucursal.objects.get(pk=orden.sucursal.id)
#                     compensacion = suc.compensacion
#                     unidad_diag = suc.nombre
#                     precio_total = orden.precio_total
#                     precio_total_compensado = str((compensacion * precio_total) / 100)
#                     if primera:
#                         resultado_tabla_ele["compensacion_um"] = compensacion
#                         resultado_tabla_ele["unidad_diag"] = unidad_diag
#                         resultado_tabla_ele["precio_total"] = precio_total
#                         resultado_tabla_ele["precio_total_compensado"] = precio_total_compensado
#                         resultado_tabla_ele["desglose"] = []
#                         primera = False
#
#
#                 elemento_desglose["id"] = orden.id
#                 elemento_desglose["precio"] = orden.precio_unitario
#                 elemento_desglose["examen"] = orden.examen.examen
#                 elemento_desglose["fecha_inicado"] = orden.consulta.fecha.strftime("%d/%m/%Y")
#                 resultado_tabla_ele["desglose"].append(elemento_desglose)
#
#                 print(orden.examen.tipo_examen.categoria+" "+str((compensacion * orden.precio_total)/100))
#                 # sumar la cantidad de categoria
#                 if orden.examen.tipo_examen.categoria == "LABORATORIO":
#                     suma_laboratorio = suma_laboratorio + (compensacion * orden.precio_total)/100
#                 if orden.examen.tipo_examen.categoria == "IMAGEN":
#                     suma_imagen = suma_imagen + (compensacion * orden.precio_total)/100
#                 if orden.examen.tipo_examen.categoria == "PROCEDIMIENTO":
#                     suma_procedimiento = suma_procedimiento + (compensacion * orden.precio_total)/100
#             resultado_tabla.append(resultado_tabla_ele)
#         compensaciones["laboratorio"] = suma_laboratorio
#         compensaciones["imagen"] = suma_imagen
#         compensaciones["procedimiento"] = suma_procedimiento
#         resultados_finales["compesaciones"] = compensaciones
#         resultados_finales["tabla"] = resultado_tabla
#         # print(desglose)
#         return JsonResponse(resultados_finales, safe=False, status=status.HTTP_200_OK)
#     else:
#         return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@ authentication_classes([TokenAuthentication])
@ permission_classes([IsAuthenticated])
@ api_view(['POST'])
def creditos_medico(request):
    if request.method != 'POST':
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    payload = json.loads(request.body)
    id_medico = payload["id_medico"]
    mes = payload["mes"]
    ano = payload["ano"]
    compensaciones = {}
    suma_laboratorio = 0
    suma_imagen = 0
    suma_procedimiento = 0
    resultado_tabla = []
    resultados_finales = {}
    consultas_con_resultados = []
    for resultados_examen in Resultados.objects.filter(consulta__medico=id_medico, consulta__fecha__month=mes, consulta__fecha__year=ano):
        consultas_con_resultados.append(resultados_examen.consulta.id)
    id_actual = -1
    tabla_ele = {}
    for orden in Orden.objects.filter(consulta__in=consultas_con_resultados).order_by('grupo_id').order_by('sucursal_id'):
    
        # adiona el elemento actual
        elemento_desglose = {}
        elemento_desglose["id"] = orden.id
        elemento_desglose["precio"] = orden.precio_unitario
        elemento_desglose["paciente"] = fullname(orden.consulta.paciente)
        elemento_desglose["examen"] = orden.examen.examen
        elemento_desglose["fecha_inicado"] = orden.consulta.fecha.strftime("%d/%m/%Y")
        
        if orden.tipo == "GRUPO":
            if orden.grupo is not None and id_actual != orden.grupo.id:
                if tabla_ele != {}:
                    resultado_tabla.append(tabla_ele)
                tabla_ele = {}
                compensacion = ifEmptyGet(orden.grupo.compensacion,3)
                id_actual = orden.grupo.id
                tabla_ele["id"] = orden.grupo.id
                tabla_ele["unidad_diag"] = orden.grupo.nombre_comercial
                tabla_ele["desglose"] = []

        if orden.tipo == "SUCURSAL":
            if orden.sucursal is not None and id_actual != orden.sucursal.id:
                if tabla_ele != {}:
                    resultado_tabla.append(tabla_ele)
                tabla_ele = {}
                compensacion = IfEmptyGet(orden.sucursal.compensacion,3)
                id_actual = orden.sucursal.id
                tabla_ele["id"] = orden.sucursal.id
                tabla_ele["unidad_diag"] = orden.sucursal.nombre
                tabla_ele["desglose"] = []
        
        tabla_ele["desglose"].append(elemento_desglose)
        tabla_ele["compensacion_um"] = compensacion
        tabla_ele["precio_total"] = orden.precio_total
        compensacionOrden = calc_compensacion(orden.precio_total,compensacion)
        tabla_ele["precio_total_compensado"] = str(compensacionOrden)

        # sumar la cantidad de categoria
        if orden.examen.tipo_examen.categoria == "LABORATORIO":
            suma_laboratorio = suma_laboratorio + compensacionOrden
        if orden.examen.tipo_examen.categoria == "IMAGEN":
            suma_imagen = suma_imagen + compensacionOrden
        if orden.examen.tipo_examen.categoria == "PROCEDIMIENTO":
            suma_procedimiento = suma_procedimiento + compensacionOrden

    if tabla_ele != {}:
        resultado_tabla.append(tabla_ele)

    compensaciones["laboratorio"] = suma_laboratorio
    compensaciones["imagen"] = suma_imagen
    compensaciones["procedimiento"] = suma_procedimiento
    resultados_finales["compesaciones"] = compensaciones
    resultados_finales["tabla"] = resultado_tabla

    return JsonResponse(resultados_finales, safe=False, status=status.HTTP_200_OK)


@ authentication_classes([TokenAuthentication])
@ permission_classes([IsAuthenticated])
@ api_view(['POST'])
def cierre_ciclo(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_medico = payload["id_medico"]
        mes = payload["mes"]
        ciclos = {}
        porciento_examen=0
        porciento_recetas=0
        cant_pacientes_examenes = len(Orden.objects.filter(consulta__medico=id_medico))
        if cant_pacientes_examenes != 0:
            cant_pacientes_resultados = len(Resultados.objects.filter(consulta__medico=id_medico, consulta__fecha__month=mes))
            porciento_examen = (cant_pacientes_resultados * 100) / cant_pacientes_examenes
        cant_paciente_con_receta = len(MedicamentoRecetado.objects.filter(consulta__medico=id_medico, farmacia__isnull=False))
        if cant_paciente_con_receta != 0:
            cant_pacientes_con_medicamento = len(MedicamentoRecetado.objects.filter(consulta__medico=id_medico, farmacia__isnull=True))
            porciento_recetas = (cant_pacientes_con_medicamento * 100) / cant_paciente_con_receta
        ciclos["examen"] = porciento_examen
        ciclos["medicamento"] = porciento_recetas
        return JsonResponse(ciclos, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
