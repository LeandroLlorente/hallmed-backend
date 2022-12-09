from operator import attrgetter
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
from ..models import Medico, Provincia, Canton, Parroquia, Especialidad, RatingMedico, MedicoSeguro, Seguro, \
    IntervalosDisponibilidad, citasMedicas
import json
from ..serializers import MedicoSerializer
from django.db import transaction
from django.db import IntegrityError
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
import shutil
from pism.settings import BASE_DIR, EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives


@api_view(['GET'])
def list_medico(request):
    tipo = Medico.objects.filter().order_by('id')
    tipoSerializer = MedicoSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_medico_no_activos(request):
    tipo = Medico.objects.filter(activado=False).order_by('id')
    tipoSerializer = MedicoSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def valida_medico(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id = payload["id"]
        validacion = payload["validacion"]
        razon = payload["razon"]
        try:
            if id is not None and validacion is not None:

                if validacion == True:
                    medico = Medico.objects.get(pk=id)
                    medico.activado = True
                    emailMedico = medico.email
                    medico.save()

                    user = User.objects.get(pk=medico.user.id)
                    user.is_active = True
                    user.save()
                    medgroup = Group.objects.get(name='MEDICO')
                    try:
                        user.groups.add(medgroup)
                    except ProgrammingError as e:
                        print('error:', str(e))

                    tabla = Medico.objects.filter(
                        activado=False).order_by('id')
                    tabla_serializer = MedicoSerializer(tabla, many=True)

                    # envia un correo de notificacion
                    subject = 'Registro en la Plataforma culminado con exito'
                    from_email = EMAIL_HOST_USER  # 'plataforma.integral.servicios@gmail.com'
                    recipient_list = [emailMedico]
                    text_content = 'Registro en la Plataforma culminado con exito'
                    html_content = '<h2>¡FELICITACIONES, YA ERES PARTE DE ESTA GRAN COMUNIDAD!</h2>' \
                                   '<h4><p>Es grato informarle que su solicitud ha sido <strong>APROBADA</strong></p>' \
                                   '<p>Nuestro equipo de trabajo se siente honrado de contar con usted como miembro importante de nuestra comunidad.</p>' \
                                   '<p>Para que otros profesionales se puedan beneficiar utilizando nuestra plataforma, por favor, comparte el siguiente enlace con tus colegas:</p>' \
                                   '<p><a href="http://www.plataformamedica.org">http://www.plataformamedica.org</a></p>' \
                                   '<p>“JUNTOS PODEMOS”</p>' \
                                   '<p>Muchas Gracias.</p></h4>'

                    msg = EmailMultiAlternatives(
                        subject, text_content, from_email, recipient_list)
                    msg.attach_alternative(html_content, "text/html")

                    try:
                        msg.send()
                    except BaseException as e:
                        print("<error> (valida_medico) [send mail]: ", str(e))

                    return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
                else:
                    medico = Medico.objects.get(pk=id)
                    emailMedico = medico.email
                    # send_mail(
                    #     subject='Sus solicitud de  registro en la plataforma no ha sido aceptada',
                    #     message=razon,
                    #     from_email='plataforma.integral.servicios@gmail.com',
                    #     recipient_list=[medico.email],
                    #     fail_silently=False,
                    # )

                    # envia un correo de notificacion
                    subject = 'Sus solicitud de  registro en la plataforma no ha sido aceptada'
                    from_email = EMAIL_HOST_USER  # 'plataforma.integral.servicios@gmail.com'
                    recipient_list = [emailMedico]
                    text_content = 'Sus solicitud de  registro en la plataforma no ha sido aceptada'
                    html_content = '<h4><p>Lamentablemente su solicitud NO ha sido APROBADA.</p>' \
                                   '<p>Detallamos a continuación los motivos:</p>' \
                                   '<p>' + razon + '</p>' \
                                   '<p>Para solucionar esta situación, por favor contáctenos.</p>' \
                                   '<p>“JUNTOS PODEMOS”</p>' \
                                   '<p>Muchas Gracias.</p></h4>'

                    msg = EmailMultiAlternatives(
                        subject, text_content, from_email, recipient_list)
                    msg.attach_alternative(html_content, "text/html")

                    try:
                        msg.send()
                    except BaseException as e:
                        print("<error> (valida_medico) [send mail]: ", str(e))

                    tabla = Medico.objects.filter(
                        activado=False).order_by('id')
                    tabla_serializer = MedicoSerializer(tabla, many=True)
                    return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
            else:
                msg = "Missing information"
                return JsonResponse({'error': '{}'.format(msg)}, safe=False, status=status.HTTP_400_BAD_REQUEST)
        except Medico.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
@api_view(['POST'])
def delete_medico_no_validado(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            with transaction.atomic():
                medico = Medico.objects.get(pk=int(payload["id"]))
                user_temp = User.objects.get(id=medico.user_id)
                # borra los ficheros asociados
                folderSene = str(BASE_DIR) + '/media/' + medico.dirnameSene()
                shutil.rmtree(folderSene, ignore_errors=True)
                folderAcess = str(BASE_DIR) + '/media/' + medico.dirnameAcess()
                shutil.rmtree(folderAcess, ignore_errors=True)
                medico.delete()
                user_temp.delete()

                tabla = Medico.objects.filter(activado=False).order_by('id')
                tabla_serializer = MedicoSerializer(tabla, many=True)
                return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except Medico.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return JsonResponse({'error': 'There is already a record with that data'}, safe=False,
                                status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
@api_view(['POST'])
def delete_medico(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            with transaction.atomic():
                obj = Medico.objects.get(pk=int(payload["id"]))
                user_temp = User.objects.get(id=obj.user_id)
                print(user_temp.id)
                obj.delete()
                user_temp.delete()
                tabla = Medico.objects.filter().order_by('id')
                tabla_serializer = MedicoSerializer(tabla, many=True)
                return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except Medico.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return JsonResponse({'error': 'There is already a record with that data'}, safe=False,
                                status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([])
@api_view(['POST'])
def register_medico(request):
    print(request)
    user = request.user
    if user.is_superuser:
        email = request.data.get("email")
        username = request.data.get("username")
        first = request.data.get("first")
        last = request.data.get("last")
        password = request.data.get("password")
        role = request.data.get("role")
        if username and \
                password and \
                first and \
                last and \
                email and \
                role:
            username_query_set = User.objects.filter(
                Q(username=username) | Q(email=email))
            if not username_query_set:
                user = User.objects.create_user(username, email, password)
                user.first_name = first
                user.last_name = last
                user.is_superuser = False
                user.is_active = False
                user.save()

                medico = Medico.objects.create(user=user)
                medico.nombre = request.data.get("first")
                medico.apellidos = request.data.get("last")
                # medico.codigoMedico = request.data.get("codigo")
                # medico.telefono = request.data.get("telefono")
                medico.email = request.data.get("email")
                medico.regSene = request.data.get("regSene")
                medico.regAcess = request.data.get("regAcess")
                medico.activado = False
                medico.save()

                subject = 'Notificación de registro en la Plataforma'
                from_email = EMAIL_HOST_USER  # 'plataforma.integral.servicios@gmail.com'
                recipient_list = [medico.email]
                text_content = 'Notificación de registro en la Plataforma'
                html_content = '<h2>¡BIENVENIDO!</h2>' \
                               '<h4><p>Primeramente, agradecemos su interés en formar parte de esta gran comunidad de profesionales de la salud.</p>' \
                               '<p>Por motivos de seguridad, en un período de 24h a 48h recibirá un correo electrónico de notificación y así podrá acceder a la plataforma.</p>' \
                               '<p>“JUNTOS PODEMOS”</p>' \
                               '<p>Muchas Gracias.</p></h4>'

                msg = EmailMultiAlternatives(
                    subject, text_content, from_email, recipient_list)
                msg.attach_alternative(html_content, "text/html")
                try:
                    msg.send()
                except BaseException as e:
                    print(
                        "<error> (register_unidad_medico) [send mail]: ", str(e))

                response = {
                    "message": 'Successfully created',
                    "email": user.email,
                    "user": user.username,
                    "first": user.first_name,
                    "last": user.last_name,
                    'role': role,
                }
                return Response(response, 200)
            else:
                msg = "The email and username fields have to be uniques"
                return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            msg = "You most provide a valid user information"
            return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                                status=status.HTTP_400_BAD_REQUEST)
    else:
        msg = 'This user has not permissions to performs this operation',
        return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                            status=status.HTTP_400_BAD_REQUEST)


# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_profile_medico(request):
    # user = request.user
    id = request.user.id
    medico = Medico.objects.get(user_id=id)
    perfil_medico = {
        "id": medico.id,
        "fullname": medico.nombre + " " + medico.apellidos,
        "cedula": medico.cedula,
        "codigo": medico.codigo,
        "cod_telefono_pais": medico.cod_telefono_pais,
        "telefono": medico.telefono,
        "telefono_cita": medico.telefono_cita,
        "direccion_consultorio": medico.direccion_consultorio,
        "referencia_consultorio": medico.referencia_consultorio,
        "estudios": medico.estudios,
        "experiencia": medico.experiencia,
        "seguro": medico.seguro,
        "precio": medico.precio,
    }
    return JsonResponse(perfil_medico, safe=False, status=status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_medico_disponibilidad(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        # print("<update_medico_disponibilidad>",payload)
        disponibilidad = json.loads(payload["disponibilidad"])
        id_medico = payload["id"]
        precio = float(payload["precio_consulta"])
        medico = Medico.objects.get(id=int(id_medico))
        medico.precio = precio
        medico.save()
        citas_intervalos = {
            cita.intervalo_disponibilidad.id for cita in citasMedicas.objects.filter(medico=id_medico)}
        try:
            with transaction.atomic():

                for obj in IntervalosDisponibilidad.objects.filter(medico=int(id_medico)):
                    if obj.id in citas_intervalos:      # hay citas en el intervalo que se quiere eliminar
                        obj.activo = False
                        obj.save()
                    else:
                        obj.delete()

                for disponibilidad_dia in disponibilidad:
                    intervalo_disp_temp = IntervalosDisponibilidad()
                    intervalo_disp_temp.dia_semana = disponibilidad_dia["dia_semana"]
                    intervalo_disp_temp.inicio = disponibilidad_dia["inicio"]
                    intervalo_disp_temp.fin = disponibilidad_dia["fin"]
                    intervalo_disp_temp.duracion = disponibilidad_dia["duracion"]
                    intervalo_disp_temp.medico = medico
                    intervalo_disp_temp.activo = True
                    intervalo_disp_temp.save()

                return JsonResponse({'Result': 'OK'}, status=status.HTTP_200_OK)
        except IntervalosDisponibilidad.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)

            # return JsonResponse({'error': 'There is already a record with that data'}, safe=False, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_seguro_medico(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        seguros_medico = json.loads(payload["seguro"])
        id_medico = payload["id"]
        # borra los seguros del medico
        for seguro in MedicoSeguro.objects.filter(medico=id_medico):
            seguro.delete()

        # adiciona los seguros del medico
        for seguro in seguros_medico:
            seguroMedicoTemp = MedicoSeguro()
            seguroMedicoTemp.seguro = Seguro.objects.get(pk=seguro)
            seguroMedicoTemp.medico = Medico.objects.get(pk=id_medico)
            seguroMedicoTemp.save()

        return JsonResponse({'Result': 'OK'}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_curriculo_medico(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        estudio = payload["estudio"]
        experiencia = payload["experiencia"]
        id_medico = payload["id"]
        medico = Medico.objects.get(id=id_medico)
        if estudio is not None and estudio != "null":
            medico.estudios = estudio
        if experiencia is not None and experiencia != "null":
            medico.experiencia = experiencia
        medico.save()
        return JsonResponse({'Result': 'OK'}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_especialidad_medico(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_medico = payload["id"]
        especialidad1 = payload["especialidad1"]
        especialidad2 = payload["especialidad2"]
        subespecialidad1 = payload["subespecialidad1"]
        subespecialidad2 = payload["subespecialidad2"]
        medico = Medico.objects.get(id=id_medico)
        if especialidad1 is not None and especialidad1 != 'null':
            medico.especialidad1 = Especialidad.objects.get(id=especialidad1)
        if especialidad2 is not None and especialidad2 != 'null':
            medico.especialidad2 = Especialidad.objects.get(id=especialidad2)
        if subespecialidad1 is not None and subespecialidad1 != 'null':
            medico.subespecialidad1 = subespecialidad1
        if subespecialidad2 is not None and subespecialidad2 != 'null':
            medico.subespecialidad2 = subespecialidad2
        medico.save()
        return JsonResponse({'Result': 'OK'}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_consultorio_medico(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_medico = payload["id"]
        direccion_consultorio1 = payload["direccion_consultorio1"]
        direccion_consultorio2 = payload["direccion_consultorio2"]
        referencia_consultorio1 = payload["referencia_consultorio1"]
        referencia_consultorio2 = payload["referencia_consultorio2"]
        latitud1 = payload["latitud1"]
        longitud1 = payload["longitud1"]
        latitud2 = payload["latitud2"]
        longitud2 = payload["longitud2"]
        provincia1 = payload["provincia1"]
        provincia2 = payload["provincia2"]
        canton1 = payload["canton1"]
        canton2 = payload["canton2"]
        parroquia1 = payload["parroquia1"]
        parroquia2 = payload["parroquia2"]
        telefono_cita1 = payload["telefono_cita1"]
        telefono_cita2 = payload["telefono_cita2"]
        medico = Medico.objects.get(id=id_medico)
        if direccion_consultorio1 is not None and direccion_consultorio1 != "null":
            medico.direccion_consultorio1 = direccion_consultorio1
        if direccion_consultorio2 is not None and direccion_consultorio2 != "null":
            medico.direccion_consultorio2 = direccion_consultorio2
        if referencia_consultorio1 is not None and referencia_consultorio1 != "null":
            medico.referencia_consultorio1 = referencia_consultorio1
        if referencia_consultorio2 is not None and referencia_consultorio2 != "null":
            medico.referencia_consultorio2 = referencia_consultorio2
        if latitud1 is not None and latitud1 != "null":
            medico.lat1 = latitud1
        if longitud1 is not None and longitud1 != "null":
            medico.lon1 = longitud1
        if latitud2 is not None and latitud2 != "null":
            medico.lat2 = latitud2
        if longitud2 is not None and longitud2 != "null":
            medico.lon2 = longitud2
        if provincia1 is not None and provincia1 != 'null':
            medico.provincia1 = Provincia.objects.get(id=provincia1)
        if provincia2 is not None and provincia2 != 'null':
            medico.provincia2 = Provincia.objects.get(id=provincia2)
        if canton1 is not None and canton1 != 'null':
            medico.canton1 = Canton.objects.get(id=canton1)
        if canton2 is not None and canton2 != 'null':
            medico.canton2 = Canton.objects.get(id=canton2)
        if parroquia1 is not None and parroquia1 != 'null':
            medico.parroquia1 = Parroquia.objects.get(id=parroquia1)
        if parroquia2 is not None and parroquia2 != 'null':
            medico.parroquia2 = Parroquia.objects.get(id=parroquia2)
        if telefono_cita1 is not None and telefono_cita1 != "null":
            medico.telefono_cita1 = telefono_cita1
        if telefono_cita2 is not None and telefono_cita2 != "null":
            medico.telefono_cita2 = telefono_cita2

        medico.save()
        return JsonResponse({'Result': 'OK'}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_generales_medico(request):
    id = request.data.get("id")
    medico = Medico.objects.get(id=id)
    if request.data.get("cedula") is not None and request.data.get("cedula") != "null":
        medico.cedula = request.data.get("cedula")
    if request.data.get("codigo") is not None and request.data.get("codigo") != "null":
        medico.codigo = request.data.get("codigo")
    if request.data.get("cod_telefono_pais") is not None and request.data.get("cod_telefono_pais") != "null":
        medico.cod_telefono_pais = request.data.get("cod_telefono_pais")
    if request.data.get("telefono") is not None and request.data.get("telefono") != "null":
        medico.telefono = request.data.get("telefono")
    if request.data.get("telefono_whatsapp") is not None and request.data.get("telefono_whatsapp") != "null":
        medico.telefono_whatsapp = request.data.get("telefono_whatsapp")
    if request.data.get("genero") is not None:
        medico.genero = request.data.get("genero")
    if request.data.get("imagenFile") is not None and request.data.get("imagenFile") != 'null':
        medico.foto = request.data.get("imagenFile")
    medico.save()
    return JsonResponse({"msg": "Perfil actualizado", "fotourl": str(medico.foto)}, safe=False, status=status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_perfil_medico(request):
    medico_id = request.GET.get('id')
    print(medico_id)
    try:
        medico = Medico.objects.get(id=medico_id)
    except Medico.DoesNotExist as e:
        return JsonResponse({'error': "No existe el médico"}, safe=False, status=status.HTTP_404_NOT_FOUND)

    if medico.provincia1 == None:
        provincia1 = None
    else:
        provincia1 = medico.provincia1.id
    if medico.provincia2 == None:
        provincia2 = None
    else:
        provincia2 = medico.provincia2.id

    if medico.canton1 == None:
        canton1 = None
    else:
        canton1 = medico.canton1.id
    if medico.canton2 == None:
        canton2 = None
    else:
        canton2 = medico.canton2.id

    if medico.parroquia1 == None:
        parroquia1 = None
    else:
        parroquia1 = medico.parroquia1.id
    if medico.parroquia2 == None:
        parroquia2 = None
    else:
        parroquia2 = medico.parroquia2.id

    if medico.especialidad1 == None:
        especialidad1 = None
    else:
        especialidad1 = medico.especialidad1.id
    if medico.especialidad2 == None:
        especialidad2 = None
    else:
        especialidad2 = medico.especialidad2.id
    if medico.genero == None or medico.genero == "":
        genero = None
    else:
        genero = medico.genero
    if medico.duracion == None or medico.duracion == "":
        duracion = None
    else:
        duracion = medico.duracion

    if medico.cod_telefono_pais == None or medico.cod_telefono_pais == "":
        cod_telefono_pais = None
    else:
        cod_telefono_pais = medico.cod_telefono_pais

    if medico.telefono == None or medico.telefono == "":
        telefono = None
    else:
        telefono = medico.telefono

    if medico.telefono_whatsapp == None or medico.telefono_whatsapp == "":
        tel_whatsapp = None
    else:
        tel_whatsapp = medico.telefono_whatsapp

    if medico.telefono_whatsapp == None or medico.telefono_whatsapp == "":
        tel_whatsapp = None
    else:
        tel_whatsapp = medico.telefono_whatsapp

    if medico.telefono_cita1 == None or medico.telefono_cita1 == "":
        telefono_cita1 = None
    else:
        telefono_cita1 = medico.telefono_cita1

    if medico.telefono_cita2 == None or medico.telefono_cita2 == "":
        telefono_cita2 = None
    else:
        telefono_cita2 = medico.telefono_cita2

    if medico.direccion_consultorio1 == None or medico.direccion_consultorio1 == "":
        direccion_consultorio1 = None
    else:
        direccion_consultorio1 = medico.direccion_consultorio1

    if medico.direccion_consultorio2 == None or medico.direccion_consultorio2 == "":
        direccion_consultorio2 = None
    else:
        direccion_consultorio2 = medico.direccion_consultorio2

    if medico.referencia_consultorio1 == None or medico.referencia_consultorio1 == "":
        referencia_consultorio1 = None
    else:
        referencia_consultorio1 = medico.referencia_consultorio1

    if medico.referencia_consultorio2 == None or medico.referencia_consultorio2 == "":
        referencia_consultorio2 = None
    else:
        referencia_consultorio2 = medico.referencia_consultorio2

    seguros = []
    for seguro in MedicoSeguro.objects.filter(medico=medico.id):
        seguro_ele = {}
        seguro_ele["id"] = seguro.seguro.id
        seguro_ele["seguro"] = seguro.seguro.seguro
        seguros.append(seguro_ele)

    # obtiene los intervalos de disponibilidad
    intervalo = []
    for inter in IntervalosDisponibilidad.objects.filter(medico=medico_id, activo=True).order_by('inicio'):
        dispo = {}
        dispo["id"] = inter.id
        dispo["dia_semana"] = inter.dia_semana
        dispo["inicio"] = inter.inicio
        dispo["fin"] = inter.fin
        dispo["duracion"] = inter.duracion
        intervalo.append(dispo)

    perfil_medico = {
        "id": medico.id,
        "fullname": medico.nombre + " " + medico.apellidos,
        "cedula": medico.cedula,
        "codigo": medico.codigo,
        "genero": genero,
        "precio": medico.precio,
        "duracion": duracion,
        "cod_telefono_pais": cod_telefono_pais,
        "telefono": telefono,
        "telefono_whatsapp": tel_whatsapp,
        "telefono_cita1": telefono_cita1,
        "telefono_cita2": telefono_cita2,
        "direccion_consultorio1": direccion_consultorio1,
        "direccion_consultorio2": direccion_consultorio2,
        "referencia_consultorio1": referencia_consultorio1,
        "referencia_consultorio2": referencia_consultorio2,
        "provincia1": provincia1,
        "provincia2": provincia2,
        "canton1": canton1,
        "canton2": canton2,
        "parroquia1": parroquia1,
        "parroquia2": parroquia2,
        "especialidad1": especialidad1,
        "especialidad2": especialidad2,
        "subespecialidad1": medico.subespecialidad1,
        "subespecialidad2": medico.subespecialidad2,
        "estudios": medico.estudios,
        "experiencia": medico.experiencia,
        "seguros": seguros,
        "latitud1": medico.lat1,
        "latitud2": medico.lat2,
        "longitud1": medico.lon1,
        "longitud2": medico.lon2,
        "fotourl": str(medico.foto),
        "disponibilidad": intervalo
    }
    return JsonResponse({"perfil": perfil_medico}, safe=False, status=status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([])
@api_view(['POST'])
def register_medico_admin(request):
    print(request)
    user = request.user
    if user.is_superuser:
        email = request.data.get("email")
        username = request.data.get("username")
        first = request.data.get("first")
        last = request.data.get("last")
        password = request.data.get("password")
        role = request.data.get("role")
        if username and \
                password and \
                first and \
                last and \
                email and \
                role:
            username_query_set = User.objects.filter(
                Q(username=username) | Q(email=email))
            if not username_query_set:
                user = User.objects.create_user(username, email, password)
                user.first_name = first
                user.last_name = last
                user.is_superuser = False
                user.is_active = True
                user.save()

                medico = Medico.objects.create(user=user)
                medico.nombre = request.data.get("first")
                medico.apellidos = request.data.get("last")
                medico.email = request.data.get("email")
                medico.regSene = request.data.get("regSene")
                medico.regAcess = request.data.get("regAcess")
                medico.activado = True
                medico.save()

                # adiciona al grupo
                medgroup = Group.objects.get(name='MEDICO')
                try:
                    user.groups.add(medgroup)
                except ProgrammingError as e:
                    print('error:', str(e))

                # envia un correo de notificacion
                # send_mail(
                #     subject = 'Registro en la Plataforma de Servicios Médicos',
                #     message = 'Usted ha registrado en la Plataforma Integral de Servicios Médicos. Para acceder a la plataforma puede usar el usuario: '+username+' y la contraseña: '+password,
                #     from_email = 'plataforma.integral.servicios@gmail.com',
                #     recipient_list = [medico.email],
                #     fail_silently=False,
                # )

                # envia un correo de notificacion
                subject = 'Registro en la Plataforma de HallMed'
                # EMAIL_HOST_USER #'plataforma.integral.servicios@gmail.com'
                from_email = EMAIL_HOST_USER
                recipient_list = [medico.email]
                text_content = 'Registro en la Plataforma culminado con exito'
                html_content = '<h2>¡FELICITACIONES, YA ERES PARTE DE ESTA GRAN COMUNIDAD!</h2>' \
                               '<h4><p>Usted ha registrado en la Plataforma de HallMed</p>' \
                               '<p>Nuestro equipo de trabajo se siente honrado de contar con usted como miembro importante de nuestra comunidad.</p>' \
                               '<p>Para acceder a la plataforma puede usar las siguientes credenciales:</p>' \
                               '<p>Usuario: '+username+'</p> ' \
                               '<p>Contraseña: '+password+'</p>' \
                               '<p><a href="http://www.plataformamedica.org">http://www.plataformamedica.org</a></p>' \
                               '<p>“JUNTOS PODEMOS”</p>' \
                               '<p>Muchas Gracias.</p></h4>'

                msg = EmailMultiAlternatives(
                    subject, text_content, from_email, recipient_list)
                msg.attach_alternative(html_content, "text/html")
                try:
                    msg.send()
                except BaseException as e:
                    print(
                        "<error> (register_medico_admin) [send mail]: ", str(e))
                response = {
                    "message": 'Successfully created',
                    "email": user.email,
                    "user": user.username,
                    "first": user.first_name,
                    "last": user.last_name,
                    'role': role,
                }
                return Response(response, 200)
            else:
                msg = "The email and username fields have to be uniques"
                return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            msg = "You most provide a valid user information"
            return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                                status=status.HTTP_400_BAD_REQUEST)
    else:
        msg = 'This user has not permissions to performs this operation',
        return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                            status=status.HTTP_400_BAD_REQUEST)


# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
@api_view(['POST'])
def medico_nombre(request):
    payload = json.loads(request.body)
    texto = payload["texto"].strip()
    if texto == "":
        tipo = []
    else:
        tipo = Medico.objects.filter(nombre__icontains=texto)[:10] | Medico.objects.filter(
            apellidos__icontains=texto)[:10] | Medico.objects.filter(
            cedula__startswith=texto)[:10]
    tipoSerializer = MedicoSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def buscar_medico(request):
    if request.method == 'POST':
        payload = json.loads(request.body)

        print('payload', payload)

        filtrosAplicar = []
        provincia = payload["provincia"]
        if provincia is not None and provincia != "":
            filtrosAplicar.append(Q(provincia1=provincia)
                                  | Q(provincia2=provincia))

        canton = payload["canton"]
        if canton is not None and canton != "":
            filtrosAplicar.append(Q(canton1=canton) | Q(canton2=canton))

        parroquia = payload["parroquia"]
        if parroquia is not None and parroquia != "":
            filtrosAplicar.append(Q(parroquia1=parroquia)
                                  | Q(parroquia2=parroquia))

        especialidad = payload["especialidad"]
        if especialidad is not None and especialidad != "":
            filtrosAplicar.append(
                Q(especialidad1=especialidad) | Q(especialidad2=especialidad))
        # filtrosAplicar.append(Q(precio__gte=25))

        orden = payload["orden"]
        if orden is None and orden != "" or orden == "precio":
            orden = "precio_consulta"

        print('filtros', filtrosAplicar)

        medicos = []
        for medico in Medico.objects.filter(*filtrosAplicar):
            medico_temp = {}
            medico_temp["id"] = medico.id
            medico_temp["nombre_completo"] = medico.nombre + \
                " " + medico.apellidos

            if medico.direccion_consultorio1 is not None:
                medico_temp["direccion"] = medico.direccion_consultorio1
            else:
                medico_temp["direccion"] = ""

            if medico.referencia_consultorio1 is not None:
                medico_temp["referencia"] = medico.referencia_consultorio1
            else:
                medico_temp["referencia"] = ""

            if medico.estudios is not None:
                medico_temp["estudios"] = medico.estudios
            else:
                medico_temp["estudios"] = ""

            if medico.experiencia is not None:
                medico_temp["experiencia"] = medico.experiencia
            else:
                medico_temp["experiencia"] = ""

            if medico.telefono is not None and medico.telefono != "null":
                medico_temp["telefono"] = medico.telefono
            else:
                medico_temp["telefono"] = ""

            seguros = ""
            for medSeg in MedicoSeguro.objects.filter(medico=medico.id):
                seguros = medSeg.seguro.seguro + ". " + seguros
            medico_temp["seguro"] = seguros

            if medico.foto is not None:
                medico_temp["foto"] = str(medico.foto)
            else:
                medico_temp["foto"] = ""

            if medico.precio is not None:
                medico_temp["precio_consulta"] = medico.precio
            else:
                medico_temp["precio_consulta"] = ""

            if medico.especialidad1 is not None:
                medico_temp["especialidad1"] = medico.especialidad1.especialidad
            else:
                medico_temp["especialidad1"] = ""

            if medico.especialidad2 is not None:
                medico_temp["especialidad2"] = medico.especialidad2.especialidad
            else:
                medico_temp["especialidad2"] = ""

            if medico.provincia1 is not None:
                medico_temp["provincia1"] = Provincia.objects.get(
                    pk=medico.provincia1.id).provincia
            if medico.provincia2 is not None:
                medico_temp["provincia2"] = Provincia.objects.get(
                    pk=medico.provincia2.id).provincia

            if medico.canton1 is not None:
                medico_temp["canton1"] = Canton.objects.get(
                    pk=medico.canton1.id).canton
            if medico.canton2 is not None:
                medico_temp["canton2"] = Canton.objects.get(
                    pk=medico.canton2.id).canton

            if medico.parroquia1 is not None:
                medico_temp["parroquia1"] = Parroquia.objects.get(
                    pk=medico.parroquia1.id).parroquia
            if medico.parroquia2 is not None:
                medico_temp["parroquia2"] = Parroquia.objects.get(
                    pk=medico.parroquia2.id).parroquia

            ratingAvg = RatingMedico.objects.filter(
                medico=medico.id).aggregate(Avg('rating'))

            if (ratingAvg["rating__avg"]) is None:
                rating = 0
            else:
                rating = ratingAvg["rating__avg"]
            medico_temp["rating"] = rating
            medicos.append(medico_temp)

        def customF(k):
            return k[orden]

        #medicos.sort(key=customF, reverse=(orden == "rating"))

        return JsonResponse(medicos, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
