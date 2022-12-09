from psycopg2._psycopg import ProgrammingError
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
from ..models import Medico, Sucursal
import json
from ..serializers import MedicoSerializer
from django.db import transaction
from django.db import IntegrityError
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
import shutil
from pism.settings import BASE_DIR
from ..models import UnidadMedica, Provincia, Canton, Parroquia
from ..serializers import UnidadMedicaSerializer
from django.core.mail import EmailMultiAlternatives
from pism.settings import BASE_DIR, EMAIL_HOST_USER


@api_view(['GET'])
def list_unidad_medica(request):
    tipo = UnidadMedica.objects.filter().order_by('id')
    tipoSerializer = UnidadMedicaSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_unidad_medica_no_activas(request):
    tipo = UnidadMedica.objects.filter(activado=False).order_by('id')
    tipoSerializer = UnidadMedicaSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([])
@api_view(['POST'])
def register_unidad_medica(request):
    print(request)
    user = request.user
    if user.is_superuser:
        email = request.data.get("email")
        username = request.data.get("username")
        first = request.data.get("first")
        password = request.data.get("password")
        role = request.data.get("role")
        if username and \
                password and \
                first and \
                email and \
                role:
            username_query_set = User.objects.filter(Q(username=username) | Q(email=email))
            if not username_query_set:
                user = User.objects.create_user(username, email, password)
                user.first_name = first
                user.is_superuser = False
                user.is_active = False
                user.save()

                um = UnidadMedica.objects.create(user=user)
                um.nombre = request.data.get("first")
                um.email = request.data.get("email")
                um.ruc = request.data.get("ruc")
                um.razon_social = request.data.get("razon_social")
                um.nombre_comercial = request.data.get("nombre_comercial")
                um.regRUC = request.data.get("regRUC")
                um.regArcsa = request.data.get("regArcsa")
                um.activado = False
                um.save()

                # envia un correo de notificacion
                subject = 'Notificación de registro en la Plataforma'
                from_email = EMAIL_HOST_USER #'plataforma.integral.servicios@gmail.com'
                recipient_list = [um.email]
                text_content = 'Notificación de registro en la Plataforma'
                html_content = '<h2>¡BIENVENIDO!</h2>' \
                               '<h4><p>Primeramente, agradecemos su interés en formar parte de esta gran comunidad.</p>' \
                               '<p>Por motivos de seguridad, en un período de 24h a 48h recibirá un correo electrónico de notificación y así podrá acceder a la plataforma.</p>' \
                               '<p>“JUNTOS PODEMOS”</p>' \
                               '<p>Muchas Gracias.</p></h4>'

                msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
                msg.attach_alternative(html_content, "text/html")
                try:
                    msg.send()
                except BaseException as e:
                    print("<error> (register_unidad_medica) [send mail]: ", str(e))

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


@authentication_classes([TokenAuthentication])
@permission_classes([])
@api_view(['POST'])
def register_unidad_medica_admin(request):
    print(request)
    user = request.user
    if user.is_superuser:
        email = request.data.get("email")
        username = request.data.get("username")
        first = request.data.get("first")
        password = request.data.get("password")
        role = request.data.get("role")
        if username and \
                password and \
                first and \
                email and \
                role:
            username_query_set = User.objects.filter(Q(username=username) | Q(email=email))
            if not username_query_set:
                user = User.objects.create_user(username, email, password)
                user.first_name = first
                user.is_superuser = False
                user.is_active = True
                user.save()

                umgroup = Group.objects.get(name='GRUPOEMPRESARIAL')
                try:
                    user.groups.add(umgroup)
                except ProgrammingError as e:
                    print('error:', str(e))

                um = UnidadMedica.objects.create(user=user)
                um.nombre = request.data.get("first")
                um.email = request.data.get("email")
                um.ruc = request.data.get("ruc")
                um.razon_social = request.data.get("razon_social")
                um.nombre_comercial = request.data.get("nombre_comercial")
                um.regRUC = request.data.get("regRUC")
                um.regArcsa = request.data.get("regArcsa")
                um.activado = False
                um.save()

                # envia un correo de notificacion
                subject = 'Registro en la Plataforma de Hallmed'
                from_email = EMAIL_HOST_USER #'plataforma.integral.servicios@gmail.com'
                recipient_list = [um.email]
                text_content = 'Registro en la Plataforma culminado con exito'
                html_content = '<h2>¡FELICITACIONES, YA ERES PARTE DE ESTA GRAN COMUNIDAD!</h2>' \
                               '<h4><p>Usted ha registrado en la Plataforma de Hallmed</p>' \
                               '<p>Nuestro equipo de trabajo se siente honrado de contar con usted como miembro importante de nuestra comunidad.</p>' \
                               '<p>Para acceder a la plataforma puede usar las siguientes credenciales:</p>' \
                               '<p>Usuario: ' + username + '</p> ' \
                               '<p>Contraseña: ' + password + '</p>' \
                               '<p><a href="http://www.plataformamedica.org">http://www.plataformamedica.org</a></p>' \
                               '<p>“JUNTOS PODEMOS”</p>' \
                               '<p>Muchas Gracias.</p></h4>'

                msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
                msg.attach_alternative(html_content, "text/html")

                try:
                    msg.send()
                except BaseException as e:
                    print("<error> (register_unidad_medica_admin) [send mail]: ", str(e))

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


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def valida_unidad_medica(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id = payload["id"]
        validacion = payload["validacion"]
        razon = payload["razon"]
        try:
            if id is not None and validacion is not None:
                if validacion == True:
                    um = UnidadMedica.objects.get(pk=id)
                    um.activado = True
                    um.save()

                    user = User.objects.get(pk=um.user.id)
                    user.is_active = True
                    user.save()

                    umgroup = Group.objects.get(name='GRUPOEMPRESARIAL')
                    print(umgroup)
                    try:
                        user.groups.add(umgroup)
                    except ProgrammingError as e:
                        print('error:', str(e))

                    tabla = UnidadMedica.objects.filter(activado=False).order_by('id')
                    tabla_serializer = UnidadMedicaSerializer(tabla, many=True)
                    # envia un correo de notificacion
                    # send_mail(
                    #     subject='Registro en la Plataforma culminado con exito',
                    #     message='Su registro en la Plataforma Integral de Servicios Médicos ha concluido satisfactoriamente !!!. Puede acceder con sus credenciales a todos nuestros servicios.',
                    #     from_email='plataforma.integral.servicios@gmail.com',
                    #     recipient_list=[um.email],
                    #     fail_silently=False,
                    # )

                    # envia un correo de notificacion
                    subject = 'Registro en la Plataforma culminado con exito'
                    from_email = EMAIL_HOST_USER #'plataforma.integral.servicios@gmail.com'
                    recipient_list = [um.email]
                    text_content = 'Registro en la Plataforma culminado con exito'
                    html_content = '<h2>¡FELICITACIONES, YA ERES PARTE DE ESTA GRAN COMUNIDAD!</h2>' \
                                   '<h4><p>Es grato informarle que su solicitud ha sido <strong>APROBADA</strong></p>' \
                                   '<p>Nuestro equipo de trabajo se siente honrado de contar con tan prestigiosa institución como miembro importante de nuestra comunidad.</p>' \
                                   '<p>“JUNTOS PODEMOS”</p>' \
                                   '<p>Muchas Gracias.</p></h4>'

                    msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
                    msg.attach_alternative(html_content, "text/html")

                    try:
                        msg.send()
                    except BaseException as e:
                        print("<error> (valida_unidad_medica) [send mail]: ", str(e))

                    return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
                else:
                    um = UnidadMedica.objects.get(pk=id)
                    # send_mail(
                    #     subject='Sus solicitud de  registro en la plataforma no ha sido aceptada',
                    #     message=razon,
                    #     from_email='plataforma.integral.servicios@gmail.com',
                    #     recipient_list=[um.email],
                    #     fail_silently=False,
                    # )

                    # envia un correo de notificacion
                    subject = 'Sus solicitud de  registro en la plataforma no ha sido aceptada'
                    from_email = EMAIL_HOST_USER #'plataforma.integral.servicios@gmail.com'
                    recipient_list = [um.email]
                    text_content = 'Sus solicitud de  registro en la plataforma no ha sido aceptada'
                    html_content = '<h4><p>Lamentablemente su solicitud NO ha sido APROBADA.</p>' \
                                   '<p>Detallamos a continuación los motivos:</p>' \
                                   '<p>' + razon + '</p>' \
                                   '<p>Para solucionar esta situación, por favor contáctenos.</p>' \
                                   '<p>“JUNTOS PODEMOS”</p>' \
                                   '<p>Muchas Gracias.</p></h4>'

                    msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
                    msg.attach_alternative(html_content, "text/html")

                    try:
                        msg.send()
                    except BaseException as e:
                        print("<error> (valida_unidad_medica) [send mail]: ", str(e))

                    tabla = UnidadMedica.objects.filter(activado=False).order_by('id')
                    tabla_serializer = UnidadMedicaSerializer(tabla, many=True)
                    return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
            else:
                msg = "Missing information"
                return JsonResponse({'error': '{}'.format(msg)}, safe=False, status=status.HTTP_400_BAD_REQUEST)
        except UnidadMedica.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def delete_UM_no_validada(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            with transaction.atomic():
                um = UnidadMedica.objects.get(pk=int(payload["id"]))
                user_temp = User.objects.get(id=um.user_id)
                # borra los ficheros asociados
                folderRUC = str(BASE_DIR) + '/media/' + um.dirnameRUC()
                shutil.rmtree(folderRUC, ignore_errors=True)
                folderArcsa= str(BASE_DIR) + '/media/' + um.dirnameArcsa()
                shutil.rmtree(folderArcsa, ignore_errors=True)
                um.delete()
                user_temp.delete()

                tabla = UnidadMedica.objects.filter(activado=False).order_by('id')
                tabla_serializer = UnidadMedicaSerializer(tabla, many=True)
                return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except UnidadMedica.DoesNotExist as e:
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
def delete_unidad_medica(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            with transaction.atomic():
                obj = UnidadMedica.objects.get(pk=int(payload["id"]))
                user_temp = User.objects.get(id=obj.user_id)
                obj.delete()
                user_temp.delete()
                tabla = UnidadMedica.objects.filter().order_by('id')
                tabla_serializer = UnidadMedicaSerializer(tabla, many=True)
                return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except UnidadMedica.DoesNotExist as e:
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
@api_view(['GET'])
def list_profile_um(request):
    user = request.user
    id = request.user.id
    um = UnidadMedica.objects.get(user_id=id)
    perfil_um = {
        "id": um.id,
        "slogan": um.slogan,
        "quienes_somos": um.quienes_somos,
        "direccion": um.direccion,
        "referencia_direccion": um.referencia_direccion,
        "ciudad": um.ciudad,
        "telefono":um.telefono,
        "pag_web": um.pag_web,
        "horario_atencion": um.horario_atencion
    }
    return JsonResponse(perfil_um, safe=False, status=status.HTTP_200_OK)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_profile_um(request):
    idgrupo = request.data.get("id")
    um = UnidadMedica.objects.get(id=idgrupo)
    um.slogan = request.data.get("slogan")
    um.quienes_somos = request.data.get("quienes_somos")
    um.direccion = request.data.get("direccion")
    um.referencia_direccion = request.data.get("referencia_direccion")
    um.ciudad = request.data.get("ciudad")
    um.telefono = request.data.get("telefono")
    um.pag_web = request.data.get("pag_web")
    um.horario_atencion = request.data.get("horario_atencion")
    um.telefono_whatsapp = request.data.get("telefono_whatsapp")
    um.facebook = request.data.get("facebook")
    um.twitter = request.data.get("twitter")
    um.ruc = request.data.get("ruc")
    um.razon_social = request.data.get("razon_social")
    um.nombre_comercial = request.data.get("nombre_comercial")
    um.compensacion = request.data.get("compensacion")

    if request.data.get("provincia") is not None:
        um.provincia = Provincia.objects.get(id=request.data.get("provincia"))
    if request.data.get("canton") is not None:
        um.canton = Canton.objects.get(id=request.data.get("canton"))
    if request.data.get("parroquia") is not None:
        um.parroquia = Parroquia.objects.get(id=request.data.get("parroquia"))

    um.save()

    if not um.compensacion is None:
        for sucursal in Sucursal.objects.filter(unidadMedica=um.id):
            sucursal.compensacion = um.compensacion
            sucursal.save()

    return JsonResponse({"msg":"Perfil actualizado"}, safe=False, status=status.HTTP_200_OK)
