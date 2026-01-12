from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Consumo,ConsumoAdicional,Irradiacao,PotGeracao,Paineis,GerEsperada,ArquivosUnidadeConsumidora,EnergiaProduzida,CustoMaterial,EcoProjetada,CustosNegocio

class ArquivosUnidadeConsumidoraInline(admin.TabularInline):
    model = ArquivosUnidadeConsumidora
    extra = 0
    verbose_name_plural = 'Arquivos da Unidade Consumidora'
    verbose_name = 'Arquivo da Unidade Consumidora'

class ConsumoAdicionalAdmin(admin.TabularInline):
    model = ConsumoAdicional
    extra = 1
    verbose_name_plural = 'Consumos Adicionais'
    verbose_name = 'Consumo Adicional'

@admin.register(Consumo)
class ConsumoAdmin(admin.ModelAdmin):
    list_display = ('id','cliente','uncons','concessionaria','logradouro','categoria','cadastro')
    search_fields = ('id','cliente','uncons','concessionaria','logradouro','categoria')
    list_filter = ('cliente','uncons','concessionaria','cadastro')
    list_display_links = ('id','cliente','uncons','concessionaria','logradouro')
    list_per_page = 20
    inlines = [ConsumoAdicionalAdmin, ArquivosUnidadeConsumidoraInline]
    search_fields = ('cliente',)
    readonly_fields = ['format_consumo','format_consumo_tot','format_consumo_ad']

    fieldsets = (
        ('Cliente', {
            'fields': (('cliente','uncons','concessionaria'),
                       ('etapa',)),
        }),

        ('Endereço Unidade Consumidora',{
            'fields':(
                ('categoria'),
                ('logradouro','numero','bairro',),
                ('cidade','uf','cep',),
                ('lat','lon'),
            ),
        }),

        ('Consumo Mensal (kWh)', {
            'fields': (
                ('cons_jan', 'cons_fev', 'cons_mar'),
                ('cons_abr', 'cons_mai', 'cons_jun'),
                ('cons_jul', 'cons_ago', 'cons_set'),
                ('cons_out', 'cons_nov', 'cons_dez')
            )
        }),
        ('Resultado',{
            'fields':('format_consumo','format_consumo_ad'),
        }),
        ('Total',{
            'fields':('format_consumo_tot',),
        }),
        
    )

    def save_model(self, request, obj, form, change):
        # Atualiza os campos vindos da API
        obj.endereco_cep_local()
        obj.format_concessionaria()

        # Salva normalmente
        super().save_model(request, obj, form, change)

    def format_consumo(self,obj):
        return f'{obj.media_consumo:.2f} kWh/mês'
    format_consumo.short_description = 'Média de Consumo'
    
    def format_consumo_tot(self,obj):
        return f'{obj.consumo_total:.2f} kWh/mês'
    format_consumo_tot.short_description = 'Consumo Total'
    
    def format_consumo_ad(self,obj):
        return f'{obj.consumo_ad_total:.2f} kWh/mês'
    format_consumo_ad.short_description = 'Consumo Adicional'

@admin.register(Irradiacao)
class IrradAdmin(admin.ModelAdmin):
    list_display = ('id','cliente','format_media_irrad')
    list_display_links = ('id','cliente')
    search_fields = ('cliente',)
    readonly_fields = ['format_media_irrad']
    
    fieldsets = (
        ('Cliente', {
            'fields': ('cliente',)
        }),
        ('Irradiação Média Anual',{
            'fields':('format_media_irrad','irrad_anual'
                      )
        }),
        ('Irradiações Mensais', {
            'fields':(
                ('irrad_jan','irrad_fev','irrad_mar'),
                ('irrad_abr','irrad_mai','irrad_jun'),
                ('irrad_jul','irrad_ago','irrad_set'),
                ('irrad_out','irrad_nov','irrad_dez')
            )
        }),

        )


    def save_model(self, request, obj, form, change):
        # Atualiza os campos vindos da API
        obj.irrad_mes_local()

        # Salva normalmente
        super().save_model(request, obj, form, change)

    def format_media_irrad(self,obj):
        return f'{obj.media_irradi:.2f}'
    format_media_irrad.short_description = 'Irradiação Média Calculada'

@admin.register(PotGeracao)
class PotGerAdmin(admin.ModelAdmin):
    list_display = ('id','cliente','rendimento','format_ger')
    list_display_links = ('id','cliente')
    autocomplete_fields = ['cliente', 'consumo']
    search_fields = ('cliente',)
    readonly_fields = ('format_ger',)

    fieldsets = (
        ('Geração',{
            'fields':(
                'cliente','consumo','rendimento'
            ),
        }),
        ('Irradiação', {
            'fields': ('irrad',)
        }),
        
        ('Resultado',{
            'fields':('format_ger',),
        }),
        
    )
    def format_ger(self,obj):
        return f'{obj.calculogeracao:.2f} kWp'
    format_ger.short_description = 'Potência minima de Geração'

@admin.register(Paineis)
class PaineisAdmin(admin.ModelAdmin):
    list_display = ('id','cliente','unidade_consumidora')
    list_display_links = ('id','cliente')
    search_fields = ('cliente',)
    readonly_fields = ['format_pger','format_painel','format_potsis','format_area','format_potsisdesej','format_potsisareadisp','format_painelareadisp','format_area_desj','unidade_consumidora']

    fieldsets = (
            ('Paineis',{
                'fields':(
                    ('cliente','unidade_consumidora',),
                    ('potgeracao',),
                    ('h','l','potpainel'),
                ),
            }),
            
            ('Resultado',{
                'fields':('format_painel','format_area','format_potsis'),
            }),
            ('Paineis Desejados',{
                'fields':(('paineisdesejados'),
                    'format_potsisdesej','format_area_desj',),
            }),
            ('Area Disponível',{
                'fields':(('areadisp'),
                          'format_painelareadisp','format_potsisareadisp',),
            }),
            
            
            
        )
    
    def unidade_consumidora(self,obj):
        return f'{obj.cliente.uncons}'
    unidade_consumidora.short_description = 'Unidade Consumidora'

    def format_area(self,obj):
        return f'{obj.area_min_necessaria:.2f} m^(2)'
    format_area.short_description = 'Área Mínima Necessária'

    def format_area_desj(self,obj):
        return f'{obj.area_necessaria_desj:.2f} m^(2)'
    format_area_desj.short_description = 'Área Necessária para Qnt de Paineis Desejados'
    
    def format_potsis(self,obj):
        return f'{obj.potenciasistema:.2f} kWp'
    format_potsis.short_description = 'Potencia Necessária do Sistema'

    def format_potsisdesej(self,obj):
        return f'{obj.potsispaineldesejado:.2f} kWp'
    format_potsisdesej.short_description = 'Pot. do Sistema para Qnt. Paineis Desejados'

    def format_potsisareadisp(self,obj):
        return f'{obj.potsisareadisp:.2f} kWp'
    format_potsisareadisp.short_description = 'Pot. do Sistema para Área Disponível'

    def format_painel(self,obj):
        return f'{obj.calculopainel:.0f} Paineis' 
    format_painel.short_description = 'Paineis Pot. Min. de Geração'

    def format_painelareadisp(self,obj):
        return f'{obj.painelareadisp:.0f} Paineis ' 
    format_painelareadisp.short_description = 'Paineis para a area Disponível'

    def format_pger(self,obj):
        return f'{obj.potgeracao.calculogeracao:.2f} kWp'
    format_pger.short_description = 'Potência Mínima de Geração'

@admin.register(GerEsperada)
class GerEsperadaAdmin(admin.ModelAdmin):
    list_display = ('id','cliente', 'pger','potsis','rend','uc','mediageresp',)
    list_display_links = ('id','cliente','pger')
    search_fields = ('cliente',)
    readonly_fields = ['rend','irrad','painel','geracao_formatada','uc','mediageresp','dic_consumo_formatado','saldo_formatado','media_saldo']

    fieldsets = (
        ('Cliente',{
            'fields':('cliente','uc','rend','irrad','pger','potsis'),
        }),
        ('Numero de Painéis',{
            'fields':('painel',),
        }),
        ('Resultado',{
            'fields':('geracao_formatada','mediageresp','dic_consumo_formatado','saldo_formatado','media_saldo'),
        }),
    )

    def geracao_formatada(self, obj):
        return "\n".join([f"{mes}: {valor:.2f} kWh" for mes, valor in obj.geresperada.items()])
    geracao_formatada.short_description = "Geração Esperada (kWh)"

    def dic_consumo_formatado(self, obj):
        return "\n".join([f"{mes}: {valor:.2f} kWh" for mes, valor in obj.dic_consumo.items()])
    dic_consumo_formatado.short_description = "Consumo Mensal (kWh)"

    def saldo_formatado(self, obj):
        return "\n".join([f"{mes}: {valor:.2f} kWh" for mes, valor in obj.saldo_esperado.items()])
    saldo_formatado.short_description = "Credito Mensal Esperado (kWh)"

    def media_saldo(self,obj):
        return f'{obj.media_saldo:.2f} kWh/mês'
    media_saldo.short_description = "Credito/Consumo Médio esperado (kWh)"

    @admin.display(description='Painéis')
    def painel(self,obj):
        return f'{obj.potsis.paineis} painéis'
    
    @admin.display(description='Rendimento')
    def rend(self,obj):
        return f'{obj.potsis.potgeracao.rendimento}%'
    
    @admin.display(description='Irradiação Média')
    def irrad(self,obj):
        return f'{obj.potsis.potgeracao.irrad.irrad_anual}'
    @admin.display(description='Unidade Consumidora')
    def uc(self,obj):
        return f'{obj.pger.consumo.uncons}'
    @admin.display(description='Geração Média Esperada')
    def mediageresp(self,obj):
        return f'{obj.media_geresp:.2f} kWh/mês'

@admin.register(EnergiaProduzida)
class EnergiaProduzidaAdmin(admin.ModelAdmin):
    list_display = ('id','cliente',)
    list_display_links = ('id','cliente',)
    search_fields = ('id','cliente',)
    readonly_fields = ['comparativo_formatado','uncons','nomecliente']

    fieldsets = (
    ('Cliente', {
            'fields': (('nomecliente','uncons',),
                       'cliente',),
        }),
        ('Geração Real Mensal (kWh)', {
            'fields': (
                ('eprod_jan', 'eprod_fev', 'eprod_mar'),
                ('eprod_abr', 'eprod_mai', 'eprod_jun'),
                ('eprod_jul', 'eprod_ago', 'eprod_set'),
                ('eprod_out', 'eprod_nov', 'eprod_dez',),
            ),
        }),
        ('Resultado',{
            'fields':('comparativo_formatado',),
        }),
        
    )
    
    def nomecliente(self,obj):
        return obj.cliente.cliente.cliente
    nomecliente.short_description = 'Cliente'
    def uncons(self,obj):
        return obj.cliente.cliente.uncons
    uncons.short_description = 'Unidade Consumidora'
    def comparativo_formatado(self, obj):
        return "\n".join([f"{mes}: {valor:.2f} kWh" for mes, valor in obj.comparativo_prod_esp.items()])
    comparativo_formatado.short_description = "Diferença entre Geração Real e Esperada (kWh)"

@admin.register(CustoMaterial)
class CustoMaterialAdmin(admin.ModelAdmin):
    list_display = ('id','nomecliente','uncons','equip','qnt','preco_format','unid')
    list_display_links = ('id','nomecliente','uncons','equip')
    search_fields = ('id','nomecliente','uncons','equip')
    readonly_fields = ['nomecliente','uncons','preco_format']


    fieldsets = (
        ('Cliente', {
            'fields': (('nomecliente','uncons',),
                       'cliente',),
        }),
        ('Equipamento', {
            'fields': (
                ('equip','qnt','preco_unit','unid'),
                ('preco_tot'),
            ),
        }),
        ('Resultado',{
            'fields':('preco_format',),
        }),
        
    )

    def preco_format(self,obj):
        return obj.preco_formatado
    preco_format.short_description = 'Custo Total'
    def nomecliente(self,obj):
        return obj.cliente.cliente
    nomecliente.short_description = 'Cliente'
    def uncons(self,obj):
        return obj.cliente.uncons
    uncons.short_description = 'Unidade Consumidora'

@admin.register(EcoProjetada)
class EcoProjetadaAdmin(admin.ModelAdmin):
    list_display = ('id','nomecliente','uncons','anos_retorno_format')
    list_display_links = ('id','nomecliente','uncons',)
    search_fields = ('id','nomecliente','uncons',)
    readonly_fields = ['nomecliente','uncons','retorno_formatado','anos_retorno_format','custo_mat_total','lista_material_format','proj_25anos_formatado',"custo_kit","mao_obra","margem",'proj_anual_25anos_format']


    fieldsets = (
    ('Cliente', {
            'fields': (
                ('nomecliente','uncons',),
               'cliente',
               'geracao',
            ),
        }),
        ('Custos da Usina', {
            'fields': (
                ('custo_kit','mao_obra',),
                
                'ano_op',
                'custo_negocio',
                'margem'

            ),
        }),
        ('Custos Conta de Energia',{
            'fields':(
                'tarifa_el',
                'ilum_public',
                'fiob',
            ),
        }),
        ('Resultado',{
            'fields':(
                'retorno_formatado',
                'anos_retorno_format',
                'lista_material_format',
                'custo_mat_total',
                'proj_25anos_formatado',
                'proj_anual_25anos_format',
            ),
        }),
        
    )

    def margem(self,obj):
        return obj.custo_negocio.margem
    margem.short_description = 'Margem de Lucro'
    def custo_kit(self,obj):
        return obj.custo_negocio.custo_kit
    custo_kit.short_description = 'Custo do Kit'
    def mao_obra(self,obj):
        return obj.custo_negocio.mao_de_obra
    mao_obra.short_description = 'Custo da Mão de Obra'

    def custo_mat_total(self,obj):
        return f'R$ {obj.custo_material_total:.2f}'
    custo_mat_total.short_description = 'Custo Total de Material'
    def nomecliente(self,obj):
        return obj.cliente.cliente
    nomecliente.short_description = 'Cliente'
    def uncons(self,obj):
        return obj.cliente.uncons
    uncons.short_description = 'Unidade Consumidora'
    def retorno_formatado(self, obj):
        linhas = []
        for ano, valor in obj.retorno.items():
            v = f"{valor:,.2f}"
            v = v.replace(',', 'X').replace('.', ',').replace('X', '.')
            linhas.append(f"{ano}: R$ {v}")
        return "\n".join(linhas)
    retorno_formatado.short_description = "Retorno Projetado"

    def proj_25anos_formatado(self, obj):
        linhas = []
        for ano, valor in obj.proj_25anos.items():
            v = f"{valor:,.2f}"
            v = v.replace(',', 'X').replace('.', ',').replace('X', '.')
            linhas.append(f"{ano}: R$ {v}")
        return "\n".join(linhas)
    proj_25anos_formatado.short_description = "Projeção Acumulada 25 anos"    

    def proj_anual_25anos_format(self,obj):
        linhas = []
        for ano, valor in obj.proj_anual_25anos.items():
            v = f"{valor:,.2f}"
            v = v.replace(',', 'X').replace('.', ',').replace('X', '.')
            linhas.append(f"{ano}: R$ {v}")
        return "\n".join(linhas)
    proj_25anos_formatado.short_description = "Projeção Anual para 25 anos"

    def anos_retorno_format(self,obj):
        return f'{obj.anos_retorno} anos'
    anos_retorno_format.short_description = 'Anos para Retorno do investimento'

    def lista_material_format(self, obj):
        linhas = "".join(
            f"""
            <tr>
                <td style="padding:4px;border:1px solid #ccc;">{equip}</td>
                <td style="padding:4px;border:1px solid #ccc;">{qnt}</td>
                <td style="padding:4px;border:1px solid #ccc;">{unid}</td>
                <td style="padding:4px;border:1px solid #ccc;">R$ {preco_unit:,.2f}</td>
                <td style="padding:4px;border:1px solid #ccc;">R$ {preco_tot:,.2f}</td>
            </tr>
            """.replace(",", "X").replace(".", ",").replace("X", ".")
            for equip, qnt, unid, preco_unit, preco_tot in obj.lista_material()
        )

        return format_html(
            """
            <table style="border-collapse: collapse; width: 100%;">
                <thead>
                    <tr style="background-color: #f8f9fa;">
                        <th style="padding:8px;border:1px solid #ccc;text-align:left;">Equipamento</th>
                        <th style="padding:8px;border:1px solid #ccc;text-align:left;">Quantidade</th>
                        <th style="padding:8px;border:1px solid #ccc;text-align:left;">Unidade</th>
                        <th style="padding:8px;border:1px solid #ccc;text-align:left;">Preço Unitário</th>
                        <th style="padding:8px;border:1px solid #ccc;text-align:left;">Valor Total</th>
                    </tr>
                </thead>
                <tbody>
                    {}
                </tbody>
            </table>
            """,
            mark_safe(linhas)
        )

    lista_material_format.short_description = "Lista de Custos"
    lista_material_format.allow_tags = True

@admin.register(CustosNegocio)
class CustosNegocioAdmin(admin.ModelAdmin):
    list_display = ('id','nomecliente','uncons','preco_format')
    list_display_links = ('id','nomecliente','uncons','preco_format')
    search_fields = ('id','nomecliente','uncons','preco_format')
    readonly_fields = ['custo_do_kit','custo_de_material','custo_de_instalação','custo_de_engenharia','nomecliente','uncons','preco_format','custo_de_impostos','custo_de_representante','custo__de_comercial']

    fieldsets = (
        ('Cliente', {
            'fields': (('nomecliente','uncons',),
                       'cliente','paineis_herd'),
        }),
        ('Custos', {
            'fields': (
                'art',
                'custo_kit',
                'custo_material',
                'mao_obra',
                'engenharia',
            ),
        }),
        ('Negocio',{
            'fields':('comissao_rep','comissao_com','imposto','margem'),
        }),
        ('Resultado',{
            'fields':('custo_do_kit','custo_de_material','custo_de_instalação','custo_de_engenharia','custo_de_representante','custo__de_comercial','custo_de_impostos',),
        }),
        ('Total',{
            'fields':('preco_format',),
        }),
    )

    def custo_do_kit(Self,obj):
        custo = obj.custo_kit
        return f'R$ {custo:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    def custo_de_material(self,obj):
        custo = obj.custo_material_total
        return f'R$ {custo:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    def custo_de_instalação(self,obj):
        custo = obj.instalacao
        return f'R$ {custo:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    def custo_de_engenharia(self,obj):
        custo = obj.custo_engenharia
        return f'R$ {custo:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    def custo_de_representante(self,obj):
        custo = (obj.comissao_rep/100)*obj.custoinstalacao
        return f'R$ {custo:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    def custo__de_comercial(self,obj):
        custo = (obj.comissao_com/100)*obj.custoinstalacao
        return f'R$ {custo:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    def custo_de_impostos(self,obj):
        custo = obj.custototal*obj.porc_imposto
        return f'R$ {custo:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    def preco_format(self,obj):
        return f'R$ {obj.custototaimp:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    preco_format.short_description = 'Custo Total'
    def nomecliente(self,obj):
        return obj.cliente.cliente
    nomecliente.short_description = 'Cliente'
    def uncons(self,obj):
        return obj.cliente.uncons
    uncons.short_description = 'Unidade Consumidora'
    