from django.urls import path

from .endpoints.calendario import add_evento, get_eventos_medico, get_todos_eventos, proximo_evento_disponible, \
    disponibilidad_dia, get_disponibilidad_doctor, disponibilidad_doctor_dia, primera_disponibilidad, agendar_cita, \
    cancelar_cita, agenda_medico, reagendar_cita, cancelar_cita_medico
from .endpoints.contablidad import get_sucursales_medico, get_sucursal_medico, get_grupos_medico, get_grupo_medico, \
    get_medicos_grupo, get_medico_grupo, get_medicos_sucursal, get_medico_sucursal, get_sucursal_grupo
from .endpoints.tipoexamen import list_tipoexamen, add_tipoexamen, update_tipoexamen, delete_tipoexamen
from .endpoints.examen import list_examen, add_examen, update_examen, delete_examen, list_unidades_todos_examen, \
    recomendar_unidades_todos_examen
from .endpoints.especialidad import list_especialidad, add_especialidad, update_especialidad, delete_especialidad
from .endpoints.medico import register_medico, valida_medico, list_medico, list_medico_no_activos, \
    delete_medico, delete_medico_no_validado, list_profile_medico, update_generales_medico, register_medico_admin, \
    medico_nombre, buscar_medico, update_medico_disponibilidad, update_seguro_medico, update_curriculo_medico, \
    update_especialidad_medico, update_consultorio_medico, get_perfil_medico
from .endpoints.unidadmedica import register_unidad_medica, valida_unidad_medica, list_unidad_medica, \
    list_unidad_medica_no_activas, delete_UM_no_validada, delete_unidad_medica, list_profile_um, update_profile_um\
    , register_unidad_medica_admin
from .endpoints.prov_canton_parroquia import list_provincia, list_canton, list_parroquia
from .endpoints.paciente import register_paciente, update_profile_paciente, list_paciente, delete_paciente, \
    paciente_nombre, paciente_id, register_paciente_profesional, paciente_cedula
from .endpoints.cie import list_cie, add_cie, update_cie, delete_cie
from .endpoints.sucursal import add_sucursal, delete_sucursal, list_sucursal, update_sucursal, list_sucursal_user, \
    update_sucursal_full, list_sucursal_grupo, delete_sucursal_grupo
from .endpoints.sucursal_examen import list_examen_by_sucursal, update_examen_sucursal, list_examen_by_sucursal_nombre, \
    update_examen_sucursal_detalles
from .endpoints.grupo_examen import list_examen_by_grupo, list_examen_by_grupo_nombre, update_examen_grupo, \
    update_examen_grupo_detalles, listexamen_grupo
from .endpoints.consulta import list_consultas, add_consulta, list_medicamentos_consulta, update_consulta, delete_consulta, \
    consultas_by_pacientes
from .endpoints.orden import list_examen_consulta, unidad_solicitada, ordenes_sucursal, ordenes_grupo, \
    filtrar_ordenes_grupo, filtrar_ordenes_sucursal
from  .endpoints.farmacia import register_farmacia, list_farmacias_no_activas, valida_farmacia, list_farmacia, \
    delete_farmacia, delete_farmacia_no_validada, update_profile_farmacia, register_farmacia_admin
from .endpoints.medicamento import list_medicamento, add_medicamento, update_medicamento, delete_medicamento, \
    medicamento_filtro_generico, medicamento_filtro_comercial, medicamento_filtro_nombre, medicamento_generico_inicial, \
    medicamentos_recetados_farmacia, medicamentos_venta, filtra_medicamentos_recetados_farmacia
from .endpoints.medicamento_farmacia import update_medicamento_farmacia, list_medicamento_by_farmacia_nombre, \
    update_medicamento_farmacia_detalles, list_farmacias_con_medicamento, list_farmacias_todos_medicamentos, \
    medicamentos_solicitados_farmacia
from .endpoints.antecedentes import list_antecedentes_familiares, list_antecedentes_personales, list_antecedentes_obtetricos, \
    list_antecedentes_pediatricos
from .endpoints.resultados import add_resultados
from .endpoints.rating import add_rating_medico, add_rating_um
from .endpoints.actividades import list_actividades_consultas, list_actividades
from .endpoints.indicadores_medicos import ultimos_dias, creditos_medico, cierre_ciclo
from .endpoints.indicadores_farmacia import ultimos_dias_farmacia, medicamentos_frecuentes, cierre_ciclo_farmacia, facturacion_farmacia
from .endpoints.seguro import list_seguro
from .endpoints.indicadores_sucursal import ultimos_dias_sucursal, examenes_frecuentes, facturacion_medicos
from .endpoints.indicadores_grupo import ultimos_dias_grupo, examenes_frecuentes_grupo, facturacion_medicos_grupo
from .endpoints.indicadores_admin import *

from django.conf import settings
from django.conf.urls.static import static
from .views import nologin

urlpatterns = [
    path("api/v1/list_tipoexamen/", list_tipoexamen),
    path("api/v1/add_tipoexamen/", add_tipoexamen),
    path("api/v1/update_tipoexamen/", update_tipoexamen),
    path("api/v1/delete_tipoexamen/", delete_tipoexamen),

    path("api/v1/list_examen/", list_examen),
    path("api/v1/add_examen/", add_examen),
    path("api/v1/update_examen/", update_examen),
    path("api/v1/delete_examen/", delete_examen),

    path("api/v1/list_especialidad/", list_especialidad),
    path("api/v1/add_especialidad/", add_especialidad),
    path("api/v1/update_especialidad/", update_especialidad),
    path("api/v1/delete_especialidad/", delete_especialidad),

    path("api/v1/register_medico/", register_medico),
    path("api/v1/valida_medico/", valida_medico),
    path("api/v1/list_medico/", list_medico),
    path("api/v1/list_medico_no_activos/", list_medico_no_activos),
    path("api/v1/delete_medico_no_validado/", delete_medico_no_validado),
    path("api/v1/delete_medico/", delete_medico),
    path("api/v1/list_profile_medico/", list_profile_medico),
    path("api/v1/update_generales_medico/", update_generales_medico),
    path("api/v1/update_medico_disponibilidad/", update_medico_disponibilidad),
    path("api/v1/update_curriculo_medico/", update_curriculo_medico),
    path("api/v1/update_especialidad_medico/", update_especialidad_medico),
    path("api/v1/update_consultorio_medico/", update_consultorio_medico),
    path("api/v1/get_perfil_medico/", get_perfil_medico),

    path("api/v1/update_seguro_medico/", update_seguro_medico),
    path("api/v1/register_medico_admin/", register_medico_admin),
    path("api/v1/register_unidad_medica/", register_unidad_medica),
    path("api/v1/valida_unidad_medica/", valida_unidad_medica),
    path("api/v1/list_unidad_medica/", list_unidad_medica),
    path("api/v1/list_unidad_medica_no_activas/", list_unidad_medica_no_activas),
    path("api/v1/delete_UM_no_validada/", delete_UM_no_validada),
    path("api/v1/delete_unidad_medica/", delete_unidad_medica),
    path("api/v1/list_profile_um/", list_profile_um),
    path("api/v1/update_profile_um/", update_profile_um),
    path("api/v1/register_unidad_medica_admin/", register_unidad_medica_admin),

    path("api/v1/list_provincia/", list_provincia),
    path("api/v1/list_canton/", list_canton),
    path("api/v1/list_parroquia/", list_parroquia),

    path("api/v1/register_paciente/", register_paciente),
    path("api/v1/register_paciente_profesional/", register_paciente_profesional),
    path("api/v1/update_profile_paciente/", update_profile_paciente),
    path("api/v1/list_paciente/", list_paciente),
    path("api/v1/delete_paciente/", delete_paciente),
    path("api/v1/paciente_nombre/", paciente_nombre),
    path("api/v1/paciente_cedula/", paciente_cedula),

    path("api/v1/paciente_id/", paciente_id),
    path("api/v1/list_cie/", list_cie),
    path("api/v1/add_cie/", add_cie),
    path("api/v1/update_cie/", update_cie),
    path("api/v1/delete_cie/", delete_cie),

    path("api/v1/list_sucursal/", list_sucursal),
    path("api/v1/add_sucursal/", add_sucursal),
    path("api/v1/update_sucursal/", update_sucursal),
    path("api/v1/delete_sucursal/", delete_sucursal),
    path("api/v1/list_sucursal_user/", list_sucursal_user),
    path("api/v1/update_sucursal_full/", update_sucursal_full),
    path("api/v1/list_sucursal_grupo/", list_sucursal_grupo),
    path("api/v1/delete_sucursal_grupo/", delete_sucursal_grupo),

    path("api/v1/examenbysucursal/", list_examen_by_sucursal),
    path("api/v1/listexamensucursal_nombre/", list_examen_by_sucursal_nombre),
    path("api/v1/update_examen_sucursal/", update_examen_sucursal),
    path("api/v1/update_exasuc_detalles/", update_examen_sucursal_detalles),

    path("api/v1/examenbygrupo/", list_examen_by_grupo),
    path("api/v1/listexamengrupo_nombre/", list_examen_by_grupo_nombre),
    path("api/v1/listexamen_grupo/", listexamen_grupo),
    path("api/v1/update_examen_grupo/", update_examen_grupo),
    path("api/v1/update_exagrp_detalles/", update_examen_grupo_detalles),

    path("api/v1/list_consultas/", list_consultas),
    path("api/v1/add_consulta/", add_consulta),
    path("api/v1/list_examen_consulta/", list_examen_consulta),
    path("api/v1/list_medicamentos_consulta/", list_medicamentos_consulta),
    path("api/v1/update_consulta/", update_consulta),
    path("api/v1/delete_consulta/", delete_consulta),
    path("api/v1/consultas_by_pacientes/", consultas_by_pacientes),
    path("api/v1/unidad_solicitada/", unidad_solicitada),
    path("api/v1/recomendar_unidades_todos_examen/", recomendar_unidades_todos_examen),
    path("api/v1/list_antecedentes_personales/", list_antecedentes_personales),
    path("api/v1/list_antecedentes_familiares/", list_antecedentes_familiares),
    path("api/v1/list_antecedentes_obtetricos/", list_antecedentes_obtetricos),
    path("api/v1/list_antecedentes_pediatricos/", list_antecedentes_pediatricos),

    path("api/v1/register_farmacia/", register_farmacia),
    path("api/v1/list_farmacias_no_activas/", list_farmacias_no_activas),
    path("api/v1/valida_farmacia/", valida_farmacia),
    path("api/v1/list_farmacia/", list_farmacia),
    path("api/v1/delete_farmacia/", delete_farmacia),
    path("api/v1/delete_farmacia_no_validada/", delete_farmacia_no_validada),
    path("api/v1/update_profile_farmacia/", update_profile_farmacia),
    path("api/v1/register_farmacia_admin/", register_farmacia_admin),

    path("api/v1/list_medicamento/", list_medicamento),
    path("api/v1/add_medicamento/", add_medicamento),
    path("api/v1/update_medicamento/", update_medicamento),
    path("api/v1/delete_medicamento/", delete_medicamento),
    path("api/v1/medicamento_filtro_generico/", medicamento_filtro_generico),
    path("api/v1/medicamento_filtro_comercial/", medicamento_filtro_comercial),
    path("api/v1/medicamento_filtro_nombre/", medicamento_filtro_nombre),
    path("api/v1/medicamento_generico_inicial/", medicamento_generico_inicial),

    path("api/v1/update_medicamento_farmacia/", update_medicamento_farmacia),
    path("api/v1/list_medicamento_by_farmacia_nombre/", list_medicamento_by_farmacia_nombre),
    path("api/v1/update_medicamento_farmacia_detalles/", update_medicamento_farmacia_detalles),
    path("api/v1/list_farmacias_con_medicamento/", list_farmacias_con_medicamento),
    path("api/v1/list_farmacias_todos_medicamentos/", list_farmacias_todos_medicamentos),
    path("api/v1/list_unidades_todos_examen/", list_unidades_todos_examen),
    path("api/v1/medicamentos_solicitados_farmacia/", medicamentos_solicitados_farmacia),
    path("api/v1/add_rating_medico/", add_rating_medico),

    path("api/v1/medicamentos_recetados_farmacia/", medicamentos_recetados_farmacia),
    path("api/v1/medicamentos_venta/", medicamentos_venta),
    path("api/v1/medico_nombre/", medico_nombre),
    path("api/v1/filtra_medicamentos_recetados_farmacia/", filtra_medicamentos_recetados_farmacia),

    path("api/v1/ordenes_sucursal/", ordenes_sucursal),
    path("api/v1/add_resultados/", add_resultados),
    path("api/v1/filtrar_ordenes_sucursal/", filtrar_ordenes_sucursal),

    path("api/v1/ordenes_grupo/", ordenes_grupo),
    path("api/v1/filtrar_ordenes_grupo/", filtrar_ordenes_grupo),

    path("api/v1/buscar_medico/", buscar_medico),
    path("api/v1/add_rating_um/", add_rating_um),

    path("api/v1/list_actividades_consultas/", list_actividades_consultas),
    path("api/v1/list_actividades/", list_actividades),

    path("api/v1/ultimos_dias/", ultimos_dias),
    path("api/v1/creditos_medico/", creditos_medico),
    path("api/v1/cierre_ciclo/", cierre_ciclo),

    path("api/v1/ultimos_dias_farmacia/", ultimos_dias_farmacia),
    path("api/v1/medicamentos_frecuentes/", medicamentos_frecuentes),
    path("api/v1/cierre_ciclo_farmacia/", cierre_ciclo_farmacia),
    path("api/v1/facturacion_farmacia/", facturacion_farmacia),

    path("api/v1/list_seguro/", list_seguro),

    path("api/v1/ultimos_dias_sucursal/", ultimos_dias_sucursal),
    path("api/v1/examenes_frecuentes/", examenes_frecuentes),
    path("api/v1/facturacion_medicos/", facturacion_medicos),

    path("api/v1/ultimos_dias_grupo/", ultimos_dias_grupo),
    path("api/v1/examenes_frecuentes_grupo/", examenes_frecuentes_grupo),
    path("api/v1/facturacion_medicos_grupo/", facturacion_medicos_grupo),

    path("api/v1/calendario/add_evento", add_evento),
    path("api/v1/calendario/get_eventos_medico", get_eventos_medico),
    path("api/v1/calendario/get_todos_eventos", get_todos_eventos),
    path("api/v1/calendario/proximo_evento_disponible", proximo_evento_disponible),

    path("api/v1/calendario/disponibilidad_dia", disponibilidad_dia),
    path("api/v1/calendario/get_disponibilidad_doctor", get_disponibilidad_doctor),
    path("api/v1/calendario/disponibilidad_doctor_dia", disponibilidad_doctor_dia),
    path("api/v1/calendario/primera_disponibilidad", primera_disponibilidad),
    path("api/v1/calendario/agendar_cita", agendar_cita),
    path("api/v1/calendario/cancelar_cita", cancelar_cita),
    path("api/v1/calendario/agenda_medico", agenda_medico),
    path("api/v1/calendario/reagendar_cita", reagendar_cita),
    path("api/v1/calendario/cancelar_cita_medico", cancelar_cita_medico),

    path("api/v1/contabilidad/get_sucursales_medico", get_sucursales_medico),
    path("api/v1/contabilidad/get_sucursal_medico", get_sucursal_medico),
    path("api/v1/contabilidad/get_grupos_medico", get_grupos_medico),
    path("api/v1/contabilidad/get_grupo_medico", get_grupo_medico),
    path("api/v1/contabilidad/get_medicos_grupo", get_medicos_grupo),
    path("api/v1/contabilidad/get_medico_grupo", get_medico_grupo),
    path("api/v1/contabilidad/get_medicos_sucursal", get_medicos_sucursal),
    path("api/v1/contabilidad/get_medico_sucursal", get_medico_sucursal),
    path("api/v1/contabilidad/get_sucursal_grupo", get_sucursal_grupo),

    path("api/v1/admin/ultimos_dias/", ultimos_dias_admin),
    path("api/v1/admin/creditos/", creditos),
    path("api/v1/admin/creditos_farmacia/", creditos_farmacia),
    path("api/v1/admin/cierre_ciclo/", cierre_ciclo_admin),
    path("api/v1/admin/get_sucursal_grupo", get_sucursal_grupo_admin),
    path("api/v1/admin/tarifas/", get_tarifas),
    path("api/v1/nologin/", nologin),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)