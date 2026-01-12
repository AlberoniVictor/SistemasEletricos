from django.db import models
import math
from apps.cliente.models import Cliente
from apps.irradiacao.views import buscar_endereco_por_cep
from django.core.validators import FileExtensionValidator
from apps.cliente.validators import validate_file_mimetype,validate_file_size
from datetime import datetime

class Local(models.Model):
    '''Modelo para os locais de instalação do cliente'''

    TENSAO = (
        ("1","127/220 V"),
        ("2","220/380 V"),
    )

    TIPO_REDE = (
        ('M','Monofásica'),
        ('B','Bifásica'),
        ('T','Trifásica'),
        ('N','Instalação Nova')
    )

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

    cliente = models.ForeignKey(Cliente,on_delete=models.CASCADE,verbose_name='Cliente',related_name='cliente_local', db_index=True)
    local = models.CharField(verbose_name='Identificação do local',max_length=100, db_index=True)
    cep = models.CharField(max_length=8,blank=False,null=False,verbose_name='CEP',default='-', db_index=True)
    logradouro = models.CharField(max_length=100,blank=True,null=False,verbose_name='Logradouro')
    numero = models.CharField(max_length=100,blank=True,null=False,verbose_name='Numero')
    bairro = models.CharField(max_length=100,blank=True,null=False,verbose_name='Bairro')
    cidade = models.CharField(max_length=100,blank=True,null=False,verbose_name='Cidade')
    uf = models.CharField(max_length=2,blank=True,null=False,verbose_name='Estado')
    rede = models.CharField(verbose_name='Alimentação Concessionária',choices=TENSAO,default='1',max_length=1)
    tipo_rede = models.CharField(verbose_name='Tipo de Rede',max_length=1,blank=False,null=False,choices=TIPO_REDE,default='N')
    etapa = models.CharField(verbose_name='Etapa do Projeto',choices=STATUS_PROJETO,max_length=1,default='1')
    cadastro = models.DateTimeField(auto_now_add=True,verbose_name='Data de Cadastro')

    class Meta:
        verbose_name = 'Local'
        verbose_name_plural = 'Locais'

    def __str__(self):
        return self.local
    
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

class Ambientes(models.Model):
    '''Modelo para os ambientes do local de instalação'''
    COMODOS = (
        ('Q', 'Quarto'),
        ('S', 'Salas'),
        ('B', 'Banheiro'),
        ('C', 'Cozinha, Copas, Lavanderias'),
        ('O', 'Escritório'),
        ('E', 'Área Externa'),
        ('V', 'Varanda'),
        ('H', 'Corredores'),
    )

    local = models.ForeignKey(Local, on_delete=models.CASCADE, related_name='local_ambiente')
    comodo = models.CharField(verbose_name='Ambiente', max_length=100)
    t_comodo = models.CharField(verbose_name='Tipo de Ambiente', choices=COMODOS, default='S', max_length=1)
    perimetro = models.FloatField(verbose_name='Perimetro do Ambiente', blank=False, null=False)
    area = models.FloatField(verbose_name='Área do Ambiente', blank=False, null=False)
    tug = models.IntegerField(default=0, verbose_name='Qnt. TUGs Propostas', blank=False, null=False)
    tue = models.IntegerField(default=0, verbose_name='Qnt. TUEs Propostas', blank=False, null=False)
    iluminacao = models.IntegerField(default=0, verbose_name='Pontos de Iluminação Propostas', blank=False, null=False)

    class Meta:
        verbose_name = 'Ambiente'
        verbose_name_plural = 'Ambientes'

    def __str__(self):
        return f'{self.comodo} - {self.local}'

class CargasTUG(models.Model):
    '''Modelo para as cargas de tomadas de uso geral (TUG)'''
    comodo = models.ForeignKey(Ambientes, on_delete=models.CASCADE, related_name='cargas_tug')

    class Meta:
        verbose_name = 'Carga TUG'
        verbose_name_plural = "Cargas TUG's"

    @property
    def calculo_tug(self):
        if self.comodo.t_comodo == 'B':
            tug = 1
        elif self.comodo.t_comodo == 'C':
            tug = math.ceil(self.comodo.perimetro / 3.5)
        elif self.comodo.t_comodo == 'V':
            tug = 1
        elif self.comodo.t_comodo == 'E':
            tug = 1
        elif self.comodo.t_comodo in ('Q', 'S'):
            tug = math.ceil(self.comodo.perimetro / 5)
        else:
            if self.comodo.area <= 6:
                tug = 1
            else:
                tug = math.ceil(self.comodo.perimetro / 5)

        if self.comodo.tug > tug:
            tug = self.comodo.tug

        return tug

    @property
    def tug_final(self):
        return self.calculo_tug

    @property
    def calculo_pot_tug(self):
        efetivo = self.tug_final
        if self.comodo.t_comodo in ('C', 'B', 'E'):
            if efetivo <= 3:
                pot_tug = efetivo * 600
            else:
                pot_tug = (3 * 600) + (efetivo - 3) * 100
        else:
            pot_tug = efetivo * 100

        grand = 'VA'
        return pot_tug, grand

    @property
    def conv_pot_tug(self):
        pot_va, grand = self.calculo_pot_tug
        if pot_va:
            pot_w = pot_va * 0.80
        else:
            pot_w = 0
        grand = 'W'
        return pot_w, grand
    
    @property
    def pot_tug(self):
        pot, _ = self.calculo_pot_tug
        return pot

    def __str__(self):
        pot, grand = self.calculo_pot_tug
        return f'Potência TUG - {self.comodo}: {pot:.2f} {grand}'

class CargasILUM(models.Model):
    '''Modelo para as cargas de Iluminação'''
    comodo = models.ForeignKey(Ambientes, on_delete=models.CASCADE, related_name='cargas_ilum')

    class Meta:
        verbose_name = 'Carga de Iluminação'
        verbose_name_plural = 'Cargas de Iluminação'

    @property
    def calculo_ilum(self):
        if self.comodo.t_comodo == 'E':
            ilum = 1
        elif self.comodo.area <= 6:
            ilum = 1
        else:
            ilum = int(1 + math.floor((self.comodo.area - 6) / 4))
        return ilum

    @property
    def calculo_pot_ilum(self):
        N = max(self.comodo.iluminacao, self.calculo_ilum)
        pot_ilum = 100 + (N - 1) * 60
        grand = 'VA'
        return pot_ilum, grand

    @property
    def conv_pot_ilum(self):
        pot_va, grand = self.calculo_pot_ilum
        if pot_va:
            pot_w = pot_va * 0.92
        else:
            pot_w = 0
        grand = 'W'
        return pot_w, grand

    def __str__(self):
        pot, grand = self.calculo_pot_ilum
        return f'Iluminação - {self.comodo}: {pot:.2f} {grand}'

class CargasTUE(models.Model):
    '''Modelo para as cargas de equipamentos de uso especifico (TUE)'''
    TIPOS_CARGAS = (
        ('R', 'Aquecimento'),
        ('A', 'Ar Condicionados Janela/Split'),
        ('B', 'Ar Condicionado Central'),
        ('M', 'Motores'),
        ('S', 'Maq. Solda a Trafo, equip. Odonto-Medico Hopitalares'),
    )
    TIPO_POT = (
        ('W', 'Watts'),  # Watts/0.92 = VA
        ('V', 'VA'),
    )

    comodo = models.ForeignKey(Ambientes, on_delete=models.CASCADE, related_name='cargas_tue')
    t_pot = models.CharField(default='V', verbose_name='Watts ou VA', blank=True, null=True, max_length=1, choices=TIPO_POT)
    pot_tue = models.IntegerField(default=0, verbose_name='Potencia TUE', blank=False, null=False)
    t_carga = models.CharField(default='R', verbose_name='Tipos de Cargas', blank=True, null=True, max_length=1, choices=TIPOS_CARGAS)
    carga = models.CharField(verbose_name='Descritivo da Carga', max_length=100)

    class Meta:
        verbose_name = 'Carga de TUE'
        verbose_name_plural = "Cargas de TUE's"

    @property
    def potencia(self):
        if self.pot_tue:
            if self.t_carga == 'R':
                pot = self.pot_tue * 1
                grand = 'VA'
            elif self.t_pot == 'W':
                if self.t_carga == 'M':
                    pot = self.pot_tue / 0.85
                    grand = 'VA'
                else:
                    pot = self.pot_tue / 0.92
                    grand = 'VA'
            else:
                pot = self.pot_tue
                grand = 'VA'
        else:
            pot = 0
            grand = 'VA'
        return pot, grand

    @property
    def conv_pot_tue(self):
        pot, grand = self.potencia
        if self.t_carga == 'R':
            pot_conv = pot * 1
            grand = 'W'
        elif grand == 'VA':
            if self.t_carga == 'M':
                pot_conv = pot * 0.85
                grand = 'W'
            else:
                pot_conv = pot * 0.92
                grand = 'W'
        return pot_conv, grand
    @property
    def pot_tue_w(self):
        pot, grand = self.conv_pot_tue
        return pot

    def __str__(self):
        pot, grand = self.potencia
        return f'{self.carga} - {self.comodo} {pot:.2f} {grand}'

class Circuitos(models.Model):
    '''Modelo para os circuitos elétricos'''
    CKT = (
        ("M", "Monofásico"),
        ("B", "Bifásico"),
        ("T", "Trifásico"),
    )
    ambiente = models.ForeignKey(Local, on_delete=models.CASCADE, related_name='ckt_local', verbose_name='Local')
    tug = models.ManyToManyField(CargasTUG, related_name='ckt_tug', blank=True, verbose_name='Cargas TUGs')
    tue = models.ManyToManyField(CargasTUE, related_name='ckt_tue', blank=True, verbose_name='Cargas TUEs')
    ilum = models.ManyToManyField(CargasILUM, related_name='ckt_ilum', blank=True, verbose_name='Cargas de Iluminação')
    nome = models.CharField(verbose_name='Identificação do Circuito', max_length=50, default="")
    ckt = models.CharField(verbose_name='Tipo do Circuito', choices=CKT, default='M', max_length=1)

    class Meta:
        verbose_name = 'Circuito'
        verbose_name_plural = 'Circuitos'

    def __str__(self):
        return f'{self.nome} - {self.ambiente}'

    @property
    def soma_tug_va(self):
        total = 0
        for carga in self.tug.all():
            pot, unidade = carga.calculo_pot_tug
            if unidade == 'VA':
                total += pot
        return total

    @property
    def soma_tug_w(self):
        total = 0
        for carga in self.tug.all():
            pot, unidade = carga.conv_pot_tug
            if unidade == 'W':
                total += pot
        return total

    @property
    def soma_tue_va(self):
        total = 0
        for carga in self.tue.all():
            pot, unidade = carga.potencia
            if unidade == 'VA':
                total += pot
        return total

    @property
    def soma_tue_w(self):
        total = 0
        for carga in self.tue.all():
            pot, unidade = carga.conv_pot_tue
            if unidade == 'W':
                total += pot
        return total

    @property
    def soma_ilum_va(self):
        total = 0
        for carga in self.ilum.all():
            pot, unidade = carga.calculo_pot_ilum
            if unidade == 'VA':
                total += pot
        return total

    @property
    def soma_ilum_w(self):
        total = 0
        for carga in self.ilum.all():
            pot, unidade = carga.conv_pot_ilum
            if unidade == 'W':
                total += pot
        return total

    @property
    def total_va(self):
        total = 0
        if self.tug.exists():
            total += self.soma_tug_va
        if self.tue.exists():
            total += self.soma_tue_va
        if self.ilum.exists():
            total += self.soma_ilum_va
        return total

    @property
    def total_w(self):
        total = 0
        if self.tug.exists():
            total += self.soma_tug_w
        if self.tue.exists():
            total += self.soma_tue_w
        if self.ilum.exists():
            total += self.soma_ilum_w
        return total

    def tensao_sist(self):
        # mapeamento direto com ifs (mantido estilo original)
        if self.ambiente.rede == '1':
            if self.ckt == 'M':
                v = 127
            elif self.ckt == 'B':
                v = 220
            elif self.ckt == 'T':
                v = 220
        elif self.ambiente.rede == '2':
            if self.ckt == 'M':
                v = 220
            elif self.ckt == 'B':
                v = 380
            elif self.ckt == 'T':
                v = 380
        else:
            v = 0
        return v

    @property
    def corrente_ckt(self):
        fp = self.total_w / self.total_va if self.total_va else 1
        pot = self.total_va
        raiz3 = 3 ** 0.5
        v = self.tensao_sist()
        if not v:
            return 0
        if self.ckt in ('M', 'B'):
            i = pot / (v * fp)
        elif self.ckt == 'T':
            i = pot / (raiz3 * v * fp)
        else:
            i = 0
        return i

class Demandas(models.Model):
    '''Modelo para o cálculo de demandas elétricas'''
    local = models.ForeignKey(Local, on_delete=models.CASCADE, related_name='demanda_local')
    tue = models.ManyToManyField(CargasTUE, related_name='demanda_tue', blank=True, verbose_name='Cargas TUEs')
    ilum = models.ManyToManyField(CargasILUM, related_name='demanda_ilum', blank=True, verbose_name='Cargas de Iluminação')
    tug = models.ManyToManyField(CargasTUG, related_name='demanda_tug', blank=True, verbose_name='Cargas TUGs')

    class Meta:
        verbose_name = 'Demanda'
        verbose_name_plural = "Demandas"

    def __str__(self):
        return f'Demanda para {self.local} - {self.demanda_total:.2f} kVA'

    @property
    def filtra_motor(self):
        qnt = 0
        total = 0
        unid = 'VA'
        filtro = self.tue.filter(t_carga='M')
        for motor in filtro:
            qnt += 1
            pot, unid = motor.potencia
            total += pot
        return total, qnt, unid

    @property
    def demanda_motor(self):
        pot, qnt, unid = self.filtra_motor
        fatores = [1.00, 0.75, 0.6333, 0.5750, 0.54, 0.50, 0.4714, 0.45, 0.4333, 0.42]
        indice = min(max(qnt, 1), 10) - 1
        fator = fatores[indice]
        dem = (pot * fator) / 1000
        unid = 'kVA'
        return dem, unid

    @property
    def filtra_resist(self):
        qnt = 0
        total = 0
        unid = 'VA'
        filtro = self.tue.filter(t_carga='R')
        for resist in filtro:
            qnt += 1
            pot, unid = resist.potencia
            total += pot
        return total, qnt, unid

    @property
    def demanda_resist(self):
        pot, qnt, unid = self.filtra_resist
        fatores = [1.00, 0.75, 0.70, 0.66, 0.62, 0.59, 0.56, 0.53, 0.51, 0.49, 0.47, 0.45, 0.43, 0.41, 0.40, 0.39, 0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.32, 0.31, 0.30]
        indice = min(max(qnt, 1), 25) - 1
        fator = fatores[indice]
        dem = (pot * fator) / 1000
        unid = 'kVA'
        return dem, unid

    @property
    def filtra_ac(self):
        qnt = 0
        total = 0
        unid = 'VA'
        filtro = self.tue.filter(t_carga='A')
        for ac in filtro:
            qnt += 1
            pot, unid = ac.potencia
            total += pot
        return total, qnt, unid

    @property
    def demanda_ac(self):
        pot, qnt, unid = self.filtra_ac
        unid = 'kVA'
        tabela = [(4, 1.00),
                  (10, 0.70),
                  (20, 0.60),
                  (30, 0.55),
                  (40, 0.53),
                  (50, 0.53),
                  (float('inf'), 0.50)
                  ]
        for limite, fator in tabela:
            if qnt <= limite:
                dem = (pot * fator) / 1000
                break
        return dem, unid

    @property
    def filtra_ac_central(self):
        qnt = 0
        total = 0
        unid = 'VA'
        filtro = self.tue.filter(t_carga='B')
        for ac in filtro:
            qnt += 1
            pot, unid = ac.potencia
            total += pot
        return total, qnt, unid

    @property
    def demanda_ac_central(self):
        pot, qnt, unid = self.filtra_ac_central
        unid = 'kVA'
        tabela = [(10, 1.00),
                  (20, 0.75),
                  (30, 0.70),
                  (40, 0.65),
                  (50, 0.60),
                  (80, 0.55),
                  (float('inf'), 0.50)
                  ]
        for limite, fator in tabela:
            if qnt <= limite:
                dem = (pot * fator) / 1000
                break
        return dem, unid

    @property
    def filtra_trafo(self):
        qnt = 0
        total = 0
        unid = 'VA'
        filtro = self.tue.filter(t_carga='S')
        for trafo in filtro:
            qnt += 1
            pot, unid = trafo.potencia
            total += pot
        return total, qnt, unid

    @property
    def demanda_trafo(self):
        pot, qnt, unid = self.filtra_trafo
        fatores = [1.00, 0.75, 0.6333, 0.5750, 0.54, 0.50, 0.4714, 0.45, 0.4333, 0.42]
        indice = min(max(qnt, 1), 10) - 1
        fator = fatores[indice]
        dem = (pot * fator) / 1000
        unid = 'kVA'
        return dem, unid

    @property
    def soma_ilum_va(self):
        qnt = 0
        total = 0
        for carga in self.ilum.all():
            qnt += carga.calculo_ilum
            pot, unidade = carga.calculo_pot_ilum
            if unidade == 'VA':
                total += pot
        return total, qnt

    @property
    def soma_tug_va(self):
        total = 0
        qnt = 0
        for carga in self.tug.all():
            qnt += carga.calculo_tug
            pot, unidade = carga.calculo_pot_tug
            if unidade == 'VA':
                total += pot
        return total, qnt

    @property
    def demanda_tug_ilum(self):
        pot_tug, qnt_tug = self.soma_tug_va
        pot_ilum, qnt_ilum = self.soma_ilum_va  # corrigido: usar soma_ilum_va
        pot_total = (pot_tug + pot_ilum) / 1000
        unid = 'kVA'
        qnt_total = qnt_tug + qnt_ilum

        faixas = [
            (1, 0.80),
            (2, 0.75),
            (3, 0.65),
            (4, 0.60),
            (5, 0.50),
            (6, 0.45),
            (7, 0.40),
            (8, 0.35),
            (9, 0.30),
            (10, 0.27),
        ]

        fator_extra = 0.24

        dem = 0
        pot_restante = pot_total

        # Mantive a sua lógica de distribuição por faixas (você pediu para não alterar).
        for i, (limite, fator) in enumerate(faixas, start=1):
            if pot_restante <= 0:
                break
            if pot_total > limite:
                incremento = 1
            else:
                incremento = pot_restante
            dem += incremento * fator
            pot_restante -= incremento

        if pot_restante > 0:
            dem += pot_restante * fator_extra

        return dem, unid

    @property
    def demanda_total(self):
        dem_tug_ilum, _ = self.demanda_tug_ilum
        dem_trafo, _ = self.demanda_trafo
        dem_motor, _ = self.demanda_motor
        dem_ac, _ = self.demanda_ac
        dem_ac_central, _ = self.demanda_ac_central
        dem_resist, _ = self.demanda_resist

        # removida duplicidade de dem_trafo (estava somando duas vezes)
        dem_total = dem_resist + dem_trafo + dem_ac + dem_ac_central + dem_motor + dem_tug_ilum

        return dem_total

    @property
    def padrao_entrada(self):
        faixa_m = [
            (5, 40),
            (8, 63),
        ]
        faixa_b = [
            (8, 40),
            (13, 63),
        ]
        faixa_t = [
            (15, 40),
            (24, 63),
            (30, 80),
            (38, 100),
            (47, 125),
            (57, 150),
            (66, 175),
            (76, 200),
            (85, 225),
            (95, 250),
        ]

        tipo_entrada = None
        disj_p = None

        if self.demanda_total < 6:
            for dem, disj in faixa_m:
                if dem >= self.demanda_total:
                    tipo_entrada = 'Monopolar'
                    disj_p = disj
                    break
        elif self.demanda_total < 13:
            for dem, disj in faixa_b:
                if dem >= self.demanda_total:
                    tipo_entrada = 'Bipolar'
                    disj_p = disj
                    break
        elif self.demanda_total >= 13:
            for dem, disj in faixa_t:
                if dem >= self.demanda_total:
                    tipo_entrada = 'Tripolar'
                    disj_p = disj
                    break
        return disj_p, tipo_entrada
    
    @property
    def disjuntor_entrada(self):
        disj_p, _ = self.padrao_entrada
        return f'{disj_p} A'
    @property
    def tipo_entrada(self):
        _, tipo_entrada = self.padrao_entrada
        return f'{tipo_entrada}'

class Condutores(models.Model):
    '''Modelo para os condutores elétricos'''
    MATERIAL_ISOL = (
        ('P', 'PVC'),
        ('E', 'EPR OU XLPE'),
    )

    local = models.ForeignKey(Local, on_delete=models.CASCADE, related_name='cond_local', verbose_name='Local')
    ckt = models.ForeignKey(Circuitos, verbose_name='Circuito', on_delete=models.CASCADE, related_name='cond_ckt')
    n_ckts = models.IntegerField(verbose_name='Nº Máximo de CKTs em um trecho', blank=False, null=False, default=1)
    temp = models.IntegerField(verbose_name='Temperatura Ambiente Máxima', blank=False, null=False, default=30)
    mat_isol = models.CharField(verbose_name='Material Isolante do Condutor', choices=MATERIAL_ISOL, default='P', max_length=1)

    class Meta:
        verbose_name = 'Condutor'
        verbose_name_plural = "Condutores"

    FCT_PVC = [
        (10, 1.22),
        (15, 1.17),
        (20, 1.12),
        (25, 1.06),
        (30, 1.00),
        (35, 0.94),
        (40, 0.87),
    ]

    FCT_EPR = [
        (10, 1.15),
        (15, 1.12),
        (20, 1.08),
        (25, 1.04),
        (30, 1.00),
        (35, 0.96),
        (40, 0.91),
    ]

    FCNC = [1.00, 0.80, 0.70, 0.65, 0.60, 0.57]

    @property
    def corrente_projetada(self):
        indice = min(max(self.n_ckts, 1), 6) - 1
        fator = self.FCNC[indice]

        if self.mat_isol == 'P':
            for temp, fct in self.FCT_PVC:
                if temp >= self.temp:
                    i_proj = self.ckt.corrente_ckt / (fator * fct)
                    break
            else:
                i_proj = self.ckt.corrente_ckt / (fator * 0.80)
        else:
            for temp, fct in self.FCT_EPR:
                if temp >= self.temp:
                    i_proj = self.ckt.corrente_ckt / (fator * fct)
                    break
            else:
                i_proj = self.ckt.corrente_ckt / (fator * 0.85)
        return i_proj

    @property
    def condutores_calc(self):
        CKT_MONO_BIFASICO = [
            (1.5, 17.5),
            (2.5, 24.0),
            (4.0, 32.0),
            (6.0, 41.0),
            (10.0, 57.0),
            (16.0, 76.0),
            (25.0, 101.0),
        ]
        CKT_TRIFASICO = [
            (1.5, 15.5),
            (2.5, 21.0),
            (4.0, 28.0),
            (6.0, 36.0),
            (10.0, 50.0),
            (16.0, 68.0),
            (25.0, 89.0),
        ]

        bitola = None
        corr = None

        if self.ckt.ckt in ('M', 'B'):
            for bit, corr in CKT_MONO_BIFASICO:
                if self.corrente_projetada < 0.95 * corr:
                    bitola = bit
                    break
        else:
            for bit, corr in CKT_TRIFASICO:
                if self.corrente_projetada < 0.95 * corr:
                    bitola = bit
                    break
        return bitola, corr

    def __str__(self):
        bit, _ = self.condutores_calc
        return f'{self.ckt} - Bitola: {bit} mm²'

class Eletrodutos(models.Model):
    '''Modelo para os eletrodutos elétricos'''
    cond = models.ManyToManyField(Condutores, verbose_name='Condutores', blank=True, related_name='eletro_ckt')
    local = models.ForeignKey(Local, on_delete=models.CASCADE, related_name='eletro_local', verbose_name='Local')
    info = models.CharField(verbose_name='Trecho do Eletroduto', max_length=100)
    conexoes = models.IntegerField(default=0, blank=True, null=True, verbose_name='Quantidade de Conexões para o eletroduto')
    c_conex = models.CharField(verbose_name='Caracteristicas das conexões', max_length=100, blank=True, null=True)
    dist = models.IntegerField(default=0, blank=True, null=True, verbose_name='Comprimento do Trecho')

    class Meta:
        verbose_name = 'Eletroduto'
        verbose_name_plural = "Eletrodutos"

    ELETRODUTO = (
        ('3/8"', 16, 12.8, 514.7),
        ('1/2"', 20, 16.4, 844.94),
        ('3/4"', 25, 21.3, 1425.27),
        ('1"', 32, 27.5, 2375.76),
        ('1 1/4"', 40, 36.1, 4094.03),
        ('1 1/2"', 50, 41.4, 5384.41),
        ('2"', 60, 52.8, 8758.00),
    )

    CONDUTOR = (
        (1.5, 3.0, 7.07),
        (2.5, 3.7, 10.75),
        (4, 4.2, 13.85),
        (6, 4.6, 16.62),
        (10, 5.9, 27.34),
        (16, 6.9, 37.39),
        (25, 8.5, 56.75),
    )

    def n_cond(self):
        n_cond = 0
        a_ocup = 0
        for ckt in self.cond.all():
            bitola, _ = ckt.condutores_calc
            d_cond = None
            a_cond = None
            for cond, d_cond_v, a_cond_v in self.CONDUTOR:
                if bitola == cond:
                    d_cond = d_cond_v
                    a_cond = a_cond_v
                    break
            if ckt.ckt == 'T':
                qnt = 4
            else:
                qnt = 3
            n_cond += qnt
            # se não encontrou a_cond, evita crash (fallback 0)
            a_ocup += qnt * (a_cond or 0)
        tot_cond = n_cond
        a_total = a_ocup
        return a_total, tot_cond

    @property
    def eletroduto(self):
        a_cond, total_cond = self.n_cond()
        nome = None
        for nome_e, _, _, area in self.ELETRODUTO:
            if a_cond <= (area * 0.40):
                nome = nome_e
                break
        return nome, total_cond

class Protecao(models.Model):
    '''Modelo para os dispositivos de proteção'''
    local = models.ForeignKey(Local, on_delete=models.CASCADE, related_name='prot_local', verbose_name='Local')
    cond = models.ForeignKey(Condutores, verbose_name='Condutores', on_delete=models.CASCADE, related_name='prot_ckt')

    class Meta:
        verbose_name = 'Proteção'
        verbose_name_plural = "Proteções"

    def __str__(self):
        disj, _, polos = self.protecao
        cliente = self.local.cliente
        return f'{cliente} - {self.cond}- Disjuntor {disj} A - {polos}'

    @property
    def protecao(self):
        DISJ = [2, 4, 6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125]

        i_ckt = self.cond.ckt.corrente_ckt
        i_proj = self.cond.corrente_projetada
        fat_correcao = i_ckt / i_proj if i_proj else 1
        bitola, i_cond = self.cond.condutores_calc
        n = 0
        disj = None
        if self.cond.ckt.ckt == 'M':
            polos = 'Monopolar'
        elif self.cond.ckt.ckt == 'B':
            polos = 'Bipolar'
        else:
            polos = 'Tripolar'

        for i in DISJ:
            n += 1
            if i >= i_ckt and i <= (i_cond * fat_correcao):
                disj = i
                obs = ('Para definir a Curva veja a característica do circuito: \n'
                       'Puramente resistivo → Curva B, \n'
                       'Cargas gerais → Curva C, \n'
                       'Cargas com corrente de partida pesada → Curva D.\n')
                break
            elif i >= i_ckt and i >= (i_cond * fat_correcao):
                disj = '-'
                disj_a = DISJ[n] if n < len(DISJ) else None
                obs = (f'Para as condições atuais, não foi possivel garantir a operação correta do disjuntor de {i} A.\n'
                       f'Estude alterar a rota do Circuito, ou a sua bitola para um valor acima.\n'
                       f'Bitola Atual: {bitola} mm²\n'
                       f'Corrente Máxima com Fator de Correção: {i_cond * fat_correcao} A\n'
                       f'Disjuntor a cima: {disj_a} A\n'
                       f'Fator de Correção: {fat_correcao}'
                       )
                break

        if disj is None:
            disj = 0
            obs = 'Busque um catálogo específico para correntes superiores a 125 A.'
        return disj, obs, polos

class EquilibrioFases(models.Model):
    '''Modelo para o equilíbrio de fases'''
    local = models.ForeignKey(Local, on_delete=models.CASCADE, related_name='EqFase_local', verbose_name='Local')
    ckt = models.ManyToManyField(Circuitos, verbose_name='Circuito', related_name='EqFase_ckt', blank=True)

    class Meta:
        verbose_name = 'Equilíbrio de Fases'
        verbose_name_plural = "Equilíbrio de Fases"

    @property
    def equilibrio(self):
        FASES = {
            'R': {'total': 0, 'itens': []},
            'S': {'total': 0, 'itens': []},
            'T': {'total': 0, 'itens': []},
        }
        for ckt_ind in sorted(self.ckt.all(), key=lambda c: c.corrente_ckt, reverse=True):
            I = ckt_ind.corrente_ckt
            P = ckt_ind.ckt
            nome_ckt = ckt_ind.nome
            if P == 'T':
                parte = I / 3
                for fase in FASES:
                    FASES[fase]['total'] += parte
                    FASES[fase]['itens'].append(nome_ckt)
            elif P == 'B':
                parte = I / 2
                ordenados = sorted(FASES.items(), key=lambda x: x[1]['total'])
                for nome, grupo in ordenados[:2]:
                    grupo['total'] += parte
                    grupo['itens'].append(nome_ckt)
            else:
                menor_nome, menor = min(FASES.items(), key=lambda x: x[1]['total'])
                menor['total'] += I
                menor['itens'].append(nome_ckt)
        return FASES

def get_upload_path(instance,filename):
    data_nome = datetime.now().strftime("%Y-%m-%d")
    filename = f"{instance.cliente.cliente} - {instance.tipo} {data_nome} - {filename}"
    return f"uploads/InstEletricas/{instance.cliente.cliente.tipo}/{instance.cliente.cliente}/Local-[{instance.cliente.local}]/{instance.tipo}/{data_nome}/{filename}"

class ArquivosInstEletricas(models.Model):
    TIPO = (
        ('Conta de Luz', 'Conta de Luz'),
        ('Diagrama Unifilar', 'Diagrama Unifilar'),
        ('Diagrama Trifilar', 'Diagrama Trifilar'),
        ('Planta do Imóvel', 'Planta do Imóvel'),
        ('ART do Projeto', 'ART do Projeto'),
        ('Memorial Descritivo', 'Memorial Descritivo'),
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
    cliente = models.ForeignKey(Local, on_delete=models.CASCADE,related_name='local_files')
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
        return f"{self.tipo} - {self.cliente.cliente.nome} - [Local: {self.cliente.local}] - [Upload: {self.data_upload.date()}]"