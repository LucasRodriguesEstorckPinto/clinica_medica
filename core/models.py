# Em: core/models.py

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
    cpf = models.CharField(max_length=14, unique=True) # [cite: 3]
    data_nascimento = models.DateField(null=True, blank=True)  # [cite: 3]
    telefone = models.CharField(max_length=15, null=True, blank=True) # [cite: 3]
    
    # O Django já cuida de: nome, e-mail, senha

    def __str__(self):
        return self.get_full_name() or self.username

# 2. MODELO CONSULTA
class Consulta(models.Model):
    class StatusConsulta(models.TextChoices):
        MARCADA = 'MARCADA', 'Marcada'
        PAGA = 'PAGA', 'Paga' # [cite: 18]
        CONCLUIDA = 'CONCLUIDA', 'Concluída'
        CANCELADA = 'CANCELADA', 'Cancelada' # [cite: 10]

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

# 3. MODELOS DO PRONTUÁRIO (Anamnese, Receita, Atestado, Exame)
# O Prontuário é o conjunto desses itens, 
# todos ligados ao Paciente ou à Consulta.

class Anamnese(models.Model):
    consulta = models.OneToOneField(Consulta, on_delete=models.CASCADE, related_name='anamnese') # Ligado à consulta [cite: 40]
    queixas = models.TextField(blank=True) # [cite: 39]
    alergias = models.TextField(blank=True) # [cite: 39]
    medicamentos_uso_continuo = models.TextField(blank=True, verbose_name="Medicamentos em Uso") # [cite: 39]
    # ... outros campos da anamnese [cite: 39]
    
    def __str__(self):
        return f"Anamnese da consulta {self.consulta.id}"

class Receita(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='receitas') # Ligado à consulta [cite: 35]
    medicamentos = models.TextField() # [cite: 34]
    posologia = models.TextField() # [cite: 34]
    assinatura_digital = models.CharField(max_length=100) # [cite: 34]
    qrcode = models.CharField(max_length=255, blank=True) # [cite: 35]
    
    def __str__(self):
        return f"Receita da consulta {self.consulta.id}"

class Atestado(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='atestados') # Ligado à consulta [cite: 37]
    periodo_dias = models.IntegerField(default=1) # [cite: 37]
    cid = models.CharField(max_length=10, blank=True, verbose_name="CID") # [cite: 37]
    assinatura_digital = models.CharField(max_length=100) # [cite: 37]
    
    def __str__(self):
        return f"Atestado da consulta {self.consulta.id} ({self.periodo_dias} dias)"

class Exame(models.Model):
    paciente = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='exames') # Ligado ao paciente [cite: 13]
    tipo = models.CharField(max_length=100) # [cite: 14]
    data_solicitacao = models.DateField(auto_now_add=True)
    data_laudo = models.DateField(null=True, blank=True) # [cite: 15]
    profissional_resp = models.CharField(max_length=100, blank=True, verbose_name="Profissional Responsável") # [cite: 15]
    arquivo_resultado = models.FileField(upload_to='exames/', null=True, blank=True, verbose_name="Resultado (PDF/Imagem)") # [cite: 15]

    def __str__(self):
        return f"Exame de {self.tipo} para {self.paciente.username}"