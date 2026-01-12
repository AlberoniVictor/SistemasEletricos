from django.shortcuts import render

from .models import Consumo
from .serializers import ConsumoSerializer, ArquivosUnidadeConsumidoraSerializer, ConsumoAdicionalSerializer, IrradiacaoSerializer, PotGeracaoSerializer, PaineisSerializer, GerEsperadaSerializer

from rest_framework import viewsets

class ConsumoViewSet(viewsets.ModelViewSet):
    serializer_class = ConsumoSerializer

    http_method_names = ['get','post','put','patch','head','options']

    def get_queryset(self):
        return Consumo.objects.select_related('cliente').prefetch_related(
            'consumo_geresp',
            'consumo_paineis',
            'potger_consumo',
            'consumo_irradiacao',
            'consumo_files',
            'consumo_adicional'
        ).all()