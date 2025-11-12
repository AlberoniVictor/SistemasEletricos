from django.contrib import admin
from apps.instEletricas.models import Demandas,Local,Ambientes,CargasTUG,CargasILUM,CargasTUE,Circuitos

class AmbientesInline(admin.TabularInline):
    model = Ambientes
    extra = 0
    verbose_name='Ambiente'
    verbose_name_plural='Ambientes'

class CargasTUEInline(admin.TabularInline):
    model = CargasTUE
    extra = 0
    verbose_name='Carga de Tomada de Uso Específico'
    verbose_name_plural='Cargas de Tomada de Uso Específico'

@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    list_display=('id','cliente','local','cidade','uf','cep','rede')
    list_display_links=('id','cliente','local')
    list_per_page=20
    search_fields=('id','cliente','local','cep')
    inlines = [AmbientesInline]

    fieldsets = (
        ('Local',{
            'fields':(
                'cliente',('local','rede',),
                ('logradouro','numero','bairro'),
                ('cidade','uf','cep'),

            ),
        }),
    )

@admin.register(Ambientes)
class AmbientesAdmin(admin.ModelAdmin):
    list_display = ('id','local','comodo')
    list_display_links = ('id','local','comodo')
    list_per_page = 20
    search_fields = ('id','local','comodo')
    inlines = [CargasTUEInline]

    fieldsets=(
        ('Ambiente',{
            'fields':(
                'local',
                ('comodo','t_comodo'),
                ('perimetro','area'),
                ('tug','tue','iluminacao')
            ),
        }),
    )

@admin.register(CargasTUG)
class CargasTUGAdmin(admin.ModelAdmin):
    list_display = ('id','format_cliente','comodo','format_calc_tug','format_calc_pot_tug')
    list_display_links = ('id','format_cliente','comodo','format_calc_tug','format_calc_pot_tug')
    list_per_page = 20
    search_fields = ('id','comodo',)
    readonly_fields = ['format_cliente','format_calc_tug','format_calc_pot_tug','format_conv_pot_tug']

    fieldsets = (
        ('Calculo de Tomadas de Uso Geral',{
            'fields':(
                'format_cliente','comodo',
                'format_calc_tug',
                'format_calc_pot_tug',
                'format_conv_pot_tug',
            ),
        }),
    )

    def format_cliente(self,obj):
        return f'{obj.comodo.local.cliente}'
    format_cliente.short_description = 'Cliente'

    def format_calc_tug(self,obj):
        return f'{obj.calculo_tug} Tomadas'
    format_calc_tug.short_description = 'Calculo de TUG'

    def format_calc_pot_tug(self,obj):
        pot,grand = obj.calculo_pot_tug
        return f'{pot:.2f} {grand}'
    format_calc_pot_tug.short_description = 'Calculo de Potencia TUG (VA)'

    def format_conv_pot_tug(self,obj):
        pot,grand = obj.conv_pot_tug
        return f'{pot:.2f} {grand}'
    format_conv_pot_tug.short_description = 'Calculo de Potencia TUG (W)'
    
@admin.register(CargasILUM)
class CargasILUMAdmin(admin.ModelAdmin):
    list_display = ('id','format_cliente','comodo','format_calc_ilum','format_calc_pot_ilum')
    list_display_links = ('id','format_cliente','comodo','format_calc_ilum','format_calc_pot_ilum')
    list_per_page = 20
    search_fields = ('id','comodo',)
    readonly_fields = ['format_cliente','format_calc_ilum','format_calc_pot_ilum','format_conv_pot_ilum']

    fieldsets = (
        ('Calculo de Tomadas de Uso Geral',{
            'fields':(
                'format_cliente','comodo',
                'format_calc_ilum',
                'format_calc_pot_ilum',
                'format_conv_pot_ilum',
            ),
        }),
    )

    def format_cliente(self,obj):
        return f'{obj.comodo.local.cliente}'
    format_cliente.short_description = 'Cliente'

    def format_calc_ilum(self,obj):
        return f'{obj.calculo_ilum} Pontos de Luz'
    format_calc_ilum.short_description = 'Calculo de Iluminação'

    def format_calc_pot_ilum(self,obj):
        pot,grand = obj.calculo_pot_ilum
        return f'{pot:.2f} {grand}'
    format_calc_pot_ilum.short_description = 'Calculo de Potencia Iluminação (VA)'

    def format_conv_pot_ilum(self,obj):
        pot,grand = obj.conv_pot_ilum
        return f'{pot:.2f} {grand}'
    format_conv_pot_ilum.short_description = 'Calculo de Potencia Iluminação (W)'

@admin.register(CargasTUE)
class CargasTUEAdmin(admin.ModelAdmin):
    list_display = ('id','comodo','format_potencia')
    list_display_links = ('id','comodo','format_potencia')
    list_per_page = 20
    search_fields = ('id','comodo',)
    readonly_fields = ['format_cliente','format_potencia','format_conv_pot_tue']

    fieldsets = (
        ('Calculo de Tomadas de Uso Especifico',{
            'fields':(
                'format_cliente',
                'comodo',
                'carga',
                ('t_pot','pot_tue','t_carga'),
                'format_potencia',
                'format_conv_pot_tue',
                
            ),
        }),
    )

    def format_cliente(self,obj):
        return f'{obj.comodo.local.cliente}'
    format_cliente.short_description = 'Cliente'

    def format_potencia(self,obj):
        pot,grand = obj.potencia
        return f'{pot:.2f} {grand}'
    format_potencia.short_description = 'Calculo de Potência TUE (VA)'


    def format_conv_pot_tue(self,obj):
        pot,grand = obj.conv_pot_tue
        return f'{pot:.2f} {grand}'
    format_conv_pot_tue.short_description = 'Calculo de Potência TUE (W)'

@admin.register(Circuitos)
class CircuitosAdmin(admin.ModelAdmin):
    list_display = ('id','nome','ambiente','format_total_va','format_total_w','format_corrente')
    list_display_links = ('id','nome','ambiente','format_total_va','format_total_w',)
    list_per_page = 20
    search_fields = ('id','nome','ambiente')
    readonly_fields = ['format_corrente','format_soma_tug_va','format_soma_tue_va','format_soma_ilum_va','format_total_va','format_total_w']
    fieldsets = (
        ('Circuito',{
            'fields':(
                'ambiente',
                ('nome','ckt'),
                ('tug','tue','ilum'),
                ('format_soma_tug_va','format_soma_tue_va','format_soma_ilum_va'),
            ),
        },),
        ('Total',{
            'fields':(
                'format_total_va',
                'format_total_w',
                'format_corrente',
            ),

        },

        ),
    )

    def format_soma_tug_va(self,obj):
        return f'{obj.soma_tug_va:.2f} VA'
    format_soma_tug_va.short_description = 'TUG (VA)'

    def format_soma_tue_va(self,obj):
        return f'{obj.soma_tue_va:.2f} VA'
    format_soma_tue_va.short_description = 'TUE (VA)'

    def format_soma_ilum_va(self,obj):
        return f'{obj.soma_ilum_va:.2f} VA'
    format_soma_ilum_va.short_description = 'Iluminação (VA)'

    def format_total_va(self,obj):
        return f'{obj.total_va:.2f} VA'
    format_total_va.short_description = 'Total (VA)'

    def format_total_w(self,obj):
        return f'{obj.total_w:.2f} W'
    format_total_w.short_description = 'Total (W)'

    def format_corrente(self,obj):
        return f'{obj.corrente_ckt:.2f} A'
    format_corrente.short_description = 'Corrente'

@admin.register(Demandas)
class DemandasAdmin(admin.ModelAdmin):
    list_display = ('id','cliente','local','format_dem_total',)
    list_display_links = ('id','cliente','local','format_dem_total',)
    list_per_page = 20
    search_fields = ('id','local',)
    readonly_fields = ['format_padrao','format_dem_tug_ilum','cliente','format_dem_resist','format_dem_ac','format_dem_ac_central','format_dem_trafo','format_dem_motor','format_dem_total',]
    fieldsets = (
        ('Demanda da Instalação',{
            'fields':(
                'local','cliente',
                ('tug','ilum','tue'),
                'format_dem_tug_ilum',
                'format_dem_resist',
                'format_dem_ac',
                'format_dem_ac_central',
                'format_dem_trafo',
                'format_dem_motor',
            ),
        }),
        ('Total',{
            'fields':(
                'format_dem_total',
                'format_padrao'
            ),
        }),
        )
    
    def format_dem_motor(self,obj):
        dem,unid = obj.demanda_motor 
        return f'{dem:.2f} {unid}'
    format_dem_motor.short_description = 'Demanda de Motores'
    def format_dem_resist(self,obj):
        dem,unid = obj.demanda_resist 
        return f'{dem:.2f} {unid}'
    format_dem_resist.short_description = 'Demanda de Cargas Resistivas'
    def format_dem_ac(self,obj):
        dem,unid = obj.demanda_ac
        return f'{dem:.2f} {unid}'
    format_dem_ac.short_description = 'Demanda de Ar-Condicionado Split ou Janela'
    def format_dem_ac_central(self,obj):
        dem,unid = obj.demanda_ac_central 
        return f'{dem:.2f} {unid}'
    format_dem_ac_central.short_description = 'Demanda de Ar-Condicionado Central'
    def format_dem_trafo(self,obj):
        dem,unid = obj.demanda_trafo 
        return f'{dem:.2f} {unid}'
    format_dem_trafo.short_description = 'Demanda de Tranformadores e Similares'
    def format_dem_tug_ilum(self,obj):
        dem,unid = obj.demanda_tug_ilum 
        return f'{dem:.2f} {unid}'
    format_dem_tug_ilum.short_description = 'Demanda de TUG e Iluminação'
    def format_dem_total(self,obj):
        return f'{obj.demanda_total:.2f} kVA'
    format_dem_total.short_description = 'Demanda Total'
    def cliente(self,obj):
        cliente = obj.local.cliente
        return cliente
    cliente.short_description = 'Cliente'

    def format_padrao(self,obj):
        disj,ckt = obj.padrao_entrada
        return f'{disj} A - {ckt}'
    format_padrao.short_description = 'Disjuntor Padrão de Entrada'
# fieldsets=(
#     ('Ambiente',{
#         'fields':(

#         ),
#     }),
# )