#from curses.ascii import CAN
import os

from .endpoints.helpers import unir

from django.db import models
from django.contrib.auth.models import User
import datetime

LABORATORIO = ('LABORATORIO', 'LABORATORIO')
IMAGEN = ('IMAGEN', 'IMAGEN')
PROCEDIMIENTO = ('PROCEDIMIENTO', 'PROCEDIMIENTO')
CATEGORIA = [LABORATORIO, IMAGEN, PROCEDIMIENTO]

MASCULINO = ('MASCULINO', 'MASCULINO')
FEMENINO = ('FEMENINO', 'FEMENINO')
GENERO = [MASCULINO, FEMENINO]

ORAL = ('ORAL', 'ORAL')
RECTAL = ('RECTAL', 'RECTAL')
SUBLINGUAL = ('SUBLINGUAL', 'SUBLINGUAL')
INTRAVENOSO = ('INTRAVENOSO', 'INTRAVENOSO')
INTRAMUSCULAR = ('INTRAMUSCULAR', 'INTRAMUSCULAR')
SUBCUTANEA = ('SUBCUTANEA', 'SUBCUTANEA')
INHALACION = ('INHALACION', 'INHALACION')
INTRANASAL = ('INTRANASAL', 'INTRANASAL')
TOPICO = ('TOPICO', 'TOPICO')
TRANSDERMICA = ('TRANSDERMICA', 'TRANSDERMICA')
VIA = [ORAL, ORAL, SUBLINGUAL, INTRAVENOSO, INTRAMUSCULAR,
       SUBCUTANEA, INHALACION, INTRANASAL, TOPICO, TRANSDERMICA]

PRESUNTIVO = ('PRESUNTIVO', 'PRESUNTIVO')
DEFINITIVO = ('DEFINITIVO', 'DEFINITIVO')
DIAGNOSTICO = [PRESUNTIVO, DEFINITIVO]

GRUPO = ('GRUPO', 'GRUPO')
SUCURSAL = ('SUCURSAL', 'SUCURSAL')
TIPOUNIDADMEDICA = [GRUPO, SUCURSAL]

PERSONAL = ('PERSONAL', 'PERSONAL')
FAMILIAR = ('FAMILIAR', 'FAMILIAR')
TIPOANTECEDENTE = [PERSONAL, FAMILIAR]

VENDIDO = ('VENDIDO', 'VENDIDO')
INDICADO = ('INDICADO', 'INDICADO')
ESTADOMEDICAMENTO = [VENDIDO, INDICADO]

RESULTADOS = ('RESULTADOS', 'RESULTADOS')
INDICADO = ('INDICADO', 'INDICADO')
ESTADOEXAMEN = [RESULTADOS, INDICADO]

CONSULTA = ('CONSULTA', 'CONSULTA')
SELECCION_FARMACIA = ('SELECCION_FARMACIA', 'SELECCION_FARMACIA')
SELECCION_UM = ('SELECCION_UM', 'SELECCION_UM')
VENTA_MEDICAMENTO = ('VENTA_MEDICAMENTO', 'VENTA_MEDICAMENTO')
RESULTADOS = ('RESULTADOS', 'RESULTADOS')
TIPO_ACTIVIDAD = [CONSULTA, SELECCION_FARMACIA,
                  SELECCION_UM, VENTA_MEDICAMENTO, RESULTADOS]

GRUPO = ('GRUPO', 'GRUPO')
SUCURSAL = ('SUCURSAL', ' SUCURSAL')
FARMACIA = ('FARMACIA', 'FARMACIA')
TIPO_ENTIDAD = [GRUPO, SUCURSAL, FARMACIA]

AGENDADO = ('AGENDADO', 'AGENDADO')
REAGENDADO = ('REAGENDADO', 'REAGENDADO')
REALIZADO = ('REALIZADO', 'REALIZADO')
CANCELADO = ('CANCELADO', 'CANCELADO')
ESTADO_EVENTO = [AGENDADO, REALIZADO, CANCELADO]

LUNES = ('LUNES', 'LUNES')
MARTES = ('MARTES', 'MARTES')
MIERCOLES = ('MIERCOLES', 'MIERCOLES')
JUEVES = ('JUEVES', 'JUEVES')
VIERNES = ('VIERNES', 'VIERNES')
SABADO = ('SABADO', 'SABADO')
DOMINGO = ('DOMINGO', 'DOMINGO')
DIASEMANA = [LUNES, MARTES, MIERCOLES, JUEVES, VIERNES, SABADO, DOMINGO]

LIQUIDADA = ('LIQUIDADA', 'LIQUIDADA')
PENDIENTE = ('PENDIENTE', 'PENDIENTE')
CANCELADA = ('CANCELADA', 'CANCELADA')
FUERA_DE_TERMINO = ('FUERA_DE_TERMINO', 'FUERA_DE_TERMINO')
ESTADO_FACTURA = [PENDIENTE, LIQUIDADA, FUERA_DE_TERMINO, CANCELADA]


class TipoExamen(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True, blank=False)
    tipo_examen = models.CharField(max_length=50, blank=True, null=True)
    categoria = models.CharField(max_length=20, default='', choices=CATEGORIA)

    class Meta:
        verbose_name = "Tipo de Examen"
        verbose_name_plural = "Tipos de Exámenes"
        db_table = 'tipo_examen'

    def __str__(self) -> str:
        return self.tipo_examen


class Examen(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True, blank=False)
    codigo = models.CharField(max_length=10, blank=True, null=True)
    examen = models.CharField(max_length=150, blank=True, null=True)
    tipo_examen = models.ForeignKey(TipoExamen, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Exámenes"
        db_table = 'examen'

    def __str__(self) -> str:
        return unir(" ", self.codigo, self.examen)


class Especialidad(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True, blank=False)
    especialidad = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'especialidad'
        verbose_name_plural = "Especialidades"

    def __str__(self) -> str:
        return self.especialidad


class CIE(models.Model):
    codigo = models.CharField(max_length=10, blank=True, null=True)
    cie = models.CharField(max_length=350, blank=True, null=True)

    class Meta:
        db_table = 'cie'
        verbose_name_plural = "CIE"

    def __str__(self) -> str:
        return unir(" ", self.codigo, self.cie)


class Provincia(models.Model):
    provincia = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        db_table = 'provincia'

    def __str__(self) -> str:
        return self.provincia


class Canton(models.Model):
    canton = models.CharField(max_length=40, blank=True, null=True)
    provincia = models.ForeignKey(Provincia, models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'canton'
        verbose_name_plural = "Cantones"

    def __str__(self) -> str:
        return unir(" ", self.canton, self.provincia.__str__())


class Parroquia(models.Model):
    parroquia = models.CharField(max_length=60, blank=True, null=True)
    canton = models.ForeignKey(Canton, models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'parroquia'

    def __str__(self) -> str:
        return unir(" ", self.parroquia, self.canton.canton)


def user_directory_path_sene(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'sene/user_{0}/{1}'.format(instance.user.id, filename)


def user_directory_path_acess(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'acess/user_{0}/{1}'.format(instance.user.id, filename)


def user_directory_path_foto_medico(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'medico/user_{0}/{1}'.format(instance.user.id, filename)


class Medico(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=30, blank=True, null=True)
    apellidos = models.CharField(max_length=30, blank=True, null=True)
    cedula = models.CharField(max_length=15, blank=True, null=True)
    codigo = models.CharField(max_length=30, blank=True, null=True)
    genero = models.CharField(max_length=10, default='', choices=GENERO)
    precio = models.FloatField(blank=True, null=True)
    duracion = models.IntegerField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    telefono_whatsapp = models.CharField(max_length=15, blank=True, null=True)
    telefono_cita1 = models.CharField(max_length=15, blank=True, null=True)
    telefono_cita2 = models.CharField(max_length=15, blank=True, null=True)
    cod_telefono_pais = models.CharField(max_length=5, blank=True, null=True)
    estudios = models.TextField(max_length=500, blank=True, null=True)
    experiencia = models.TextField(max_length=500, blank=True, null=True)
    seguro = models.TextField(max_length=500, blank=True, null=True)
    direccion_consultorio1 = models.CharField(
        max_length=150, blank=True, null=True)
    direccion_consultorio2 = models.CharField(
        max_length=150, blank=True, null=True)
    referencia_consultorio1 = models.CharField(
        max_length=150, blank=True, null=True)
    referencia_consultorio2 = models.CharField(
        max_length=150, blank=True, null=True)
    provincia1 = models.ForeignKey(
        Provincia, on_delete=models.CASCADE, blank=True, null=True, related_name="provincia1")
    provincia2 = models.ForeignKey(
        Provincia, on_delete=models.CASCADE, blank=True, null=True, related_name="provincia2")
    canton1 = models.ForeignKey(
        Canton, on_delete=models.CASCADE, blank=True, null=True, related_name="canton1")
    canton2 = models.ForeignKey(
        Canton, on_delete=models.CASCADE, blank=True, null=True, related_name="pcanton2")
    parroquia1 = models.ForeignKey(
        Parroquia, on_delete=models.CASCADE, blank=True, null=True, related_name="parroquia1")
    parroquia2 = models.ForeignKey(
        Parroquia, on_delete=models.CASCADE, blank=True, null=True, related_name="parroquia2")
    especialidad1 = models.ForeignKey(
        Especialidad, on_delete=models.CASCADE, blank=True, null=True, related_name="especialidad1")
    especialidad2 = models.ForeignKey(
        Especialidad, on_delete=models.CASCADE, blank=True, null=True,  related_name="especialidad2")
    subespecialidad1 = models.CharField(max_length=50, blank=True, null=True)
    subespecialidad2 = models.CharField(max_length=50, blank=True, null=True)
    lat1 = models.CharField(max_length=10, blank=True, null=True)
    lat2 = models.CharField(max_length=10, blank=True, null=True)
    lon1 = models.CharField(max_length=10, blank=True, null=True)
    lon2 = models.CharField(max_length=10, blank=True, null=True)
    email = models.CharField(max_length=30, blank=True, null=True)
    activado = models.BooleanField(blank=True, null=True)
    regSene = models.FileField(upload_to=user_directory_path_sene, null=True)
    regAcess = models.FileField(upload_to=user_directory_path_acess, null=True)
    foto = models.FileField(
        upload_to=user_directory_path_foto_medico, null=True)

    class Meta:
        db_table = 'medico'
        verbose_name_plural = "Médicos"

    def __str__(self) -> str:
        return unir(" ", self.nombre, self.apellidos)

    def dirnameSene(self):
        return os.path.dirname(self.regSene.name)

    def dirnameAcess(self):
        return os.path.dirname(self.regAcess.name)

    def dirnameFoto(self):
        return os.path.dirname(self.foto.name)


def user_directory_path_ruc(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'ruc/user_{0}/{1}'.format(instance.user.id, filename)


def user_directory_path_arcsa(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'arcsa/user_{0}/{1}'.format(instance.user.id, filename)


class UnidadMedica(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    ruc = models.CharField(max_length=30, blank=True, null=True)
    razon_social = models.CharField(max_length=100, blank=True, null=True)
    nombre_comercial = models.CharField(max_length=100, blank=True, null=True)
    lat = models.CharField(max_length=10, blank=True, null=True)
    lon = models.CharField(max_length=10, blank=True, null=True)
    slogan = models.CharField(max_length=50, blank=True, null=True)
    quienes_somos = models.CharField(max_length=250, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    referencia_direccion = models.CharField(
        max_length=150, blank=True, null=True)
    compensacion = models.IntegerField(blank=True, null=True)
    provincia = models.ForeignKey(
        Provincia, on_delete=models.CASCADE, blank=True, null=True, related_name="provincia_um")
    canton = models.ForeignKey(
        Canton, on_delete=models.CASCADE, blank=True, null=True, related_name="canton_um")
    parroquia = models.ForeignKey(
        Parroquia, on_delete=models.CASCADE, blank=True, null=True, related_name="parroquia_um")
    telefono = models.CharField(max_length=30, blank=True, null=True)
    telefono_whatsapp = models.CharField(max_length=15, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    pag_web = models.CharField(max_length=100, blank=True, null=True)
    horario_atencion = models.CharField(max_length=100, blank=True, null=True)
    activado = models.BooleanField(blank=True, null=True)
    regRUC = models.FileField(upload_to=user_directory_path_ruc, null=True)
    regArcsa = models.FileField(upload_to=user_directory_path_arcsa, null=True)

    class Meta:
        db_table = 'unidad_medica'
        verbose_name_plural = "Unidades Médicas"

    def __str__(self) -> str:
        return self.nombre

    def dirnameRUC(self):
        return os.path.dirname(self.regRUC.name)

    def dirnameArcsa(self):
        return os.path.dirname(self.regArcsa.name)


class Sucursal(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    lat = models.CharField(max_length=10, blank=True, null=True)
    lon = models.CharField(max_length=10, blank=True, null=True)
    slogan = models.CharField(max_length=50, blank=True, null=True)
    quienes_somos = models.CharField(max_length=250, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    compensacion = models.IntegerField(blank=True, null=True)
    referencia_direccion = models.CharField(
        max_length=150, blank=True, null=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE,
                                  blank=True, null=True, related_name="provincia_sucursal")
    canton = models.ForeignKey(Canton, on_delete=models.CASCADE,
                               blank=True, null=True, related_name="canton_sucursal")
    parroquia = models.ForeignKey(Parroquia, on_delete=models.CASCADE,
                                  blank=True, null=True, related_name="parroquia_sucursal")
    telefono = models.CharField(max_length=30, blank=True, null=True)
    telefono_whatsapp = models.CharField(max_length=15, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    pag_web = models.CharField(max_length=100, blank=True, null=True)
    horario_atencion = models.CharField(max_length=100, blank=True, null=True)
    activado = models.BooleanField(blank=True, null=True)
    unidadMedica = models.ForeignKey(
        UnidadMedica, models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'sucursal'
        verbose_name_plural = "Sucursales"

    def __str__(self) -> str:
        return self.nombre


def user_directory_path_foto_paciente(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'paciente/user_{0}/{1}'.format(instance.user.id, filename)


class Paciente(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=30, blank=True, null=True)
    apellidos = models.CharField(max_length=30, blank=True, null=True)
    cedula = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=30, blank=True, null=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE,
                                  blank=True, null=True, related_name="provincia_paciente")
    canton = models.ForeignKey(Canton, on_delete=models.CASCADE,
                               blank=True, null=True, related_name="canton_paciente")
    parroquia = models.ForeignKey(Parroquia, on_delete=models.CASCADE,
                                  blank=True, null=True, related_name="parroquia_paciente")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_nac = models.DateField(null=True)
    genero = models.CharField(max_length=10, default='', choices=GENERO)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    historia_clinica = models.CharField(max_length=10, blank=True, null=True)
    foto = models.FileField(
        upload_to=user_directory_path_foto_paciente, null=True)
    representante = models.ForeignKey(
        'Paciente', models.DO_NOTHING, blank=True, null=True, db_column='id_representante')

    def dirnameFoto(self):
        return os.path.dirname(self.foto.name)

    class Meta:
        db_table = 'paciente'

    def __str__(self) -> str:
        return unir(" ", self.nombre, self.apellidos)


class SucursalExamen(models.Model):
    sucursal = models.ForeignKey(
        Sucursal, on_delete=models.CASCADE, blank=True, null=True)
    examen = models.ForeignKey(
        Examen, on_delete=models.CASCADE, blank=True, null=True)
    precio = models.FloatField(blank=True, null=True)
    preparacion = models.CharField(max_length=250, blank=True, null=True)
    entrega = models.CharField(max_length=100, blank=True, null=True)
    referencia = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        db_table = 'sucursal_examen'
        verbose_name_plural = "Exámenes - Sucursales"

    def __str__(self) -> str:
        return unir(" ", self.codigo, self.examen)


class GrupoExamen(models.Model):
    grupo = models.ForeignKey(
        UnidadMedica, on_delete=models.CASCADE, blank=True, null=True)
    examen = models.ForeignKey(
        Examen, on_delete=models.CASCADE, blank=True, null=True)
    precio = models.FloatField(blank=True, null=True)
    preparacion = models.CharField(max_length=250, blank=True, null=True)
    entrega = models.CharField(max_length=100, blank=True, null=True)
    referencia = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        db_table = 'grupo_examen'
        verbose_name_plural = "Exámenes - Grupos"

    def __str__(self) -> str:
        return unir(" ", self.grupo.nombre, self.examen.nombre)


class Consulta(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True, blank=False)
    medico = models.ForeignKey(
        Medico, models.DO_NOTHING, db_column='id_medico')
    paciente = models.ForeignKey(
        Paciente, models.DO_NOTHING, db_column='id_paciente')
    diagnostico = models.ForeignKey(
        CIE, models.DO_NOTHING, db_column='id_diagnostico')
    tipo_diagnostico = models.CharField(
        max_length=50, default='', choices=DIAGNOSTICO)
    fecha = models.DateField("FechaConsulta", default=datetime.date.today)
    motivo_consulta = models.CharField(max_length=500, blank=True, null=True)
    historia_enfermedad = models.CharField(
        max_length=500, blank=True, null=True)
    examenClinico = models.CharField(max_length=500, blank=True, null=True)
    estado = models.CharField(
        max_length=15, default='INDICADO', choices=ESTADOEXAMEN)

    class Meta:
        db_table = 'consulta'
        verbose_name_plural = "Consultas"

    def __str__(self) -> str:
        return unir("-", self.medico, self.paciente, self.diagnostico)


class Orden(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True, blank=False)
    consulta = models.ForeignKey(
        Consulta, models.DO_NOTHING, db_column='id_consulta')
    examen = models.ForeignKey(
        Examen, models.DO_NOTHING, db_column='id_examen')
    tipo = models.CharField(max_length=50, default='',
                            choices=TIPOUNIDADMEDICA)
    sucursal = models.ForeignKey(
        Sucursal, on_delete=models.CASCADE, blank=True, null=True)
    grupo = models.ForeignKey(
        UnidadMedica, on_delete=models.CASCADE, blank=True, null=True)
    precio_unitario = models.IntegerField(blank=True, null=True)
    precio_total = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'orden'
        verbose_name_plural = "Órdenes"

    def __str__(self) -> str:
        return unir(" ", self.consulta, self.examen)


class UnidadesRecomendadas(models.Model):
    tipo = models.CharField(max_length=50, default='',
                            choices=TIPOUNIDADMEDICA)
    sucursal = models.ForeignKey(
        Sucursal, on_delete=models.CASCADE, blank=True, null=True)
    grupo = models.ForeignKey(
        UnidadMedica, on_delete=models.CASCADE, blank=True, null=True)
    consulta = models.ForeignKey(
        Consulta, models.DO_NOTHING, db_column='id_consulta', blank=True, null=True)

    class Meta:
        db_table = 'unidades_recomendadas'
        verbose_name_plural = "Unidades Recomendadas"

    def __str__(self) -> str:
        return unir(" ", self.tipo, self.sucursal, self.grupo)


class Farmacia(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    ruc = models.CharField(max_length=30, blank=True, null=True)
    razon_social = models.CharField(max_length=100, blank=True, null=True)
    nombre_comercial = models.CharField(max_length=100, blank=True, null=True)
    lat = models.CharField(max_length=10, blank=True, null=True)
    lon = models.CharField(max_length=10, blank=True, null=True)
    slogan = models.CharField(max_length=50, blank=True, null=True)
    quienes_somos = models.CharField(max_length=250, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    referencia_direccion = models.CharField(
        max_length=150, blank=True, null=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE,
                                  blank=True, null=True, related_name="provincia_farmacia")
    canton = models.ForeignKey(Canton, on_delete=models.CASCADE,
                               blank=True, null=True, related_name="canton_farmacia")
    parroquia = models.ForeignKey(Parroquia, on_delete=models.CASCADE,
                                  blank=True, null=True, related_name="parroquia_farmacia")
    telefono = models.CharField(max_length=30, blank=True, null=True)
    telefono_whatsapp = models.CharField(max_length=15, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    pag_web = models.CharField(max_length=100, blank=True, null=True)
    horario_atencion = models.CharField(max_length=100, blank=True, null=True)
    activado = models.BooleanField(blank=True, null=True)
    regRUC = models.FileField(upload_to=user_directory_path_ruc, null=True)
    regArcsa = models.FileField(upload_to=user_directory_path_arcsa, null=True)
    compensacion = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'farmacia'
        verbose_name_plural = "Farmacias"

    def __str__(self) -> str:
        return unir(" ", self.nombre, self.user)

    def dirnameRUC(self):
        return os.path.dirname(self.regRUC.name)

    def dirnameArcsa(self):
        return os.path.dirname(self.regArcsa.name)


class Factura(models.Model):
    puntos = models.FloatField(blank=True, null=True)
    estado = models.CharField(
        max_length=50, default='', choices=ESTADO_FACTURA)
    fecha_creacion = models.DateField(
        db_column="fecha_creacion", auto_now_add=True, blank=True, null=True)
    fecha_vencimiento = models.DateField(
        db_column="fecha_vencimiento", blank=True, null=True)

    class Meta:
        db_table = 'factura'

    def __str__(self) -> str:
        return unir("-", self.fecha_creacion, self.estado, self.puntos)


class OrdenFactura(models.Model):
    orden = models.ForeignKey(Orden, models.DO_NOTHING, db_column='id_orden')
    tipo = models.CharField(max_length=50, default='', choices=TIPO_ENTIDAD)
    sucursal = models.ForeignKey(
        Sucursal, on_delete=models.CASCADE, blank=True, null=True)
    grupo = models.ForeignKey(
        UnidadMedica, on_delete=models.CASCADE, blank=True, null=True)
    farmacia = models.ForeignKey(
        Farmacia, on_delete=models.CASCADE, blank=True, null=True)
    puntos = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'orden_factura'
        verbose_name_plural = "Órdenes - Facturas"

    def __str__(self) -> str:
        return unir(" ", self.orden, self.tipo, self.grupo)


class Comision(models.Model):
    factura = models.ForeignKey(
        Factura, models.DO_NOTHING, db_column='id_factura')
    puntos = models.FloatField(blank=True, null=True)
    fecha = models.DateField(
        db_column="fecha_creacion", auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'comision'
        verbose_name_plural = "Comisiones"

    def __str__(self) -> str:
        return unir(" ", self.fecha, self.factura)


class Tarifa(models.Model):
    tipo_entidad = models.CharField(
        max_length=50, default='', choices=TIPO_ENTIDAD)
    porcentaje = models.FloatField(blank=True, null=True)
    profesional = models.FloatField(blank=True, null=True)
    hallmed = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'tarifa'

    def __str__(self) -> str:
        return unir(" ", self.tipo_entidad, self.porcentaje)


class Medicamento(models.Model):
    nombre_generico = models.CharField(max_length=50, blank=True, null=True)
    nombre_comercial = models.CharField(max_length=50, blank=True, null=True)
    tipo_especifico = models.CharField(max_length=50, blank=True, null=True)
    tipo_generico = models.CharField(max_length=50, blank=True, null=True)
    via_aplicacion = models.CharField(max_length=50, default='', choices=VIA)

    class Meta:
        db_table = 'medicamento'

    def __str__(self) -> str:
        return f"{self.nombre_generico} ( {self.nombre_comercial} ) [ {self.tipo_especifico} ]"


class MedicamentoRecetado(models.Model):
    consulta = models.ForeignKey(
        Consulta, models.DO_NOTHING, db_column='id_consulta')
    medicamento = models.ForeignKey(
        Medicamento, models.DO_NOTHING, db_column='id_medicamento')
    indicaciones = models.CharField(max_length=150, blank=True, null=True)
    farmacia = models.ForeignKey(
        Farmacia, models.DO_NOTHING, blank=True, null=True, db_column='id_farmacia')
    precio_total = models.FloatField(blank=True, null=True)
    estado = models.CharField(
        max_length=15, default='INDICADO', choices=ESTADOMEDICAMENTO)

    class Meta:
        db_table = 'medicamento_recetado'
        verbose_name_plural = "Medicamentos Recetados"

    def __str__(self) -> str:
        return f"{self.medicamento} {self.precio_total} {self.estado}"


class MedicamentoFarmacia(models.Model):
    medicamento = models.ForeignKey(
        Medicamento, models.DO_NOTHING, db_column='id_medicamento')
    farmacia = models.ForeignKey(
        Farmacia, models.DO_NOTHING, db_column='id_farmacia')
    precio = models.FloatField(blank=True, null=True)
    descripcion = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        db_table = 'medicamento_farmacia'
        verbose_name_plural = "Medicamentos - Farmacias"

    def __str__(self) -> str:
        return unir(" ", self.medicamento, self.farmacia)


class Antecedentes(models.Model):
    consulta = models.ForeignKey(
        Consulta, models.DO_NOTHING, db_column='id_consulta')
    diagnostico = models.ForeignKey(
        'CIE', models.DO_NOTHING, db_column='id_diagnostico')
    tipo = models.CharField(max_length=50, default='', choices=TIPOANTECEDENTE)

    class Meta:
        db_table = 'antecedentes'
        verbose_name_plural = "Antecedentes"

    def __str__(self) -> str:
        return unir(" ", self.consulta, self.diagnostico, self.tipo)


class AntecedentesObstetricos(models.Model):
    consulta = models.ForeignKey(
        Consulta, models.DO_NOTHING, db_column='id_consulta')
    numGestas = models.IntegerField(blank=True, null=True)
    numPartos = models.IntegerField(blank=True, null=True)
    numAbortos = models.IntegerField(blank=True, null=True)
    descPartos = models.CharField(max_length=250, blank=True, null=True)
    descAbortos = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        db_table = 'antecedentes_obstetricos'
        verbose_name_plural = "Antecedentes Obstétricos"

    def __str__(self) -> str:
        return self.consulta


class AntecedentesPediatricos(models.Model):
    consulta = models.ForeignKey(
        Consulta, models.DO_NOTHING, db_column='id_consulta')
    antecedentePrenatal = models.CharField(
        max_length=500, blank=True, null=True)
    antecedenteNatal = models.CharField(max_length=500, blank=True, null=True)
    antecedentePostnatal = models.CharField(
        max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'antecedentes_pediatricos'
        verbose_name_plural = "Antecedentes Pediátricos"

    def __str__(self) -> str:
        return unir(" ", self.consulta, self.diagnostico, self.tipo)


def user_directory_path_resultados(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'resultados/consulta_{0}/{1}'.format(instance.consulta.id, filename)


class Resultados(models.Model):
    resultadosFile = models.FileField(
        upload_to=user_directory_path_resultados, null=True)
    consulta = models.ForeignKey(
        Consulta, models.DO_NOTHING, blank=True, null=True, db_column='id_consulta')
    fecha = models.DateField(db_column="fecha_resultados",
                             auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'resultados'
        verbose_name_plural = "Resultados"

    def __str__(self) -> str:
        return unir(" ", self.consulta, self.fecha)

    def dirnameResultados(self):
        return os.path.dirname(self.resultadosFile.name)


class RatingMedico(models.Model):
    paciente = models.ForeignKey(
        Paciente, models.DO_NOTHING, blank=True, null=True, db_column='id_paciente')
    medico = models.ForeignKey(
        Medico, models.DO_NOTHING, blank=True, null=True, db_column='id_medico')
    consulta = models.ForeignKey(
        Consulta, models.DO_NOTHING, blank=True, null=True, db_column='id_consulta')
    rating = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        db_table = 'rating_medico'
        verbose_name_plural = "Rating - Médico"

    def __str__(self) -> str:
        return unir("-", self.medico, self.paciente, self.consulta)


class RatingMedioDiagnostico(models.Model):
    paciente = models.ForeignKey(
        Paciente, models.DO_NOTHING, blank=True, null=True, db_column='id_paciente')
    grupo = models.ForeignKey(
        UnidadMedica, models.DO_NOTHING, blank=True, null=True, db_column='id_grupo')
    sucursal = models.ForeignKey(
        Sucursal, models.DO_NOTHING, blank=True, null=True, db_column='id_sucursal')
    tipo = models.CharField(max_length=50, default='',
                            choices=TIPOUNIDADMEDICA)
    consulta = models.ForeignKey(
        Consulta, models.DO_NOTHING, blank=True, null=True, db_column='id_consulta')
    rating = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        db_table = 'rating_medio_diagnostico'
        verbose_name_plural = "Rating - Medio Diagnóstico"

    def __str__(self) -> str:
        return unir(" ", self.consulta, self.diagnostico, self.tipo)


class Actividad(models.Model):
    paciente = models.ForeignKey(
        Paciente, models.DO_NOTHING, blank=True, null=True, db_column='id_paciente')
    tipoActividad = models.CharField(
        max_length=50, default='', choices=TIPO_ACTIVIDAD)
    consulta = models.ForeignKey(
        Consulta, blank=True, null=True, on_delete=models.CASCADE, db_column='id_consulta')
    entidad = models.IntegerField(blank=True, null=True, default=0)
    tipoEntidad = models.CharField(
        max_length=50, blank=True, null=True, default='', choices=TIPO_ENTIDAD)
    nombreEntidad = models.CharField(max_length=100, blank=True, null=True)
    fechaHora = models.DateTimeField(
        db_column="fecha_actividad", auto_now_add=True, blank=True)

    class Meta:
        db_table = 'actividad'
        verbose_name_plural = "Actividades"

    def __str__(self) -> str:
        return unir(" ", self.paciente, self.tipoActividad, self.consulta)


class Seguro(models.Model):
    seguro = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'seguro'
        verbose_name_plural = "Seguros"

    def __str__(self) -> str:
        return self.seguro


class MedicoSeguro(models.Model):
    medico = models.ForeignKey(
        Medico, models.CASCADE, blank=True, null=True, db_column='id_profesional')
    seguro = models.ForeignKey(
        Seguro, models.CASCADE, blank=True, null=True, db_column='id_seguro')

    class Meta:
        db_table = 'medico_seguro'
        verbose_name_plural = "Seguro Médico"

    def __str__(self) -> str:
        return unir("-", self.medico, self.seguro)


class EventosCalendario(models.Model):
    titulo = models.CharField(max_length=500, blank=True, null=True)
    inicio = models.DateTimeField("inicio", default=datetime.date.today)
    fin = models.DateTimeField("fin", default=datetime.date.today)
    paciente = models.ForeignKey(
        Paciente, models.DO_NOTHING, blank=True, null=True, db_column='id_paciente')
    consulta = models.ForeignKey(
        Consulta, models.DO_NOTHING, blank=True, null=True, db_column='id_consulta')
    estado = models.CharField(
        max_length=50, blank=True, null=True, default='', choices=ESTADO_EVENTO)
    motivo = models.CharField(max_length=1000, blank=True, null=True)
    medico = models.ForeignKey(
        Medico, models.DO_NOTHING, blank=True, null=True, db_column='id_profesional')

    class Meta:
        db_table = 'evento_calendario'
        verbose_name_plural = "Eventos de Calendario"

    def __str__(self) -> str:
        return unir(" ", self.titulo, self.inicio, self.fin, self.paciente, self.consulta)


class IntervalosDisponibilidad(models.Model):
    dia_semana = models.CharField(
        max_length=10, blank=True, null=True, default='', choices=DIASEMANA)
    inicio = models.TimeField(blank=True, null=True)
    fin = models.TimeField(blank=True, null=True)
    duracion = models.IntegerField(null=True, default='')
    medico = models.ForeignKey(
        'Medico', models.DO_NOTHING, db_column='id_medico')
    activo = models.BooleanField(null=True, default='')

    class Meta:
        db_table = 'intervalos_disponibilidad'
        verbose_name_plural = "Intervalos de Disponibilidad"

    def __str__(self) -> str:
        return unir(" ", self.dia_semana, self.inicio, self.fin, self.medico)


class citasMedicas(models.Model):
    inicio = models.TimeField(blank=True, null=True)
    fin = models.TimeField(blank=True, null=True)
    duracion = models.IntegerField(null=True, default='')
    fecha_cita = models.DateTimeField(null=True, default='')
    medico = models.ForeignKey(
        'Medico', models.DO_NOTHING, db_column='id_medico')
    paciente = models.ForeignKey(
        Paciente, models.DO_NOTHING, blank=True, null=True, db_column='id_paciente')
    consulta = models.ForeignKey(
        Consulta, models.DO_NOTHING, blank=True, null=True, db_column='id_consulta')
    intervalo_disponibilidad = models.ForeignKey(
        IntervalosDisponibilidad, models.DO_NOTHING, blank=True, null=True, db_column='id_intervalo')
    motivo = models.CharField(max_length=1000, blank=True, null=True)
    estado = models.CharField(
        max_length=50, blank=True, null=True, default='', choices=ESTADO_EVENTO)

    class Meta:
        db_table = 'citas_medicas'
        verbose_name_plural = "Citas Médicas"

    def __str__(self) -> str:
        return unir(" ", self.fecha_cita, self.inicio, self.fin, self.medico, self.paciente)
