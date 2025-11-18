from django.db import models
from datetime import datetime
from django.core.validators import FileExtensionValidator
from apps.cliente.validators import validate_file_mimetype,validate_file_size

class Cliente(models.Model):
    TIPO = {
        'PF':'Pessoa Física',
        'PJ':'Pessoa Jurídica',
    }
    tipo = models.CharField(verbose_name='Tipo de Cliente',choices=TIPO,default='PF',max_length=2)
    nome = models.CharField(verbose_name='Cliente',max_length=100,blank=False,null=False)
    doc = models.CharField(max_length=14,unique=True,verbose_name='CPF/CNPJ')
    email = models.EmailField(blank=False,null=False,max_length=200,verbose_name='Email')
    tel1 = models.CharField(max_length=11,null=False,blank=False,verbose_name='Contato 1')
    tel2 = models.CharField(max_length=11,null=True,blank=True,verbose_name='Contato 2')
    cep = models.CharField(max_length=8,blank=False,null=False,verbose_name='CEP')
    logradouro = models.CharField(max_length=100,blank=True,null=True,verbose_name='Logradouro')
    numero = models.CharField(max_length=100,blank=True,null=True,verbose_name='Numero')
    bairro = models.CharField(max_length=100,blank=True,null=True,verbose_name='Bairro')
    cidade = models.CharField(max_length=100,blank=True,null=True,verbose_name='Cidade')
    uf = models.CharField(max_length=2,blank=True,null=True,verbose_name='Estado')
    cadastro = models.DateField(default=datetime.now,blank=False,verbose_name='Data de Cadastro')

    def __str__(self):
        return self.nome

def get_upload_path(instance,filename):
    data_nome = datetime.now().strftime("%Y-%m-%d")
    filename = f"{instance.cliente} - {instance.tipo} {data_nome} - {filename}"
    return f"uploads/{instance.cliente.tipo}/{instance.cliente}/{instance.tipo}/{data_nome}/{filename}"

class ArquivosClientes(models.Model):
    TIPO = {
        'Documento do Cliente':'Documento do Cliente',
        'Proposta':'Proposta',
        'Contrato Assinado':'Contrato Assinado',
        'Orçamento':'Orçamento',
        'Outros':'Outros',
        
        
    }
    tipo = models.CharField(max_length=100,choices=TIPO,verbose_name='Tipo de Arquivo',default='Documento do Cliente')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE,related_name='files')
    arquivo = models.FileField(
        upload_to=get_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png']),
            validate_file_mimetype,
            validate_file_size
        ],
        verbose_name="Arquivos"
    )
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.cliente.nome} [Upload: {self.data_upload.date()}]"