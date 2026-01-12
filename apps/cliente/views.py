from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Cliente, ArquivosClientes
from .serializers import ClienteSerializer, ArquivosClientesSerializer, ListaClienteSerializer
from apps.instEletricas.models import Local

from rest_framework import viewsets, status

class ListaClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ListaClienteSerializer

    http_method_names = ['get','head','options']

    def get_queryset(self):
        return Cliente.objects.prefetch_related('cliente_local','cliente_solar','cliente_solar__potger_consumo').all()

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer

    http_method_names = ['get','post','put','patch','head','options']

    def get_queryset(self):
        return Cliente.objects.prefetch_related('files','cliente_local').all()