from rest_framework import serializers
from apps.instEletricas.models import (
    Local, Ambientes, CargasTUG, CargasILUM, CargasTUE, 
    Circuitos, Demandas, Condutores, Eletrodutos, Protecao, EquilibrioFases
)
from apps.cliente.models import Cliente


class ClienteSimplesSerializer(serializers.ModelSerializer):
    """
    Exibe apenas os dados básicos do cliente.
    Não inclui campos que chamam o Local de volta.
    """
    class Meta:
        model = Cliente
        fields = ['id', 'nome', 'email', 'tel1', 'tel2']


class CargasTUGSerializer(serializers.ModelSerializer):
    tug_final = serializers.ReadOnlyField()
    calculo_pot_tug = serializers.ReadOnlyField()
    conv_pot_tug = serializers.ReadOnlyField()

    pot_tug = serializers.ReadOnlyField()

    class Meta:
        model = CargasTUG
        fields = '__all__'

class CargasILUMSerializer(serializers.ModelSerializer):
    calculo_ilum = serializers.ReadOnlyField()
    calculo_pot_ilum = serializers.ReadOnlyField()
    conv_pot_ilum = serializers.ReadOnlyField()

    class Meta:
        model = CargasILUM
        fields = '__all__'

class CargasTUESerializer(serializers.ModelSerializer):
    potencia = serializers.ReadOnlyField()
    conv_pot_tue = serializers.ReadOnlyField()
    pot_tue_w = serializers.ReadOnlyField()

    class Meta:
        model = CargasTUE
        fields = '__all__'

# -----------------------------------------------------------------------------
# 2. SERIALIZERS INTERMEDIÁRIOS (Contêm as cargas)
# -----------------------------------------------------------------------------

class AmbientesSerializer(serializers.ModelSerializer):
    # Aqui trazemos as cargas que pertencem a este ambiente
    # Os nomes (cargas_tug, etc) vêm do related_name no models.py
    cargas_tug = CargasTUGSerializer(many=True, read_only=True)
    cargas_ilum = CargasILUMSerializer(many=True, read_only=True)
    cargas_tue = CargasTUESerializer(many=True, read_only=True)

    tug_final = serializers.SerializerMethodField()
    ilum_final = serializers.SerializerMethodField()
    pot_tug = serializers.SerializerMethodField()
    pot_ilum = serializers.SerializerMethodField()
    pot_tue_w = serializers.SerializerMethodField()

    class Meta:
        
        model = Ambientes
        fields = [
            'id', 'local', 'comodo', 't_comodo', 'perimetro', 'area', 
            'tug', 'tue', 'iluminacao',
            'cargas_tug', 'cargas_ilum', 'cargas_tue', 'tug_final', 'ilum_final', 'pot_tug','pot_ilum','pot_tue_w',    # Adicionamos os campos aqui
        ]
    def get_tug_final(self, obj):
        carga = obj.cargas_tug.first()
        return carga.tug_final if carga else 0
    def get_pot_tug(self, obj):
        carga = obj.cargas_tug.first()
        if carga:
            return carga.pot_tug 
        return 0
    def get_ilum_final(self, obj):
        carga = obj.cargas_ilum.first()
        return carga.calculo_ilum if carga else 0
    def get_pot_ilum(self, obj):
        carga = obj.cargas_ilum.first()
        if carga:
            pot, _ = carga.calculo_pot_ilum
            return pot
        return 0
    def get_pot_tue_w(self, obj):
        cargas = obj.cargas_tue.all()
        total = sum(carga.pot_tue_w for carga in cargas if carga.pot_tue_w)
        return total

class CircuitosSerializer(serializers.ModelSerializer):
    # Mostra quais cargas estão ligadas neste circuito
    tug = CargasTUGSerializer(many=True, read_only=True)
    tue = CargasTUESerializer(many=True, read_only=True)
    ilum = CargasILUMSerializer(many=True, read_only=True)
    
    # Propriedades calculadas
    soma_tug_va = serializers.ReadOnlyField()
    soma_tug_w = serializers.ReadOnlyField()
    soma_tue_va = serializers.ReadOnlyField()
    soma_tue_w = serializers.ReadOnlyField()
    soma_ilum_va = serializers.ReadOnlyField()
    soma_ilum_w = serializers.ReadOnlyField()
    total_va = serializers.ReadOnlyField()
    total_w = serializers.ReadOnlyField()
    corrente_ckt = serializers.ReadOnlyField()

    class Meta:
        model = Circuitos
        fields = '__all__'

class DemandasSerializer(serializers.ModelSerializer):
    demanda_motor = serializers.ReadOnlyField()
    demanda_resist = serializers.ReadOnlyField()
    demanda_ac = serializers.ReadOnlyField()
    demanda_ac_central = serializers.ReadOnlyField()
    demanda_trafo = serializers.ReadOnlyField()
    demanda_total = serializers.ReadOnlyField()
    padrao_entrada = serializers.ReadOnlyField()

    tipo_entrada = serializers.ReadOnlyField()

    class Meta:
        model = Demandas
        fields = '__all__'
    
    def get_tipo_entrada(self, obj):
        tipo_entrada = obj.tipo_entrada()
        return tipo_entrada

# Adicionei estes para completar a visualização do Local
class CondutoresSerializer(serializers.ModelSerializer):
    corrente_projetada = serializers.ReadOnlyField()
    condutores_calc = serializers.ReadOnlyField()

    class Meta:
        model = Condutores
        fields = '__all__'

class EletrodutosSerializer(serializers.ModelSerializer):
    eletroduto = serializers.ReadOnlyField()
    
    class Meta:
        model = Eletrodutos
        fields = '__all__'

class ProtecaoSerializer(serializers.ModelSerializer):
    protecao = serializers.ReadOnlyField()

    class Meta:
        model = Protecao
        fields = '__all__'

class EquilibrioFasesSerializer(serializers.ModelSerializer):
    equilibrio = serializers.ReadOnlyField()

    class Meta:
        model = EquilibrioFases
        fields = '__all__'

# -----------------------------------------------------------------------------
# 3. SERIALIZER PRINCIPAL (O Pai de todos: Local)
# -----------------------------------------------------------------------------

class LocalSerializer(serializers.ModelSerializer):
    # Usamos 'source' porque o related_name no model é, por exemplo, 'local_ambiente',
    # mas no JSON queremos que apareça como 'ambientes'.
    cliente = ClienteSimplesSerializer(read_only=True)
    ambientes = AmbientesSerializer(many=True, read_only=True, source='local_ambiente')
    circuitos = CircuitosSerializer(many=True, read_only=True, source='ckt_local')
    demandas = DemandasSerializer(many=True, read_only=True, source='demanda_local')
    condutores = CondutoresSerializer(many=True, read_only=True, source='cond_local')
    eletrodutos = EletrodutosSerializer(many=True, read_only=True, source='eletro_local')
    protecoes = ProtecaoSerializer(many=True, read_only=True, source='prot_local')
    equilibrio = EquilibrioFasesSerializer(many=True, read_only=True, source='EqFase_local')
    tug = CargasTUGSerializer(many=True, read_only=True, source='cargas_tug_local')
    

    class Meta:
        model = Local
        fields = [
            'id', 'cliente', 'local', 'cep', 'logradouro', 'numero', 
            'bairro', 'cidade', 'uf', 'rede',
            # Listas aninhadas
            'ambientes', 
            'circuitos', 
            'demandas',
            'condutores',
            'eletrodutos',
            'protecoes',
            'equilibrio',
            'tug',
        ]

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.endereco_cep_local()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.endereco_cep_local()
        instance.save()
        return instance