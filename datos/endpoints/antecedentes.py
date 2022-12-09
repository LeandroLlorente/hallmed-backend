from django.http.response import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import Antecedentes, CIE, AntecedentesObstetricos, AntecedentesPediatricos
from ..serializers import AntecedentesSerializer
import json
from django.db import IntegrityError
from rest_framework import status
from django.db import transaction

#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_antecedentes_personales(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_consulta = payload["id_consulta"]
        antecedentes = []
        for antecedente in Antecedentes.objects.filter(tipo="PERSONAL", consulta=id_consulta).order_by('id'):
            antecedenteTemp = {}
            antecedenteTemp["id"] = CIE.objects.get(pk=antecedente.diagnostico.id).id
            antecedenteTemp["name"] = CIE.objects.get(pk=antecedente.diagnostico.id).cie
            antecedentes.append(antecedenteTemp)
        return JsonResponse(antecedentes, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_antecedentes_familiares(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_consulta = payload["id_consulta"]
        antecedentes = []
        for antecedente in Antecedentes.objects.filter(tipo="FAMILIAR", consulta=id_consulta).order_by('id'):
            antecedenteTemp = {}
            antecedenteTemp["id"] = CIE.objects.get(pk=antecedente.diagnostico.id).id
            antecedenteTemp["name"] = CIE.objects.get(pk=antecedente.diagnostico.id).cie
            antecedentes.append(antecedenteTemp)
        return JsonResponse(antecedentes, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_antecedentes_obtetricos(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_consulta = payload["id_consulta"]
        if len(AntecedentesObstetricos.objects.filter(consulta=id_consulta)) == 0:
            return JsonResponse({}, safe=False)
        antecedente = AntecedentesObstetricos.objects.filter(consulta=id_consulta)[0]
        antecedenteTemp = {}
        antecedenteTemp["gestas"] = antecedente.numGestas
        antecedenteTemp["partos"] = antecedente.numPartos
        antecedenteTemp["abortos"] = antecedente.numAbortos
        antecedenteTemp["desc_partos"] = antecedente.descPartos
        antecedenteTemp["desc_abortos"] = antecedente.descAbortos
        return JsonResponse(antecedenteTemp, safe=False)

# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_antecedentes_pediatricos(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_consulta = payload["id_consulta"]
        antecedenteTemp = {}
        if len(AntecedentesPediatricos.objects.filter(consulta=id_consulta)) == 0:
            return JsonResponse({}, safe=False)
        antecedente = AntecedentesPediatricos.objects.filter(consulta=id_consulta)[0]
        antecedenteTemp["antecedentes_prenatales"] = antecedente.antecedentePrenatal
        antecedenteTemp["antecedentes_natales"] = antecedente.antecedenteNatal
        antecedenteTemp["antecedentes_postnatales"] = antecedente.antecedentePostnatal
        return JsonResponse(antecedenteTemp, safe=False)

