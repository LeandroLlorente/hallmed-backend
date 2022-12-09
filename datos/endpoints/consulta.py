from django.db.models import Avg
from django.http.response import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from ..models import Consulta, Medico, Paciente, CIE, Orden, Examen, MedicamentoRecetado, Medicamento, Farmacia, \
    Sucursal, UnidadMedica, UnidadesRecomendadas, Antecedentes, Resultados, AntecedentesObstetricos, RatingMedico, \
    RatingMedioDiagnostico, Actividad, AntecedentesPediatricos
from ..serializers import ConsultaSerializer
import json
from django.db import IntegrityError
from rest_framework import status
from django.db import transaction


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_consultas(request):
    user = request.user
    consultas = []
    print(user.id)
    id_medico = Medico.objects.get(user_id=user.id).id
    for consultas_temp in Consulta.objects.filter(medico=id_medico).order_by('-id'):
        consultas_ele = {}
        consultas_ele["id"] = consultas_temp.id
        consultas_ele["id_paciente"] = consultas_temp.paciente.id
        consultas_ele["paciente"] = consultas_temp.paciente.nombre + " "  + consultas_temp.paciente.apellidos
        consultas_ele["id_diagnostico"] = consultas_temp.diagnostico.id
        consultas_ele["diagnostico"] = consultas_temp.diagnostico.cie
        consultas_ele["tipo_diagnostico"] = consultas_temp.tipo_diagnostico
        fecha = consultas_temp.fecha
        arrFecha = str(fecha).split("-")
        consultas_ele["fecha"] = arrFecha[2] + "/" + arrFecha[1] + "/" + arrFecha[0]
        resultados = ""
        if len(Resultados.objects.filter(consulta=consultas_temp.id)) > 0:
            resultados = str(Resultados.objects.filter(consulta=consultas_temp.id)[0].resultadosFile)
        consultas_ele["resultados"] = resultados
        consultas_ele["motivo_consulta"] = consultas_temp.motivo_consulta
        consultas_ele["examen_clinico"] = consultas_temp.examenClinico
        consultas_ele["historia_enfermedad"] = consultas_temp.historia_enfermedad
        consultas.append(consultas_ele)
    return JsonResponse(consultas, safe=False)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_consulta(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        medico = Medico.objects.get(user_id=request.user.id)
        examenes_ordenados = json.loads(payload["examenes_ordenados"])
        motivo_consulta = payload["motivo_consulta"]
        examen_clinico = payload["examen_clinico"]
        tipoDiagnostico = payload["tipoDiagnostico"]
        historia_enfermedad = payload["historia_enfermedad"]
        medicamentos_recetados = json.loads(payload["medicamentos_recetados"])
        unidades_recomendadas = json.loads(payload["unidades_recomendadas"])
        antecedentes_personales = json.loads(payload["antecedentes_personales"])
        antecedentes_familiares = json.loads(payload["antecedentes_familiares"])
        antecedentes_prenatales = payload["antecedentes_prenatales"]
        antecedentes_natales = payload["antecedentes_natales"]
        antecedentes_postnatales = payload["antecedentes_postnatales"]
        # print(medicamentos_recetados)
        with transaction.atomic():
            obj = Consulta()
            obj.medico = medico
            obj.paciente = Paciente.objects.get(id=payload["id_paciente"])
            obj.diagnostico = CIE.objects.get(id=payload["id_diagnostico"])
            obj.motivo_consulta = motivo_consulta
            obj.examenClinico = examen_clinico
            obj.historia_enfermedad = historia_enfermedad
            obj.tipo_diagnostico = tipoDiagnostico
            obj.save()
            id_consulta = obj.id
            print(obj.id)

            # adiciona examenes
            for examen in examenes_ordenados:
                OrdenTemp = Orden()
                OrdenTemp.consulta = obj
                OrdenTemp.examen = Examen.objects.get(id=examen) 
                OrdenTemp.save()

            # adiciona medicamentos recetados
            for medi in medicamentos_recetados:
                # print(medi)
                medicaRecetadoTemp = MedicamentoRecetado()
                medicaRecetadoTemp.consulta = obj
                medicaRecetadoTemp.medicamento = Medicamento.objects.get(id=medi["id"])
                medicaRecetadoTemp.indicaciones = medi["indicaciones"]

                medicaRecetadoTemp.save()

            # adiciona las unidades recomendadas
            for recomendacion in unidades_recomendadas:
                recomendadoTemp = UnidadesRecomendadas()
                recomendadoTemp.tipo = recomendacion["tipo"]
                if (recomendacion["tipo"] == "sucursal"):
                    recomendadoTemp.sucursal = Sucursal.objects.get(pk=recomendacion["id"])
                if (recomendacion["tipo"] == "grupo"):
                    recomendadoTemp.grupo = UnidadMedica.objects.get(pk=recomendacion["id"])
                recomendadoTemp.consulta = Consulta.objects.get(pk=id_consulta)
                recomendadoTemp.save()

            # adiciona los antecedentes personales
            for antecedente in antecedentes_personales:
                antecedenteTemp = Antecedentes()
                antecedenteTemp.consulta = Consulta.objects.get(pk=id_consulta)
                antecedenteTemp.diagnostico = CIE.objects.get(pk=antecedente)
                antecedenteTemp.tipo = "PERSONAL"
                antecedenteTemp.save()

            # adiciona los antecedentes familiares
            for antecedente in antecedentes_familiares:
                antecedenteTemp = Antecedentes()
                antecedenteTemp.consulta = Consulta.objects.get(pk=id_consulta)
                antecedenteTemp.diagnostico = CIE.objects.get(pk=antecedente)
                antecedenteTemp.tipo = "FAMILIAR"
                antecedenteTemp.save()

            if antecedentes_prenatales != "" and antecedentes_natales != "" and antecedentes_postnatales != "":
                antecedente = AntecedentesPediatricos()
                antecedente.consulta = Consulta.objects.get(pk=id_consulta)
                antecedente.antecedentePrenatal = antecedentes_prenatales
                antecedente.antecedenteNatal = antecedentes_natales
                antecedente.antecedentePostnatal = antecedentes_postnatales
                antecedente.save()

            # adiciona los antecedentes obstetricos
            antObst = AntecedentesObstetricos()
            if payload["gesta"] != "":
                antObst.numGestas = int(payload["gesta"])
            if payload["partos"] != "":
                antObst.numPartos = int(payload["partos"])
            if payload["abortos"] != "":
                antObst.numAbortos = int(payload["abortos"])
            antObst.descPartos = payload["desc_partos"]
            antObst.descAbortos = payload["desc_abortos"]
            antObst.consulta = Consulta.objects.get(pk=id_consulta)
            antObst.save()

            # adiciona las actividades
            actividad = Actividad()
            actividad.paciente = Paciente.objects.get(pk=payload["id_paciente"])
            actividad.consulta = Consulta.objects.get(pk=id_consulta)
            actividad.tipoActividad = "CONSULTA"
            actividad.save()

            consultas = []
            # id_medico = Medico.objects.get(user_id=user.id).id
            for consultas_temp in Consulta.objects.filter(medico=medico.id).order_by('-id'):
                consultas_ele = {}
                consultas_ele["id"] = consultas_temp.id
                consultas_ele["id_paciente"] = consultas_temp.paciente.id
                consultas_ele["paciente"] = consultas_temp.paciente.nombre + " " + consultas_temp.paciente.apellidos
                consultas_ele["id_diagnostico"] = consultas_temp.diagnostico.id
                consultas_ele["diagnostico"] = consultas_temp.diagnostico.cie
                consultas_ele["tipo_diagnostico"] = consultas_temp.tipo_diagnostico
                fecha = consultas_temp.fecha
                arrFecha = str(fecha).split("-")
                consultas_ele["fecha"] = arrFecha[2] + "/" + arrFecha[1] + "/" + arrFecha[0]
                resultados = ""
                if len(Resultados.objects.filter(consulta=consultas_temp.id)) > 0:
                    resultados = str(Resultados.objects.filter(consulta=consultas_temp.id)[0].resultadosFile)
                consultas_ele["resultados"] = resultados
                consultas_ele["motivo_consulta"] = consultas_temp.motivo_consulta
                consultas_ele["examen_clinico"] = consultas_temp.examenClinico
                consultas_ele["historia_enfermedad"] = consultas_temp.historia_enfermedad
                consultas.append(consultas_ele)
            return JsonResponse(consultas, safe=False, status=status.HTTP_201_CREATED)
    else:
            return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_consulta(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        medico = Medico.objects.get(user_id=request.user.id)
        examenes_ordenados = json.loads(payload["examenes_ordenados"])
        unidades_recomendadas = json.loads(payload["unidades_recomendadas"])
        antecedentes_personales = json.loads(payload["antecedentes_personales"])
        antecedentes_familiares = json.loads(payload["antecedentes_familiares"])
        antecedentes_prenatales = payload["antecedentes_prenatales"]
        antecedentes_natales = payload["antecedentes_natales"]
        antecedentes_postnatales = payload["antecedentes_postnatales"]
        examen_clinico = payload["examen_clinico"]


        tipoDiagnostico = payload["tipoDiagnostico"]
        estado = payload["estado"]
        motivo_consulta = ""
        if payload["motivo_consulta"] is not None:
            motivo_consulta = payload["motivo_consulta"]
        historia_enfermedad = ""
        if payload["historia_enfermedad"] is not None:
            historia_enfermedad = payload["historia_enfermedad"]
        medicamentos_recetados = json.loads(payload["medicamentos_recetados"])
        id_consulta = int(payload["id"])
        # print(medicamentos_recetados)
        with transaction.atomic():
            obj = Consulta.objects.get(pk=id_consulta)
            obj.medico = medico
            obj.paciente = Paciente.objects.get(id=payload["id_paciente"])
            obj.diagnostico = CIE.objects.get(id=payload["id_diagnostico"])
            obj.tipo_diagnostico = tipoDiagnostico
            obj.motivo_consulta = motivo_consulta
            obj.historia_enfermedad = historia_enfermedad
            obj.examenClinico = examen_clinico
            obj.save()
            id_consulta = obj.id

            if estado == "INDICADO":
                # borra todos los examenes
                for examenDel in Orden.objects.filter(consulta=id_consulta):
                    examenDel.delete()

                # adiciona examenes
                for examen in examenes_ordenados:
                    OrdenTemp = Orden()
                    OrdenTemp.consulta = obj
                    OrdenTemp.examen = Examen.objects.get(id=examen)
                    OrdenTemp.save()

            # borra los medicamentos recetados
            for medicamentoDel in MedicamentoRecetado.objects.filter(consulta=id_consulta):
                medicamentoDel.delete()

            # adiciona medicamentos recetados
            for medi in medicamentos_recetados:
                # print(medi)
                medicaRecetadoTemp = MedicamentoRecetado()
                medicaRecetadoTemp.consulta = obj
                medicaRecetadoTemp.medicamento = Medicamento.objects.get(id=medi["id"])
                medicaRecetadoTemp.indicaciones = medi["indicaciones"]
                medicaRecetadoTemp.save()

            # borra las unidades recomendadas
            for recomendacion in UnidadesRecomendadas.objects.filter(consulta=id_consulta):
                recomendacion.delete()

            # adiciona las unidades recomendadas
            for recomendacion in unidades_recomendadas:
                recomendadoTemp = UnidadesRecomendadas()
                recomendadoTemp.tipo = recomendacion["tipo"]
                if (recomendacion["tipo"] == "sucursal"):
                    recomendadoTemp.sucursal = Sucursal.objects.get(pk=recomendacion["id"])
                if (recomendacion["tipo"] == "grupo"):
                    recomendadoTemp.grupo = UnidadMedica.objects.get(pk=recomendacion["id"])
                recomendadoTemp.consulta = Consulta.objects.get(pk=id_consulta)
                recomendadoTemp.save()

            # borra los antecedentes personales
            for antecedente in Antecedentes.objects.filter(consulta=id_consulta, tipo="PERSONAL"):
                antecedente.delete()

            # adiciona los antecedentes personales
            for antecedente in antecedentes_personales:
                antecedenteTemp = Antecedentes()
                antecedenteTemp.consulta = Consulta.objects.get(pk=id_consulta)
                antecedenteTemp.diagnostico = CIE.objects.get(pk=antecedente)
                antecedenteTemp.tipo = "PERSONAL"
                antecedenteTemp.save()

            # borra los antecedentes familiares
            for antecedente in Antecedentes.objects.filter(consulta=id_consulta, tipo="FAMILIAR"):
                antecedente.delete()

            # adiciona los antecedentes familiares
            for antecedente in antecedentes_familiares:
                antecedenteTemp = Antecedentes()
                antecedenteTemp.consulta = Consulta.objects.get(pk=id_consulta)
                antecedenteTemp.diagnostico = CIE.objects.get(pk=antecedente)
                antecedenteTemp.tipo = "FAMILIAR"
                antecedenteTemp.save()

            # adiciona los antecedentes obstetricos
            if payload["gesta"] != "" or payload["partos"] != "" or payload["desc_partos"] != "" or payload["abortos"] != "" or payload["desc_abortos"] != "":
                antObst = AntecedentesObstetricos.objects.filter(consulta=id_consulta)
                print(len(antObst))
                if len(antObst) == 0:
                    antObst = AntecedentesObstetricos()
                else:
                    antObst = AntecedentesObstetricos.objects.filter(consulta=id_consulta)[0]
                if payload["gesta"] != "" and payload["gesta"] is not None:
                    antObst.numGestas = int(payload["gesta"])
                if payload["partos"] != "" and payload["partos"] is not None:
                    antObst.numPartos = int(payload["partos"])
                if payload["abortos"] != "" and payload["abortos"] is not None:
                    antObst.numAbortos = int(payload["abortos"])
                antObst.descPartos = payload["desc_partos"]
                antObst.descAbortos = payload["desc_abortos"]
                antObst.consulta = Consulta.objects.get(pk=id_consulta)
                antObst.save()

            if antecedentes_prenatales != "" and antecedentes_natales != "" and antecedentes_postnatales != "":
                if len(AntecedentesPediatricos.objects.filter(consulta=id_consulta)) > 0:
                    antecedente = AntecedentesPediatricos.objects.filter(consulta=id_consulta)[0]
                    antecedente.delete()
                antecedente = AntecedentesPediatricos()
                antecedente.consulta = Consulta.objects.get(pk=id_consulta)
                antecedente.antecedentePrenatal = antecedentes_prenatales
                antecedente.antecedenteNatal = antecedentes_natales
                antecedente.antecedentePostnatal = antecedentes_postnatales
                antecedente.save()

            consultas = []
            # id_medico = Medico.objects.get(user_id=user.id).id
            for consultas_temp in Consulta.objects.filter(medico=medico.id).order_by('-id'):
                consultas_ele = {}
                consultas_ele["id"] = consultas_temp.id
                consultas_ele["id_paciente"] = consultas_temp.paciente.id
                consultas_ele["paciente"] = consultas_temp.paciente.nombre + " " + consultas_temp.paciente.apellidos
                consultas_ele["id_diagnostico"] = consultas_temp.diagnostico.id
                consultas_ele["diagnostico"] = consultas_temp.diagnostico.cie
                consultas_ele["tipo_diagnostico"] = consultas_temp.tipo_diagnostico
                fecha = consultas_temp.fecha
                arrFecha = str(fecha).split("-")
                consultas_ele["fecha"] = arrFecha[2] + "/" + arrFecha[1] + "/" + arrFecha[0]
                resultados = ""
                if len(Resultados.objects.filter(consulta=consultas_temp.id)) > 0:
                    resultados = str(Resultados.objects.filter(consulta=consultas_temp.id)[0].resultadosFile)
                consultas_ele["resultados"] = resultados
                consultas_ele["motivo_consulta"] = consultas_temp.motivo_consulta
                consultas_ele["examen_clinico"] = consultas_temp.examenClinico
                consultas_ele["historia_enfermedad"] = consultas_temp.historia_enfermedad
                consultas.append(consultas_ele)
            return JsonResponse(consultas, safe=False, status=status.HTTP_201_CREATED)
    else:
            return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def list_medicamentos_consulta(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        id_consulta = payload["id_consulta"]

        medicamento = []
        for medRecetado in MedicamentoRecetado.objects.filter(consulta=id_consulta).order_by('id'):
            medRecetado_ele = {}
            medRecetado_ele["id"] = medRecetado.medicamento.id
            medRecetado_ele["name"] = str(medRecetado.medicamento.nombre_generico) + " - " + \
                                      str(medRecetado.medicamento.nombre_comercial) + " " + \
                                      str(medRecetado.medicamento.tipo_especifico)
            # medRecetado_ele["medicamento"] = []

            medRecetado_ele["indicaciones"] = medRecetado.indicaciones

            medicamento.append(medRecetado_ele)
        return JsonResponse(medicamento, safe=False, status=status.HTTP_201_CREATED)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def delete_consulta(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        medico = Medico.objects.get(user_id=request.user.id)

        try:
            with transaction.atomic():
                id_consulta = int(payload["id"])
                obj = Consulta.objects.get(pk=id_consulta)
                medicamentosRecetados = MedicamentoRecetado.objects.filter(consulta=id_consulta).order_by('id')
                if len(medicamentosRecetados) > 0:
                    print("tiene medicamnetos")
                    msg = "No se puede borrar la consulta porque tiene asociada medicamentos recetados"
                    return JsonResponse({'error': '{}'.format(msg)}, safe=False, status=status.HTTP_409_CONFLICT)

                ordenesExamen = Orden.objects.filter(consulta=id_consulta).order_by('id')
                if len(ordenesExamen) > 0:
                    print("tiene examenes")
                    msg = "No se puede borrar la consulta porque tiene asociada indicaciones de exámenes"
                    return JsonResponse({'error': '{}'.format(msg)}, safe=False, status=status.HTTP_409_CONFLICT)

                obj.delete()
                consultas = []
                # id_medico = Medico.objects.get(user_id=user.id).id
                for consultas_temp in Consulta.objects.filter(medico=medico.id).order_by('-id'):
                    consultas_ele = {}
                    consultas_ele["id"] = consultas_temp.id
                    consultas_ele["id_paciente"] = consultas_temp.paciente.id
                    consultas_ele["paciente"] = consultas_temp.paciente.nombre + " " + consultas_temp.paciente.apellidos
                    consultas_ele["id_diagnostico"] = consultas_temp.diagnostico.id
                    consultas_ele["diagnostico"] = consultas_temp.diagnostico.cie
                    consultas_ele["tipo_diagnostico"] = consultas_temp.tipo_diagnostico
                    fecha = consultas_temp.fecha
                    arrFecha = str(fecha).split("-")
                    consultas_ele["fecha"] = arrFecha[2] + "/" + arrFecha[1] + "/" + arrFecha[0]
                    resultados = ""
                    if len(Resultados.objects.filter(consulta=consultas_temp.id)) > 0:
                        resultados = str(Resultados.objects.filter(consulta=consultas_temp.id)[0].resultadosFile)
                    consultas_ele["resultados"] = resultados
                    consultas_ele["motivo_consulta"] = consultas_temp.motivo_consulta
                    consultas_ele["examen_clinico"] = consultas_temp.examenClinico
                    consultas_ele["historia_enfermedad"] = consultas_temp.historia_enfermedad
                    consultas.append(consultas_ele)
                return JsonResponse(consultas, safe=False, status=status.HTTP_201_CREATED)
        except Consulta.DoesNotExist as e:
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
def consultas_by_pacientes(request):
    if request.method == 'POST':
        id_paciente = Paciente.objects.get(user_id=request.user.id).id
        consultas = []
        for consulta_temp in Consulta.objects.filter(paciente=id_paciente).order_by('-fecha')[:15]:
            consultas_ele = {}
            consultas_ele["id_consulta"] = consulta_temp.id
            consultas_ele["estado"] = consulta_temp.estado
            resultado = ""
            if consulta_temp.estado == "RESULTADOS":
                resultado = str(Resultados.objects.get(consulta=consulta_temp.id).resultadosFile)
            consultas_ele["resultado"] = resultado
            consultas_ele["id_medico"] = consulta_temp.medico.id
            consultas_ele["nombre_medico"] = consulta_temp.medico.nombre
            consultas_ele["apellidos_medico"] = consulta_temp.medico.apellidos
            consultas_ele["cedula"] = consulta_temp.medico.cedula
            consultas_ele["codigo"] = consulta_temp.medico.codigo
            especialidad = ""
            if consulta_temp.medico.especialidad1 is not None:
                especialidad = str(consulta_temp.medico.especialidad1.especialidad)
            consultas_ele["especialidad_medico"] = especialidad
            consultas_ele["diagnostico"] = consulta_temp.diagnostico.cie
            consultas_ele["tipo_diagnostico"] = consulta_temp.tipo_diagnostico
            fecha = consulta_temp.fecha
            arrFecha = str(fecha).split("-")
            consultas_ele["fecha"] = arrFecha[2]+"/"+arrFecha[1]+"/"+arrFecha[0]

            if len(RatingMedico.objects.filter(consulta=consulta_temp.id)) >0:
                consultas_ele["rating"] = RatingMedico.objects.filter(consulta=consulta_temp.id)[0].rating
            else:
                consultas_ele["rating"] = 0

            if len(RatingMedioDiagnostico.objects.filter(consulta=consulta_temp.id)) >0:
                consultas_ele["rating_um"] = RatingMedioDiagnostico.objects.filter(consulta=consulta_temp.id)[0].rating
            else:
                consultas_ele["rating_um"] = 0

            # adiciona los examenes ordenados  ------------------------------------------------------------------------
            examenesSolicitados = False
            ordenes = []
            tipoUnidad = ""
            unidad_ele = {}
            for orden_temp in Orden.objects.filter(consulta=consulta_temp.id):
                if orden_temp.tipo != "":
                    examenesSolicitados = True
                    tipoUnidad = orden_temp.tipo
                orden_ele = {}
                orden_ele["id"] = orden_temp.id
                orden_ele["id_examen"] = orden_temp.examen.id
                orden_ele["examen"] = orden_temp.examen.examen
                orden_ele["codigo"] = orden_temp.examen.codigo
                orden_ele["tipo_examen"] = orden_temp.examen.tipo_examen.tipo_examen

                ordenes.append(orden_ele)
            consultas_ele["orden_examen"] = ordenes

            if examenesSolicitados:
                precio_total = Orden.objects.filter(consulta=consulta_temp.id)[0].precio_total
                if tipoUnidad == "SUCURSAL":
                    id = Orden.objects.filter(consulta=consulta_temp.id)[0].sucursal.id
                    sucursalTemp = Sucursal.objects.get(pk=id)
                    unidad_ele["id"] = sucursalTemp.id
                    unidad_ele["nombre"] = sucursalTemp.nombre
                    unidad_ele["direccion"] = sucursalTemp.direccion
                    unidad_ele["referencia_direccion"] = sucursalTemp.referencia_direccion
                    unidad_ele["referencia_direccion"] = sucursalTemp.referencia_direccion
                    unidad_ele["tipo"] = "sucursal"
                    unidad_ele["unidad_solicitada"] = examenesSolicitados

                    provincia = ""
                    if sucursalTemp.provincia is not None:
                        provincia = sucursalTemp.provincia.provincia
                    unidad_ele["provincia"] = provincia

                    canton = ""
                    if sucursalTemp.canton is not None:
                        canton = sucursalTemp.canton.canton
                    unidad_ele["canton"] = canton

                    parroquia = ""
                    if sucursalTemp.parroquia is not None:
                        parroquia = sucursalTemp.parroquia.parroquia
                    unidad_ele["parroquia"] = parroquia

                    unidad_ele["telefono"] = sucursalTemp.telefono
                    unidad_ele["lat"] = sucursalTemp.lat
                    unidad_ele["lon"] = sucursalTemp.lon
                    unidad_ele["precio_total"] = precio_total

                if tipoUnidad == "GRUPO":
                    id = Orden.objects.filter(consulta=consulta_temp.id)[0].grupo.id
                    grupoTemp = UnidadMedica.objects.get(pk=id)
                    unidad_ele["id"] = grupoTemp.id
                    unidad_ele["nombre"] = grupoTemp.nombre
                    unidad_ele["direccion"] = grupoTemp.direccion
                    unidad_ele["referencia_direccion"] = grupoTemp.referencia_direccion
                    unidad_ele["referencia_direccion"] = grupoTemp.referencia_direccion
                    unidad_ele["tipo"] = "grupo"
                    unidad_ele["unidad_solicitada"] = examenesSolicitados

                    provincia = ""
                    if grupoTemp.provincia is not None:
                        provincia = grupoTemp.provincia.provincia
                    unidad_ele["provincia"] = provincia

                    canton = ""
                    if grupoTemp.canton is not None:
                        canton = grupoTemp.canton.canton
                    unidad_ele["canton"] = canton

                    parroquia = ""
                    if grupoTemp.parroquia is not None:
                        parroquia = grupoTemp.parroquia.parroquia
                    unidad_ele["parroquia"] = parroquia

                    unidad_ele["telefono"] = grupoTemp.telefono
                    unidad_ele["lat"] = grupoTemp.lat
                    unidad_ele["lon"] = grupoTemp.lon
                    unidad_ele["precio_total"] = precio_total

                consultas_ele["unidadSolicitada"] = examenesSolicitados
                consultas_ele["unidad"] = unidad_ele
            else:
                consultas_ele["unidadSolicitada"] = False
                consultas_ele["unidad"] = {}

            # adiciona los medicamentos -------------------------------------------------------------------------------
            medicamentosSolicitados = False
            farmaciaMedicamento_ele = {}
            medicamentos = []
            for medRecetadoTemp in MedicamentoRecetado.objects.filter(consulta=consulta_temp.id):
                if medRecetadoTemp.farmacia is not None:
                    medicamentosSolicitados = True
                medicamentos_ele = {}
                medicamentos_ele["id"] = orden_temp.id
                medicamentos_ele["id_medicamento"] = medRecetadoTemp.medicamento.id
                medicamentos_ele["nombre_generico"] = medRecetadoTemp.medicamento.nombre_generico
                medicamentos_ele["nombre_comercial"] = medRecetadoTemp.medicamento.nombre_comercial
                medicamentos_ele["tipo_especifico"] = medRecetadoTemp.medicamento.tipo_especifico
                medicamentos_ele["indicaciones"] = medRecetadoTemp.indicaciones
                medicamentos.append(medicamentos_ele)

            if medicamentosSolicitados:
                id_farmacia = MedicamentoRecetado.objects.filter(consulta=consulta_temp.id)[0].farmacia.id
                precio_total = MedicamentoRecetado.objects.filter(consulta=consulta_temp.id)[0].precio_total
                farmaciaTemp = Farmacia.objects.get(pk=id_farmacia)
                farmaciaMedicamento_ele["id"] = farmaciaTemp.id
                farmaciaMedicamento_ele["nombre_comercial"] = farmaciaTemp.nombre_comercial
                farmaciaMedicamento_ele["direccion"] = farmaciaTemp.direccion
                farmaciaMedicamento_ele["referencia_direccion"] = farmaciaTemp.referencia_direccion
                farmaciaMedicamento_ele["tipo"] = "farmacia"
                farmaciaMedicamento_ele["medicamento_solicitado"] = medicamentosSolicitados

                provincia = ""
                if farmaciaTemp.provincia is not None:
                    provincia = farmaciaTemp.provincia.provincia
                farmaciaMedicamento_ele["provincia"] = provincia

                canton = ""
                if farmaciaTemp.canton is not None:
                    canton = farmaciaTemp.canton.canton
                farmaciaMedicamento_ele["canton"] = canton

                parroquia = ""
                if farmaciaTemp.parroquia is not None:
                    parroquia = farmaciaTemp.parroquia.parroquia
                farmaciaMedicamento_ele["parroquia"] = parroquia

                farmaciaMedicamento_ele["telefono"] = farmaciaTemp.telefono
                farmaciaMedicamento_ele["lat"] = farmaciaTemp.lat
                farmaciaMedicamento_ele["lon"] = farmaciaTemp.lon
                farmaciaMedicamento_ele["precio_total"] = precio_total

            consultas_ele["medicamentosSolicitados"] = medicamentosSolicitados
            consultas_ele["farmacia"] = farmaciaMedicamento_ele
            consultas_ele["medicamentos"] = medicamentos
            consultas.append(consultas_ele)
        return JsonResponse(consultas, safe=False, status=status.HTTP_201_CREATED)
    else:
        return JsonResponse({'Method not Allowed. Only POST.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)