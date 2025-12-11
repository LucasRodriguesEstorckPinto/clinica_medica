from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

class EmailOrUsernameBackend(ModelBackend):
    """
    Backend de autenticação customizado.
    Permite o login usando E-MAIL ou USERNAME.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        if username is None:
            return None
            
        try:
            # Tenta encontrar o usuário pelo E-MAIL ou pelo USERNAME
            # A 'Q' object permite consultas 'OU' (OR)
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except UserModel.DoesNotExist:
            # Nenhum usuário encontrado
            return None
        
        # Se encontrou o usuário, verifica a senha
        if user.check_password(password):
            return user
        
        return None 