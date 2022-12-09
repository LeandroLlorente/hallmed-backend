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
from ..models import Medico
import json
from ..serializers import MedicoSerializer
from django.db import transaction
from django.db import IntegrityError
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
import shutil
from pism.settings import BASE_DIR, EMAIL_HOST_USER
from ..models import Farmacia, Provincia, Canton, Parroquia
from ..serializers import FarmaciaSerializer
from django.core.mail import EmailMultiAlternatives


@api_view(['GET'])
def list_farmacia(request):
    tipo = Farmacia.objects.filter().order_by('id')
    tipoSerializer = FarmaciaSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_farmacias_no_activas(request):
    tipo = Farmacia.objects.filter(activado=False).order_by('id')
    tipoSerializer = FarmaciaSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([])
@api_view(['POST'])
def register_farmacia(request):
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
            username_query_set = User.objects.filter(username=username)
            if not username_query_set:
                user = User.objects.create_user(username, email, password)
                user.first_name = first
                user.is_superuser = False
                user.is_active = False
                user.save()

                um = Farmacia.objects.create(user=user)
                um.nombre = request.data.get("first")
                um.email = request.data.get("email")
                um.ruc = request.data.get("ruc")
                um.razon_social = request.data.get("razon_social")
                um.nombre_comercial = request.data.get("nombre_comercial")
                um.regRUC = request.data.get("regRUC")
                um.regArcsa = request.data.get("regArcsa")
                um.compensacion = request.data.get("compensacion")
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
                    print("<error> (register_farmacia) [send mail]: ", str(e))

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
def register_farmacia_admin(request):
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
            username_query_set = User.objects.filter(username=username)
            if not username_query_set:
                user = User.objects.create_user(username, email, password)
                user.first_name = first
                user.is_superuser = False
                user.is_active = True
                user.save()

                fargroup = Group.objects.get(name='FARMACIA')
                try:
                    user.groups.add(fargroup)
                except ProgrammingError as e:
                    print('error:', str(e))

                far = Farmacia.objects.create(user=user)
                far.nombre = request.data.get("first")
                far.email = request.data.get("email")
                far.ruc = request.data.get("ruc")
                far.razon_social = request.data.get("razon_social")
                far.nombre_comercial = request.data.get("nombre_comercial")
                far.regRUC = request.data.get("regRUC")
                far.regArcsa = request.data.get("regArcsa")
                far.compensacion = request.data.get("compensacion")
                far.activado = False
                far.save()

                # envia un correo de notificacion
                subject = 'Registro en la Plataforma de HallMed'
                from_email = EMAIL_HOST_USER #'plataforma.integral.servicios@gmail.com'
                recipient_list = [far.email]
                text_content = 'Registro en la Plataforma culminado con exito'
                html_content = '<h2>¡FELICITACIONES, YA ERES PARTE DE ESTA GRAN COMUNIDAD!</h2>' \
                               '<h4><p>Usted ha registrado en la Plataforma de HallMed</p>' \
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
                    print("<error> (register_farmacia_admin) [send mail]: ", str(e))

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
def valida_farmacia(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id = payload["id"]
        validacion = payload["validacion"]
        razon = payload["razon"]
        try:
            if id is not None and validacion is not None:
                if validacion == True:
                    um = Farmacia.objects.get(pk=id)
                    um.activado = True
                    um.save()

                    user = User.objects.get(pk=um.user.id)
                    user.is_active = True
                    user.save()

                    umgroup = Group.objects.get(name='FARMACIA')
                    print(umgroup)
                    try:
                        user.groups.add(umgroup)
                    except ProgrammingError as e:
                        print('error:', str(e))

                    tabla = Farmacia.objects.filter(activado=False).order_by('id')
                    tabla_serializer = FarmaciaSerializer(tabla, many=True)
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
                        print("<error> (valida_farmacia) [send mail]: ", str(e))

                    return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
                else:
                    um = Farmacia.objects.get(pk=id)
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
                        print("<error> (valida_farmacia) [send mail]: ", str(e))

                    tabla = Farmacia.objects.filter(activado=False).order_by('id')
                    tabla_serializer = FarmaciaSerializer(tabla, many=True)
                    return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
            else:
                msg = "Missing information"
                return JsonResponse({'error': '{}'.format(msg)}, safe=False, status=status.HTTP_400_BAD_REQUEST)
        except Farmacia.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def delete_farmacia(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            with transaction.atomic():
                obj = Farmacia.objects.get(pk=int(payload["id"]))
                user_temp = User.objects.get(id=obj.user_id)
                obj.delete()
                user_temp.delete()
                tabla = Farmacia.objects.filter().order_by('id')
                tabla_serializer = FarmaciaSerializer(tabla, many=True)
                return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except Farmacia.DoesNotExist as e:
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
def update_profile_farmacia(request):
    id = request.data.get("id")
    far = Farmacia.objects.get(id=id)
    far.slogan = request.data.get("slogan")
    far.quienes_somos = request.data.get("quienes_somos")
    far.direccion = request.data.get("direccion")
    far.referencia_direccion = request.data.get("referencia_direccion")
    far.ciudad = request.data.get("ciudad")
    far.telefono = request.data.get("telefono")
    far.pag_web = request.data.get("pag_web")
    far.horario_atencion = request.data.get("horario_atencion")
    far.telefono_whatsapp = request.data.get("telefono_whatsapp")
    far.facebook = request.data.get("facebook")
    far.twitter = request.data.get("twitter")
    far.ruc = request.data.get("ruc")
    far.razon_social = request.data.get("razon_social")
    far.nombre_comercial = request.data.get("nombre_comercial")
    far.compensacion = request.data.get("compensacion")

    if request.data.get("provincia") is not None:
        far.provincia = Provincia.objects.get(id=request.data.get("provincia"))
    if request.data.get("canton") is not None:
        far.canton = Canton.objects.get(id=request.data.get("canton"))
    if request.data.get("parroquia") is not None:
        far.parroquia = Parroquia.objects.get(id=request.data.get("parroquia"))

    far.save()
    return JsonResponse({"msg":"Perfil actualizado"}, safe=False, status=status.HTTP_200_OK)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def delete_farmacia_no_validada(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            with transaction.atomic():
                um = Farmacia.objects.get(pk=int(payload["id"]))
                user_temp = User.objects.get(id=um.user_id)
                # borra los ficheros asociados
                folderRUC = str(BASE_DIR) + '/media/' + um.dirnameRUC()
                shutil.rmtree(folderRUC, ignore_errors=True)
                folderArcsa= str(BASE_DIR) + '/media/' + um.dirnameArcsa()
                shutil.rmtree(folderArcsa, ignore_errors=True)
                um.delete()
                user_temp.delete()

                tabla = Farmacia.objects.filter(activado=False).order_by('id')
                tabla_serializer = FarmaciaSerializer(tabla, many=True)
                return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except Farmacia.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return JsonResponse({'error': 'There is already a record with that data'}, safe=False,
                                status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


