from django.utils import timezone
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Consulta, Anamnese, Receita, Atestado

class PacienteCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
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
        queryset=CustomUser.objects.filter(tipo_usuario=CustomUser.TipoUsuario.MEDICO),
        label="Especialista",
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'})
    )
    
    data_hora = forms.DateTimeField(
        label="Data e Horário",
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control form-control-lg' 
            },
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Consulta
        fields = ['medico', 'data_hora']

    def clean_data_hora(self):
        data_hora_selecionada = self.cleaned_data.get('data_hora')
        if data_hora_selecionada:
            if data_hora_selecionada < timezone.now():
                raise ValidationError(
                    "Não é possível agendar consultas em datas ou horários passados.",
                    code='data_passada'
                )
        return data_hora_selecionada

class AnamneseForm(forms.ModelForm):
    class Meta:
        model = Anamnese
        fields = ['queixas', 'alergias', 'medicamentos_uso_continuo']
        widgets = {
            # ⬇️ ADICIONAMOS A CLASSE 'form-control' para Textareas ⬇️
            'queixas': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'alergias': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'medicamentos_uso_continuo': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
        labels = {
            'queixas': 'Queixa Principal',
            'alergias': 'Alergias Conhecidas',
            'medicamentos_uso_continuo': 'Medicamentos em Uso Contínuo'
        }

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['medicamentos', 'posologia']
        widgets = {
            'medicamentos': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Ex: Amoxicilina 500mg - 1 comprimido a cada 8 horas por 7 dias'}),
            'posologia': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ex: Uso contínuo. / Tomar durante 7 dias.'}),
        }
        labels = {
            'medicamentos': 'Medicamentos e Doses',
            'posologia': 'Instruções de Uso (Posologia)',
        }

class AtestadoForm(forms.ModelForm):
    cid = forms.CharField(
        label="CID (Opcional)", 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: A09'})
    )

    class Meta:
        model = Atestado
        fields = ['periodo_dias', 'cid']
        labels = {
            'periodo_dias': 'Período de Afastamento (em dias)',
        }
        widgets = {
            'periodo_dias': forms.NumberInput(attrs={'min': 1, 'value': 1, 'class': 'form-control'}),
        }