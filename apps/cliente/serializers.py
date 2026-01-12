from django.forms import ValidationError as DjangoValidationError
from rest_framework import serializers
from .models import Cliente, ArquivosClientes
from apps.instEletricas.serializers import LocalSerializer
from apps.instEletricas.models import Local
from apps.solar.models import Consumo,PotGeracao
from apps.solar.serializers import ConsumoSerializer

class LocalInstEletSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Local
        fields = ['id', 'local', 'endereco','etapa']

class PotGeracaoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PotGeracao
        fields = ['id', 'calculogeracao']

class ConsumoSimplesSerializer(serializers.ModelSerializer):
    potger_consumo = PotGeracaoSimplesSerializer(many=True, read_only=True)
    class Meta:
        model = Consumo
        fields = ['id', 'uncons', 'endereco','etapa', 'potger_consumo']

class ArquivosClientesSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = ArquivosClientes
        fields = [
            'id',
            'tipo',
            'tipo_display',
            'arquivo',
            'data_upload',
            'cliente',
        ]

class ListaClienteSerializer(serializers.ModelSerializer):
    cliente_local = LocalInstEletSimplesSerializer(many=True, read_only=True)
    cliente_solar = ConsumoSimplesSerializer(many=True, read_only=True)
    cadastro = serializers.ReadOnlyField()
    class Meta:
        model = Cliente
        fields = [
            'id',
            'tipo',
            'nome',
            'doc',
            'email',
            'tel1',
            'tel2',
            'cep',
            'logradouro',
            'numero',
            'bairro',
            'cidade',
            'uf',
            'cadastro',
            'cliente_local',
            'cliente_solar',
        ]

class ClienteSerializer(serializers.ModelSerializer):
    files = ArquivosClientesSerializer(many=True, read_only=True)
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    cliente_local = LocalSerializer(many=True, read_only=True)
    cliente_solar = ConsumoSerializer(many=True, read_only=True)
    cadastro = serializers.ReadOnlyField()
    
    class Meta:
        model = Cliente
        fields = [
            'id',
            'tipo',
            'tipo_display',
            'nome',
            'doc',
            'email',
            'tel1',
            'tel2',
            'cep',
            'logradouro',
            'numero',
            'bairro',
            'cidade',
            'uf',
            'cadastro',
            'files',
            'cliente_local',
            'cliente_solar',
        ]
    
    def validate(self, data):
        """
        Força o DRF a rodar o método .clean() do seu Model
        antes de salvar os dados.
        """
        # Cria uma instância temporária com os dados recebidos do formulário
        instance = Cliente(**data)

        # Se for edição (PUT/PATCH), precisamos garantir que o ID existe
        if self.instance:
            instance.id = self.instance.id
        
        try:
            # Aqui é onde a sua mágica do models.py é chamada!
            instance.clean()
        except DjangoValidationError as e:
            # Converte o erro do Model para um erro que o Frontend entende (400 Bad Request)
            raise serializers.ValidationError(e.message_dict)

        return data
