from django.db.models.functions import ExtractMonth
from psycopg2._psycopg import ProgrammingError
from django.db.models import Avg
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import exceptions, permissions
from rest_framework.permissions import AllowAny
from django.contrib.auth import login as django_login, logout as django_logout
from ..roles import ROLES
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from ..models import Medico, Especialidad, RatingMedico, MedicoSeguro, Seguro, \
    EventosCalendario, Paciente, IntervalosDisponibilidad, citasMedicas
import json
from ..serializers import MedicoSerializer, EventosCalendarioSerializer
from django.db import transaction
from django.db import IntegrityError
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
import shutil
from pism.settings import BASE_DIR
from django.core.mail import EmailMultiAlternatives
import datetime
from dateutil.parser import parse
from django.utils.timezone import get_current_timezone
from datetime import date
from django.utils import timezone
from dateutil.tz import tzutc, tzlocal
from django.db import connection

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_evento(request):
    payload = json.loads(request.body)
    if "titulo" not in payload.keys() and payload["titulo"] is None and payload["titulo"] == 'null' and payload["titulo"] == '':
        return JsonResponse({'error': 'El campo Titulo es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if "inicio" not in payload.keys() and payload["inicio"] is None and payload["inicio"] == 'null' and payload["inicio"] == '':
        return JsonResponse({'error': 'El campo Inicio es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if "fin" not in payload.keys() and payload["fin"] is None and payload["fin"] == 'null' and payload["fin"] == '':
        return JsonResponse({'error': 'El campo Inicio es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if "paciente" not in payload.keys() and payload["paciente"] is None and payload["paciente"] == 'null' and payload["paciente"] == '':
        return JsonResponse({'error': 'El campo Paciente es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if "medico" not in payload.keys() and payload["medico"] is None and payload["medico"] == 'null' and payload["medico"] == '':
        return JsonResponse({'error': 'El campo Paciente es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if "estado" not in payload.keys() and payload["estado"] is None and payload["estado"] == 'null' and payload["estado"] == '':
        return JsonResponse({'error': 'El campo Estado es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        obj = EventosCalendario()
        obj.titulo = payload["titulo"]
        obj.inicio = parse(payload["inicio"]).astimezone(tz=get_current_timezone())
        obj.fin = parse(payload["fin"]).astimezone(tz=get_current_timezone())
        obj.paciente = Paciente.objects.get(id=payload["paciente"])
        obj.motivo = payload["motivo"]
        obj.medico = Medico.objects.get(id=payload["medico"])
        obj.estado = payload["estado"]
        obj.save()
    except Paciente.DoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    except Medico.DoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse([], safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_eventos_medico(request):
    payload = json.loads(request.body)
    if "mes" not in payload.keys() or payload["mes"] is None or payload["mes"] == 'null' or payload["mes"] == '':
        return JsonResponse({'error': 'El campo Mes es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if "ano" not in payload.keys() or payload["ano"] is None or payload["ano"] == 'null' or payload["ano"] == '':
        return JsonResponse({'error': 'El campo Ano es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if "medico" not in payload.keys() or payload["medico"] is None or payload["medico"] == 'null' or payload["medico"] == '':
        return JsonResponse({'error': 'El campo Medico es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    lista_eventos = []
    for evento in EventosCalendario.objects.filter(medico=payload["medico"], inicio__year=payload["ano"], inicio__month=payload["mes"]).order_by('id'):
        evento_temp = {}
        evento_temp["title"] = evento.titulo
        # evento_temp["start"] = datetime.datetime.strptime(evento.inicio, "%Y-%m-%d %H:%M:%S").date().astimezone(tz=get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
        # evento_temp["start"] = evento.inicio.astimezone(tz=get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
        # evento_temp["end"] = evento.fin.astimezone(tz=get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
        evento_temp["id"] = evento.id
        evento_temp["start"] = evento.inicio
        evento_temp["end"] = evento.fin
        evento_temp["allDay"] = False
        evento_temp["idPaciente"] = evento.paciente.id
        if evento.consulta is not None:
            evento_temp["idConsulta"] = evento.consulta.id
        else:
            evento_temp["idConsulta"] = None
        evento_temp["estado"] = evento.estado
        lista_eventos.append(evento_temp)
    return JsonResponse(lista_eventos, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_todos_eventos(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo Medico es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "visible" not in payload.keys() or payload["visible"] is None \
                or payload["visible"] == 'null' \
                or payload["visible"] == '':
            return JsonResponse({'error': 'El campo Visible es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        lista_eventos = []
        for evento in EventosCalendario.objects.filter(medico=payload["medico"]).order_by('id'):
            evento_temp = {}
            if payload["visible"] == True:
                evento_temp["title"] = evento.titulo
                evento_temp["idPaciente"] = evento.paciente.id
                if evento.consulta is not None:
                    evento_temp["idConsulta"] = evento.consulta.id
                else:
                    evento_temp["idConsulta"] = None
                evento_temp["estado"] = evento.estado
            else:
                evento_temp["title"] = "Reservado"
                evento_temp["idPaciente"] = None
                evento_temp["idConsulta"] = None
                evento_temp["estado"] = "Agendado"

            evento_temp["id"] = evento.id
            evento_temp["start"] = evento.inicio
            evento_temp["end"] = evento.fin
            evento_temp["allDay"] = False

            lista_eventos.append(evento_temp)

    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(lista_eventos, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def proximo_evento_disponible(request):
    if request.method == 'POST':
        payload = json.loads(request.body)

        if "duracion" not in payload.keys() or payload["duracion"] is None \
                or payload["duracion"] == 'null' \
                or payload["duracion"] == '':
            return JsonResponse({'error': 'El campo Duracion es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if "primera_consulta" not in payload.keys() or payload["primera_consulta"] is None \
                or payload["primera_consulta"] == 'null' \
                or payload["primera_consulta"] == '':
            return JsonResponse({'error': 'El campo primera_consulta es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "ultima_consulta" not in payload.keys() or payload["ultima_consulta"] is None \
                or payload["ultima_consulta"] == 'null' \
                or payload["ultima_consulta"] == '':
            return JsonResponse({'error': 'El campo ultima_consulta es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if "dia" not in payload.keys() or payload["dia"] is None \
                or payload["dia"] == 'null' \
                or payload["dia"] == '':
            dia = None
        else:
            dia = payload["dia"]

        lista_eventos = []
        tz = get_current_timezone()
        print(tz)
        if dia is not None:
            for evento in EventosCalendario.objects.filter(inicio__date=payload["dia"]).order_by('id'):
                evento_temp = {}
                evento_temp["start"] = evento.inicio.astimezone(tzlocal()).strftime("%H:%M:%S")
                print(evento.inicio)
                print(tz.utcoffset(evento.inicio))
                evento_temp["end"] = evento.fin.astimezone(tzlocal()).strftime("%H:%M:%S")
                # evento_temp["start"] = evento.inicio.astimezone(tz=get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
                # evento_temp["end"] = evento.fin.astimezone(tz=get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
                lista_eventos.append(evento_temp)



    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(lista_eventos, safe=False)

''' Nueva funciones'''

def estaReservado(listaIntervalosReservados, horaIni, minIni, horaFin, minFin):
    for inter in listaIntervalosReservados:
        if inter["horaIni"] == horaIni and inter["minInicial"] == minIni and inter["horaFin"] == horaFin and inter["minutoFin"] == minFin:
            return True
    return False

def generaIntervalos(horaIntervaloInicial, minutoIntervaloInicial, horaIntervaloFinal, minutoIntervaloFinal, listaIntervalosReservados, duracion):
    print("Intervalo", listaIntervalosReservados)
    hora = horaIntervaloInicial
    minutos = minutoIntervaloInicial
    fin = False
    intervalosGenerados = []
    if minutoIntervaloInicial < 10:
        strMinutos = "0"+str(minutoIntervaloInicial)
    else:
        strMinutos = str(minutoIntervaloInicial)
    intervaloTemp = str(horaIntervaloInicial) + ":" + strMinutos

    while not fin:
        minAnt = minutos
        minutos = minutos + duracion
        if minutos == 60:
            horaAnt = hora
            hora = hora + 1
            minutos = 0
            if not estaReservado(listaIntervalosReservados, horaAnt, minAnt, hora, minutos):
                if minutos < 10:
                    strMinutos = "0" + str(minutos)
                else:
                    strMinutos = str(minutos)
                intervaloTemp = intervaloTemp + " - " + str(hora) + ":" + strMinutos
                intervalosGenerados.append(intervaloTemp)
            intervaloTemp = str(hora) + ":" + strMinutos
        elif minutos > 60:
            horaAnt = hora
            hora = hora + 1
            minutos = minutos - 60
            if not estaReservado(listaIntervalosReservados, horaAnt, minAnt, hora, minutos):
                if minutos < 10:
                    strMinutos = "0" + str(minutos)
                else:
                    strMinutos = str(minutos)
                intervaloTemp = intervaloTemp + " - " + str(hora) + ":" + strMinutos
                intervalosGenerados.append(intervaloTemp)
            intervaloTemp = str(hora) + ":" + strMinutos
        if hora == horaIntervaloFinal and minutos >= minutoIntervaloFinal or hora > horaIntervaloFinal:
            fin = True
    return intervalosGenerados


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def disponibilidad_dia(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "dia" not in payload.keys() or payload["dia"] is None \
                or payload["dia"] == 'null' \
                or payload["dia"] == '':
            return JsonResponse({'error': 'El campo: dia es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        arrDiasSemana = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
        dia = payload["dia"]
        medico = payload["medico"]

        datetimeobj = datetime.datetime.strptime(dia, "%Y-%m-%d")
        diaSemana = datetimeobj.weekday()
        print(dia, arrDiasSemana[diaSemana])
        sql = "select t1.id,t1.dis_inicio,t1.dis_fin,t2.inicio,t2.fin,t1.duracion from (select id, inicio as dis_inicio, fin as dis_fin, duracion from intervalos_disponibilidad ind where dia_semana = '{diasemana}' and id_medico = {idmedico} and activo = true) as t1 left join (select inicio, fin, id_intervalo from citas_medicas cm where CAST(fecha_cita AS DATE)  = '{dia}') as t2 on t1.id = t2.id_intervalo order by dis_inicio, id".format(diasemana=arrDiasSemana[diaSemana], idmedico=medico, dia=dia)
        # print(sql)
        intervalosGeneradosResult = []
        with connection.cursor() as cursor:
            cursor.execute(sql)
            intervaloActual = -1
            listaIntervalosReservados = []
            for index in range(cursor.rowcount):
                row = cursor.fetchone()
                if intervaloActual == -1:   # primera vez
                    intervaloTemp = {"horaIni": -1, "minInicial": -1, "horaFin": -1, "minutoFin": -1}
                    horaIntervaloInicial = row[1].hour
                    minutoIntervaloInicial = row[1].minute
                    horaIntervaloFinal = row[2].hour
                    minutoIntervaloFinal = row[2].minute
                    duracion = row[5]
                    if row[3] is not None:
                        intervaloTemp["horaIni"] = row[3].hour
                        intervaloTemp["minInicial"] = row[3].minute
                        intervaloTemp["horaFin"] = row[4].hour
                        intervaloTemp["minutoFin"] = row[4].minute
                    intervaloActual = row[0]
                    listaIntervalosReservados.append(intervaloTemp)
                elif intervaloActual == row[0]:
                    intervaloTemp = {}
                    intervaloTemp["horaIni"] = row[3].hour
                    intervaloTemp["minInicial"] = row[3].minute
                    intervaloTemp["horaFin"] = row[4].hour
                    intervaloTemp["minutoFin"] = row[4].minute
                    duracion = row[5]
                    listaIntervalosReservados.append(intervaloTemp)
                else:
                    intervalosGenerados = generaIntervalos(horaIntervaloInicial, minutoIntervaloInicial, horaIntervaloFinal, minutoIntervaloFinal, listaIntervalosReservados, duracion)
                    intervalosGeneradosResult = intervalosGeneradosResult + intervalosGenerados
                    listaIntervalosReservados = []

                    intervaloTemp = {"horaIni": -1, "minInicial": -1, "horaFin": -1, "minutoFin": -1}
                    horaIntervaloInicial = row[1].hour
                    minutoIntervaloInicial = row[1].minute
                    horaIntervaloFinal = row[2].hour
                    minutoIntervaloFinal = row[2].minute
                    duracion = row[5]

                    if row[3] is not None:
                        intervaloTemp["horaIni"] = row[3].hour
                        intervaloTemp["minInicial"] = row[3].minute
                        intervaloTemp["horaFin"] = row[4].hour
                        intervaloTemp["minutoFin"] = row[4].minute

                    intervaloActual = row[0]
                    listaIntervalosReservados.append(intervaloTemp)
                print(row)
            intervalosGenerados = generaIntervalos(horaIntervaloInicial, minutoIntervaloInicial, horaIntervaloFinal, minutoIntervaloFinal, listaIntervalosReservados, duracion)
            intervalosGeneradosResult = intervalosGeneradosResult + intervalosGenerados
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(intervalosGeneradosResult, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_disponibilidad_doctor(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        medico = payload["medico"]
        intervalo = []
        for inter in IntervalosDisponibilidad.objects.filter(medico=medico, activo=True).order_by('inicio'):
            dispo = {}
            dispo["id"] = inter.id
            dispo["dia_semana"] = inter.dia_semana
            dispo["inicio"] = inter.inicio
            dispo["fin"] = inter.fin
            dispo["duracion"] = inter.duracion
            intervalo.append(dispo)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(intervalo, safe=False)


def disponibilidad_doctor(id):
        intervalo = []
        for inter in IntervalosDisponibilidad.objects.filter(medico=id, activo=True).order_by('inicio'):
            dispo = {}
            dispo["id"] = inter.id
            dispo["dia_semana"] = inter.dia_semana
            dispo["inicio"] = inter.inicio
            dispo["fin"] = inter.fin
            dispo["duracion"] = inter.duracion
            intervalo.append(dispo)

# devuelve la disponibilidad del medico dado un paciente en particular
def disponibilidad(dia, medico, paciente):
    arrDiasSemana = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
    datetimeobj = datetime.datetime.strptime(dia, "%Y-%m-%d")
    diaSemana = datetimeobj.weekday()
    print(dia, arrDiasSemana[diaSemana])

    sql = "select t1.id,t1.dis_inicio,t1.dis_fin, t2.id_paciente, t2.id as id_cita from (select id, inicio as dis_inicio, fin as dis_fin from intervalos_disponibilidad ind where dia_semana = '{diasemana}' and id_medico = {idmedico} and activo = true) as t1 left join (select id_intervalo, id_paciente, id from citas_medicas cm where CAST(fecha_cita AS DATE)  = '{dia}' ) as t2 on t1.id = t2.id_intervalo order by dis_inicio".format(
        diasemana=arrDiasSemana[diaSemana], idmedico=medico, dia=dia)
    # print(sql)
    intervalosGeneradosResult = []
    with connection.cursor() as cursor:
        cursor.execute(sql)
        listaIntervalos = []
        for index in range(cursor.rowcount):
            row = cursor.fetchone()
            intervaloTemp = {}
            if row[3] is None:
                intervaloTemp["id"] = row[0]
                intervaloTemp["inicio"] = row[1]
                intervaloTemp["fin"] = row[2]
                intervaloTemp["estado"] = "DISPONIBLE"
                intervaloTemp["cita"] = None
                listaIntervalos.append(intervaloTemp)
            elif row[3] == paciente:
                intervaloTemp["id"] = row[0]
                intervaloTemp["inicio"] = row[1]
                intervaloTemp["fin"] = row[2]
                intervaloTemp["estado"] = "AGENDADO"
                intervaloTemp["cita"] = row[4]
                listaIntervalos.append(intervaloTemp)
            print(row)
    return listaIntervalos



@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def disponibilidad_doctor_dia(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "paciente" not in payload.keys() or payload["paciente"] is None \
                or payload["paciente"] == 'null' \
                or payload["paciente"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "dia" not in payload.keys() or payload["dia"] is None \
                or payload["dia"] == 'null' \
                or payload["dia"] == '':
            return JsonResponse({'error': 'El campo: dia es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        arrDiasSemana = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
        dia = payload["dia"]
        medico = payload["medico"]
        paciente = payload["paciente"]
        # Busca los intervalos del dia disponible
        listaIntervalos = disponibilidad(dia, medico, paciente)
        # datetimeobj = datetime.datetime.strptime(dia, "%Y-%m-%d")
        # diaSemana = datetimeobj.weekday()
        # print(dia, arrDiasSemana[diaSemana])
        #
        # sql = "select t1.id,t1.dis_inicio,t1.dis_fin, t2.id_paciente, t2.id as id_consulta from (select id, inicio as dis_inicio, fin as dis_fin from intervalos_disponibilidad ind where dia_semana = '{diasemana}' and id_medico = {idmedico} and activo = true) as t1 left join (select id_intervalo, id_paciente, id from citas_medicas cm where CAST(fecha_cita AS DATE)  = '{dia}' ) as t2 on t1.id = t2.id_intervalo order by dis_inicio".format(diasemana=arrDiasSemana[diaSemana], idmedico=medico, dia=dia)
        # # print(sql)
        # intervalosGeneradosResult = []
        # with connection.cursor() as cursor:
        #     cursor.execute(sql)
        #     listaIntervalos = []
        #     for index in range(cursor.rowcount):
        #         row = cursor.fetchone()
        #         intervaloTemp = {}
        #         if row[3] is None:
        #             intervaloTemp["id"] = row[0]
        #             intervaloTemp["inicio"] = row[1]
        #             intervaloTemp["fin"] = row[2]
        #             intervaloTemp["estado"] = "DISPONIBLE"
        #             intervaloTemp["consulta"] = None
        #             listaIntervalos.append(intervaloTemp)
        #         elif row[3] == paciente:
        #             intervaloTemp["id"] = row[0]
        #             intervaloTemp["inicio"] = row[1]
        #             intervaloTemp["fin"] = row[2]
        #             intervaloTemp["estado"] = "AGENDADO"
        #             intervaloTemp["consulta"] = row[4]
        #             listaIntervalos.append(intervaloTemp)
        #         print(row)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(listaIntervalos, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def primera_disponibilidad(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "paciente" not in payload.keys() or payload["paciente"] is None \
                or payload["paciente"] == 'null' \
                or payload["paciente"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        medico = payload["medico"]
        paciente = payload["paciente"]
        primera_disponibilidad_result = {}
        sql = "select t3.fecha_cita, t4.disponibles - t3.reservadas as dif from (select t1.dia_semana, t2.fecha_cita, count(*) as reservadas from (select id, dia_semana from intervalos_disponibilidad where id_medico = {idmedico} and activo = true) as t1 inner join (select fecha_cita, id_intervalo from citas_medicas) as t2 on t1.id = t2.id_intervalo group by dia_semana, fecha_cita) as t3 inner join (select dia_semana, count(*) as disponibles from intervalos_disponibilidad id where id_medico = {idmedico} and activo = true group by dia_semana) as t4 on t3.dia_semana=t4.dia_semana where t4.disponibles - t3.reservadas = 0".format(idmedico=medico)
        # print(sql)
        intervalosGeneradosResult = []
        with connection.cursor() as cursor:
            cursor.execute(sql)
            fechas_completamente_reservadas = set()
            for index in range(cursor.rowcount):
                row = cursor.fetchone()
                ano_str = str(row[0].year)
                if row[0].month < 10:
                    mes_str = "0" + str(row[0].month)
                else:
                    mes_str = str(row[0].month)
                if row[0].day < 10:
                    dia_str = "0" + str(row[0].day)
                else:
                    dia_str = str(row[0].day)
                date_str = ano_str + "-" + mes_str + "-" + dia_str
                fechas_completamente_reservadas.add(date_str)
            print(fechas_completamente_reservadas)
            # busca la primera disponibilidad
            disponibilidad_encontrada = False
            fecha_actual = datetime.datetime.today()
            day_count = 1
            # fechas_completamente_reservadas = {'2021-09-12', '2021-09-14', '2021-09-16'}
            while disponibilidad_encontrada == False:
                fecha_str = str(fecha_actual).split()[0]
                if fecha_str in fechas_completamente_reservadas:
                    fecha_actual = fecha_actual + datetime.timedelta(days=1)
                else:
                    disponibilidad_encontrada = True
            print("nueva fecha", fecha_str)

        # Busca los intervalos del dia disponible
        listaIntervalos = disponibilidad(fecha_str, payload["medico"], payload["paciente"])
        # arrDiasSemana = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
        # datetimeobj = datetime.datetime.strptime(fecha_str, "%Y-%m-%d")
        # diaSemana = datetimeobj.weekday()
        # sql = "select t1.id,t1.dis_inicio,t1.dis_fin, t2.id_paciente, t2.id as id_consulta from (select id, inicio as dis_inicio, fin as dis_fin from intervalos_disponibilidad ind where dia_semana = '{diasemana}' and id_medico = {idmedico} and activo = true) as t1 left join (select id_intervalo, id_paciente, id from citas_medicas cm where CAST(fecha_cita AS DATE)  = '{dia}' ) as t2 on t1.id = t2.id_intervalo order by dis_inicio".format(
        #     diasemana=arrDiasSemana[diaSemana], idmedico=medico, dia=fecha_str)
        # print(sql)
        # intervalosGeneradosResult = []
        # with connection.cursor() as cursor:
        #     cursor.execute(sql)
        #     listaIntervalos = []
        #     for index in range(cursor.rowcount):
        #         row = cursor.fetchone()
        #         intervaloTemp = {}
        #         if row[3] is None:
        #             intervaloTemp["id"] = row[0]
        #             intervaloTemp["inicio"] = row[1]
        #             intervaloTemp["fin"] = row[2]
        #             intervaloTemp["estado"] = "DISPONIBLE"
        #             intervaloTemp["consulta"] = None
        #             listaIntervalos.append(intervaloTemp)
        #         elif row[3] == paciente:
        #             intervaloTemp["id"] = row[0]
        #             intervaloTemp["inicio"] = row[1]
        #             intervaloTemp["fin"] = row[2]
        #             intervaloTemp["estado"] = "AGENDADO"
        #             intervaloTemp["consulta"] = row[4]
        #             listaIntervalos.append(intervaloTemp)
        #         print(row)
        primera_disponibilidad_result["dia"] = fecha_str
        primera_disponibilidad_result["disponibilidad"] = listaIntervalos
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse(primera_disponibilidad_result, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def agendar_cita(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "inicio" not in payload.keys() or payload["inicio"] is None \
                or payload["inicio"] == 'null' \
                or payload["inicio"] == '':
            return JsonResponse({'error': 'El campo: inicio es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "fin" not in payload.keys() or payload["fin"] is None \
                or payload["fin"] == 'null' \
                or payload["fin"] == '':
            return JsonResponse({'error': 'El campo: fin es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "paciente" not in payload.keys() or payload["paciente"] is None \
                or payload["paciente"] == 'null' \
                or payload["paciente"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "fecha" not in payload.keys() or payload["fecha"] is None \
                or payload["fecha"] == 'null' \
                or payload["fecha"] == '':
            return JsonResponse({'error': 'El campo: fecha es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "intervalo" not in payload.keys() or payload["intervalo"] is None \
                or payload["intervalo"] == 'null' \
                or payload["intervalo"] == '':
            return JsonResponse({'error': 'El campo: intervalo es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "motivo" not in payload.keys():
            return JsonResponse({'error': 'El campo: intervalo es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            obj = citasMedicas()
            obj.inicio = payload["inicio"]
            obj.fin = payload["fin"]
            obj.duracion = 60
            obj.fecha_cita = payload["fecha"]
            obj.intervalo_disponibilidad = IntervalosDisponibilidad.objects.get(id=payload["intervalo"])
            obj.medico = Medico.objects.get(id=payload["medico"])
            obj.paciente = Paciente.objects.get(id=payload["paciente"])
            obj.consulta = None
            obj.motivo = payload["motivo"]

            obj.estado = "AGENDADO"

            obj.save()
            lista_diaponibilidad = disponibilidad(payload["fecha"], payload["medico"], payload["paciente"])
            return JsonResponse(lista_diaponibilidad, safe=False, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return JsonResponse({'error': 'There is already a record with that data'}, safe=False,
                                status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse([], safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def cancelar_cita(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "id" not in payload.keys() or payload["id"] is None \
                or payload["id"] == 'null' \
                or payload["id"] == '':
            return JsonResponse({'error': 'El campo: id es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            with transaction.atomic():
                obj = citasMedicas.objects.get(pk=int(payload["id"]))
                dia = obj.fecha_cita.strftime("%Y-%m-%d")
                print(obj.fecha_cita.strftime("%Y-%m-%d"))
                medico = obj.medico.id
                paciente = obj.paciente.id
                obj.delete()
                lista_diaponibilidad = disponibilidad(dia, medico, paciente)
                return JsonResponse(lista_diaponibilidad, safe=False, status=status.HTTP_201_CREATED)
        except Especialidad.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return JsonResponse({'error': 'There is already a record with that data'}, safe=False,
                                status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse([], safe=False)


def disponibilidad_todos_pacientes(medico, dia):
    arrDiasSemana = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
    datetimeobj = datetime.datetime.strptime(dia, "%Y-%m-%d")
    diaSemana = datetimeobj.weekday()

    print(dia, arrDiasSemana[diaSemana])

    sql = "select t3.id,t3.dis_inicio,t3.dis_fin, t3.id_cita, t3.id_consulta, t4.id as id_paciente, t4.nombre,t4.apellidos, t3.motivo from (select t1.id,t1.dis_inicio,t1.dis_fin, t2.id_paciente, t2.id as id_cita, t2.id_consulta, t2.motivo from (select id, inicio as dis_inicio, fin as dis_fin from intervalos_disponibilidad ind where dia_semana = '{diasemana}' and id_medico = {idmedico} and activo = true) as t1 left join (select id_intervalo, id_paciente, id, id_consulta, motivo from citas_medicas cm where CAST(fecha_cita AS DATE)  = '{dia}' ) as t2 on t1.id = t2.id_intervalo order by dis_inicio) as t3 left join (select id,nombre, apellidos from paciente) as t4 on t3.id_paciente = t4.id order by t3.dis_inicio".format(
        diasemana=arrDiasSemana[diaSemana], idmedico=medico, dia=dia)
    print(sql)
    intervalosGeneradosResult = []
    with connection.cursor() as cursor:
        cursor.execute(sql)
        listaIntervalos = []
        for index in range(cursor.rowcount):
            row = cursor.fetchone()
            intervaloTemp = {}
            if row[3] is None:
                intervaloTemp["id"] = row[0]
                intervaloTemp["inicio"] = row[1]
                intervaloTemp["fin"] = row[2]
                intervaloTemp["estado"] = "DISPONIBLE"
                intervaloTemp["cita"] = None
                intervaloTemp["consulta"] = None
                intervaloTemp["id_paciente"] = None
                intervaloTemp["paciente"] = None
                intervaloTemp["motivo"] = None
                listaIntervalos.append(intervaloTemp)
            elif row[3] is not None:
                intervaloTemp["id"] = row[0]
                intervaloTemp["inicio"] = row[1]
                intervaloTemp["fin"] = row[2]
                intervaloTemp["estado"] = "AGENDADO"
                intervaloTemp["cita"] = row[3]
                intervaloTemp["consulta"] = row[4]
                intervaloTemp["id_paciente"] = row[5]
                intervaloTemp["paciente"] = str(row[6]) + " " + str(row[7])
                intervaloTemp["motivo"] = row[8]
                listaIntervalos.append(intervaloTemp)
            print(row[3])
        return listaIntervalos
    return []


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def agenda_medico(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "fecha" not in payload.keys() or payload["fecha"] is None \
                or payload["fecha"] == 'null' \
                or payload["fecha"] == '':
            return JsonResponse({'error': 'El campo: fecha es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        dia = payload["fecha"]
        medico = payload["medico"]
        listaIntervalos = disponibilidad_todos_pacientes(medico, dia)
        return JsonResponse(listaIntervalos, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse([], safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def reagendar_cita(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "medico" not in payload.keys() or payload["medico"] is None \
                or payload["medico"] == 'null' \
                or payload["medico"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "cita" not in payload.keys() or payload["cita"] is None \
                or payload["cita"] == 'null' \
                or payload["cita"] == '':
            return JsonResponse({'error': 'El campo: medico es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "fecha" not in payload.keys() or payload["fecha"] is None \
                or payload["fecha"] == 'null' \
                or payload["fecha"] == '':
            return JsonResponse({'error': 'El campo: fecha es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "intervalo" not in payload.keys() or payload["intervalo"] is None \
                or payload["intervalo"] == 'null' \
                or payload["intervalo"] == '':
            return JsonResponse({'error': 'El campo: intervalo es obligatorio'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        obj = citasMedicas.objects.get(pk=int(payload["cita"]))
        fecha_cita_anterior = obj.fecha_cita
        obj.fecha_cita=payload["fecha"]
        obj.intervalo_disponibilidad=IntervalosDisponibilidad.objects.get(id=payload["intervalo"])
        obj.save()
        listaIntervalos = disponibilidad_todos_pacientes(payload["medico"], fecha_cita_anterior.strftime("%Y-%m-%d"))
        return JsonResponse(listaIntervalos, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse([], safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def cancelar_cita_medico(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if "id" not in payload.keys() or payload["id"] is None \
                or payload["id"] == 'null' \
                or payload["id"] == '':
            return JsonResponse({'error': 'El campo: id es obligatorio'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            with transaction.atomic():
                obj = citasMedicas.objects.get(pk=int(payload["id"]))
                dia = obj.fecha_cita.strftime("%Y-%m-%d")
                print(obj.fecha_cita.strftime("%Y-%m-%d"))
                medico = obj.medico.id
                obj.delete()
                lista_diaponibilidad = disponibilidad_todos_pacientes(medico, dia)
                return JsonResponse(lista_diaponibilidad, safe=False, status=status.HTTP_201_CREATED)
        except Especialidad.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return JsonResponse({'error': 'There is already a record with that data'}, safe=False,
                                status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return JsonResponse([], safe=False)
