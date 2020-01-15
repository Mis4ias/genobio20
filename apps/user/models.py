from django.db import models
from django.contrib.auth.models import User
import hashlib

##########################################################
# Models de Localização
##########################################################
class Pais( models.Model ):
    id    = models.AutoField( primary_key = True )  
    sigla = models.CharField( max_length = 2, null = False, blank = False, default = "" )
    nome  = models.CharField( max_length = 50, null = False, blank = False )  

class Estado( models.Model ):
    id    = models.AutoField( primary_key = True )  
    nome  = models.CharField( max_length = 19, null = False, blank = False )  
    sigla = models.CharField( max_length = 2, null = False, blank = False )  

class Cidade( models.Model ):
    nome      = models.CharField( max_length = 32, null = False, blank = False )  
    id_estado = models.ForeignKey(Estado, on_delete = models.PROTECT, null = False, blank = False )  

##########################################################
# Models de cadastro do usuário
##########################################################
class Tipo_Inscricao(models.Model):
    tipo   = models.CharField(max_length=25, null=False, blank=False)
    valor  = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.BooleanField(null=False)

class Titulacao(models.Model):
    titulo = models.CharField(max_length=32, null=False, blank=False)

class Area(models.Model):
    nome = models.CharField(max_length=35, null=False, blank=False)

class Usuario( models.Model ):
    # Chave estrangeira da tabela auth_user padrão do django related_name='usuario'
    user = models.OneToOneField( User, on_delete = models.CASCADE, default = '', null = False, blank = False )  

    # Dados de indentificação
    nome           = models.CharField(max_length=100, null=False, blank=False)
    curso_formacao = models.CharField(max_length=100, null=False, blank=False)
    instituicao    = models.CharField(max_length=100, null=True, blank=True)
    titulacao      = models.ForeignKey(Titulacao, on_delete=models.PROTECT, null=False, blank=False)
    area           = models.ForeignKey(Area, on_delete=models.PROTECT, null=False, blank=False)

    # Dados para o evento
    tipo_inscricao   = models.ForeignKey(Tipo_Inscricao, on_delete=models.PROTECT, null=False, blank=False)

    # Dados de contato
    celular = models.CharField(max_length=30, null=False, blank=False)  
    # OBS: O email e senha do usuário fica na tabela auth_user

    # Dados de localização
    pais     = models.ForeignKey( Pais, on_delete = models.PROTECT, null = False, blank = False )  
    cep      = models.CharField( max_length = 30, null = False, blank = False )  
    estado   = models.ForeignKey( Estado, on_delete = models.PROTECT, null = True, blank = True )  
    cidade   = models.ForeignKey( Cidade, on_delete = models.PROTECT, null = True, blank = True )  
    endereco = models.TextField( max_length = 300, null = False, blank = False )

    # Campos para troca de senha e confirmação de inscrição
    hash_confirm_register = models.CharField(max_length=128, null=True, blank=True, default="")
    hash_confirm_senha    = models.CharField(max_length=128, null=True, blank=True, default="")

    def hash(self):
        return hashlib.sha512((self.nome + self.user.email).encode('utf-8')).hexdigest() # Gerando hash

##########################################################
# Models de Pagamento
##########################################################
class Situacao_de_pagamento(models.Model):
    id                  = models.AutoField(primary_key = True)  
    descricao           = models.CharField(max_length = 100, null = False, blank = False)  
    descricao_detalhada = models.CharField(max_length = 300, null = True, blank = True, default = "")

class Pagamento(models.Model):
    usuario          = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=False, blank=False)
    status           = models.ForeignKey(Situacao_de_pagamento, on_delete=models.CASCADE, null=True, blank=False)
    codigo_transacao = models.CharField(max_length=32, null=True, blank=True, default="")
