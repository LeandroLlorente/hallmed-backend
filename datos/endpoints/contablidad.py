from django.db.models.functions import ExtractMonth
from psycopg2._psycopg import ProgrammingError
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.http.response import JsonResponse
from rest_framework import status
from django.db import connection
import json


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_sucursales_medico(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "mes" not in payload.keys() or payload["mes"] is None \
                or payload["mes"] == 'null' \
                or payload["mes"] == '':
            return JsonResponse({'error': 'El campo: mes es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        medico = payload["medico"]
        mes = payload["mes"]
        sql = "select t9.sucursal , t9.sucursal_id, concat(t10.nombre,' ', t10.apellidos) as paciente, t9.examen,t9.puntos from (select t7.sucursal , t7.sucursal_id, t7.examen,t7.puntos, t8.id_paciente from (select t6.nombre as sucursal , t5.sucursal_id, t5.examen,t5.id_consulta, t5.precio_unitario, t6.compensacion, t5.precio_unitario * t6.compensacion / 100.0 as puntos from (select t4.examen, t3.precio_unitario, t3.sucursal_id, t3.id_consulta from (select t1.id_consulta, t2.precio_unitario, t2.id_examen, t2.sucursal_id from (select id_consulta from resultados r where EXTRACT(MONTH FROM fecha_resultados) = {mes}) as t1 inner join (select id_consulta, precio_unitario, id_examen, sucursal_id from orden o ) t2 on t1.id_consulta = t2.id_consulta) t3 inner join  (select id,examen from examen) t4 on t3.id_examen = t4.id) t5 inner join  (select id, nombre, compensacion from sucursal s2 ) t6 on t5.sucursal_id = t6.id) t7 inner join  (select id,id_paciente from consulta c2 where id_medico = {idmedico} ) t8 on t7.id_consulta=t8.id) t9 inner join  (select id,nombre,apellidos from paciente ) t10 on t9.id_paciente = t10.id".format(mes=mes, idmedico=medico)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            sucursales = []
            for index in range(cursor.rowcount):
                row = cursor.fetchone()
                sucursales.append(row)
            JsonResponse(sucursales, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(sucursales, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_sucursal_medico(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "mes" not in payload.keys() or payload["mes"] is None \
                or payload["mes"] == 'null' \
                or payload["mes"] == '':
            return JsonResponse({'error': 'El campo: mes es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "sucursal" not in payload.keys() or payload["sucursal"] is None \
                or payload["sucursal"] == 'null' \
                or payload["sucursal"] == '':
            return JsonResponse({'error': 'El campo: sucursal es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        medico = payload["medico"]
        mes = payload["mes"]
        sucursal = payload["sucursal"]
        sql = "select t9.sucursal , t9.sucursal_id, concat(t10.nombre,' ', t10.apellidos) as paciente, t9.examen,t9.puntos from (select t7.sucursal , t7.sucursal_id, t7.examen,t7.puntos, t8.id_paciente from (select t6.nombre as sucursal , t5.sucursal_id, t5.examen,t5.id_consulta, t5.precio_unitario, t6.compensacion, t5.precio_unitario * t6.compensacion / 100.0 as puntos from (select t4.examen, t3.precio_unitario, t3.sucursal_id, t3.id_consulta from (select t1.id_consulta, t2.precio_unitario, t2.id_examen, t2.sucursal_id from (select id_consulta from resultados r where EXTRACT(MONTH FROM fecha_resultados) = {mes}) as t1 inner join (select id_consulta, precio_unitario, id_examen, sucursal_id from orden o ) t2 on t1.id_consulta = t2.id_consulta) t3 inner join  (select id,examen from examen) t4 on t3.id_examen = t4.id) t5 inner join  (select id, nombre, compensacion from sucursal s2 where id={sucursal}) t6 on t5.sucursal_id = t6.id) t7 inner join  (select id,id_paciente from consulta c2 where id_medico = {idmedico} ) t8 on t7.id_consulta=t8.id) t9 inner join  (select id,nombre,apellidos from paciente ) t10 on t9.id_paciente = t10.id".format(mes=mes, idmedico=medico, sucursal=sucursal)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            sucursales = []
            for index in range(cursor.rowcount):
                row = cursor.fetchone()
                sucursales.append(row)
            JsonResponse(sucursales, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(sucursales, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_grupos_medico(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "mes" not in payload.keys() or payload["mes"] is None \
                or payload["mes"] == 'null' \
                or payload["mes"] == '':
            return JsonResponse({'error': 'El campo: mes es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        medico = payload["medico"]
        mes = payload["mes"]
        sql = "select t9.sucursal , t9.grupo_id, concat(t10.nombre,' ', t10.apellidos) as paciente, t9.examen,t9.puntos from (select t7.sucursal , t7.grupo_id, t7.examen,t7.puntos, t8.id_paciente from (select t6.nombre as sucursal , t5.grupo_id, t5.examen,t5.id_consulta, t5.precio_unitario, t6.compensacion, t5.precio_unitario * t6.compensacion / 100.0 as puntos from (select t4.examen, t3.precio_unitario, t3.grupo_id, t3.id_consulta from (select t1.id_consulta, t2.precio_unitario, t2.id_examen, t2.grupo_id from (select id_consulta from resultados r where EXTRACT(MONTH FROM fecha_resultados) = {mes}) as t1 inner join (select id_consulta, precio_unitario, id_examen, grupo_id from orden o ) t2 on t1.id_consulta = t2.id_consulta) t3 inner join  (select id,examen from examen) t4 on t3.id_examen = t4.id) t5 inner join  (select id, nombre, compensacion from unidad_medica s2 ) t6 on t5.grupo_id = t6.id) t7 inner join  (select id,id_paciente from consulta c2 where id_medico = {idmedico} ) t8 on t7.id_consulta=t8.id) t9 inner join  (select id,nombre,apellidos from paciente ) t10 on t9.id_paciente = t10.id".format(mes=mes, idmedico=medico)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            grupos = []
            for index in range(cursor.rowcount):
                row = cursor.fetchone()
                grupos.append(row)
            JsonResponse(grupos, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(grupos, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_grupo_medico(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "mes" not in payload.keys() or payload["mes"] is None \
                or payload["mes"] == 'null' \
                or payload["mes"] == '':
            return JsonResponse({'error': 'El campo: mes es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "grupo" not in payload.keys() or payload["grupo"] is None \
                or payload["grupo"] == 'null' \
                or payload["grupo"] == '':
            return JsonResponse({'error': 'El campo: grupo es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        medico = payload["medico"]
        mes = payload["mes"]
        grupo = payload["grupo"]
        sql = "select t9.sucursal , t9.grupo_id, concat(t10.nombre,' ', t10.apellidos) as paciente, t9.examen,t9.puntos from (select t7.sucursal , t7.grupo_id, t7.examen,t7.puntos, t8.id_paciente from (select t6.nombre as sucursal , t5.grupo_id, t5.examen,t5.id_consulta, t5.precio_unitario, t6.compensacion, t5.precio_unitario * t6.compensacion / 100.0 as puntos from (select t4.examen, t3.precio_unitario, t3.grupo_id, t3.id_consulta from (select t1.id_consulta, t2.precio_unitario, t2.id_examen, t2.grupo_id from (select id_consulta from resultados r where EXTRACT(MONTH FROM fecha_resultados) = {mes}) as t1 inner join (select id_consulta, precio_unitario, id_examen, grupo_id from orden o ) t2 on t1.id_consulta = t2.id_consulta) t3 inner join  (select id,examen from examen) t4 on t3.id_examen = t4.id) t5 inner join  (select id, nombre, compensacion from unidad_medica s2 where id={grupo}) t6 on t5.grupo_id = t6.id) t7 inner join  (select id,id_paciente from consulta c2 where id_medico = {idmedico} ) t8 on t7.id_consulta=t8.id) t9 inner join  (select id,nombre,apellidos from paciente ) t10 on t9.id_paciente = t10.id".format(mes=mes, idmedico=medico, grupo=grupo)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            grupos = []
            for index in range(cursor.rowcount):
                row = cursor.fetchone()
                grupos.append(row)
            JsonResponse(grupos, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(grupos, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_medicos_grupo(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "mes" not in payload.keys() or payload["mes"] is None \
                or payload["mes"] == 'null' \
                or payload["mes"] == '':
            return JsonResponse({'error': 'El campo: mes es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "grupo" not in payload.keys() or payload["grupo"] is None \
                or payload["grupo"] == 'null' \
                or payload["grupo"] == '':
            return JsonResponse({'error': 'El campo: grupo es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        mes = payload["mes"]
        grupo = payload["grupo"]
        sql = "select t8.nombre,t7.examen,t7.precio_unitario from  (select t5.id_medico,t5.precio_unitario,t6.examen  from (select t3.id_medico,t4.precio_unitario, t4.id_examen from (select t1.id_consulta, t2.id_medico from (select id_consulta from resultados r where EXTRACT(MONTH FROM fecha_resultados) = {mes}) as t1 inner join (select id, id_medico from consulta c2 ) as t2 on t1.id_consulta = t2.id) as t3 inner join (select id_consulta,grupo_id,precio_unitario, id_examen from orden o2 where grupo_id = {grupo} ) as t4 on t3.id_consulta = t4.id_consulta) as t5 inner join  (select id, examen from examen e2 ) as t6 on t5.id_examen = t6.id) as t7 inner join  (select id,concat(nombre, ' ', apellidos) as nombre from medico m ) t8 on t7.id_medico = t8.id".format(mes=mes,grupo=grupo)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            grupos = []
            for index in range(cursor.rowcount):
                row = cursor.fetchone()
                grupos.append(row)
            JsonResponse(grupos, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(grupos, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_medico_grupo(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "mes" not in payload.keys() or payload["mes"] is None \
                or payload["mes"] == 'null' \
                or payload["mes"] == '':
            return JsonResponse({'error': 'El campo: mes es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "grupo" not in payload.keys() or payload["grupo"] is None \
                or payload["grupo"] == 'null' \
                or payload["grupo"] == '':
            return JsonResponse({'error': 'El campo: grupo es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        mes = payload["mes"]
        grupo = payload["grupo"]
        sql = "select t8.nombre,t7.examen,t7.precio_unitario from  (select t5.id_medico,t5.precio_unitario,t6.examen  from (select t3.id_medico,t4.precio_unitario, t4.id_examen from (select t1.id_consulta, t2.id_medico from (select id_consulta from resultados r where EXTRACT(MONTH FROM fecha_resultados) = {mes}) as t1 inner join (select id, id_medico from consulta c2 id_medico = {medico}) as t2 on t1.id_consulta = t2.id) as t3 inner join (select id_consulta,grupo_id,precio_unitario, id_examen from orden o2 where grupo_id = {grupo} ) as t4 on t3.id_consulta = t4.id_consulta) as t5 inner join  (select id, examen from examen e2 ) as t6 on t5.id_examen = t6.id) as t7 inner join  (select id,concat(nombre, ' ', apellidos) as nombre from medico m ) t8 on t7.id_medico = t8.id".format(mes=mes, grupo=grupo, medico=medico)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            grupos = []
            for index in range(cursor.rowcount):
                row = cursor.fetchone()
                grupos.append(row)
            JsonResponse(grupos, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(grupos, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_medico_sucursal(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "mes" not in payload.keys() or payload["mes"] is None \
                or payload["mes"] == 'null' \
                or payload["mes"] == '':
            return JsonResponse({'error': 'El campo: mes es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "sucursal" not in payload.keys() or payload["sucursal"] is None \
                or payload["sucursal"] == 'null' \
                or payload["sucursal"] == '':
            return JsonResponse({'error': 'El campo: sucursal es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        mes = payload["mes"]
        sucursal = payload["sucursal"]
        medico = payload["medico"]
        sql = "select t8.nombre,t7.examen,t7.precio_unitario from  (select t5.id_medico,t5.precio_unitario,t6.examen  from (select t3.id_medico,t4.precio_unitario, t4.id_examen from (select t1.id_consulta, t2.id_medico from (select id_consulta from resultados r where EXTRACT(MONTH FROM fecha_resultados) = {mes}) as t1 inner join (select id, id_medico from consulta c2 where id_medico = 106) as t2 on t1.id_consulta = t2.id) as t3 inner join (select id_consulta,sucursal_id,precio_unitario, id_examen from orden o2 where sucursal_id = {sucursal} ) as t4 on t3.id_consulta = t4.id_consulta) as t5 inner join  (select id, examen from examen e2 ) as t6 on t5.id_examen = t6.id) as t7 inner join  (select id,concat(nombre, ' ', apellidos) as nombre from medico m ) t8 on t7.id_medico = t8.id".format(mes=mes, sucursal=sucursal)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            grupos = []
            for index in range(cursor.rowcount):
                row = cursor.fetchone()
                grupos.append(row)
            JsonResponse(grupos, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(grupos, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_medicos_sucursal(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "mes" not in payload.keys() or payload["mes"] is None \
                or payload["mes"] == 'null' \
                or payload["mes"] == '':
            return JsonResponse({'error': 'El campo: mes es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "sucursal" not in payload.keys() or payload["sucursal"] is None \
                or payload["sucursal"] == 'null' \
                or payload["sucursal"] == '':
            return JsonResponse({'error': 'El campo: sucursal es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        mes = payload["mes"]
        sucursal = payload["sucursal"]
        sql = "select t8.nombre,t7.examen,t7.precio_unitario from  (select t5.id_medico,t5.precio_unitario,t6.examen  from (select t3.id_medico,t4.precio_unitario, t4.id_examen from (select t1.id_consulta, t2.id_medico from (select id_consulta from resultados r where EXTRACT(MONTH FROM fecha_resultados) = {mes}) as t1 inner join (select id, id_medico from consulta c2 ) as t2 on t1.id_consulta = t2.id) as t3 inner join (select id_consulta,sucursal_id,precio_unitario, id_examen from orden o2 where sucursal_id = {sucursal} ) as t4 on t3.id_consulta = t4.id_consulta) as t5 inner join  (select id, examen from examen e2 ) as t6 on t5.id_examen = t6.id) as t7 inner join  (select id,concat(nombre, ' ', apellidos) as nombre from medico m ) t8 on t7.id_medico = t8.id".format(mes=mes, sucursal=sucursal)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            grupos = []
            for index in range(cursor.rowcount):
                row = cursor.fetchone()
                grupos.append(row)
            JsonResponse(grupos, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(grupos, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_sucursal_grupo(request):
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
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        mes = payload["mes"]
        ano = payload["ano"]
        medico = payload["medico"]
        sql = "select t7.tipo,t7.grupo_id, t7.sucursal_id, t7.nombre_grupo, t8.nombre as nombre_sucursal from (select t5.tipo,t5.grupo_id, t5.sucursal_id, t6.nombre as nombre_grupo from (select t4.tipo,t4.grupo_id, t4.sucursal_id from (select t1.id_consulta, t2.id_medico from (select id_consulta from resultados r where EXTRACT(MONTH FROM fecha_resultados) = {mes} and EXTRACT(YEAR FROM fecha_resultados) = {ano}) as t1 inner join (select id, id_medico from consulta c2 where id_medico = {medico}) as t2 on t1.id_consulta = t2.id) as t3 inner join  (select distinct id_consulta,sucursal_id, tipo,grupo_id from orden) as t4 on t3.id_consulta = t4.id_consulta) as t5 left join  (select id,nombre from unidad_medica um ) as t6 on t5.grupo_id=t6.id) as t7 left join  (select id, nombre from sucursal s2 ) as t8 on t7.sucursal_id=t8.id".format(mes=mes, ano=ano, medico=medico)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            grupos_sucursales = []
            for index in range(cursor.rowcount):
                row = cursor.fetchone()
                grupos_sucursales.append(row)
            JsonResponse(grupos_sucursales, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(grupos_sucursales, safe=False)

