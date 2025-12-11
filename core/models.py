from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. MODELO USUARIO (Baseado no diagrama)
# Vamos estender o usuário padrão do Django para adicionar os campos do seu diagrama
class CustomUser(AbstractUser):
    # Enumeração para os tipos de usuário (Paciente, Medico, Recepcionista)
    class TipoUsuario(models.TextChoices):
        PACIENTE = 'PACIENTE', 'Paciente'
        MEDICO = 'MEDICO', 'Médico'
        RECEPCIONISTA = 'RECEPCIONISTA', 'Recepcionista'

    
    email = models.EmailField(unique=True)
    tipo_usuario = models.CharField(max_length=15, choices=TipoUsuario.choices, default=TipoUsuario.PACIENTE)
    cpf = models.CharField(max_length=14, unique=True) 
    data_nascimento = models.DateField(null=True, blank=True)  
    telefone = models.CharField(max_length=15, null=True, blank=True)
    
    # O Django já cuida de: nome, e-mail, senha

    def __str__(self):
        return self.get_full_name() or self.username

# 2. MODELO CONSULTA
class Consulta(models.Model):
    class StatusConsulta(models.TextChoices):
        MARCADA = 'MARCADA', 'Marcada'
        PAGA = 'PAGA', 'Paga'
        CONCLUIDA = 'CONCLUIDA', 'Concluída'
        CANCELADA = 'CANCELADA', 'Cancelada'

    # Relacionamentos baseados no diagrama
    paciente = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='consultas_paciente')
    medico = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='consultas_medico')
    
    # Atributos
    data_hora = models.DateTimeField() #
    status = models.CharField(max_length=10, choices=StatusConsulta.choices, default=StatusConsulta.MARCADA)

    # Armazena o ID do 'Payment Intent' do Stripe.
    # É assim que saberemos qual consulta o webhook está se referindo.
    stripe_checkout_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Consulta de {self.paciente.username} com {self.medico.username} em {self.data_hora}"



class Anamnese(models.Model):
    consulta = models.OneToOneField(Consulta, on_delete=models.CASCADE, related_name='anamnese') 
    queixas = models.TextField(blank=True) 
    alergias = models.TextField(blank=True) 
    medicamentos_uso_continuo = models.TextField(blank=True, verbose_name="Medicamentos em Uso") 
  
    def __str__(self):
        return f"Anamnese da consulta {self.consulta.id}"

class Receita(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='receitas') # Ligado à consulta [cite: 35]
    medicamentos = models.TextField() 
    posologia = models.TextField() 
    assinatura_digital = models.CharField(max_length=100) 
    qrcode = models.CharField(max_length=255, blank=True) 
    
    def __str__(self):
        return f"Receita da consulta {self.consulta.id}"

class Atestado(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='atestados')  
    periodo_dias = models.IntegerField(default=1)
    cid = models.CharField(max_length=10, blank=True, verbose_name="CID") 
    assinatura_digital = models.CharField(max_length=100) 
    
    def __str__(self):
        return f"Atestado da consulta {self.consulta.id} ({self.periodo_dias} dias)"

class Exame(models.Model):
    paciente = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='exames') 
    tipo = models.CharField(max_length=100) 
    data_solicitacao = models.DateField(auto_now_add=True)
    data_laudo = models.DateField(null=True, blank=True) 
    profissional_resp = models.CharField(max_length=100, blank=True, verbose_name="Profissional Responsável")
    arquivo_resultado = models.FileField(upload_to='exames/', null=True, blank=True, verbose_name="Resultado (PDF/Imagem)")
    def __str__(self):
        return f"Exame de {self.tipo} para {self.paciente.username}"