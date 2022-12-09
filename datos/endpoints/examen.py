from django.http.response import JsonResponse
from django.db.models import Avg
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ..models import Examen, TipoExamen, Orden, SucursalExamen, Sucursal, GrupoExamen, UnidadMedica, \
    UnidadesRecomendadas, RatingMedioDiagnostico
from ..serializers import ExamenSerializer
import json
from django.db import IntegrityError
from rest_framework import status
from django.db import transaction
from django.db.models import Sum, Count
from operator import itemgetter

#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_examen(request):
    tipo = Examen.objects.filter().order_by('id')
    tipoSerializer = ExamenSerializer(tipo, many=True)
    return JsonResponse(tipoSerializer.data, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_examen(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            obj = Examen()
            obj.examen = payload["examen"]
            obj.tipo_examen = TipoExamen.objects.get(pk=payload["tipo_examen"])
            obj.codigo = payload["codigo"]
            obj.save()
            tabla = Examen.objects.filter().order_by('id')
            tabla_serializer = ExamenSerializer(tabla, many=True)
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
def update_examen(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            obj = Examen.objects.get(pk=int(payload["id"]))
            obj.examen = payload["examen"]
            obj.tipo_examen = TipoExamen.objects.get(pk=int(payload["tipoexamen"]))
            obj.codigo = payload["codigo"]

            obj.save()
            tabla = Examen.objects.filter().order_by('id')
            tabla_serializer = ExamenSerializer(tabla, many=True)
            return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except Examen.DoesNotExist as e:
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
def delete_examen(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            with transaction.atomic():
                obj = Examen.objects.get(pk=int(payload["id"]))
                obj.delete()
                tabla = Examen.objects.filter().order_by('id')
                tabla_serializer = ExamenSerializer(tabla, many=True)
                return JsonResponse(tabla_serializer.data, safe=False, status=status.HTTP_201_CREATED)
        except Examen.DoesNotExist as e:
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
def list_unidades_todos_examen(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_consulta = payload["id_consulta"]

        # obtiene los grupos y sucursales recomendados
        gruposRecomedados = []
        sucuralesRecomendas = []
        for recomendacion in UnidadesRecomendadas.objects.filter(consulta=id_consulta):
            if recomendacion.tipo == "sucursal":
                sucuralesRecomendas.append(recomendacion.sucursal.id)
            if recomendacion.tipo == "grupo":
                gruposRecomedados.append(recomendacion.grupo.id)

        print(sucuralesRecomendas)
        print(gruposRecomedados)

        idExamenes = []
        for examenesOrdenados in Orden.objects.filter(consulta=id_consulta):
            idExamenes.append(examenesOrdenados.examen.id)
        # print(idExamenes)
        cantidadExamenesConsulta = len(idExamenes)

        # procesa los examenes de las sucursales
        examenes = []
        for examSucursal_temp in SucursalExamen.objects.filter(examen__in=idExamenes).values('sucursal').order_by('sucursal').annotate(precio=Sum('precio')).annotate(cantidad=Count('id')):
            if examSucursal_temp["cantidad"] == cantidadExamenesConsulta:
                sucursalTemp = Sucursal.objects.get(pk=examSucursal_temp["sucursal"])
                # print(sucursalTemp.nombre)
                examSucursal_ele = {}
                examSucursal_ele["id"] = sucursalTemp.id
                examSucursal_ele["nombre"] = sucursalTemp.nombre
                examSucursal_ele["direccion"] = sucursalTemp.direccion
                examSucursal_ele["referencia_direccion"] = sucursalTemp.referencia_direccion
                examSucursal_ele["tipo"] = "sucursal"
                if sucursalTemp.id in sucuralesRecomendas:
                    examSucursal_ele["recomendada"] = True
                else:
                    examSucursal_ele["recomendada"] = False

                provincia = ""
                idProvincia = 0
                if sucursalTemp.provincia is not None:
                    provincia = sucursalTemp.provincia.provincia
                    idProvincia = sucursalTemp.provincia.id
                examSucursal_ele["provincia"] = provincia
                examSucursal_ele["id_provincia"] = idProvincia

                canton = ""
                idCanton = 0
                if sucursalTemp.canton is not None:
                    canton = sucursalTemp.canton.canton
                    idCanton = sucursalTemp.canton.id
                examSucursal_ele["canton"] = canton
                examSucursal_ele["id_canton"] = idCanton

                parroquia = ""
                idParroquia = 0
                if sucursalTemp.parroquia is not None:
                    parroquia = sucursalTemp.parroquia.parroquia
                    idParroquia = sucursalTemp.parroquia.id
                examSucursal_ele["parroquia"] = parroquia
                examSucursal_ele["id_parroquia"] = idParroquia

                examSucursal_ele["telefono"] = sucursalTemp.telefono
                examSucursal_ele["lat"] = sucursalTemp.lat
                examSucursal_ele["lon"] = sucursalTemp.lon
                if examSucursal_temp["precio"] is None:
                    examSucursal_ele["precio_total"] = 0
                else:
                    examSucursal_ele["precio_total"] = float(format(examSucursal_temp["precio"], '.2f'))

                ratingAvg = RatingMedioDiagnostico.objects.filter(sucursal=sucursalTemp.id).aggregate(Avg('rating'))
                if ratingAvg["rating__avg"] is not None:
                    examSucursal_ele["rating_um_total"] = str(ratingAvg["rating__avg"])
                else:
                    examSucursal_ele["rating_um_total"] = '0'

                examenes.append(examSucursal_ele)

        # procesa los examenes de los grupos
        for examGrupo_temp in GrupoExamen.objects.filter(examen__in=idExamenes).values('grupo').order_by(
                'grupo').annotate(precio=Sum('precio')).annotate(cantidad=Count('id')):
            if examGrupo_temp["cantidad"] == cantidadExamenesConsulta:
                grupoTemp = UnidadMedica.objects.get(pk=examGrupo_temp["grupo"])
                # print(grupoTemp.nombre)
                examGrupo_ele = {}
                examGrupo_ele["id"] = grupoTemp.id
                examGrupo_ele["nombre"] = grupoTemp.nombre_comercial
                examGrupo_ele["direccion"] = grupoTemp.direccion
                examGrupo_ele["referencia_direccion"] = grupoTemp.referencia_direccion
                examGrupo_ele["tipo"] = "grupo"
                if grupoTemp.id in gruposRecomedados:
                    examGrupo_ele["recomendada"] = True
                else:
                    examGrupo_ele["recomendada"] = False

                provincia = ""
                idProvincia = 0
                if grupoTemp.provincia is not None:
                    provincia = grupoTemp.provincia.provincia
                    idProvincia = grupoTemp.provincia.id
                examGrupo_ele["provincia"] = provincia
                examGrupo_ele["id_provincia"] = idProvincia

                canton = ""
                idCanton = 0
                if grupoTemp.canton is not None:
                    canton = grupoTemp.canton.canton
                    idCanton = grupoTemp.canton.id
                examGrupo_ele["canton"] = canton
                examGrupo_ele["id_canton"] = idCanton

                parroquia = ""
                idParroquia = 0
                if grupoTemp.parroquia is not None:
                    parroquia = grupoTemp.parroquia.parroquia
                    idParroquia = grupoTemp.parroquia.id
                examGrupo_ele["parroquia"] = parroquia
                examGrupo_ele["id_parroquia"] = idParroquia

                examGrupo_ele["telefono"] = grupoTemp.telefono
                examGrupo_ele["lat"] = grupoTemp.lat
                examGrupo_ele["lon"] = grupoTemp.lon
                if examGrupo_temp["precio"] is not None:
                    examGrupo_ele["precio_total"] = float(format(examGrupo_temp["precio"], '.2f'))
                else:
                    examGrupo_ele["precio_total"] = 0

                ratingAvg = RatingMedioDiagnostico.objects.filter(grupo=grupoTemp.id).aggregate(Avg('rating'))
                if ratingAvg["rating__avg"] is not None:
                    examGrupo_ele["rating_um_total"] = str(ratingAvg["rating__avg"])
                else:
                    examGrupo_ele["rating_um_total"] = '0'

                examenes.append(examGrupo_ele)

        ordenada = sorted(examenes, key=itemgetter('precio_total'))

        return JsonResponse(ordenada, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def recomendar_unidades_todos_examen(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        idExamenes = json.loads(payload["examenes"])
        print(idExamenes)
        cantidadExamenesConsulta = len(idExamenes)
        # print(SucursalExamen.objects.filter(examen__in=idExamenes).values('sucursal').order_by('sucursal').annotate(precio=Sum('precio')).annotate(cantidad=Count('id')))
        # procesa los examenes de las sucursales
        examenes = []
        for examSucursal_temp in SucursalExamen.objects.filter(examen__in=idExamenes).values('sucursal').order_by('sucursal').annotate(precio=Sum('precio')).annotate(cantidad=Count('id')):
            if examSucursal_temp["cantidad"] == cantidadExamenesConsulta:
                sucursalTemp = Sucursal.objects.get(pk=examSucursal_temp["sucursal"])
                # print(sucursalTemp.nombre)
                examSucursal_ele = {}
                examSucursal_ele["id"] = sucursalTemp.id
                examSucursal_ele["nombre"] = sucursalTemp.nombre
                examSucursal_ele["direccion"] = sucursalTemp.direccion
                examSucursal_ele["referencia_direccion"] = sucursalTemp.referencia_direccion
                examSucursal_ele["tipo"] = "sucursal"

                provincia = ""
                idProvincia = 0
                if sucursalTemp.provincia is not None:
                    provincia = sucursalTemp.provincia.provincia
                    idProvincia = sucursalTemp.provincia.id
                examSucursal_ele["provincia"] = provincia
                examSucursal_ele["id_provincia"] = idProvincia

                canton = ""
                idCanton = 0
                if sucursalTemp.canton is not None:
                    canton = sucursalTemp.canton.canton
                    idCanton = sucursalTemp.canton.id
                examSucursal_ele["canton"] = canton
                examSucursal_ele["id_canton"] = idCanton

                parroquia = ""
                idParroquia = 0
                if sucursalTemp.parroquia is not None:
                    parroquia = sucursalTemp.parroquia.parroquia
                    idParroquia = sucursalTemp.parroquia.id
                examSucursal_ele["parroquia"] = parroquia
                examSucursal_ele["id_parroquia"] = idParroquia

                examSucursal_ele["telefono"] = sucursalTemp.telefono
                examSucursal_ele["lat"] = sucursalTemp.lat
                examSucursal_ele["lon"] = sucursalTemp.lon
                examSucursal_ele["precio_total"] = float(format(examSucursal_temp["precio"], '.2f'))
                examenes.append(examSucursal_ele)

        # procesa los examenes de los grupos
        for examGrupo_temp in GrupoExamen.objects.filter(examen__in=idExamenes).values('grupo').order_by(
                'grupo').annotate(precio=Sum('precio')).annotate(cantidad=Count('id')):
            if examGrupo_temp["cantidad"] == cantidadExamenesConsulta:
                grupoTemp = UnidadMedica.objects.get(pk=examGrupo_temp["grupo"])
                # print(grupoTemp.nombre)
                examGrupo_ele = {}
                examGrupo_ele["id"] = grupoTemp.id
                examGrupo_ele["nombre"] = grupoTemp.nombre_comercial
                examGrupo_ele["direccion"] = grupoTemp.direccion
                examGrupo_ele["referencia_direccion"] = grupoTemp.referencia_direccion
                examGrupo_ele["tipo"] = "grupo"

                provincia = ""
                idProvincia = 0
                if grupoTemp.provincia is not None:
                    provincia = grupoTemp.provincia.provincia
                    idProvincia = grupoTemp.provincia.id
                examGrupo_ele["provincia"] = provincia
                examGrupo_ele["id_provincia"] = idProvincia

                canton = ""
                idCanton = 0
                if grupoTemp.canton is not None:
                    canton = grupoTemp.canton.canton
                    idCanton = grupoTemp.canton.id
                examGrupo_ele["canton"] = canton
                examGrupo_ele["id_canton"] = idCanton

                parroquia = ""
                idParroquia = 0
                if grupoTemp.parroquia is not None:
                    parroquia = grupoTemp.parroquia.parroquia
                    idParroquia = grupoTemp.parroquia.id
                examGrupo_ele["parroquia"] = parroquia
                examGrupo_ele["id_parroquia"] = idParroquia

                examGrupo_ele["telefono"] = grupoTemp.telefono
                examGrupo_ele["lat"] = grupoTemp.lat
                examGrupo_ele["lon"] = grupoTemp.lon
                if examGrupo_temp["precio"] is not None:
                    examGrupo_ele["precio_total"] = float(format(examGrupo_temp["precio"], '.2f'))
                else:
                    examGrupo_ele["precio_total"] = 0
                examenes.append(examGrupo_ele)

        ordenada = sorted(examenes, key=itemgetter('precio_total'))

        return JsonResponse(ordenada, safe=False)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)