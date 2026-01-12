from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator,RegexValidator
from apps.cliente.validators import validate_file_mimetype,validate_file_size,validate_cpf,validate_cnpj
from apps.irradiacao.views import buscar_endereco_por_cep


class Cliente(models.Model):
    TIPO = (
        ('PF','Pessoa Física'),
        ('PJ','Pessoa Jurídica'),
        )
    tipo = models.CharField(verbose_name='Tipo de Cliente',choices=TIPO,default='PF',max_length=2, db_index=True)
    nome = models.CharField(verbose_name='Cliente',max_length=100,blank=False,null=False, db_index=True)
    doc = models.CharField(max_length=14,unique=True,verbose_name='CPF/CNPJ', db_index=True)
    email = models.EmailField(blank=False,null=False,max_length=200,verbose_name='Email', db_index=True)
    tel1 = models.CharField(max_length=11,null=False,blank=False,verbose_name='Contato 1', db_index=True,validators=[RegexValidator(r'^\d{10,11}$', "Telefone 1 inválido .")])
    tel2 = models.CharField(max_length=11,null=True,blank=True,verbose_name='Contato 2',validators=[RegexValidator(r'^\d{10,11}$', "Telefone 2 inválido .")])
    cep = models.CharField(max_length=8,blank=False,null=False,verbose_name='CEP',validators=[RegexValidator(r'^\d{8}$', "CEP inválido.")])
    logradouro = models.CharField(max_length=100,blank=True,null=True,verbose_name='Logradouro')
    numero = models.CharField(max_length=100,blank=True,null=True,verbose_name='Numero')
    bairro = models.CharField(max_length=100,blank=True,null=True,verbose_name='Bairro')
    cidade = models.CharField(max_length=100,blank=True,null=True,verbose_name='Cidade')
    uf = models.CharField(max_length=2,blank=True,null=True,verbose_name='Estado')
    cadastro = models.DateField(default=timezone.now,blank=False,verbose_name='Data de Cadastro')

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def atualizar_endereco_por_cep(self):
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
    
    def clean(self):
        super().clean()
        
        if not self.doc:
            return

        doc_limpo = ''.join(filter(str.isdigit, self.doc))

        if self.tipo == 'PF':
            if len(doc_limpo) != 11:
                raise ValidationError({'doc': "Para Pessoa Física, o CPF deve ter 11 dígitos."})
            try:
                validate_cpf(self.doc)
            except ValidationError as e:
                raise ValidationError({'doc': e})
                
        elif self.tipo == 'PJ':
            if len(doc_limpo) != 14:
                raise ValidationError({'doc': "Para Pessoa Jurídica, o CNPJ deve ter 14 dígitos."})
            try:
                validate_cnpj(self.doc)
            except ValidationError as e:
                raise ValidationError({'doc': e})

def get_upload_path(instance, filename):
    data = timezone.now().strftime("%Y-%m-%d")

    cliente_slug = slugify(instance.cliente.nome)
    tipo_slug = slugify(instance.get_tipo_display())

    # Mantém extensão, mas evita nomes conflitantes
    ext = filename.split('.')[-1]
    new_name = f"{cliente_slug}-{tipo_slug}-{data}.{ext}"

    return f"uploads/clientes/{instance.cliente.id}/{tipo_slug}/{data}/{new_name}"

class ArquivosClientes(models.Model):
    TIPO = (
        ('DC','Documento do Cliente'),
        ('PR','Proposta'),
        ('CA','Contrato Assinado'),
        ('OR','Orçamento'),
        ('OU','Outros'),
    )

    tipo = models.CharField(max_length=2,choices=TIPO,verbose_name='Tipo de Arquivo',default='DC', db_index=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE,related_name='files', db_index=True)
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

    class Meta:
        verbose_name = "Arquivo do Cliente"
        verbose_name_plural = "Arquivos dos Clientes"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.cliente.nome} [Upload: {self.data_upload.date()}]"