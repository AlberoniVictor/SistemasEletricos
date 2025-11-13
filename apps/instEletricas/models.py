from django.db import models
import math

class Local(models.Model):
    TENSAO = (
        ("1","127/220 V"),
        ("2","220/380 V"),
    )

    cliente = models.CharField(verbose_name='Cliente',max_length=100)
    local = models.CharField(verbose_name='Identificação do local',max_length=100)
    cep = models.CharField(max_length=8,blank=False,null=False,verbose_name='CEP',default='-')
    logradouro = models.CharField(max_length=100,blank=True,null=True,verbose_name='Logradouro')
    numero = models.CharField(max_length=100,blank=True,null=True,verbose_name='Numero')
    bairro = models.CharField(max_length=100,blank=True,null=True,verbose_name='Bairro')
    cidade = models.CharField(max_length=100,blank=True,null=True,verbose_name='Cidade')
    uf = models.CharField(max_length=2,blank=True,null=True,verbose_name='Estado')
    rede = models.CharField(verbose_name='Alimentação Concessionária',choices=TENSAO,default='1',max_length=1)

    class Meta:
        verbose_name = 'Local'
        verbose_name_plural = 'Locais'
    def __str__(self):
        return self.local

class Ambientes(models.Model):
    COMODOS = (
        ('Q','Quarto'),
        ('S','Salas'),
        ('B','Banheiro'),
        ('C','Cozinha, Copas, Lavanderias'),
        ('O','Escritório'),
        ('E','Área Externa'),
        ('V','Varanda'),
        ('H','Corredores'),
    )

    local = models.ForeignKey(Local,on_delete=models.CASCADE,related_name='local_ambiente')
    comodo = models.CharField(verbose_name='Ambiente',max_length=100)
    t_comodo =  models.CharField(verbose_name='Tipo de Ambiente',choices=COMODOS,default='S',max_length=1)
    perimetro = models.FloatField(verbose_name='Perimetro do Ambiente',blank=False,null=False,)
    area = models.FloatField(verbose_name='Área do Ambiente',blank=False,null=False,)
    tug = models.IntegerField(default=0,verbose_name='Qnt. TUGs Propostas',blank=True,null=True)
    tue = models.IntegerField(default=0,verbose_name='Qnt. TUEs Propostas',blank=True,null=True)
    iluminacao = models.IntegerField(default=0,verbose_name='Pontos de Iluminação Propostas',blank=True,null=True)
    class Meta:
        verbose_name = 'Ambiente'
        verbose_name_plural = 'Ambientes'

    def __str__(self):
        return f'{self.comodo} - {self.local}'

class CargasTUG(models.Model):
    comodo = models.ForeignKey(Ambientes,on_delete=models.CASCADE,related_name='cargas_tug')

    class Meta:
        verbose_name = 'Carga TUG'
        verbose_name_plural = "Cargas TUG's"

    @property
    def calculo_tug(self):
        if self.comodo.t_comodo == 'B':
            tug = 1
        elif self.comodo.t_comodo == 'C':
            tug = math.ceil(self.comodo.perimetro/3.5)
        elif self.comodo.t_comodo == 'V':
            tug = 1
        elif self.comodo.t_comodo == 'E':
            tug = 1
        elif self.comodo.t_comodo in ('Q','S'):
            tug = math.ceil(self.comodo.perimetro/5)
        else:
            if self.area <= 6:
                tug = 1
                # obs.: 'Se a area Menor ou Igual a 2.25, será aceito um ponto de tomada exteno a dependencia, no máximo a 0,80 m da porta de acesso'
            else:
                tug = math.ceil(self.comodo.perimetro/5)
        if self.comodo.tug > tug:
            tug = self.comodo.tug
        return tug
    
    @property
    def calculo_pot_tug(self):
        if self.comodo.tug > self.calculo_tug:
            if self.comodo.t_comodo in ('C','B','E'):
                if self.comodo.tug <= 3:
                    pot_tug = self.comodo.tug*600
                else:
                    pot_tug = (self.comodo.tug - 3)*600
            else:
                pot_tug = self.comodo.tug*100
        else:
            if self.comodo.t_comodo in ('C','B','E'):
                pot_tug = self.calculo_tug*600
            else:    
                pot_tug = self.calculo_tug*100
        grand = 'VA'

        return pot_tug,grand
    
    @property
    def conv_pot_tug(self):
        pot_va, grand = self.calculo_pot_tug
        if pot_va:
            pot_w = pot_va*0.80
        else:
            pot_w = 0
        grand = 'W'
        return pot_w,grand

    def __str__(self):
        pot,grand = self.calculo_pot_tug
        return f'Potência TUG - {self.comodo}: {pot:.2f} {grand}'

class CargasILUM(models.Model):
    comodo = models.ForeignKey(Ambientes,on_delete=models.CASCADE,related_name='cargas_ilum')

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
            ilum = int(1 + math.floor((self.comodo.area-6)/4))
        
        return ilum
    
    @property
    def calculo_pot_ilum(self):
        N = max(self.comodo.iluminacao, self.calculo_ilum)
        pot_ilum = 100 + (N - 1) * 60
        grand = 'VA'
        return pot_ilum,grand
    
    @property
    def conv_pot_ilum(self):
        pot_va,grand = self.calculo_pot_ilum
        if pot_va:
            pot_w = pot_va*0.92
        else:
            pot_w = 0

        grand = 'W'
        return pot_w,grand

    def __str__(self):
        pot,grand = self.calculo_pot_ilum
        return f'Iluminação - {self.comodo}: {pot:.2f} {grand}'
    
class CargasTUE(models.Model):

    TIPOS_CARGAS = (
        ('R','Aquecimento'),
        ('A','Ar Condicionados Janela/Split'),
        ('B','Ar Condicionado Central'),
        ('M','Motores'),
        ('S','Maq. Solda a Trafo, equip. Odonto-Medico Hopitalares'),
    )
    TIPO_POT = (
        ('W','Watts'), # Watts/0.92 = VA
        ('V','VA'), 
    )

    comodo = models.ForeignKey(Ambientes,on_delete=models.CASCADE,related_name='cargas_tue')
    t_pot = models.CharField(default='V',verbose_name='Watts ou VA',blank=True,null=True,max_length=1,choices=TIPO_POT)
    pot_tue = models.IntegerField(default=0,verbose_name='Potencia TUE',blank=False,null=False)
    t_carga = models.CharField(default='R',verbose_name='Tipos de Cargas',blank=True,null=True,max_length=1,choices=TIPOS_CARGAS)
    carga = models.CharField(verbose_name='Descritivo da Carga',max_length=100)

    class Meta:
        verbose_name = 'Carga de TUE'
        verbose_name_plural = "Cargas de TUE's"

    @property
    def potencia(self):
        if self.pot_tue:
            if self.t_carga=='R':
                pot = self.pot_tue*1
                grand = 'VA'
            elif self.t_pot == 'W':
                if self.t_carga =='M':
                    pot = self.pot_tue/0.85
                    grand = 'VA'
                else:
                    pot = self.pot_tue/0.92
                    grand = 'VA'
            else:
                pot = self.pot_tue
                grand = 'VA'
        else:
            pot = 0
            grand = 'VA'
        return pot,grand

    @property
    def conv_pot_tue(self):
        pot,grand = self.potencia
        if self.t_carga=='R':
            pot_conv = pot*1
            grand = 'W'
        elif grand == 'VA':
            if self.t_carga =='M':
                pot_conv = pot*0.85
                grand = 'W'
            else:
                pot_conv = pot*0.92
                grand = 'W'
        return pot_conv,grand

    def __str__(self):
        pot,grand = self.potencia
        return f'{self.carga} - {self.comodo} {pot:.2f} {grand}'
    
class Circuitos(models.Model):
    CKT = (
        ("M","Monofásico"),
        ("B","Bifásico"),
        ("T","Trifásico"),
    )
    ambiente = models.ForeignKey(Local,on_delete=models.CASCADE,related_name='ckt_local',verbose_name='Local')
    tug = models.ManyToManyField(CargasTUG,related_name='ckt_tug',blank=True,verbose_name='Cargas TUGs')
    tue = models.ManyToManyField(CargasTUE,related_name='ckt_tue',blank=True,verbose_name='Cargas TUEs')
    ilum = models.ManyToManyField(CargasILUM,related_name='ckt_ilum',blank=True,verbose_name='Cargas de Iluminação')
    nome = models.CharField(verbose_name='Identificação do Circuito',max_length=20,default="")
    ckt = models.CharField(verbose_name='Tipo do Circuito',choices=CKT,default='M',max_length=1)

    class Meta:
        verbose_name = 'Circuito'
        verbose_name_plural = 'Circuitos'

    def __str__(self):
        return f'{self.nome} - {self.ambiente}'

    @property
    def soma_tug_va(self):
        total = 0
        for carga in self.tug.all():
            pot,unidade = carga.calculo_pot_tug
            if unidade == 'VA':
                total+= pot
        return total

    @property
    def soma_tug_w(self):
        total = 0
        for carga in self.tug.all():
            pot,unidade = carga.conv_pot_tug
            if unidade == 'W':
                total+= pot
        return total
    
    @property
    def soma_tue_va(self):
        total = 0
        for carga in self.tue.all():
            pot,unidade = carga.potencia
            if unidade == 'VA':
                total+= pot
        return total
    
    @property
    def soma_tue_w(self):
        total = 0
        for carga in self.tue.all():
            pot,unidade = carga.conv_pot_tue
            if unidade == 'W':
                total+= pot
        return total
    
    @property
    def soma_ilum_va(self):
        total = 0
        for carga in self.ilum.all():
            pot,unidade = carga.calculo_pot_ilum
            if unidade == 'VA':
                total+= pot
        return total
    
    @property
    def soma_ilum_w(self):
        total = 0
        for carga in self.ilum.all():
            pot,unidade = carga.conv_pot_ilum
            if unidade == 'W':
                total+= pot
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
        return v

    @property
    def corrente_ckt(self):
        fp = self.total_w/self.total_va if self.total_va else 1
        pot = self.total_va
        raiz3= 3**0.5
        v = self.tensao_sist()
        if self.ckt == 'M':
                i = pot/(v*fp)
        elif self.ckt == 'B':
            i = pot/(v*fp)
        elif self.ckt == 'T':
            i = pot/(raiz3*v*fp)
        else:
            i = 0
        return i

class Demandas(models.Model):
    local = models.ForeignKey(Local,on_delete=models.CASCADE,related_name='demanda_local')
    tue = models.ManyToManyField(CargasTUE, related_name='demanda_tue', blank=True,verbose_name='Cargas TUEs')
    ilum = models.ManyToManyField(CargasILUM, related_name='demanda_ilum', blank=True,verbose_name='Cargas de Iluminação')
    tug = models.ManyToManyField(CargasTUG, related_name='demanda_tug', blank=True,verbose_name='Cargas TUGs')

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
            pot,unid = motor.potencia
            total+= pot
        return total,qnt,unid
    
    @property
    def demanda_motor(self):
        pot,qnt,unid = self.filtra_motor
        fatores = [1.00, 0.75, 0.6333, 0.5750, 0.54, 0.50, 0.4714, 0.45, 0.4333, 0.42]
        indice = min(max(qnt, 1), 10) - 1
        fator = fatores[indice]
        dem = (pot * fator)/1000
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
            pot,unid = resist.potencia
            total+= pot
        return total,qnt,unid
    
    @property
    def demanda_resist(self):
        pot,qnt,unid = self.filtra_resist
        fatores = [1.00, 0.75, 0.70, 0.66, 0.62, 0.59, 0.56, 0.53, 0.51, 0.49, 0.47, 0.45, 0.43, 0.41, 0.40, 0.39, 0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.32, 0.31, 0.30]
        indice = min(max(qnt, 1), 25) - 1
        fator = fatores[indice]
        dem = (pot * fator)/1000
        unid = 'kVA'
        return dem,unid
    
    @property
    def filtra_ac(self):
        qnt = 0
        total = 0
        unid = 'VA'
        filtro = self.tue.filter(t_carga='A')
        for ac in filtro:
            qnt += 1
            pot,unid = ac.potencia
            total+= pot
        return total,qnt,unid
    
    @property
    def demanda_ac(self):
        pot,qnt,unid = self.filtra_ac
        unid = 'kVA'
        tabela = [(4,1.00),
                  (10,0.70),
                  (20,0.60),
                  (30,0.55),
                  (40,0.53),
                  (50,0.53),
                  (float('inf'),0.50)
                  ]
        for limite,fator in tabela:
            if qnt <= limite:
                dem = (pot*fator)/1000
                break
        return dem,unid
    
    @property
    def filtra_ac_central(self):
        qnt = 0
        total = 0
        unid = 'VA'
        filtro = self.tue.filter(t_carga='B')
        for ac in filtro:
            qnt += 1
            pot,unid = ac.potencia
            total+= pot
        return total,qnt,unid
    
    @property
    def demanda_ac_central(self):
        pot,qnt,unid = self.filtra_ac_central
        unid = 'kVA'
        tabela = [(10,1.00),
                  (20,0.75),
                  (30,0.70),
                  (40,0.65),
                  (50,0.60),
                  (80,0.55),
                  (float('inf'),0.50)
                  ]
        for limite,fator in tabela:
            if qnt <= limite:
                dem = (pot*fator)/1000
                break
        return dem,unid

    @property
    def filtra_trafo(self):
        qnt = 0
        total = 0
        unid = 'VA'
        filtro = self.tue.filter(t_carga='S')
        for trafo in filtro:
            qnt += 1
            pot,unid = trafo.potencia
            total+= pot
        return total,qnt,unid
    
    @property
    def demanda_trafo(self):
        pot,qnt,unid = self.filtra_trafo
        fatores = [1.00, 0.75, 0.6333, 0.5750, 0.54, 0.50, 0.4714, 0.45, 0.4333, 0.42]
        indice = min(max(qnt, 1), 10) - 1
        fator = fatores[indice]
        dem = (pot*fator)/1000
        unid = 'kVA'
        return dem, unid

    @property
    def soma_ilum_va(self):
        qnt = 0
        total = 0
        for carga in self.ilum.all():
            qnt += carga.calculo_ilum
            pot,unidade = carga.calculo_pot_ilum
            if unidade == 'VA':
                total+= pot
        return total,qnt
    
    @property
    def soma_tug_va(self):
        total = 0
        qnt = 0
        for carga in self.tug.all():
            qnt += carga.calculo_tug
            pot,unidade = carga.calculo_pot_tug
            if unidade == 'VA':
                total+= pot
        return total,qnt
    
    @property
    def demanda_tug_ilum(self):
        pot_tug,qnt_tug = self.soma_tug_va
        pot_ilum,qnt_ilum = self.soma_tug_va

        pot_total = (pot_tug + pot_ilum)/1000
        unid = 'kVA'
        qnt_total = qnt_tug+qnt_ilum
        
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

        for i,(limite,fator) in enumerate(faixas,start=1):
            if pot_restante <=0:
                break
            if pot_total > limite:
                incremento = 1
            else:
                incremento = pot_restante
            dem += incremento*fator
            pot_restante -= incremento
        
        if pot_restante >0:
            dem += pot_restante*fator_extra

        return dem,unid
    
    @property
    def demanda_total(self):
        dem_tug_ilum, _ = self.demanda_tug_ilum
        dem_trafo, _ = self.demanda_trafo
        dem_motor, _ = self.demanda_motor
        dem_ac, _ = self.demanda_ac
        dem_ac_central, _ = self.demanda_ac_central
        dem_resist, _ = self.demanda_resist

        dem_total = dem_resist+dem_trafo+dem_ac+dem_ac_central+dem_motor+dem_trafo+dem_tug_ilum

        return dem_total
    
    @property
    def padrao_entrada(self):
        faixa_m = [
            (5,40),
            (8,63),
        ]
        faixa_b = [
            (8,40),
            (13,63),
        ]
        faixa_t = [
            (15,40),
            (24,63),
            (30,80),
            (38,100),
            (47,125),
            (57,150),
            (66,175),
            (76,200),
            (85,225),
            (95,250),            
        ]

        if self.demanda_total < 6:
            for dem,disj in faixa_m:
                if dem >= self.demanda_total:
                    ckt = 'Monopolar'
                    disj_p = disj
                    break
        elif self.demanda_total < 13:
            for dem,disj in faixa_b:
                if dem >= self.demanda_total:
                    ckt = 'Bipolar'
                    disj_p = disj
                    break
        elif self.demanda_total >= 13:
            for dem,disj in faixa_t:
                if dem >= self.demanda_total:
                    ckt = 'Tripolar'
                    disj_p = disj
                    break
        return disj_p,ckt
    
class Condutores(models.Model):
    MATERIAL_ISOL = (
        ('P','PVC'),
        ('E','EPR OU XLPE'),
    )

    local = models.ForeignKey(Local,on_delete=models.CASCADE,related_name='cond_local',verbose_name='Local')
    ckt = models.ForeignKey(Circuitos,verbose_name='Circuito',on_delete=models.CASCADE,related_name='cond_ckt')
    n_ckts = models.IntegerField(verbose_name='Nº Máximo de CKTs em um trecho',blank=False,null=False,default=1)
    temp = models.IntegerField(verbose_name='Temperatura Ambiente Máxima',blank=False,null=False,default=30)
    mat_isol = models.CharField(verbose_name='Material Isolante do Condutor',choices=MATERIAL_ISOL,default='P',max_length=1)

    class Meta:
        verbose_name = 'Condutor'
        verbose_name_plural = "Condutores"

    FCT_PVC = [
        (10,1.22),
        (15,1.17),
        (20,1.12),
        (25,1.06),
        (30,1.00),
        (35,0.94),
        (40,0.87),
    ]

    FCT_EPR = [
        (10,1.15),
        (15,1.12),
        (20,1.08),
        (25,1.04),
        (30,1.00),
        (35,0.96),
        (40,0.91),
    ]

    FCNC = [1.00,0.80,0.70,0.65,0.60,0.57]
    

    @property
    def corrente_projetada(self):
        indice = min(max(self.n_ckts, 1), 6) - 1
        fator = self.FCNC[indice]

        if self.mat_isol == 'P':
            for temp,fct in self.FCT_PVC:
                if temp >= self.temp:
                    i_proj = self.ckt.corrente_ckt/(fator*fct)
                    break
            else:
                i_proj = self.ckt.corrente_ckt/(fator*0.80)
        else:
            for temp,fct in self.FCT_EPR:
                if temp >= self.temp:
                    i_proj = self.ckt.corrente_ckt/(fator*fct)
                    break
            else:
                i_proj = self.ckt.corrente_ckt/(fator*0.85)
        return i_proj

    @property
    def condutores_calc(self):
        CKT_MONO_BIFASICO = [
            (1.5,17.5),
            (2.5,24.0),
            (4.0,32.0),
            (6.0,41.0),
            (10.0,57.0),
            (16.0,76.0),
            (25.0,101.0),
        ]
        CKT_TRIFASICO = [
            (1.5,15.5),
            (2.5,21.0),
            (4.0,28.0),
            (6.0,36.0),
            (10.0,50.0),
            (16.0,68.0),
            (25.0,89.0),
        ]

        if self.ckt.ckt in ('M','B'):
            for bit,corr in CKT_MONO_BIFASICO:
                if self.corrente_projetada < 0.95*corr:
                    bitola = bit
                    break
        else:
            for bit,corr in CKT_TRIFASICO:
                if self.corrente_projetada < 0.95*corr:
                    bitola = bit
                    break
        return bitola,corr
    
    def __str__(self):
        bit, _ = self.condutores_calc
        return f'{self.ckt} - Bitola: {bit} mm²'
    
# class Eletrodutos(models.Model):

class Protecao(models.Model):
    local = models.ForeignKey(Local,on_delete=models.CASCADE,related_name='prot_local',verbose_name='Local')
    cond = models.ForeignKey(Condutores,verbose_name='Condutores',on_delete=models.CASCADE,related_name='prot_ckt')

    @property
    def protecao(self):
        DISJ = [2,4,6,10,16,20,25,32,40,50,63,80,100,125]

        i_ckt = self.cond.ckt.corrente_ckt
        i_proj = self.cond.corrente_projetada
        fat_correcao = i_ckt/i_proj
        bitola, i_cond = self.cond.condutores_calc

        disj = None
        for i in DISJ:
            if i >= i_ckt and i <= (i_cond*fat_correcao):
                disj = i
                obs = ('Para definir a Curva veja a característica do circuito: \n'
                    'Puramente resistivo → Curva B, \n'
                    'Cargas gerais → Curva C, \n'
                    'Cargas com corrente de partida pesada → Curva D.\n')
                break
        if disj is None:
            disj = 0
            obs = 'Busque um catálogo específico para correntes superiores a 125 A.'
        return disj,obs

# Class Equilibrio de Fases