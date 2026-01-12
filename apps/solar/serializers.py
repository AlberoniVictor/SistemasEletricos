from rest_framework import serializers
from .models import Consumo, ConsumoAdicional, ArquivosUnidadeConsumidora, Irradiacao, PotGeracao, Paineis, GerEsperada

class GerEsperadaSerializer(serializers.ModelSerializer):
    geresperada = serializers.ReadOnlyField()
    media_geresp = serializers.ReadOnlyField()
    saldo_esperado = serializers.ReadOnlyField()
    media_saldo = serializers.ReadOnlyField()

    class Meta:
        model = GerEsperada
        fields = '__all__'

class PaineisSerializer(serializers.ModelSerializer):
    calculopainel = serializers.ReadOnlyField()
    area_min_necessaria = serializers.ReadOnlyField()
    potencia_sistema = serializers.ReadOnlyField()
    painelareadisp = serializers.ReadOnlyField()
    potsisareadisp = serializers.ReadOnlyField()
    paineis = serializers.ReadOnlyField()
    potenciasistema = serializers.ReadOnlyField()
    area_sistema = serializers.ReadOnlyField()
    area_painel = serializers.ReadOnlyField()

    class Meta:
        model = Paineis
        fields = '__all__'

class PotGeracaoSerializer(serializers.ModelSerializer):
    calculogeracao = serializers.ReadOnlyField()
    class Meta:
        model = PotGeracao
        fields = '__all__'

class IrradiacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Irradiacao
        fields = '__all__'

class ArquivosUnidadeConsumidoraSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = ArquivosUnidadeConsumidora
        fields = [
            'id',
            'tipo',
            'tipo_display',
            'arquivo',
            'data_upload',
            'consumo',
        ]

class ConsumoAdicionalSerializer(serializers.ModelSerializer):
    calculo_kwh = serializers.ReadOnlyField()
    class Meta:
        model = ConsumoAdicional
        fields = '__all__'

class ConsumoSerializer(serializers.ModelSerializer):
    consumo_mensal_total = serializers.ReadOnlyField
    consumo_geresp = GerEsperadaSerializer(many=True, read_only=True)
    consumo_paineis = PaineisSerializer(many=True, read_only=True)
    potger_consumo = PotGeracaoSerializer(many=True, read_only=True)
    consumo_irradiacao = IrradiacaoSerializer(many=True, read_only=True)
    arquivos_consumo = ArquivosUnidadeConsumidoraSerializer(many=True, read_only=True)
    consumo_adicional = ConsumoAdicionalSerializer(many=True, read_only=True)

    class Meta:
        model = Consumo
        fields = [
            'id',
            'uncons',
            'endereco',
            'etapa',
            'cons_jan',
            'cons_fev',
            'cons_mar',
            'cons_abr',
            'cons_mai',
            'cons_jun',
            'cons_jul',
            'cons_ago',
            'cons_set',
            'cons_out',
            'cons_nov',
            'cons_dez',
            'media_consumo',
            'consumo_ad_total',
            'consumo_total',
            'potger_consumo',
            'arquivos_consumo',
            'consumo_adicional',
            'consumo_geresp',
            'consumo_paineis',
            'consumo_irradiacao',
            'consumo_mensal_total',
            
        ]