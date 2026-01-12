from django.db import models
from apps.cliente.models import Cliente
import math
from datetime import datetime
from django.utils import timezone
from calendar import monthrange
from django.core.validators import FileExtensionValidator
from apps.cliente.validators import validate_file_mimetype,validate_file_size
from apps.irradiacao.views import buscar_endereco_por_cep,buscar_irradiacao,irradiacao_mais_proxima

class Consumo(models.Model):
    STATUS_PROJETO = (
        ('1','Prospecção'),
        ('2','Captação de Documentos'),
        ('3','Captação de Dados'),
        ('4','Análise Técnica'),
        ('5','Orçamento'),
        ('6','Aprovação do Cliente'),
        ('7','Execução do Projeto'),
        ('8','Projeto Concluído'),
    )

    CONCESS = (
        ('L','LIGHT'),
        ('E','ENEL'),
    )

    CAT = (
        ('3','B3 - COMERCIAL'),
        ('1', 'B1 - RESIDENCIAL'),
    )

    NIVEL_TENSAO = (
        ('AT','ALTA TENSÃO'),
        ('BT','BAIXA TENSÃO'),
        ('MT','MÉDIA TENSÃO'),
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE,related_name='cliente_solar')
    uncons = models.CharField(null=False,blank=False,default='-----',verbose_name='Unidade Consumidora',max_length=20)
    concessionaria = models.CharField(null=False,blank=False,default='L',choices=CONCESS,verbose_name='Concessionária',max_length=20)
    lat = models.FloatField( verbose_name='Latitude (S)', null=True, blank=True)
    lon = models.FloatField( verbose_name='Longitude (O)', null=True, blank=True)
    cep = models.CharField(max_length=8,blank=False,null=False,verbose_name='CEP',default='-')
    logradouro = models.CharField(max_length=100,blank=True,null=True,verbose_name='Logradouro')
    numero = models.CharField(max_length=100,blank=True,null=True,verbose_name='Numero')
    bairro = models.CharField(max_length=100,blank=True,null=True,verbose_name='Bairro')
    cidade = models.CharField(max_length=100,blank=True,null=True,verbose_name='Cidade')
    uf = models.CharField(max_length=2,blank=True,null=True,verbose_name='Estado')
    cons_jan = models.IntegerField(default=0,verbose_name='Janeiro',null=False,blank=False)
    cons_fev = models.IntegerField(default=0,verbose_name='Fevereiro',null=False,blank=False)
    cons_mar = models.IntegerField(default=0,verbose_name='Março',null=False,blank=False)
    cons_abr = models.IntegerField(default=0,verbose_name='Abril',null=False,blank=False)
    cons_mai = models.IntegerField(default=0,verbose_name='Maio',null=False,blank=False)
    cons_jun = models.IntegerField(default=0,verbose_name='Junho',null=False,blank=False)
    cons_jul = models.IntegerField(default=0,verbose_name='Julho',null=False,blank=False)
    cons_ago = models.IntegerField(default=0,verbose_name='Agosto',null=False,blank=False)
    cons_set = models.IntegerField(default=0,verbose_name='Setembro',null=False,blank=False)
    cons_out = models.IntegerField(default=0,verbose_name='Outubro',null=False,blank=False)
    cons_nov = models.IntegerField(default=0,verbose_name='Novembro',null=False,blank=False)
    cons_dez = models.IntegerField(default=0,verbose_name='Dezembro',null=False,blank=False)
    etapa = models.CharField(verbose_name='Etapa do Projeto',choices=STATUS_PROJETO,max_length=1,default='1')
    categoria = models.CharField(verbose_name='Categoria do Empreendimento',choices=CAT,max_length=1,default='1')
    cadastro = models.DateTimeField(auto_now_add=True,verbose_name='Data de Cadastro')

    def format_concessionaria(self):
        cons = self.concessionaria.upper()
        self.concessionaria = cons
        return True

    def endereco_cep_local(self):
        endereco = buscar_endereco_por_cep(self.cep)

        if not endereco:
            return False

        if not self.logradouro:
            self.logradouro = endereco.get("logradouro", "")
        if not self.bairro:
            self.bairro = endereco.get("bairro", "")
        if not self.cidade:
            self.cidade = endereco.get("localidade", "")
        if not self.uf:
            self.uf = endereco.get("uf", "")

        return True
    
    @property
    def endereco(self):
        return f'{self.logradouro}, {self.numero} - {self.bairro}, {self.cidade} - {self.uf}, CEP: {self.cep}'

    @property
    def media_consumo(self):
        
        meses = [
            self.cons_jan,self.cons_fev,self.cons_mar,
            self.cons_abr,self.cons_mai,self.cons_jun,
            self.cons_jul,self.cons_ago,self.cons_set,
            self.cons_out,self.cons_nov,self.cons_dez
        ]
        return sum(meses)/12 if all(meses) else 0
    
    @property
    def consumo_ad_total(self):
        return sum(item.calculo_kwh for item in self.consumo_adicional.all())

    @property
    def consumo_total(self):
        return (self.consumo_ad_total + self.media_consumo)

    def __str__(self):
        if self.consumo_ad_total == 0:
            return f'{self.cliente.nome} - UC: {self.uncons} - Média: {self.media_consumo:.2f} kWh/mês'
        else:
            return f'{self.cliente.nome} - UC: {self.uncons} - Média: {self.consumo_total:.2f} kWh/mês'

    @property
    def consumo_mensal_total(self):
        cons = {
            'Janeiro': self.cons_jan + self.consumo_ad_total,'Fevereiro': self.cons_fev + self.consumo_ad_total,'Março': self.cons_mar + self.consumo_ad_total,
            'Abril': self.cons_abr + self.consumo_ad_total,'Maio': self.cons_mai + self.consumo_ad_total,'Junho': self.cons_jun + self.consumo_ad_total,
            'Julho': self.cons_jul + self.consumo_ad_total,'Agosto': self.cons_ago + self.consumo_ad_total,'Setembro': self.cons_set + self.consumo_ad_total,
            'Outubro': self.cons_out + self.consumo_ad_total,'Novembro': self.cons_nov + self.consumo_ad_total,'Dezembro': self.cons_dez + self.consumo_ad_total
        }
        return cons

    class Meta:
        verbose_name = 'Consumo Médio'
        verbose_name_plural = 'Consumos Médios'

class ConsumoAdicional(models.Model):
    TIPO = (
        ('1', 'Por kWh'),
        ('2', 'Por Watt'),
    )

    cliente = models.ForeignKey(Consumo,on_delete=models.CASCADE,related_name='consumo_adicional')
    tipo = models.CharField(max_length=1,choices=TIPO,verbose_name='Tipo de Envio (Watt ou kWh/mês)')
    equipamento = models.CharField(max_length=30,blank=False,null=False)
    potencia = models.FloatField(verbose_name='Potência ou Consumo')
    horas = models.FloatField(verbose_name='Tempo de Uso (H)')
    dias = models.IntegerField(verbose_name='Dias de Uso')

    @property
    def calculo_kwh(self):
        if None in (self.potencia,self.horas,self.dias):
            return 0
        else:
            if self.tipo == '1':
                potad = self.potencia*(self.dias/30)*(self.horas)
            else:
                potad = (self.potencia/1000)*(self.dias)*(self.horas)
            return potad
    
    def __str__(self):
        return f'Consumo de {self.equipamento}: {self.calculo_kwh:.2f} kWh/mês'
    
    class Meta:
        verbose_name = 'Consumo Adicional'
        verbose_name_plural = 'Consumos Adicionais'

class Irradiacao(models.Model):
    cliente = models.ForeignKey(Consumo,on_delete=models.CASCADE,related_name='consumo_irradiacao')
    irrad_anual = models.FloatField(default=0, verbose_name= 'Irradiação Anual', null=True,blank=True)
    irrad_jan = models.FloatField(default=0, verbose_name= 'Irradiação Janeiro', null=True,blank=True)
    irrad_fev = models.FloatField(default=0, verbose_name= 'Irradiação Fevereiro', null=True,blank=True)
    irrad_mar = models.FloatField(default=0, verbose_name= 'Irradiação Março', null=True,blank=True)
    irrad_abr = models.FloatField(default=0, verbose_name= 'Irradiação Abril', null=True,blank=True)
    irrad_mai = models.FloatField(default=0, verbose_name= 'Irradiação Maio', null=True,blank=True)
    irrad_jun = models.FloatField(default=0, verbose_name= 'Irradiação Junho', null=True,blank=True)
    irrad_jul = models.FloatField(default=0, verbose_name= 'Irradiação Julho', null=True,blank=True)
    irrad_ago = models.FloatField(default=0, verbose_name= 'Irradiação Agosto', null=True,blank=True)
    irrad_set = models.FloatField(default=0, verbose_name= 'Irradiação Setembro', null=True,blank=True)
    irrad_out = models.FloatField(default=0, verbose_name= 'Irradiação Outubro', null=True,blank=True)
    irrad_nov = models.FloatField(default=0, verbose_name= 'Irradiação Novembro', null=True,blank=True)
    irrad_dez = models.FloatField(default=0, verbose_name= 'Irradiação Dezembro', null=True,blank=True)

    def irrad_mes_local(self):
        irradiacao = irradiacao_mais_proxima(self.cliente.lat, self.cliente.lon)

        if not irradiacao:
            return False

        self.irrad_anual = irradiacao.get("ANNUAL", 0)
        self.irrad_jan = irradiacao.get("JAN", 0)
        self.irrad_fev = irradiacao.get("FEB", 0)
        self.irrad_mar = irradiacao.get("MAR", 0)
        self.irrad_abr = irradiacao.get("APR", 0)
        self.irrad_mai = irradiacao.get("MAY", 0)
        self.irrad_jun = irradiacao.get("JUN", 0)
        self.irrad_jul = irradiacao.get("JUL", 0)
        self.irrad_ago = irradiacao.get("AUG", 0)
        self.irrad_set = irradiacao.get("SEP", 0)
        self.irrad_out = irradiacao.get("OCT", 0)
        self.irrad_nov = irradiacao.get("NOV", 0)
        self.irrad_dez = irradiacao.get("DEC", 0)

        return True

    @property
    def media_irradi(self):
        meses = [
            self.irrad_jan,self.irrad_fev,self.irrad_mar,
            self.irrad_abr,self.irrad_mai,self.irrad_jun,
            self.irrad_jul,self.irrad_ago,self.irrad_set,
            self.irrad_out,self.irrad_nov,self.irrad_dez
        ]
        return sum(meses)/12 if all(meses) else self.irrad_anual
    
    def __str__(self):
        return f'Irradiação Média Anual: {self.media_irradi:.2f}'
        
    class Meta:
        verbose_name = 'Irradiação Média'
        verbose_name_plural = 'Irradiações Médias'

class PotGeracao(models.Model):
    cliente = models.ForeignKey(Cliente,on_delete=models.CASCADE,related_name='cliente_pger')
    irrad = models.ForeignKey(Irradiacao,on_delete=models.CASCADE, verbose_name='Irradiação',related_name='potger_irrad')
    consumo = models.ForeignKey(Consumo,on_delete=models.CASCADE,related_name='potger_consumo')
    rendimento = models.IntegerField(default=100, null=False, blank=False, verbose_name='Eficiência do Sistema %')
    
    @property
    def calculogeracao(self):
        if self.irrad.media_irradi == 0:
            return 0
        else:
            pger = (self.consumo.consumo_total)*1 / (30 * self.irrad.media_irradi * (self.rendimento / 100)) 
            return pger
    
    def __str__(self):
        return f'{self.cliente} - Potencia Mínima do Sistema: {round(self.calculogeracao,3)} kWp'
    
    class Meta:
        verbose_name = 'Potência de Geração Necessária'
        verbose_name_plural = 'Potências de Geração Necessárias'

class Paineis(models.Model):
    cliente = models.ForeignKey(Consumo,on_delete=models.CASCADE,related_name='consumo_paineis')
    potgeracao = models.ForeignKey(PotGeracao,on_delete=models.CASCADE,verbose_name='Potência de Geração',related_name='paineis_potger')
    potpainel = models.IntegerField(default=0,null=False,blank=False,verbose_name='Potencia do Painel (W)')
    areadisp = models.FloatField(default=0,null=False,blank=False,verbose_name='Area Disponivel')
    paineisdesejados = models.IntegerField(null=True,blank=True,verbose_name='Quantidade de Painéis Desejada')
    h = models.FloatField(default=0,null=False,blank=False,verbose_name='Comprimento do Painel')
    l = models.FloatField(default=0,null=False,blank=False,verbose_name='Largura do Painel')

    @property
    def calculopainel(self):
        if self.potpainel > 0:
            n_painel = math.ceil(self.potgeracao.calculogeracao/(self.potpainel/1000))
        else:
            n_painel = 0
        return n_painel
    
    @property
    def potenciasistema(self):
        potsis = self.calculopainel*self.potpainel/1000
        return potsis
    
    @property
    def area_min_necessaria(self):
        if self.h > 0 and self.l > 0:    
            a = self.calculopainel*((self.l+0.05)*(self.h+0.1))
        else:
            a = 0
        return a
    
    @property
    def area_necessaria_desj(self):
        if self.paineisdesejados:
            if self.h > 0 and self.l > 0:    
                a = self.paineisdesejados*((self.l+0.05)*(self.h+0.1))
            else:
                a = 0
        else:
            a = 0
        return a
    
    @property
    def painelareadisp(self):
        if self.h > 0 and self.l > 0:
            n_painel = math.floor(self.areadisp/((self.l+0.05)*(self.h+0.1)))
        else:
            n_painel = 0
        return n_painel
    
    @property
    def potsispaineldesejado(self):
        if self.paineisdesejados:
            potsis = self.paineisdesejados*self.potpainel/1000
        else:
            potsis = 0
        return potsis
    
    @property
    def potsisareadisp(self):
        potsis = self.painelareadisp*self.potpainel/1000
        return potsis
    
    @property
    def paineis(self):
        try:
            if self.areadisp < self.area_min_necessaria or self.areadisp < self.area_necessaria_desj:
                n_painel = self.painelareadisp
            elif self.area_necessaria_desj > 0:
                n_painel = self.paineisdesejados
            else:
                n_painel = self.calculopainel
        except (AttributeError, TypeError, ValueError):
            n_painel = 0
        return n_painel

    @property
    def potencia_sistema(self):
        try:
            if self.areadisp < self.area_min_necessaria or self.areadisp < self.area_necessaria_desj:
                potsis = self.potsisareadisp
            elif self.area_necessaria_desj > 0:
                potsis = self.potsispaineldesejado
            else:
                potsis = self.potenciasistema
        except (AttributeError, TypeError, ValueError):
            potsis = 0
        return potsis
    
    @property
    def area_sistema(self):
        try:
            if self.areadisp < self.area_min_necessaria or self.areadisp < self.area_necessaria_desj:
                area = ((self.l+0.05)*(self.h+0.1))*self.painelareadisp
            elif self.area_necessaria_desj > 0:
                area = self.area_necessaria_desj
            else:
                area = self.area_min_necessaria
        except (AttributeError, TypeError, ValueError):
            area = 0
        return area

    def __str__(self):
        try:
            if self.areadisp < self.area_min_necessaria or self.areadisp < self.area_necessaria_desj:
                potsis = self.potsisareadisp
            elif self.area_necessaria_desj > 0:
                potsis = self.potsispaineldesejado
            else:
                potsis = self.potenciasistema
        except (AttributeError, TypeError, ValueError):
            potsis = 0
        return f'Potencia do Sistema: {potsis} kWp'
    
    @property
    def area_painel(self):
        try:
            area = ((self.l+0.05)*(self.h+0.1))
        except (AttributeError, TypeError, ValueError):
            area = 0
        return area
    
    class Meta:
        verbose_name = 'Paineis Necessários'
        verbose_name_plural = 'Painéis Necessários'
    
class GerEsperada(models.Model):
    cliente = models.ForeignKey(Consumo, on_delete=models.CASCADE,related_name='consumo_geresp')
    potsis = models.ForeignKey(Paineis,on_delete=models.CASCADE,related_name='geresp_potsis',verbose_name='Potencia do Sistema')
    pger = models.ForeignKey(PotGeracao,on_delete=models.CASCADE, verbose_name='Potencia Necessária de Geração',related_name='geresp_rend')


    @property
    def geresperada(self):
        
        irradiancias = [
            float(self.pger.irrad.irrad_jan), float(self.pger.irrad.irrad_fev), float(self.pger.irrad.irrad_mar),
            float(self.pger.irrad.irrad_abr), float(self.pger.irrad.irrad_mai), float(self.pger.irrad.irrad_jun),
            float(self.pger.irrad.irrad_jul), float(self.pger.irrad.irrad_ago), float(self.pger.irrad.irrad_set),
            float(self.pger.irrad.irrad_out), float(self.pger.irrad.irrad_nov), float(self.pger.irrad.irrad_dez),
        ]
        # dias_mes = [
        #     31, 28, 31,
        #     30, 31, 30,
        #     31, 31, 30,
        #     31, 30, 31,
        # ]
        year = timezone.now().year
        dias_mes = [monthrange(year, m)[1] for m in range(1, 13)]

        meses = [
            'Janeiro', 'Fevereiro', 'Março',
            'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro',
            'Outubro', 'Novembro', 'Dezembro',
        ]
        ger_mensal = {}
        for mes, irradiancia, dia in zip(meses, irradiancias, dias_mes):
            try:
                if self.potsis.areadisp < self.potsis.area_min_necessaria or self.potsis.areadisp < self.potsis.area_necessaria_desj:
                    pot_sistema = float(self.potsis.potsisareadisp)
                    ger = (irradiancia * dia * pot_sistema * self.pger.rendimento) / 100
                elif self.potsis.area_necessaria_desj > 0:
                    pot_sistema = float(self.potsis.potsispaineldesejado)
                    ger = (irradiancia * dia * pot_sistema * self.pger.rendimento) / 100
                else:
                    pot_sistema = float(self.potsis.potenciasistema)
                    ger = (irradiancia * dia * pot_sistema * self.pger.rendimento) / 100
            except (AttributeError, TypeError, ValueError):
                ger = 0
            ger_mensal.update({mes: ger})
        return ger_mensal
    
    @property
    def dic_consumo(self):
        meses = [
            'Janeiro', 'Fevereiro', 'Março',
            'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro',
            'Outubro', 'Novembro', 'Dezembro',
        ]
        consumo = [
            float(self.cliente.cons_jan + self.cliente.consumo_ad_total),float(self.cliente.cons_fev + self.cliente.consumo_ad_total),float(self.cliente.cons_mar + self.cliente.consumo_ad_total),
            float(self.cliente.cons_abr + self.cliente.consumo_ad_total),float(self.cliente.cons_mai + self.cliente.consumo_ad_total),float(self.cliente.cons_jun + self.cliente.consumo_ad_total),
            float(self.cliente.cons_jul + self.cliente.consumo_ad_total),float(self.cliente.cons_ago + self.cliente.consumo_ad_total),float(self.cliente.cons_set + self.cliente.consumo_ad_total),
            float(self.cliente.cons_out + self.cliente.consumo_ad_total),float(self.cliente.cons_nov + self.cliente.consumo_ad_total),float(self.cliente.cons_dez + self.cliente.consumo_ad_total)
        ]

        cons = {}
        for mes,valor in zip(meses,consumo):
            cons.update({mes: valor})
        return cons
        
    @property
    def saldo_esperado(self):
        saldo_esp = {}
        for chave,valor in self.dic_consumo.items():
            valor_geresp = self.geresperada[chave]
            credito = valor_geresp - valor
            saldo_esp.update({chave: credito})
        return saldo_esp

    @property
    def media_saldo(self):
        dados_mensais = self.saldo_esperado.values()
        if not dados_mensais:
            return 0
        return sum(dados_mensais)/len(dados_mensais)

    @property
    def media_geresp(self):
        dados_mensais = self.geresperada.values()
        if not dados_mensais: 
            return 0
        return sum(dados_mensais)/len(dados_mensais)

    
    def __str__(self):
        return f"Geracao Prevista para {self.cliente.cliente} - {self.media_geresp:.2f} kWh/mês"
    
    class Meta:
        verbose_name = 'Geração Esperada do Sistema'
        verbose_name_plural = 'Gerações Esperadas dos Sistemas'

def get_upload_path(instance,filename):
    data_nome = datetime.now().strftime("%Y-%m-%d")
    filename = f"{instance.cliente.cliente} - {instance.tipo} {data_nome} - {filename}"
    return f"uploads/solar/{instance.cliente.cliente.tipo}/{instance.cliente.cliente}/UC-[{instance.cliente.uncons}]/{instance.tipo}/{data_nome}/{filename}"

class ArquivosUnidadeConsumidora(models.Model):
    TIPO = (
        ('Conta de Luz', 'Conta de Luz'),
        ('Planta de Localização', 'Planta de Localização'),
        ('Disposição dos Paineis', 'Disposição dos Paineis'),
        ('Diagrama Unifilar', 'Diagrama Unifilar'),
        ('Diagrama Trifilar', 'Diagrama Trifilar'),
        ('Mapa de Strings', 'Mapa de Strings'),
        ('Planta do Imóvel', 'Planta do Imóvel'),
        ('ART do Projeto', 'ART do Projeto'),
        ('Memorial Descritivo', 'Memorial Descritivo'),
        ('Registro INMETRO', 'Registro INMETRO'),
        ('Procuração', 'Procuração'),
        ('Documento do Cliente', 'Documento do Cliente'),
        ('Formulário de Solicitação', 'Formulário de Solicitação'),
        ('Proposta', 'Proposta'),
        ('Contrato Assinado', 'Contrato Assinado'),
        ('Orçamento', 'Orçamento'),
        ('Fotos', 'Fotos'),
        ('Outros', 'Outros'),
    )
    tipo = models.CharField(max_length=100,choices=TIPO,verbose_name='Tipo de Arquivo',default='Conta de Luz')
    cliente = models.ForeignKey(Consumo, on_delete=models.CASCADE,related_name='consumo_files')
    arquivo = models.FileField(
        upload_to=get_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'gif','dwg']),
            validate_file_mimetype,
            validate_file_size
        ],
        verbose_name="Arquivos"
    )
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.cliente.cliente.nome} - [UC {self.cliente.uncons}] - [Upload: {self.data_upload.date()}]"

class EnergiaProduzida(models.Model):
    cliente = models.ForeignKey(GerEsperada, on_delete=models.CASCADE,related_name='geresp_Eprod')

    eprod_jan = models.FloatField(default=0,verbose_name='Janeiro',null=False,blank=False)
    eprod_fev = models.FloatField(default=0,verbose_name='Fevereiro',null=False,blank=False)
    eprod_mar = models.FloatField(default=0,verbose_name='Março',null=False,blank=False)
    eprod_abr = models.FloatField(default=0,verbose_name='Abril',null=False,blank=False)
    eprod_mai = models.FloatField(default=0,verbose_name='Maio',null=False,blank=False)
    eprod_jun = models.FloatField(default=0,verbose_name='Junho',null=False,blank=False)
    eprod_jul = models.FloatField(default=0,verbose_name='Julho',null=False,blank=False)
    eprod_ago = models.FloatField(default=0,verbose_name='Agosto',null=False,blank=False)
    eprod_set = models.FloatField(default=0,verbose_name='Setembro',null=False,blank=False)
    eprod_out = models.FloatField(default=0,verbose_name='Outubro',null=False,blank=False)
    eprod_nov = models.FloatField(default=0,verbose_name='Novembro',null=False,blank=False)
    eprod_dez = models.FloatField(default=0,verbose_name='Dezembro',null=False,blank=False)

    class Meta:
        verbose_name = 'Energia Produzida'
        verbose_name_plural = 'Energias Produzidas'

    @property
    def comparativo_prod_esp(self):
        dados_esperados = self.cliente.geresperada
        dados_reais = [
            self.eprod_jan,self.eprod_fev,self.eprod_mar,
            self.eprod_abr,self.eprod_mai,self.eprod_jun,
            self.eprod_jul,self.eprod_ago,self.eprod_set,
            self.eprod_out,self.eprod_nov,self.eprod_dez
        ]
        meses = [
            'Janeiro', 'Fevereiro', 'Março',
            'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro',
            'Outubro', 'Novembro', 'Dezembro',
        ]
        ger_real = {}

        for mes,ger in zip(meses,dados_reais):
            ger_real.update({mes: ger})
        
        result = {}
        for chave,valor in dados_esperados.items():
            valor_real = ger_real[chave]
            sub = valor - valor_real
            result.update({chave: sub})
        return result

    def __str__(self):
        return 'Energia Produzida'

class CustoMaterial(models.Model):

    UNID = (
        ('M','Metros'),
        ('U','Unidade'),
        ('P','Peso'),
    )

    cliente = models.ForeignKey(Consumo,on_delete=models.CASCADE,related_name='equip_solar',verbose_name='Cliente')
    equip = models.CharField(verbose_name='Material',null=False,blank=False,max_length=50)
    qnt = models.FloatField(verbose_name='Quantidade do Material',null=False,blank=False)
    unid = models.CharField(verbose_name='Grandeza da Unidade',choices=UNID,default='U',max_length=1)
    preco_unit = models.FloatField(verbose_name='Preço Unitário',null=False,blank=False)
    preco_tot = models.FloatField(verbose_name='Preço Total',null=False,blank=False,default=0)
    
    @property
    def preco_calculado(self):
        if self.qnt is None or self.preco_unit is None:
            return 0
        preco_tot = self.preco_tot or 0
        preco_calc = self.qnt * self.preco_unit

        if preco_tot > 0:
            return max(preco_calc, preco_tot)

        return preco_calc

    @property
    def preco_formatado(self):
        return f'R$ {self.preco_calculado:.2f}'

    def __str__(self):
        return f'{self.equip}: {self.preco_formatado} '
    
    class Meta:
        verbose_name = 'Custo do Material'
        verbose_name_plural = 'Custo dos Materiais'

class CustosNegocio(models.Model):
    paineis_herd = models.ForeignKey(Paineis,on_delete=models.CASCADE,related_name='paineis_negocio',verbose_name='Potencia de Instalação')
    custo_kit = models.FloatField(verbose_name='Custo Kit Usina Solar', blank=False,null=False)
    custo_material = models.ManyToManyField(CustoMaterial,verbose_name='Materiais',related_name='negocio_material')
    mao_obra = models.FloatField(verbose_name='Custo Mão de Obra por Painel', blank=False,null=False,default=250)
    margem = models.IntegerField(verbose_name='Margem de Lucro',blank=False,null=False,default=30)
    engenharia = models.IntegerField(verbose_name='Custo Engenharia por Painel',blank=False,null=False,default=100)
    comissao_rep = models.IntegerField(verbose_name='Comissão Representante',blank=False,null=False,default=3)
    comissao_com = models.IntegerField(verbose_name='Comissão Comercial',blank=False,null=False,default=2)
    imposto = models.IntegerField(verbose_name='Impostos',blank=False,null=False,default=10)
    cliente = models.ForeignKey(Consumo,on_delete=models.CASCADE,related_name='consumo_negocio',verbose_name='Consumo')
    art = models.FloatField(verbose_name='Custo da ART', blank=False,null=False,default=271.47)

    def __str__(self):
        custo = f'{self.custototaimp:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        return f'Custo do Negócio: R$ {custo}'

    @property
    def custo_material_total(self):
        try:
            total = 0
            for custo in self.custo_material.all():
                total+= custo.preco_calculado
        except:
            total = 0
        return total
    @property
    def paineis(self):
        return self.paineis_herd.paineis

    @property
    def instalacao(self):
        return (self.mao_obra*self.paineis) or 0

    @property
    def custo_engenharia(self):
        return (self.engenharia*self.paineis + self.art) or 0

    @property
    def mao_de_obra(self):
        return self.instalacao + self.custo_engenharia

    @property
    def porc_imposto(self):
        try:
            return self.imposto/100
        except:
            return 10/100
        
    @property
    def custoinstalacao(self):
        try:
            custo = self.custo_kit + self.custo_material_total + self.instalacao + self.custo_engenharia
        except:
            custo = 0
        return custo
    
    @property
    def custototal(self):
        custoinst = self.custoinstalacao
        com_rep = self.comissao_rep/100
        com_com = self.comissao_com/100
        try:
            custo = (custoinst + custoinst*com_com + com_rep*custoinst)*(1+self.margem/100)
            total = custo + (custo*self.porc_imposto)
        except:
            custo = 0
        return custo
    
    @property
    def custototaimp(self):
        try:
            return self.custototal*(1+self.porc_imposto)
        except:
            return 0



class EcoProjetada(models.Model):
    def ano_atual():
        return str(timezone.now().year)
    
    geracao = models.ForeignKey(GerEsperada,on_delete=models.CASCADE,related_name='economia_geracao',verbose_name='Geração Esperada')
    material = models.ManyToManyField(CustoMaterial,verbose_name='Materiais',related_name='economia_materia')
    tarifa_el = models.FloatField(verbose_name='Valor Tarifa Elétrica (R$/kWh)',blank=False,null=False)
    ilum_public = models.FloatField(verbose_name='Valor Iluminação Publica',blank=False,null=False)
    fiob = models.IntegerField(verbose_name='Porcentagem Fio B (Lei 14.300/2022)',blank=False,null=False,default=60)
    cliente =  models.ForeignKey(Consumo,on_delete=models.CASCADE,related_name='economia_geracao',verbose_name='Consumo')
    ano_op = models.CharField(verbose_name='Ano de operação da Usina', max_length=4,default=ano_atual())
    custo_negocio = models.ForeignKey(CustosNegocio,on_delete=models.CASCADE,related_name='economia_negocio',verbose_name='Custos do Negocio')

    @property
    def custo_material_total(self):
        # total = 0
        # for custo in self.material.all():
        #     total+= custo.preco_calculado
        total = self.custo_negocio.custo_material_total
        return total
    
    @property
    def tusd_fiob(self):
        tusdB = 0
        if self.cliente.concessionaria == 'L':
            if self.cliente.categoria == ' 1':
                tusdB =  0.163
            else:
                tusdB =  0.184
        else:
            if self.cliente.categoria == ' 1':
                tusdB =  0.189
            else:
                tusdB =  0.201
        return tusdB
    

    def lista_material(self):
        material = self.custo_negocio
        try:
            custo_kit = material.custo_kit or 0
            mao_obra = material.mao_obra or 0
            custo_material_total = self.custo_material_total or 0
            margem = material.margem or 0

            preco_kit = custo_kit + ((custo_kit + mao_obra + custo_material_total) * (margem / 100))

            lista = [
                ('Kit de Geração', 1.0, 'Unidade', preco_kit, preco_kit),
                ('Mão de Obra',      1.0, 'Unidade', mao_obra, mao_obra),
            ]

            for material in material.custo_material.all():
                equip = material.equip or ''
                qnt = material.qnt or 0
                unid = material.get_unid_display()
                preco_unit = material.preco_unit or 0
                preco_tot = material.preco_calculado or 0
                lista.append((equip, qnt, unid, preco_unit, preco_tot))
        except (TypeError, ValueError):
            lista = ["","","","",""]
        return lista

    @property
    def calculo_retorno(self):
        incremento = 1
        retorno = - self.custo_negocio.custototaimp
        try:
            ano = int(self.ano_op)
        except (TypeError, ValueError):
            ano = timezone.now().year
        retorno_lista = {}
        tabela = [
            (2023,0.15),
            (2024,0.3),
            (2025,0.45),
            (2026,0.6),
            (2027,0.75),
            (2028,0.9),
            (float('inf'), 1)
        ]
        tarifa_el = self.tarifa_el
        while retorno <= 0:
            for ano_lei,fator in tabela:
                if ano <= ano_lei:
                    fator = fator
            retorno_lista.update({ano: retorno})
            retorno += (12*self.geracao.media_geresp*tarifa_el*(1 - self.tusd_fiob*fator))
            ano += 1
            incremento += 1
            tarifa_el = tarifa_el*1.1
        retorno_lista.update({ano: retorno})

        return retorno_lista,incremento
    
    @property
    def retorno(self):
        try:
            retorno,_ = self.calculo_retorno
        except (TypeError, ValueError):
            retorno = 0
        return retorno
    @property
    def anos_retorno(self):
        try:
            _ ,anos = self.calculo_retorno
        except (TypeError, ValueError):
            anos = '-'
        return anos   

    @property
    def proj_25anos(self):
        try:
            incremento = 1
            retorno = -self.custo_negocio.custototaimp
            try:
                ano = int(self.ano_op)
            except (TypeError, ValueError):
                ano = timezone.now().year
            retorno_lista = {}
            tabela = [
                (2023,0.15),
                (2024,0.3),
                (2025,0.45),
                (2026,0.6),
                (2027,0.75),
                (2028,0.9),
                (float('inf'), 1)
            ]
            tarifa_el = self.tarifa_el
            while incremento <= 25:
                for ano_lei,fator in tabela:
                    if ano <= ano_lei:
                        fator = fator
                retorno_lista.update({ano: retorno})
                retorno += (12*self.geracao.media_geresp*tarifa_el*(1 - self.tusd_fiob*fator))
                ano += 1
                incremento += 1
                tarifa_el = tarifa_el*1.1
            retorno_lista.update({ano: retorno})
        except (TypeError, ValueError):
            retorno_lista = {"-": "-"}
        return retorno_lista
    
    @property
    def proj_anual_25anos(self):
        try:    
            incremento = 1
            try:
                ano = int(self.ano_op)
            except (TypeError, ValueError):
                ano = timezone.now().year
            retorno_lista = {}
            tabela = [
                (2023,0.15),
                (2024,0.3),
                (2025,0.45),
                (2026,0.6),
                (2027,0.75),
                (2028,0.9),
                (float('inf'), 1)
            ]
            tarifa_el = self.tarifa_el
            retorno = (12*self.geracao.media_geresp*tarifa_el*(1 - self.tusd_fiob*self.fiob/100))
            while incremento <= 25:
                retorno_lista.update({ano: retorno})
                for ano_lei,i in tabela:
                    if ano <= ano_lei:
                        fator = i
                        break
                ano += 1
                incremento += 1
                tarifa_el = tarifa_el*1.1
                retorno = (12*self.geracao.media_geresp*tarifa_el*(1 - self.tusd_fiob*fator))
            retorno_lista.update({ano: retorno})
        except (TypeError, ValueError):
            retorno_lista = {"-": "-"}
        return retorno_lista

    class Meta:
        verbose_name = 'Retorno Projetado'
        verbose_name_plural = 'Retornos Projetados'

