from rest_framework import serializers

from .models import TipoExamen, Examen, Especialidad, Medico, UnidadMedica, Provincia, Canton, Parroquia, Paciente, \
    CIE, Sucursal, SucursalExamen, GrupoExamen, Consulta, Orden, Farmacia, Medicamento, MedicamentoFarmacia, \
    Antecedentes, Resultados, Seguro, EventosCalendario, citasMedicas, Tarifa


class TipoExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoExamen
        fields = '__all__'


class ExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Examen
        fields = '__all__'


class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = '__all__'


class MedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medico
        fields = '__all__'


class UnidadMedicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedica
        fields = '__all__'


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = '__all__'


class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = '__all__'


class CantonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Canton
        fields = '__all__'


class ParroquiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parroquia
        fields = '__all__'


class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'


class CIESerializer(serializers.ModelSerializer):
    class Meta:
        model = CIE
        fields = '__all__'


class SucursalExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SucursalExamen
        fields = '__all__'


class GrupoExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoExamen
        fields = '__all__'


class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = '__all__'


class OrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orden
        fields = '__all__'


class FarmaciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmacia
        fields = '__all__'


class MedicamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicamento
        fields = '__all__'


class MedicamentoFarmaciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicamentoFarmacia
        fields = '__all__'


class AntecedentesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Antecedentes
        fields = '__all__'


class ResultadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resultados
        fields = '__all__'


class SeguroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seguro
        fields = '__all__'


class EventosCalendarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventosCalendario
        fields = '__all__'


class citasMedicasSerializer(serializers.ModelSerializer):
    class Meta:
        model = citasMedicas
        fields = '__all__'


class TarifaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarifa
        fields = '__all__'
