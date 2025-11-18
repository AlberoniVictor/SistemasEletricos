
from django.contrib import admin
from .models import Cliente,ArquivosClientes

class ArquivosClientesInline(admin.TabularInline):
    model = ArquivosClientes
    extra = 0
    verbose_name_plural = 'Arquivos do Cliente'
    verbose_name = 'Arquivo do Cliente'

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome','email','tel1')
    list_display_links = ('id','nome')
    list_per_page = 20
    search_fields = ('nome',)
    inlines = [ArquivosClientesInline]
    fieldsets = (
        ('Cliente',{
            'fields':(
                'tipo',
                ('nome','doc',),
                ('email','tel1','tel2',),
                ('cep','logradouro','numero',),
                ('bairro','cidade','uf',),
                'cadastro',
            ),
        }),
    )