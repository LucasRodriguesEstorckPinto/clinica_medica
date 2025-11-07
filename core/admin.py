from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Consulta, Anamnese, Receita, Atestado, Exame

# Configuração para mostrar os campos customizados (cpf, tipo_usuario) no admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Campos que aparecem na lista de usuários
    list_display = ['username', 'email', 'first_name', 'last_name', 'tipo_usuario']
    # Campos que aparecem ao editar o usuário
    fieldsets = UserAdmin.fieldsets + (
        ('Dados Customizados', {'fields': ('tipo_usuario', 'cpf', 'data_nascimento', 'telefone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Dados Customizados', {'fields': ('tipo_usuario', 'cpf', 'data_nascimento', 'telefone')}),
    )

# Registra os modelos para aparecerem no painel admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Consulta)
admin.site.register(Anamnese)
admin.site.register(Receita)
admin.site.register(Atestado)
admin.site.register(Exame)