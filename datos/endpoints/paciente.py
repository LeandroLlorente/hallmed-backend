from psycopg2._psycopg import ProgrammingError
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.contrib.auth.models import User, Group
from django.db.models import Q
from ..models import Paciente, Provincia, Canton, Parroquia
from ..serializers import PacienteSerializer
from django.db import transaction
from django.db import IntegrityError
from django.core.mail import EmailMultiAlternatives
from datetime import date
from pism.settings import EMAIL_HOST_USER
import json


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_paciente(request):
    tipo = Paciente.objects.filter().order_by('id')
    tipoSerializer = PacienteSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def paciente_nombre(request):
    payload = json.loads(request.body)
    texto = payload["texto"].strip()
    if texto == "":
        tipo = []
    else:
        tipo = Paciente.objects.filter(nombre__icontains=texto)[:10] | Paciente.objects.filter(
            apellidos__icontains=texto)[:10] | Paciente.objects.filter(
            cedula__startswith=texto)[:10]
    tipoSerializer = PacienteSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def paciente_cedula(request):
    payload = json.loads(request.body)
    texto = payload["texto"].strip()
    if texto == "":
        tipo = []
    else:
        tipo = Paciente.objects.filter(cedula__startswith=texto)[:10]
    tipoSerializer = PacienteSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


def calcula_edad(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def paciente_id(request):
    payload = json.loads(request.body)
    id_paciente = payload["id_paciente"]
    paciente = Paciente.objects.get(pk=id_paciente)
    paciente_ele = {}
    paciente_ele["id"] = paciente.id
    paciente_ele["nombre"] = paciente.nombre
    paciente_ele["apellidos"] = paciente.apellidos
    paciente_ele["email"] = paciente.email
    paciente_ele["cedula"] = paciente.cedula
    paciente_ele["telefono"] = paciente.telefono
    paciente_ele["genero"] = paciente.genero
    if paciente.foto is not None:
        paciente_ele["foto"] = str(paciente.foto)
    else:
        paciente_ele["foto"] = ""
    if paciente.fecha_nac is not None:
        paciente_ele["edad"] = calcula_edad(paciente.fecha_nac)
    else:
        paciente_ele["edad"] = ""
    paciente_ele["historia_clinica"] = paciente.historia_clinica
    paciente_ele["direccion"] = paciente.direccion
    if paciente.parroquia is not None:
        paciente_ele["parroquia"] = paciente.parroquia.parroquia
    else:
        paciente_ele["parroquia"] = ""
    if paciente.canton is not None:
        paciente_ele["canton"] = paciente.canton.canton
    else:
        paciente_ele["canton"] = ""
    if paciente.provincia is not None:
        paciente_ele["provincia"] = paciente.provincia.provincia
    else:
        paciente_ele["provincia"] = ""
    return JsonResponse(paciente_ele, safe=False)


@authentication_classes([TokenAuthentication])
@permission_classes([])
@api_view(['POST'])
def register_paciente(request):
    # user = request.user
    # if user.is_superuser:
    try:
        email = request.data.get("email")
        username = request.data.get("username")
        first = request.data.get("first")
        last = request.data.get("last")
        password = request.data.get("password")
        role = request.data.get("role")
        if username and password and first and \
            last and email and role:
            username_query_set = User.objects.filter(Q(username=username) | Q(email=email))
            if not username_query_set:
                user = User.objects.create_user(username, email, password)
                user.first_name = first
                user.last_name = last
                user.is_superuser = False
                user.is_active = True
                user.save()
                
                pacgroup = Group.objects.get(name='PACIENTE')
                try:
                    user.groups.add(pacgroup)
                except ProgrammingError as e:
                    print('<Error> (register_paciente):', str(e))

                paciente = Paciente.objects.create(user=user)
                paciente.nombre = request.data.get("first")
                paciente.apellidos = request.data.get("last")
                paciente.email = request.data.get("email")
                paciente.save()
                # envia un correo de notificacion

                subject = 'Notificación de registro en la Plataforma'
                from_email = EMAIL_HOST_USER  
                recipient_list = [user.email]
                text_content = 'Notificación de registro en la Plataforma'
                html_content = '<h2>¡FELICITACIONES, YA ERES PARTE DE ESTA GRAN COMUNIDAD!</h2>' \
                               '<h4><p>Agradecemos tu interés en formar parte de esta plataforma, en la cual podrás encontrar GRATIS, para ti y tus seres queridos todo lo necesario para el cuidado de la salud.</p>' \
                               '<p>Para que otras personas se puedan beneficiar utilizando nuestra plataforma, por favor, comparte el siguiente enlace con todos tus amigos, familiares o compañeros de trabajo:</p>' \
                               '<p><a href="http://www.plataformamedica.org">http://www.plataformamedica.org</a></p>' \
                               '<p>“JUNTOS PODEMOS”</p>' \
                               '<p>Muchas Gracias.</p></h4>'

                msg = EmailMultiAlternatives(
                    subject, text_content, from_email, recipient_list)
                msg.attach_alternative(html_content, "text/html")

                try:
                    msg.send()
                except BaseException as e:
                    print("<error> (register_paciente) [send mail]: ", str(e))
                
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
                msg = "El campo Nombre de Usuario y Correo Electrónico deben ser únicos"
                return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                                    status=status.HTTP_409_CONFLICT)
        else:
            # msg = "You must provide a valid user information"
            msg = "Debe proporcionar una información de usuario válida"
            return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                                status=status.HTTP_406_NOT_ACCEPTABLE)

    except BaseException as e:
        msg = str(e)
        print("<error> (register_paciente): ", msg)
        return JsonResponse({'error': msg}, safe=False, status=status.HTTP_400_BAD_REQUEST)                                
    # else:
    #     # msg = 'This user has not permissions to performs this operation'
    #     msg = 'Este usuario no tiene permisos para realizar esta operación'
    #     return JsonResponse({'error': '{}'.format(msg)}, safe=False,
    #                         status=status.HTTP_401_UNAUTHORIZED)


@authentication_classes([TokenAuthentication])
@permission_classes([])
@api_view(['POST'])
def register_paciente_profesional(request):
    user = request.user
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

            pacgroup = Group.objects.get(name='PACIENTE')
            try:
                user.groups.add(pacgroup)
            except ProgrammingError as e:
                print('error:', str(e))

            paciente = Paciente.objects.create(user=user)
            paciente.nombre = request.data.get("first")
            paciente.apellidos = request.data.get("last")
            paciente.email = request.data.get("email")
            paciente.save()
            # envia un correo de notificacion

            # subject = 'Notificación de registro en la Plataforma'
            # from_email = 'plataforma.integral.servicios@gmail.com'
            # recipient_list = ['goarorue@gmail.com']
            # text_content = 'Notificación de registro en la Plataforma'
            # html_content = '<h2>¡FELICITACIONES, YA ERES PARTE DE ESTA GRAN COMUNIDAD!</h2>' \
            #                '<h4><p>Agradecemos tu interés en formar parte de esta plataforma, en la cual podrás encontrar GRATIS, para ti y tus seres queridos todo lo necesario para el cuidado de la salud.</p>' \
            #                '<p>Para acceder a la plataforma puede usar el usuario: '+username+' y la contraseña: '+password</p>'
            #                '<p>Para que otras personas se puedan beneficiar utilizando nuestra plataforma, por favor, comparte el siguiente enlace con todos tus amigos, familiares o compañeros de trabajo:</p>' \
            #                '<p><a href="http://www.plataformamedica.org">http://www.plataformamedica.org</a></p>' \
            #                '<p>“JUNTOS PODEMOS”</p>' \
            #                '<p>Muchas Gracias.</p></h4>'
            #
            # msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
            # msg.attach_alternative(html_content, "text/html")
            # msg.send()

            # response = {
            #     "message": 'Successfully created',
            #     "email": user.email,
            #     "user": user.username,
            #     "first": user.first_name,
            #     "last": user.last_name,
            #     'role': role,
            # }
            # return Response(response, 200)
            tipo = Paciente.objects.filter().order_by('id')
            tipoSerializer = PacienteSerializer(tipo, many=True)
            return JsonResponse(tipoSerializer.data, safe=False)

        else:
            msg = "The email and username fields have to be uniques"
            return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                                status=status.HTTP_400_BAD_REQUEST)
    else:
        msg = "You most provide a valid user information"
        return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                            status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_profile_paciente(request):
    id = request.data.get("id")
    pac = Paciente.objects.get(pk=id)
    pac.cedula = request.data.get("cedula")
    pac.telefono = request.data.get("telefono")
    pac.fecha_nac = request.data.get("fecha_nac")
    pac.genero = request.data.get("genero")
    pac.direccion = request.data.get("direccion")
    print(request.data.get("representante"))
    if request.data.get("representante") != "":
        pac.representante = Paciente.objects.get(
            pk=request.data.get("representante"))

    if request.data.get("imagenFile") is not None and request.data.get("imagenFile") != 'null':
        pac.foto = request.data.get("imagenFile")

    if request.data.get("provincia") is not None and request.data.get("provincia") != 'null':
        pac.provincia = Provincia.objects.get(id=request.data.get("provincia"))

    if request.data.get("canton") is not None and request.data.get("canton") != 'null':
        pac.canton = Canton.objects.get(id=request.data.get("canton"))

    if request.data.get("parroquia") is not None and request.data.get("parroquia") != 'null':
        pac.parroquia = Parroquia.objects.get(id=request.data.get("parroquia"))

    pac.save()
    print(pac.foto)
    return JsonResponse({"msg": "Perfil actualizado", "fotourl": str(pac.foto)}, safe=False, status=status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_profile_paciente_old(request):
    print(request.data.get("fecha_nac"))
    id = request.data.get("id")
    pac = Paciente.objects.get(id=id)
    pac.cedula = request.data.get("cedula")
    pac.telefono = request.data.get("telefono")
    pac.fecha_nac = request.data.get("fecha_nac")
    pac.genero = request.data.get("genero")
    pac.direccion = request.data.get("direccion")

    if request.data.get("provincia") is not None:
        pac.provincia = Provincia.objects.get(id=request.data.get("provincia"))

    if request.data.get("canton") is not None:
        pac.canton = Canton.objects.get(id=request.data.get("canton"))

    if request.data.get("parroquia") is not None:
        pac.parroquia = Parroquia.objects.get(id=request.data.get("parroquia"))

    pac.save()
    return JsonResponse({"msg": "Perfil actualizado"}, safe=False, status=status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def delete_paciente(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            with transaction.atomic():
                obj = Paciente.objects.get(pk=int(payload["id"]))
                user_temp = User.objects.get(id=obj.user_id)
                print(user_temp.id)
                obj.delete()
                user_temp.delete()
                tabla = Paciente.objects.filter().order_by('id')
                tabla_serializer = PacienteSerializer(tabla, many=True)
                return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except Paciente.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return JsonResponse({'error': 'There is already a record with that data'}, safe=False,
                                status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
