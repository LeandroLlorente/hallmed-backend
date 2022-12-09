from django.http.response import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import Sucursal, UnidadMedica, Provincia, Canton, Parroquia
from ..serializers import SucursalSerializer
import json
from django.db import IntegrityError
from rest_framework import status
from django.db import transaction
from django.contrib.auth.models import User, Group
from django.db.models import Q
import random, string
from psycopg2._psycopg import ProgrammingError
from django.core.mail import send_mail

#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_sucursal(request):
    tipo = Sucursal.objects.filter().order_by('id')
    tipoSerializer = SucursalSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


def list_sucursal_grupo(request):
    sucursal_list = []
    for sucursal_temp in Sucursal.objects.all():
        sucursal_ele = {}
        sucursal_ele["id"] = sucursal_temp.id
        sucursal_ele["nombre"] = sucursal_temp.nombre
        sucursal_ele["email"] = sucursal_temp.email
        sucursal_ele["activado"] = sucursal_temp.activado
        if not sucursal_temp.unidadMedica is None:
            id_unidad = sucursal_temp.unidadMedica.id
            sucursal_ele["grupo"] = UnidadMedica.objects.get(id=id_unidad).nombre
        sucursal_list.append(sucursal_ele)
    return JsonResponse(sucursal_list, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_sucursal_user(request):
    payload = json.loads(request.body)
    tipo = Sucursal.objects.filter(unidadMedica=payload["unidadmedica"]).order_by('id')
    tipoSerializer = SucursalSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


def random_string_generator(str_size, allowed_chars):
    return ''.join(random.choice(allowed_chars) for x in range(str_size))


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_sucursal(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            nombre = payload["nombre"]
            email = payload["email"]
            unidadMedica = payload["unidadMedica"]
            # username_original = email[0: email.index('@')]
            password = random_string_generator(8, string.ascii_letters)

            # while True:
            #     username_code = random_string_generator(6, string.digits)
            #     username = username_original + "_" + username_code
            #     username_query_set = User.objects.filter(Q(username=username) | Q(email=email))
            #     if not username_query_set:
            #         newuser = User.objects.create_user(username=username, email=email, password=password, first_name=nombre, last_name='')
            #         break

            username = email
            username_query_set = User.objects.filter(Q(username=username) | Q(email=email))
            if not username_query_set:
                newuser = User.objects.create_user(username=username, email=email, password=password, first_name=nombre, last_name='')
            else:
                return JsonResponse({'error': 'Ya existe el el nombre de usuario o el email'}, safe=False, status=status.HTTP_409_CONFLICT)
            umgroup = Group.objects.get(name='SUCURSAL')

            try:
                newuser.groups.add(umgroup)
            except ProgrammingError as e:
                print('error:', str(e))

            print("username: " + username)
            print("password: " + password)
            obj = Sucursal.objects.create(user=newuser)
            obj.nombre = nombre
            obj.email = email
            obj.unidadMedica = UnidadMedica.objects.get(pk=unidadMedica)
            obj.activado = False
            obj.save()
            # envia un correo de notificacion
            try:
                send_mail(
                    subject='Registro en la Plataforma HallMed',
                    message='Usted ha sido registrado en la Plataforma HallMed. Para acceder a la plataforma puede usar el usuario: '+username+' y la contraseña: '+password,
                    from_email='plataforma.integral.servicios@gmail.com',
                    recipient_list=[obj.email],
                    fail_silently=False,
                )
            except e:
                print('error:', str(e))

            id_um = UnidadMedica.objects.get(pk=unidadMedica).id
            tabla = Sucursal.objects.filter(unidadMedica=unidadMedica).order_by('id')
            tabla_serializer = SucursalSerializer(tabla, many=True)
            return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
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
def update_sucursal(request):
    if request.method == 'POST':
        user = request.user
        grupoId = UnidadMedica.objects.get(user_id=user.id).id
        payload = json.loads(request.body)
        try:
            obj = Sucursal.objects.get(pk=int(payload["id"]))
            obj.nombre = payload["nombre"]
            obj.email = payload["email"]

            obj.save()
            tabla = Sucursal.objects.filter(unidadMedica=grupoId).order_by('id')
            tabla_serializer = SucursalSerializer(tabla, many=True)
            return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except Sucursal.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return JsonResponse({'error': 'There is already a record with that data'}, safe=False,
                                status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def update_sucursal_full(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            obj = Sucursal.objects.get(pk=int(payload["id"]))
            obj.nombre = payload["nombre"]
            obj.slogan = payload["slogan"]
            obj.quienes_somos = payload["quienes_somos"]
            obj.direccion = payload["direccion"]
            obj.compensacion = payload["compensacion"]
            obj.referencia_direccion = payload["referencia_direccion"]
            obj.telefono = payload["telefono"]
            obj.telefono_whatsapp = payload["telefono_whatsapp"]
            obj.facebook = payload["facebook"]
            obj.twitter = payload["twitter"]
            obj.pag_web = payload["pag_web"]
            obj.horario_atencion = payload["horario_atencion"]
            obj.lat = payload["latitud"]
            obj.lon = payload["longitud"]
            obj.activado = True

            if payload["provincia"] is not None:
                obj.provincia = Provincia.objects.get(id=payload["provincia"])
            if payload["canton"] is not None:
                obj.canton = Canton.objects.get(id=payload["canton"])
            if payload["parroquia"] is not None:
                obj.parroquia = Parroquia.objects.get(id=payload["parroquia"])

            obj.save()
            tabla = Sucursal.objects.filter().order_by('id')
            tabla_serializer = SucursalSerializer(tabla, many=True)
            return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except Sucursal.DoesNotExist as e:
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
def delete_sucursal(request):
    if request.method == 'POST':
        user = request.user
        grupoId = UnidadMedica.objects.get(user_id=user.id).id
        payload = json.loads(request.body)
        try:
            with transaction.atomic():
                obj = Sucursal.objects.get(pk=int(payload["id"]))
                obj.delete()
                tabla = Sucursal.objects.filter(unidadMedica=grupoId).order_by('id')
                tabla_serializer = SucursalSerializer(tabla, many=True)
                return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except Sucursal.DoesNotExist as e:
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
def delete_sucursal_grupo(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            with transaction.atomic():
                obj = Sucursal.objects.get(pk=int(payload["id"]))
                obj.delete()
                sucursal_list = []
                for sucursal_temp in Sucursal.objects.all():
                    sucursal_ele = {}
                    sucursal_ele["id"] = sucursal_temp.id
                    sucursal_ele["nombre"] = sucursal_temp.nombre
                    sucursal_ele["email"] = sucursal_temp.email
                    sucursal_ele["activado"] = sucursal_temp.activado
                    id_unidad = sucursal_temp.unidadMedica.id
                    sucursal_ele["grupo"] = UnidadMedica.objects.get(id=id_unidad).nombre
                    sucursal_list.append(sucursal_ele)
                return JsonResponse(sucursal_list, safe=False)
        except Sucursal.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return JsonResponse({'error': 'There is already a record with that data'}, safe=False,
                                status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return JsonResponse({'error': '{}'.format(str(e))}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)