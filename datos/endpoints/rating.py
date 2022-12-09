from django.http.response import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import Resultados, Orden, Consulta, RatingMedico, Medico, Paciente, RatingMedioDiagnostico, Sucursal, \
    UnidadMedica
from ..serializers import MedicamentoSerializer
import json
from django.db import IntegrityError
from rest_framework import status
from django.db import transaction

@authentication_classes([TokenAuthentication])
@permission_classes([])
@api_view(['POST'])
def add_rating_medico(request):
    if request.method == 'POST':
        id_paciente = request.data.get("id_paciente")
        id_medico = request.data.get("id_medico")
        id_consulta = request.data.get("id_consulta")
        rating = request.data.get("rating")
        if len(RatingMedico.objects.filter(paciente=id_paciente, medico=id_medico, consulta=id_consulta)) > 0:
            rating_medico = RatingMedico.objects.filter(paciente=id_paciente, medico=id_medico, consulta=id_consulta)[0]
            rating_medico.rating = rating
            rating_medico.save()
        else:
            rating_medico = RatingMedico()
            rating_medico.medico = Medico.objects.get(pk=id_medico)
            rating_medico.paciente = Paciente.objects.get(pk=id_paciente)
            rating_medico.consulta = Consulta.objects.get(pk=id_consulta)
            rating_medico.rating = rating
            rating_medico.save()
        return JsonResponse({"msg":"OK"}, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)





@authentication_classes([TokenAuthentication])
@permission_classes([])
@api_view(['POST'])
def add_rating_um(request):
    if request.method == 'POST':
        id_paciente = request.data.get("id_paciente")
        id_um = request.data.get("id_um")
        tipo_unidad = request.data.get("tipo_unidad")
        id_consulta = request.data.get("id_consulta")
        rating = request.data.get("rating")
        if tipo_unidad == "sucursal":
            records = RatingMedioDiagnostico.objects.filter(paciente=id_paciente, sucursal=id_um, tipo="SUCURSAL", consulta=id_consulta)
        else:
            records = RatingMedioDiagnostico.objects.filter(paciente=id_paciente, grupo=id_um, tipo="GRUPO", consulta=id_consulta)
        if len(records) > 0:
            rating_um = records[0]
            rating_um.rating = rating
            rating_um.save()
        else:
            rating_um = RatingMedioDiagnostico()
            rating_um.paciente = Paciente.objects.get(pk=id_paciente)
            if tipo_unidad == "sucursal":
                rating_um.sucursal = Sucursal.objects.get(pk=id_um)
                rating_um.tipo = "SUCURSAL"
            else:
                rating_um.grupo = UnidadMedica.objects.get(pk=id_um)
                rating_um.tipo = "GRUPO"
            rating_um.consulta = Consulta.objects.get(pk=id_consulta)
            rating_um.rating = rating
            rating_um.save()
        return JsonResponse({"msg":"OK"}, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)