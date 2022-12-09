from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.permissions import AllowAny
from django.contrib.auth import login as django_login, logout as django_logout
from ..roles import ROLES
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.contrib.auth import authenticate
from ..serializers import DeleteSerializer, UserAllSerializer
from datos.models import Medico, UnidadMedica, Paciente, Sucursal, Farmacia, MedicoSeguro


def list_users_aux(user):
    global_rol = user.groups.all()[0].name
    if global_rol == 'ADMINISTRATOR':
        types = User.objects.all().order_by('username')
    elif global_rol == 'USER_MANAGER':
        business = user.userbusiness.business.id
        types = User.objects.filter(
            userbusiness__business__id=business).order_by('username').distinct()
    else:
        raise Exception('You could not perform this operation')
    types_serializer = UserAllSerializer(types, many=True)
    return types_serializer


@api_view(['POST'])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            if not user.is_active:
                msg = "El usuario está desactivado"
                return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                                    status=status.HTTP_400_BAD_REQUEST)
            django_login(request=request, user=user)
            token, created = Token.objects.get_or_create(user=user)
            user_belongs_to = user.groups.values_list('name', flat=True)
            print(user_belongs_to[0])
            respuesta = {
                "id": user.id,
                "user": user.username,
                "email": user.email,
                "first": user.first_name,
                "last": user.last_name,
                "role": list(user_belongs_to),
                "token": token.key,
                "profile": {}
            }

            if user_belongs_to[0] == 'MEDICO':
                medico = Medico.objects.get(user_id=user.id)
                print(medico)
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

                perfil_medico = {
                    "id": medico.id,
                    "fullname": medico.nombre + " " + medico.apellidos,
                    # "cedula": medico.cedula,
                    # "codigo": medico.codigo,
                    # "genero": genero,
                    # "precio": medico.precio,
                    # "duracion": duracion,
                    # "cod_telefono_pais": cod_telefono_pais,
                    # "telefono": telefono,
                    # "telefono_whatsapp": tel_whatsapp,
                    # "telefono_cita1": telefono_cita1,
                    # "telefono_cita2": telefono_cita2,
                    # "direccion_consultorio1": direccion_consultorio1,
                    # "direccion_consultorio2": direccion_consultorio2,
                    # "referencia_consultorio1": referencia_consultorio1,
                    # "referencia_consultorio2": referencia_consultorio2,
                    # "provincia1": provincia1,
                    # "provincia2": provincia2,
                    # "canton1": canton1,
                    # "canton2": canton2,
                    # "parroquia1": parroquia1,
                    # "parroquia2": parroquia2,
                    # "especialidad1": especialidad1,
                    # "especialidad2": especialidad2,
                    # "subespecialidad1": medico.subespecialidad1,
                    # "subespecialidad2": medico.subespecialidad2,
                    # "estudios": medico.estudios,
                    # "experiencia": medico.experiencia,
                    # "seguros": seguros,
                    # "latitud1": medico.lat1,
                    # "latitud2": medico.lat2,
                    # "longitud1": medico.lon1,
                    # "longitud2": medico.lon2,
                    # "fotourl": str(medico.foto),
                }
                respuesta["profile"] = perfil_medico
            elif user_belongs_to[0] == 'GRUPOEMPRESARIAL':
                um = UnidadMedica.objects.get(user_id=user.id)
                if um.provincia == None:
                    provincia = None
                else:
                    provincia = um.provincia.id
                if um.canton == None:
                    canton = None
                else:
                    canton = um.canton.id
                if um.parroquia == None:
                    parroquia = None
                else:
                    parroquia = um.parroquia.id

                perfil_um = {
                    "id": um.id,
                    "nombre": um.nombre,
                    "slogan": um.slogan,
                    "quienes_somos": um.quienes_somos,
                    "direccion": um.direccion,
                    "referencia_direccion": um.referencia_direccion,
                    "telefono": um.telefono,
                    "telefono_whatsapp": um.telefono_whatsapp,
                    "facebook": um.facebook,
                    "twitter": um.twitter,
                    "pag_web": um.pag_web,
                    "horario_atencion": um.horario_atencion,
                    "provincia": provincia,
                    "canton": canton,
                    "parroquia": parroquia,
                    "ruc": um.ruc,
                    "razon_social": um.razon_social,
                    "nombre_comercial": um.nombre_comercial,
                }
                respuesta["profile"] = perfil_um
            elif user_belongs_to[0] == 'SUCURSAL':
                suc = Sucursal.objects.get(user_id=user.id)
                if suc.provincia == None:
                    provincia = None
                else:
                    provincia = suc.provincia.id
                if suc.canton == None:
                    canton = None
                else:
                    canton = suc.canton.id
                if suc.parroquia == None:
                    parroquia = None
                else:
                    parroquia = suc.parroquia.id

                perfil_suc = {
                    "id": suc.id,
                    "nombre": suc.nombre,
                    "slogan": suc.slogan,
                    "quienes_somos": suc.quienes_somos,
                    "provincia": provincia,
                    "canton": canton,
                    "parroquia": parroquia,
                    "direccion": suc.direccion,
                    "compensacion": suc.compensacion,
                    "referencia_direccion": suc.referencia_direccion,
                    "telefono": suc.telefono,
                    "telefono_whatsapp": suc.telefono_whatsapp,
                    "facebook": suc.facebook,
                    "twitter": suc.twitter,
                    "pag_web": suc.pag_web,
                    "horario_atencion": suc.horario_atencion,
                    "latitud": suc.lat,
                    "longitud": suc.lon,

                }
                # activa la sucursal
                suc.activado = True
                suc.save()
                respuesta["profile"] = perfil_suc
            elif user_belongs_to[0] == 'PACIENTE':
                pac = Paciente.objects.get(user_id=user.id)
                if pac.provincia == None:
                    provincia = None
                else:
                    provincia = pac.provincia.id
                if pac.canton == None:
                    canton = None
                else:
                    canton = pac.canton.id
                if pac.parroquia == None:
                    parroquia = None
                else:
                    parroquia = pac.parroquia.id
                if pac.representante == None:
                    representante = ""
                else:
                    representante = {}
                    representante["id"] = pac.representante.id
                    representante["nombre"] = pac.representante.nombre
                    representante["apellidos"] = pac.representante.apellidos
                    representante["cedula"] = pac.representante.cedula

                perfil_paciente = {
                    "id": pac.id,
                    "fullname": pac.nombre + " " + pac.apellidos,
                    "cedula": pac.cedula,
                    "telefono": pac.telefono,
                    "genero": pac.genero,
                    "fotourl": str(pac.foto),
                    "direccion": pac.direccion,
                    "provincia": provincia,
                    "canton": canton,
                    "parroquia": parroquia,
                    "fecha_nac": pac.fecha_nac,
                    "representante": representante
                }
                respuesta["profile"] = perfil_paciente
            elif user_belongs_to[0] == 'FARMACIA':
                far = Farmacia.objects.get(user_id=user.id)
                if far.provincia == None:
                    provincia = None
                else:
                    provincia = far.provincia.id
                if far.canton == None:
                    canton = None
                else:
                    canton = far.canton.id
                if far.parroquia == None:
                    parroquia = None
                else:
                    parroquia = far.parroquia.id
                perfil_farma = {
                    "id": far.id,
                    "nombre": far.nombre,
                    "slogan": far.slogan,
                    "quienes_somos": far.quienes_somos,
                    "provincia": provincia,
                    "canton": canton,
                    "parroquia": parroquia,
                    "direccion": far.direccion,
                    "referencia_direccion": far.referencia_direccion,
                    "telefono": far.telefono,
                    "telefono_whatsapp": far.telefono_whatsapp,
                    "facebook": far.facebook,
                    "twitter": far.twitter,
                    "pag_web": far.pag_web,
                    "horario_atencion": far.horario_atencion,
                    "latitud": far.lat,
                    "longitud": far.lon,
                    "ruc": far.ruc,
                    "razon_social": far.razon_social,
                    "nombre_comercial": far.nombre_comercial,

                }
                # activa la sucursal
                far.activado = True
                far.save()
                respuesta["profile"] = perfil_farma

            response = Response(respuesta, status=200)
            return response
        else:
            msg = "Error de autenticación en el sistema"
            return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                                status=status.HTTP_400_BAD_REQUEST)
    else:
        msg = "Debe de proveer un nombre de usuario y contraseña"
        return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                            status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def logout(request):
    user = request.user
    if user:
        try:
            user.auth_token.delete()
            django_logout(request)
            response_msg = "Successfully logout"
            response = {
                "message": response_msg
            }
            return Response(response, 200)
        except Exception:
            msg = "Something went wrong"
            return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                                status=status.HTTP_400_BAD_REQUEST)
    else:
        msg = "Invalid credentials were provided"
        return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                            status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_user(request):
    user = request.user
    if user.is_superuser:
        email = request.data.get("email")
        username = request.data.get("username")
        first = request.data.get("first")
        last = request.data.get("last")
        password = request.data.get("password")
        is_admin = request.data.get("admin")
        role = request.data.get("role")
        if username and \
                password and \
                first and \
                last and \
                email and \
                role:
            username_query_set = User.objects.filter(
                Q(username=username))  # | Q(email=email)
            if not username_query_set:
                if is_admin is True:
                    s_user = User.objects.create_superuser(username=username, email=email, password=password,
                                                           first_name=first, last_name=last)
                    ROLES.set_role(s_user, "ADMINISTRATOR")
                else:
                    if role == "ADMINISTRADOR":
                        msg = "ADMINISTRATOR is not valid for non admin users"
                        return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                                            status=status.HTTP_400_BAD_REQUEST)
                    s_user = User.objects.create_user(username=username, email=email, password=password,
                                                      first_name=first, last_name=last)
                    ROLES.set_role(s_user, role)

                business = Business.objects.get(
                    pk=int(request.data.get("autenticacion")))
                obj = UserBusiness()
                obj.user = s_user
                if business:
                    obj.business = business
                else:
                    obj.business = UserBusiness.objects.get(
                        user_id=user.id).business
                obj.save()
                users = User.objects.all()
                types_serializer = UserAllSerializer(users, many=True)
                return JsonResponse(types_serializer.data, safe=False)
                # response = {
                #     "message": 'Successfully created',
                #     "email": user.email,
                #     "user": user.username,
                #     "first": user.first_name,
                #     "last": user.last_name,
                #     'role': role,
                #     'autenticacion': autenticacion.name,
                # }
                # return Response(response, 200)
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
def change_password(request):
    password = request.data.get("password")
    if password:
        user = request.user
        try:
            user.set_password(password)
            user.save()
            msg = 'Password was successfully updated',
            return JsonResponse({'result': '{}'.format(msg)}, safe=False,
                                status=status.HTTP_200_OK)
        except Exception as e:
            msg = "Password was not changed"
            return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                                status=status.HTTP_400_BAD_REQUEST)
    else:
        msg = "Password mus be included"
        return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                            status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def delete_user(request):
    user = request.user
    global_rol = user.groups.all()[0].name
    if global_rol == 'ADMINISTRATOR' or global_rol == 'USER_MANAGER':
        username = user.username
        user_to_delete = User.objects.get(username=username)
        if not user_to_delete:
            return JsonResponse({'error': '{}'.format('The given username do not belongs to any user')}, safe=False,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            if user_to_delete.is_superuser:
                return JsonResponse({'error': '{}'.format('The given user is an admin user, can not be removed')}, safe=False,
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    user_to_delete.delete()
                    types_serializer = list_users_aux(user)
                    return JsonResponse(types_serializer.data, safe=False)
                    # return JsonResponse({'result': '{}'.format('User deleted successfully')}, safe=False,
                    #                     status=status.HTTP_200_OK)
                except Exception as e:
                    return JsonResponse({'error': '{}'.format(e)}, safe=False,
                                        status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error': '{}'.format('You could not perform this operation')}, safe=False,
                            status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def roles_view(request):
    user = request.user
    if user.is_superuser:
        roles = list(ROLES.APP_ROLES.keys())
        return JsonResponse({'roles': '{}'.format(roles)}, safe=False,
                            status=status.HTTP_200_OK)
    else:
        msg = 'You could not perform this operation'
        return JsonResponse({'error': '{}'.format(msg)}, safe=False,
                            status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_users(request):
    user = request.user
    try:
        types_serializer = list_users_aux(user)
        to_out = types_serializer.data
        return JsonResponse(to_out, safe=False)
    except Exception as e:
        return JsonResponse({'error': '{}'.format(e)}, safe=False,
                            status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_user(request):
    user = request.user
    try:
        target = request.data
        print("target>", target)
        user_instance = User.objects.get(username=target['username'])
        if user_instance:
            user_instance.first_name = target['first']
            user_instance.last_name = target['last']
            if target['password'] is not None:
                user_instance.set_password(target['password'])
            user_instance.email = target['email']
            user_instance.save()

            # actualiza los datos del medico
            if target['role'] == 'MEDICO':
                medico = Medico.objects.get(user_id=user_instance.id)
                medico.nombre = target['first']
                medico.apellidos = target['last']
                medico.email = target['email']
                medico.save()

            # actualiza los datos de GRUPOEMPRESARIAL
            if target['role'] == 'GRUPOEMPRESARIAL':
                um = UnidadMedica.objects.get(user_id=user_instance.id)
                um.nombre = target['first']
                um.email = target['email']
                um.save()

            # actualiza los datos de sucursal
            if target['role'] == 'SUCURSAL':
                um = Sucursal.objects.get(user_id=user_instance.id)
                um.nombre = target['first']
                um.email = target['email']
                um.save()

            return JsonResponse({'msg': 'Datos Actualizado'}, safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error1': '{}'.format('Error occurred')}, safe=False,
                                status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'error2': '{}'.format(e)}, safe=False,
                            status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_user_by_id(request):
    user = request.user
    try:
        target = request.data
        print("target>", target)
        user_instance = User.objects.get(id=target['id'])
        if user_instance:
            user_instance.username = target['username']
            user_instance.first_name = target['first']
            user_instance.last_name = target['last']
            if target['password'] is not None:
                user_instance.set_password(target['password'])
            user_instance.email = target['email']
            user_instance.save()

            # actualiza los datos del medico
            if target['role'] == 'MEDICO':
                medico = Medico.objects.get(user_id=user_instance.id)
                medico.nombre = target['first']
                medico.apellidos = target['last']
                medico.email = target['email']
                medico.save()

            # actualiza los datos de GRUPOEMPRESARIAL
            if target['role'] == 'GRUPOEMPRESARIAL':
                um = UnidadMedica.objects.get(user_id=user_instance.id)
                um.nombre = target['first']
                um.email = target['email']
                um.save()

            # actualiza los datos de sucursal
            if target['role'] == 'SUCURSAL':
                um = Sucursal.objects.get(user_id=user_instance.id)
                um.nombre = target['first']
                um.email = target['email']
                um.save()

            return JsonResponse({'msg': 'Datos Actualizado'}, safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error1': '{}'.format('Error occurred')}, safe=False,
                                status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'error2': '{}'.format(e)}, safe=False,
                            status=status.HTTP_400_BAD_REQUEST)
