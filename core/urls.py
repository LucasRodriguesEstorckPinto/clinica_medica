
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CadastroPacienteView, HomeView, HistoricoFinanceiroView, CriarCheckoutSessionView ,SucessoPagamentoView, CanceladoPagamentoView, stripe_webhook_view, MarcarConsultaView, MinhasConsultasView, CancelarConsultaView, MinhasExamesView, AnamneseView, ReceitaView, AtestadoView, ProntuarioView, ConcluirConsultaView

urlpatterns = [
    # Rota para o cadastro
    path('cadastro/', CadastroPacienteView.as_view(), name='cadastro'),
    # Rota 'home' (página principal)
    path('', HomeView.as_view(), name='home'), # <-- ADICIONE ESTA LINHA
    
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('pagamentos/', HistoricoFinanceiroView.as_view(), name='pagar_consulta'),

    # Rota que o botão "Pagar" vai chamar
    path('pagamentos/criar-checkout-session/<int:consulta_id>/', CriarCheckoutSessionView.as_view(), name='criar_checkout_session'),
    
    # Rotas de redirecionamento do Stripe
    path('pagamentos/sucesso/', SucessoPagamentoView.as_view(), name='sucesso_pagamento'),
    path('pagamentos/cancelado/', CanceladoPagamentoView.as_view(), name='cancelado_pagamento'),
    path('pagamentos/stripe-webhook/', stripe_webhook_view, name='stripe_webhook'),

    path('marcar-consulta/', MarcarConsultaView.as_view(), name='marcar_consulta'),

    path('consultas/', MinhasConsultasView.as_view(), name='minhas_consultas'),
    path('consultas/cancelar/<int:consulta_id>/', CancelarConsultaView.as_view(), name='cancelar_consulta'),

    path('meus-exames/', MinhasExamesView.as_view(), name='meus_exames'),

    path('consulta/<int:consulta_id>/anamnese/', AnamneseView.as_view(), name='cadastrar_anamnese'),

    path('consulta/<int:consulta_id>/receita/', ReceitaView.as_view(), name='emitir_receita'),

    path('consulta/<int:consulta_id>/atestado/', AtestadoView.as_view(), name='emitir_atestado'),

    path('prontuario/<int:paciente_id>/', ProntuarioView.as_view(), name='prontuario_paciente'),

    path('consulta/<int:consulta_id>/concluir/', ConcluirConsultaView.as_view(), name='concluir_consulta'),

]