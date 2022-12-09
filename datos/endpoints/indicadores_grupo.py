from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from django.db.models import Q
from ..models import Orden, UnidadMedica, Examen, Resultados, Consulta, Tarifa
from ..serializers import TarifaSerializer
import json
from django.db.models import Count
import datetime
from django.db import connection



@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def ultimos_dias_grupo(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_grupo = payload["id_grupo"]
        hoy = datetime.datetime.now()
        ultimos7dias = hoy - datetime.timedelta(days=8) # se le adiciona 1 para que tome la ultima semana ej de sabado a sabado
        ultimos30dias = hoy - datetime.timedelta(days=31)
        ultimos_dias = {}

        # Examenes
        cantHoy = len(Orden.objects.filter(grupo=id_grupo, consulta__fecha=hoy))
        cant7dias = len(Orden.objects.filter(grupo=id_grupo, consulta__fecha__gt=ultimos7dias))
        cant30dias = len(Orden.objects.filter(grupo=id_grupo, consulta__fecha__gt=ultimos30dias))
        examenes = {}
        examenes["hoy"] = cantHoy
        examenes["ultimos7dias"] = cant7dias
        examenes["ultimos30dias"] = cant30dias
        ultimos_dias["examenes"] = examenes

        # Examenes laboratorios
        cantHoy = len(Orden.objects.filter(grupo=id_grupo, examen__tipo_examen__categoria="LABORATORIO", consulta__fecha=hoy))
        cant7dias = len(Orden.objects.filter(grupo=id_grupo, examen__tipo_examen__categoria="LABORATORIO", consulta__fecha__gt=ultimos7dias))
        cant30dias = len(Orden.objects.filter(grupo=id_grupo, examen__tipo_examen__categoria="LABORATORIO", consulta__fecha__gt=ultimos30dias))
        examenes = {}
        examenes["hoy"] = cantHoy
        examenes["ultimos7dias"] = cant7dias
        examenes["ultimos30dias"] = cant30dias
        ultimos_dias["examenes_lab"] = examenes

        # Examenes Imagenes
        cantHoy = len(Orden.objects.filter(grupo=id_grupo, examen__tipo_examen__categoria="IMAGEN",
                                           consulta__fecha=hoy))
        cant7dias = len(Orden.objects.filter(grupo=id_grupo, examen__tipo_examen__categoria="IMAGEN", consulta__fecha__gt=ultimos7dias))
        cant30dias = len(Orden.objects.filter(grupo=id_grupo, examen__tipo_examen__categoria="IMAGEN", consulta__fecha__gt=ultimos30dias))
        examenes = {}
        examenes["hoy"] = cantHoy
        examenes["ultimos7dias"] = cant7dias
        examenes["ultimos30dias"] = cant30dias
        ultimos_dias["examenes_img"] = examenes

        # Examenes procedimientos
        cantHoy = len(Orden.objects.filter(grupo=id_grupo, examen__tipo_examen__categoria="PROCEDIMIENTO",
                                           consulta__fecha=hoy))
        cant7dias = len(Orden.objects.filter(grupo=id_grupo, examen__tipo_examen__categoria="PROCEDIMIENTO", consulta__fecha__gt=ultimos7dias))
        cant30dias = len(Orden.objects.filter(grupo=id_grupo, examen__tipo_examen__categoria="PROCEDIMIENTO", consulta__fecha__gt=ultimos30dias))
        examenes = {}
        examenes["hoy"] = cantHoy
        examenes["ultimos7dias"] = cant7dias
        examenes["ultimos30dias"] = cant30dias
        ultimos_dias["examenes_proc"] = examenes

        return JsonResponse(ultimos_dias, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def examenes_frecuentes_grupo(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_grupo = payload["id_grupo"]
        examenes_frecuentes = []
        for orden in Orden.objects.filter(grupo=id_grupo).values('examen').annotate(total=Count('id')).order_by('-total')[:3]:
            examen_ele = {}
            examen_ele["examen"] = Examen.objects.get(id=orden["examen"]).examen
            examen_ele["cantidad"] = orden["total"]
            examenes_frecuentes.append(examen_ele)
            # print(orden)
        return JsonResponse(examenes_frecuentes, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@ authentication_classes([TokenAuthentication])
@ permission_classes([IsAuthenticated])
@ api_view(['POST'])
def facturacion_medicos_grupo(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_grupo = payload["id_grupo"]
        mes = payload["mes"]
        ano = payload["ano"]
        compensacion = 3
        UM = UnidadMedica.objects.get(pk=id_grupo)
        if not UM.compensacion is None:
            compensacion = UM.compensacion
        id_medico_actual = -1
        suma_laboratorio = 0
        suma_imagen = 0
        suma_procedimiento = 0
        resultado_tabla = []
        categorias = {}
        tabla_ele = {}
        resultados_finales = {}
        with connection.cursor() as cursor:
            cursor.execute("select t4.id_consulta, t4.id_examen,t4.precio_unitario,t4.fecha_resultados,t4.id_medico, t4.nombre, t4.apellidos, t4.examen ,t4.tipo_examen_id, ti.categoria from (select t3.id_consulta, t3.id_examen,t3.precio_unitario,t3.fecha_resultados,t3.id_medico, t3.nombre, t3.apellidos, exa.examen ,exa.tipo_examen_id from (select t2.id_consulta, t2.id_examen,t2.precio_unitario,t2.fecha_resultados,t2.id_medico, med.nombre, med.apellidos from (select t1.id_consulta, t1.id_examen,t1.precio_unitario,t1.fecha_resultados,con.id_medico from (select o.id_consulta, o.id_examen,o.precio_unitario,r.fecha_resultados from resultados r inner join orden o on r.id_consulta = o.id_consulta where o.grupo_id=%s and extract (month from fecha_resultados) =%s and extract (year from fecha_resultados) =%s ) t1 inner join consulta con on t1.id_consulta = con.id) t2 inner join medico med on t2.id_medico=med.id) t3 inner join examen exa on t3.id_examen=exa.id) t4 inner join tipo_examen ti on t4.tipo_examen_id = ti.id order by t4.id_medico, ti.categoria",[str(id_grupo),mes,ano])
            filas = cursor.fetchall()
            for row in filas:
                if id_medico_actual != row[4]:
                    if tabla_ele != {}:
                        tabla_ele["compensacion"] = str((tabla_ele["total_precio_unitario"] * compensacion) / 100)
                        resultado_tabla.append(tabla_ele)
                    tabla_ele = {}
                    tabla_ele["medico"] = row[5] + " " + row[6]
                    if row[2] is not None:
                        tabla_ele["total_precio_unitario"] = row[2]
                    else:
                        tabla_ele["total_precio_unitario"] = 0
                    tabla_ele["compensacion"] = 0
                    tabla_ele["desglose"] = []


                    # adiciona el elemento actual
                    elemento_desglose = {}
                    elemento_desglose["id"]=row[1]
                    elemento_desglose["examen"] = row[7]
                    if row[2] is not None:
                        elemento_desglose["precio_unitario"] = row[2]
                    else:
                        elemento_desglose["precio_unitario"] = 0
                    tabla_ele["desglose"].append(elemento_desglose)
                    id_medico_actual = row[4]
                else:
                    if row[2] is not None:
                        tabla_ele["total_precio_unitario"] = tabla_ele["total_precio_unitario"] + row[2]
                    else:
                        tabla_ele["total_precio_unitario"] = 0
                    # adiciona el elemento actual
                    elemento_desglose = {}
                    elemento_desglose["id"] = row[1]
                    elemento_desglose["examen"] = row[7]
                    if row[2] is not None:
                        elemento_desglose["precio_unitario"] = row[2]
                    else:
                        elemento_desglose["precio_unitario"] = 0
                    tabla_ele["desglose"].append(elemento_desglose)
                # sumar la cantidad de categoria
                if row[9] == "LABORATORIO":
                    if row[2] is not None:
                        suma_laboratorio = suma_laboratorio + row[2]
                if row[9] == "IMAGEN":
                    if row[2] is not None:
                        suma_imagen = suma_imagen + row[2]
                if row[9] == "PROCEDIMIENTO":
                    if row[2] is not None:
                        suma_procedimiento = suma_procedimiento + row[2]
                # print(row[4])
                # print(row[9])
            if tabla_ele != {}:
                tabla_ele["compensacion"] = str((tabla_ele["total_precio_unitario"] * compensacion) / 100)
                resultado_tabla.append(tabla_ele)
            categorias["laboratorio"] = suma_laboratorio
            categorias["imagen"] = suma_imagen
            categorias["procedimiento"] = suma_procedimiento
            resultados_finales["categorias"] = categorias
            resultados_finales["tabla"] = resultado_tabla


        return JsonResponse(resultados_finales, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

