from django.http.response import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import Resultados, Orden, Consulta, Actividad, Sucursal, UnidadMedica
from ..serializers import MedicamentoSerializer
import json
from django.db import IntegrityError
from rest_framework import status
from django.db import transaction


@authentication_classes([TokenAuthentication])
@permission_classes([])
@api_view(['POST'])
def add_resultados(request):
    if request.method == 'POST':
        id_consulta = request.data.get("id_consulta")
        resultado = Resultados()
        resultado.resultadosFile = request.data.get("resultado")
        resultado.consulta = Consulta.objects.get(pk=id_consulta)
        resultado.save()
        consulta = Consulta.objects.get(pk=id_consulta)
        consulta.estado = "RESULTADOS"
        consulta.save()
        resultadoLink = str(resultado.resultadosFile)

        # adiciona las actividades
        actividad = Actividad()
        actividad.consulta = Consulta.objects.get(pk=id_consulta)
        actividad.paciente = Consulta.objects.get(pk=id_consulta).paciente
        actividad.tipoActividad = "RESULTADOS"
        tipo = request.data.get("tipo")
        id = request.data.get("id")
        actividad.entidad = request.data.get("id")
        actividad.tipoEntidad = tipo
        if tipo == "SUCURSAL":
            actividad.nombreEntidad = Sucursal.objects.get(pk=id).nombre
        if tipo == "GRUPO":
            actividad.nombreEntidad = UnidadMedica.objects.get(pk=id).nombre_comercial
        actividad.save()
        return JsonResponse({"resultado": resultadoLink}, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)