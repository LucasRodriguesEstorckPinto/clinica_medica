from django.utils import timezone
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Consulta, Anamnese, Receita, Atestado

class PacienteCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # Campos que o paciente deve preencher
        # [cite: 3]
        fields = ('first_name', 'last_name', 'email', 'cpf', 'data_nascimento', 'telefone')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        # Define este usuário como Paciente por padrão
        user.tipo_usuario = CustomUser.TipoUsuario.PACIENTE 
        if commit:
            user.save()
        return user


class ConsultaForm(forms.ModelForm):
    medico = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(tipo_usuario=CustomUser.TipoUsuario.MEDICO)
    )
    
    data_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Consulta
        fields = ['medico', 'data_hora']

    # ⬇️ 2. ADICIONE ESTE MÉTODO DE VALIDAÇÃO ⬇️
    def clean_data_hora(self):
        """
        Validação customizada para o campo 'data_hora'.
        Garante que a data/hora não esteja no passado.
        """
        # Pega o valor do campo já limpo pelo Django
        data_hora_selecionada = self.cleaned_data.get('data_hora')
        
        # Se o campo não estiver vazio (já passou na validação básica)
        if data_hora_selecionada:
            # Compara com o horário atual (com fuso horário)
            if data_hora_selecionada < timezone.now():
                # Lança um erro de validação
                raise ValidationError(
                    "Não é possível agendar consultas em datas ou horários passados.",
                    code='data_passada'
                )
        
        # Sempre retorne o dado limpo
        return data_hora_selecionada


class AnamneseForm(forms.ModelForm):
    class Meta:
        model = Anamnese
        # Campos baseados no seu diagrama
        fields = ['queixas', 'alergias', 'medicamentos_uso_continuo']
        widgets = {
            'queixas': forms.Textarea(attrs={'rows': 4}),
            'alergias': forms.Textarea(attrs={'rows': 4}),
            'medicamentos_uso_continuo': forms.Textarea(attrs={'rows': 4}),
        }


class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        # Campos baseados no seu diagrama/critérios
        fields = ['medicamentos', 'posologia']
        widgets = {
            'medicamentos': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Ex: Amoxicilina 500mg - 1 comprimido a cada 8 horas por 7 dias'}),
            'posologia': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ex: Uso contínuo. / Tomar durante 7 dias.'}),
        }
        labels = {
            'medicamentos': 'Medicamentos e Doses',
            'posologia': 'Instruções de Uso (Posologia)',
        }


class AtestadoForm(forms.ModelForm):
    # [cite_start]Campo CID é opcional, conforme critério de aceitação [cite: 37]
    cid = forms.CharField(
        label="CID (Opcional)", 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: A09'})
    )

    class Meta:
        model = Atestado
        fields = ['periodo_dias', 'cid']
        labels = {
            'periodo_dias': 'Período de Afastamento (em dias)',
        }
        widgets = {
            'periodo_dias': forms.NumberInput(attrs={'min': 1, 'value': 1}),
        }