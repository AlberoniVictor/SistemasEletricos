from django.db import models
import math

class Local(models.Model):
    cliente = models.CharField(verbose_name='Cliente',max_length=100)
    local = models.CharField(verbose_name='Identificação do local',max_length=100)
    cep = models.CharField(max_length=8,blank=False,null=False,verbose_name='CEP',default='-')
    logradouro = models.CharField(max_length=100,blank=True,null=True,verbose_name='Logradouro')
    numero = models.CharField(max_length=100,blank=True,null=True,verbose_name='Numero')
    bairro = models.CharField(max_length=100,blank=True,null=True,verbose_name='Bairro')
    cidade = models.CharField(max_length=100,blank=True,null=True,verbose_name='Cidade')
    uf = models.CharField(max_length=2,blank=True,null=True,verbose_name='Estado')

class Ambientes(models.Model):
    COMODOS = (
        ('Q','Quarto'),
        ('S','Salas'),
        ('B','Banheiro'),
        ('C','Cozinha, Copas, Lavanderias'),
        ('O','Escritório'),
        ('E','Área Externa'),
        ('V','Varanda'),
    )

    comodo = models.CharField(verbose_name='Ambiente',max_length=100)
    t_comodo =  models.CharField(verbose_name='Tipo de Ambiente',choices=COMODOS,default='S')
    perimetro = models.FloatField(verbose_name='Perimetro do Ambiente',blank=False,null=False,)
    area = models.FloatField(verbose_name='Área do Ambiente',blank=False,null=False,)
    tug = models.IntegerField(default=0,verbose_name='Tomadas de Uso Geral',blank=True,null=True)
    tue = models.IntegerField(default=0,verbose_name='Tomadas de Uso Especifico',blank=True,null=True)
    iluminacao = models.IntegerField(default=0,verbose_name='Pontos de Iluminação',blank=True,null=True)
    
    @property
    def calculo_tug(self):
        if self.t_comodo == 'B':
            tug = 1
        elif self.t_comodo == 'C':
            tug = math.ceil(self.perimetro/3.5)
        elif self.t_comodo == 'V':
            tug = 1
        elif self.t_comodo in ('Q','S','E'):
            tug = math.ceil(self.perimetro/5)
        else:
            if self.area <= 6:
                tug = 1
                # obs.: 'Se a area Menor ou Igual a 2.25, será aceito um ponto de tomada exteno a dependencia, no máximo a 0,80 m da porta de acesso'
            else:
                tug = math.ceil(self.perimetro/5)
        
        return tug
    
    @property
    def calculo_pot_tug(self):
        if self.tug > self.calculo_tug:
            if self.t_comodo in ('C','B'):
                if self.tug <= 3:
                    pot_tug = self.tug*600
                else:
                    pot_tug = (self.tug - 3)*600
            else:
                pot_tug = self.tug*100
        else:
            if self.t_comodo in ('C','B'):
                pot_tug = self.tug*600
            else:    
                pot_tug = self.calculo_tug*100

        return pot_tug
    
    @property
    def calculo_ilum(self):
        if self.area <= 6:
            ilum = 1
        else:
            ilum = (1 + math.floor((self.area-6)/4))
        
        return ilum
    
    @property
    def calculo_pot_ilum(self):
        N = max(self.iluminacao, self.calculo_ilum)
        pot_ilum = 100 + (N - 1) * 60
        return pot_ilum