from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from .models import CustomUser, Consulta, Exame, Anamnese, Receita, Atestado
from .forms import PacienteCreationForm, ConsultaForm, AnamneseForm, ReceitaForm, AtestadoForm
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.views.generic import TemplateView 
import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

stripe.api_key = settings.STRIPE_SECRET_KEY

class CadastroPacienteView(CreateView):
    form_class = PacienteCreationForm
    # Redireciona para o 'login' após o sucesso
    success_url = reverse_lazy('login') 
    template_name = 'core/cadastro.html'

method_decorator(login_required, name='dispatch')
class HomeView(View):
    def get(self, request, *args, **kwargs):
        
        usuario = request.user
        if usuario.is_superuser or usuario.tipo_usuario == CustomUser.TipoUsuario.RECEPCIONISTA:
            
            agora = timezone.now()
            
            consultas_hoje = Consulta.objects.filter(
                data_hora__date=agora.date()
            ).order_by('data_hora')
            
            context = {
                'usuario': usuario,
                'consultas_hoje': consultas_hoje
            }
            return render(request, 'core/recepcionista_home.html', context)
        
        elif usuario.tipo_usuario == CustomUser.TipoUsuario.MEDICO:
            
            agora = timezone.now()
            
            consultas_hoje = Consulta.objects.filter(
                medico=usuario,
                data_hora__gte=agora,
                data_hora__date=agora.date(),
                status__in=[Consulta.StatusConsulta.MARCADA, Consulta.StatusConsulta.PAGA] # Filtra apenas pendentes
            ).order_by('data_hora')
            
            consultas_futuras = Consulta.objects.filter(
                medico=usuario,
                data_hora__date__gt=agora.date(),
                status__in=[Consulta.StatusConsulta.MARCADA, Consulta.StatusConsulta.PAGA] # Filtra apenas pendentes
            ).order_by('data_hora')
            
            # ⬇️ ADICIONE ESTA NOVA CONSULTA ⬇️
            consultas_concluidas = Consulta.objects.filter(
                medico=usuario,
                status=Consulta.StatusConsulta.CONCLUIDA
            ).order_by('-data_hora')[:10] # Pega as últimas 10 concluídas
            
            context = {
                'usuario': usuario,
                'consultas_hoje': consultas_hoje,
                'consultas_futuras': consultas_futuras,
                'consultas_concluidas': consultas_concluidas
            }
            return render(request, 'core/medico_home.html', context)
        
        else: # Paciente
            context = {'usuario': usuario}
            return render(request, 'core/home.html', context)
        

@method_decorator(login_required, name='dispatch')
class HistoricoFinanceiroView(View):
    """
    Controlador para listar o histórico financeiro do paciente
    (consultas pendentes E pagas).
    """
    def get(self, request, *args, **kwargs):
        # 1. Busca consultas pendentes (status MARCADA)
        consultas_pendentes = Consulta.objects.filter(
            paciente=request.user, 
            status=Consulta.StatusConsulta.MARCADA
        ).order_by('data_hora')
        
        # 2. Busca consultas já pagas (status PAGA)
        consultas_pagas = Consulta.objects.filter(
            paciente=request.user, 
            status=Consulta.StatusConsulta.PAGA
        ).order_by('-data_hora') # (Mais recentes primeiro)
        
        context = {
            'consultas_pendentes': consultas_pendentes,
            'consultas_pagas': consultas_pagas
        }
        # Vamos continuar usando o mesmo nome de template
        return render(request, 'core/pagar_consulta.html', context)
    

@method_decorator(login_required, name='dispatch')
class CriarCheckoutSessionView(View):
    def post(self, request, consulta_id, *args, **kwargs):
        consulta = get_object_or_404(Consulta, id=consulta_id, paciente=request.user)

        # Domínio do seu site (para o Stripe redirecionar de volta)
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        
        try:
            # Crie a Sessão de Checkout no Stripe
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'brl', # Moeda: Real Brasileiro
                            'product_data': {
                                'name': f'Consulta com Dr(a). {consulta.medico.first_name}',
                                'description': f'Agendada para: {consulta.data_hora.strftime("%d/%m/%Y %H:%M")}',
                            },
                            # PREÇO EM CENTAVOS: 15000 = R$ 150,00
                            # (Em um projeto real, puxe isso do BD)
                            'unit_amount': 15000, 
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                # URLs de redirecionamento
                success_url=YOUR_DOMAIN + reverse('sucesso_pagamento'),
                cancel_url=YOUR_DOMAIN + reverse('cancelado_pagamento'),
            )
            
            # Salva o ID do "Payment Intent" na consulta
            # Isso é VITAL para o webhook saber qual consulta foi paga
            consulta.stripe_checkout_id = checkout_session.id
            consulta.save()

            # Redireciona o usuário para a página de pagamento do Stripe
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            # Lide com o erro (por enquanto, apenas redirecionamos)
            return redirect('pagar_consulta')


class SucessoPagamentoView(TemplateView):
    template_name = 'core/sucesso.html'

class CanceladoPagamentoView(TemplateView):
    template_name = 'core/cancelado.html'


@csrf_exempt
@require_POST
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    
    # MUDAMOS O EVENTO QUE OUVIMOS
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        checkout_session_id = session.get('id') # Pegamos o ID 'cs_...'

        print(f"Webhook recebido: checkout.session.completed (ID: {checkout_session_id})")

        # Encontre a consulta no seu banco de dados
        try:
            # MUDAMOS O CAMPO DA BUSCA
            consulta = Consulta.objects.get(stripe_checkout_id=checkout_session_id)
            
            # ATUALIZA O STATUS DA CONSULTA
            if consulta.status == Consulta.StatusConsulta.MARCADA:
                consulta.status = Consulta.StatusConsulta.PAGA
                consulta.save()
                print(f"Pagamento da Consulta {consulta.id} confirmado com sucesso!")
            else:
                print(f"Consulta {consulta.id} já estava com status '{consulta.status}'.")

        except Consulta.DoesNotExist:
            print(f"ERRO: Consulta com ID de checkout {checkout_session_id} não encontrada.")
            return HttpResponse(status=404)
        except Exception as e:
            print(f"ERRO ao processar pagamento: {e}")
            return HttpResponse(status=500)

    else:
        print(f"Evento de webhook não tratado: {event['type']}")

    return HttpResponse(status=200)


@method_decorator(login_required, name='dispatch')
class MarcarConsultaView(View):
    template_name = 'core/marcar_consulta.html'

    def get(self, request, *args, **kwargs):
        form = ConsultaForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ConsultaForm(request.POST)
        
        if form.is_valid():
            # Critério de Aceitação: "verificação de conflitos" 
            # (Lógica baseada no diagrama 'AGENDA')
            
            nova_consulta = form.save(commit=False)
            
            # 1. Verifica se já existe consulta do MÉDICO nesse horário
            conflito_medico = Consulta.objects.filter(
                medico=nova_consulta.medico,
                data_hora=nova_consulta.data_hora
            ).exists()

            # 2. Verifica se o PACIENTE já tem consulta nesse horário
            conflito_paciente = Consulta.objects.filter(
                paciente=request.user,
                data_hora=nova_consulta.data_hora
            ).exists()

            if conflito_medico:
                form.add_error(None, 'Este médico não está disponível no horário selecionado.')
            elif conflito_paciente:
                form.add_error(None, 'Você já possui uma consulta marcada neste mesmo horário.')
            else:
                # Se não houver conflitos, salva a consulta
                nova_consulta.paciente = request.user
                nova_consulta.status = Consulta.StatusConsulta.MARCADA
                nova_consulta.save()
                
                # Redireciona o usuário direto para a página de pagamentos
                return redirect('pagar_consulta')

        # Se o formulário for inválido ou houver conflito, renderiza a página novamente
        return render(request, self.template_name, {'form': form})

@method_decorator(login_required, name='dispatch')
class MinhasConsultasView(View):
    template_name = 'core/minhas_consultas.html'

    def get(self, request, *args, **kwargs):
        agora = timezone.now()
        
        # Consultas futuras (marcadas ou pagas)
        consultas_futuras = Consulta.objects.filter(
            paciente=request.user,
            data_hora__gt=agora, # __gt = "maior que" (greater than)
            status__in=[Consulta.StatusConsulta.MARCADA, Consulta.StatusConsulta.PAGA]
        ).order_by('data_hora')
        
        # Consultas passadas ou canceladas
        consultas_passadas = Consulta.objects.filter(
            paciente=request.user
        ).exclude(
            id__in=consultas_futuras.values_list('id', flat=True)
        ).order_by('-data_hora')
        
        context = {
            'consultas_futuras': consultas_futuras,
            'consultas_passadas': consultas_passadas
        }
        return render(request, self.template_name, context)

  
@method_decorator(login_required, name='dispatch')
class CancelarConsultaView(View):
    def post(self, request, consulta_id, *args, **kwargs):
        consulta = get_object_or_404(Consulta, id=consulta_id, paciente=request.user)
        
        # REGRA DE NEGÓCIO: Critério de Aceitação 
        # Só pode cancelar com 24h de antecedência
        limite_cancelamento = consulta.data_hora - timedelta(hours=24)

        if timezone.now() > limite_cancelamento:
            # Se o tempo atual for MAIOR que o limite, bloqueia
            messages.error(request, 'Erro: Consultas só podem ser canceladas com mais de 24 horas de antecedência.')
        else:
            # Se for permitido, cancela
            consulta.status = Consulta.StatusConsulta.CANCELADA
            consulta.save()
            messages.success(request, 'Consulta cancelada com sucesso!')
        
        # Redireciona de volta para a lista de consultas
        return redirect('minhas_consultas')
    

@method_decorator(login_required, name='dispatch')
class MinhasExamesView(View):
    """
    Controlador para listar os exames e laudos do paciente.
    """
    template_name = 'core/meus_exames.html'

    def get(self, request, *args, **kwargs):
        # Busca exames do paciente logado, ordenados por data
        meus_exames = Exame.objects.filter(
            paciente=request.user
        ).order_by('-data_laudo') # Lista por data 
        
        context = {
            'meus_exames': meus_exames
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class AnamneseView(View):
    template_name = 'core/anamnese_form.html'

    def get(self, request, consulta_id, *args, **kwargs):
        # Garante que o médico só acesse sua própria consulta
        consulta = get_object_or_404(Consulta, id=consulta_id, medico=request.user)
        
        # Tenta buscar a anamnese. Se não existir, 'instance' será None.
        try:
            anamnese_existente = Anamnese.objects.get(consulta=consulta)
            form = AnamneseForm(instance=anamnese_existente)
        except Anamnese.DoesNotExist:
            form = AnamneseForm()
            
        context = {
            'form': form,
            'consulta': consulta
        }
        return render(request, self.template_name, context)

    def post(self, request, consulta_id, *args, **kwargs):
        consulta = get_object_or_404(Consulta, id=consulta_id, medico=request.user)
        
        # Tenta buscar a anamnese. Se não existir, 'instance' será None.
        try:
            anamnese_existente = Anamnese.objects.get(consulta=consulta)
            form = AnamneseForm(request.POST, instance=anamnese_existente)
        except Anamnese.DoesNotExist:
            form = AnamneseForm(request.POST)

        if form.is_valid():
            nova_anamnese = form.save(commit=False)
            nova_anamnese.consulta = consulta # Garante a ligação com a consulta
            nova_anamnese.save()
            
            # Redireciona de volta para a agenda do médico
            return redirect('home') 

        # Se o formulário for inválido
        context = {
            'form': form,
            'consulta': consulta
        }
        return render(request, self.template_name, context)
    

@method_decorator(login_required, name='dispatch')
class ReceitaView(View):
    template_name = 'core/receita_form.html'

    def get(self, request, consulta_id, *args, **kwargs):
        consulta = get_object_or_404(Consulta, id=consulta_id, medico=request.user)
        
        # Tenta buscar a receita. Se não existir, 'instance' será None.
        try:
            receita_existente = Receita.objects.get(consulta=consulta)
            form = ReceitaForm(instance=receita_existente)
        except Receita.DoesNotExist:
            form = ReceitaForm()
            
        context = {
            'form': form,
            'consulta': consulta
        }
        return render(request, self.template_name, context)

    def post(self, request, consulta_id, *args, **kwargs):
        consulta = get_object_or_404(Consulta, id=consulta_id, medico=request.user)
        
        # Tenta buscar a receita para editá-la
        try:
            receita_existente = Receita.objects.get(consulta=consulta)
            form = ReceitaForm(request.POST, instance=receita_existente)
        except Receita.DoesNotExist:
            form = ReceitaForm(request.POST)

        if form.is_valid():
            nova_receita = form.save(commit=False)
            nova_receita.consulta = consulta # Garante a ligação com a consulta
            
            # Simulação da Assinatura Digital (Critério de Aceitação) 
            nova_receita.assinatura_digital = f"Dr(a). {request.user.get_full_name()} (Assinado Digitalmente)"
            
            # Simulação do QR Code (Critério de Aceitação) [cite: 35]
            # (A geração real exigiria outra biblioteca)
            nova_receita.qrcode = f"validar-receita/{nova_receita.id}" 
            
            nova_receita.save()
            
            # Redireciona de volta para o "painel de atendimento" (a Anamnese)
            messages.success(request, 'Receita salva com sucesso!')
            return redirect('cadastrar_anamnese', consulta_id=consulta.id) 

        # Se o formulário for inválido
        context = {
            'form': form,
            'consulta': consulta
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class AtestadoView(View):
    template_name = 'core/atestado_form.html'

    def get(self, request, consulta_id, *args, **kwargs):
        consulta = get_object_or_404(Consulta, id=consulta_id, medico=request.user)
        
        try:
            atestado_existente = Atestado.objects.get(consulta=consulta)
            form = AtestadoForm(instance=atestado_existente)
        except Atestado.DoesNotExist:
            form = AtestadoForm()
            
        context = {
            'form': form,
            'consulta': consulta
        }
        return render(request, self.template_name, context)

    def post(self, request, consulta_id, *args, **kwargs):
        consulta = get_object_or_404(Consulta, id=consulta_id, medico=request.user)
        
        try:
            atestado_existente = Atestado.objects.get(consulta=consulta)
            form = AtestadoForm(request.POST, instance=atestado_existente)
        except Atestado.DoesNotExist:
            form = AtestadoForm(request.POST)

        if form.is_valid():
            novo_atestado = form.save(commit=False)
            novo_atestado.consulta = consulta # Garante a ligação
            
            # [cite_start]Simulação da Assinatura Digital (Critério de Aceitação) [cite: 37]
            novo_atestado.assinatura_digital = f"Dr(a). {request.user.get_full_name()} (Assinado Digitalmente)"
            
            novo_atestado.save()
            
            # Redireciona de volta para o "painel de atendimento" (a Anamnese)
            messages.success(request, 'Atestado salvo com sucesso!')
            return redirect('cadastrar_anamnese', consulta_id=consulta.id) 

        # Se o formulário for inválido
        context = {
            'form': form,
            'consulta': consulta
        }
        return render(request, self.template_name, context)
    

@method_decorator(login_required, name='dispatch')
class ProntuarioView(View):
    """
    Controlador para exibir o histórico completo (Prontuário) de um paciente
    para o médico.
    """
    template_name = 'core/prontuario.html'

    def get(self, request, paciente_id, *args, **kwargs):
        # Apenas médicos e recepcionistas podem ver prontuários
        if not (request.user.tipo_usuario == CustomUser.TipoUsuario.MEDICO or 
                request.user.tipo_usuario == CustomUser.TipoUsuario.RECEPCIONISTA):
            return redirect('home')

        # Busca o paciente (que é um CustomUser) pelo ID
        paciente = get_object_or_404(CustomUser, id=paciente_id, tipo_usuario=CustomUser.TipoUsuario.PACIENTE)
        
        # Busca todo o histórico cronológico (Critério de Aceitação) 
        consultas = Consulta.objects.filter(paciente=paciente).order_by('-data_hora')
        exames = Exame.objects.filter(paciente=paciente).order_by('-data_laudo')
        
        context = {
            'paciente': paciente,
            'consultas': consultas, # Lista principal
            'exames': exames         # Lista separada de exames
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class ConcluirConsultaView(View):
    """
    Controlador para marcar uma consulta como 'CONCLUÍDA'.
    Esta view só aceita POST.
    """
    def post(self, request, consulta_id, *args, **kwargs):
        # Garante que o médico só possa concluir suas próprias consultas
        consulta = get_object_or_404(Consulta, id=consulta_id, medico=request.user)
        
        # Altera o status
        consulta.status = Consulta.StatusConsulta.CONCLUIDA
        consulta.save()
        
        # Avisa o médico e redireciona para a agenda principal
        messages.success(request, f'Atendimento do paciente {consulta.paciente.first_name} concluído com sucesso!')
        return redirect('home')


@method_decorator(login_required, name='dispatch')
class DetalheConsultaView(View):
    """
    Controlador para o PACIENTE ver os detalhes
    de uma consulta concluída.
    """
    template_name = 'core/detalhe_consulta.html'

    def get(self, request, consulta_id, *args, **kwargs):
        # Garante que o paciente só possa ver suas próprias consultas
        consulta = get_object_or_404(Consulta, id=consulta_id, paciente=request.user)
        
        # Busca os documentos associados (se existirem)
        try:
            anamnese = Anamnese.objects.get(consulta=consulta)
        except Anamnese.DoesNotExist:
            anamnese = None
            
        receitas = Receita.objects.filter(consulta=consulta)
        atestados = Atestado.objects.filter(consulta=consulta)
        
        context = {
            'consulta': consulta,
            'anamnese': anamnese,
            'receitas': receitas,
            'atestados': atestados
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class ReceitaPDFView(View):
    """
    Gera e serve o PDF de uma Receita Médica.
    """
    def get(self, request, receita_id, *args, **kwargs):
        # Busca o objeto Receita
        receita = get_object_or_404(Receita, id=receita_id)
        
        # Garante que apenas o médico ou o paciente da consulta possam ver
        user = request.user
        if user != receita.consulta.medico and user != receita.consulta.paciente:
            return HttpResponse("Acesso Negado", status=403)
            
        # 1. Renderiza o template HTML para uma string
        context = {'receita': receita}
        html_string = render_to_string('core/receita_pdf.html', context)
        
        # 2. Converte o HTML para PDF usando WeasyPrint
        html = HTML(string=html_string)
        pdf_file = html.write_pdf()
        
        # 3. Cria a Resposta HTTP com o PDF
        response = HttpResponse(pdf_file, content_type='application/pdf')
        
        # 4. Define o cabeçalho para forçar o download (opcional, mas recomendado)
        response['Content-Disposition'] = f'filename="receita_consulta_{receita.consulta.id}.pdf"'
        
        return response


@method_decorator(login_required, name='dispatch')
class AtestadoPDFView(View):
    """
    Gera e serve o PDF de um Atestado Médico.
    """
    def get(self, request, atestado_id, *args, **kwargs):
        # 1. Busca o objeto Atestado
        atestado = get_object_or_404(Atestado, id=atestado_id)
        
        # 2. Garante que apenas o médico ou o paciente da consulta possam ver
        user = request.user
        if user != atestado.consulta.medico and user != atestado.consulta.paciente:
            return HttpResponse("Acesso Negado", status=403)
            
        # 3. Renderiza o template HTML para uma string
        context = {'atestado': atestado}
        html_string = render_to_string('core/atestado_pdf.html', context)
        
        # 4. Converte o HTML para PDF
        html = HTML(string=html_string)
        pdf_file = html.write_pdf()
        
        # 5. Cria a Resposta HTTP com o PDF
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'filename="atestado_consulta_{atestado.consulta.id}.pdf"'
        
        return response


@method_decorator(login_required, name='dispatch')
class RelatorioFinanceiroView(View):
    template_name = 'core/relatorio_financeiro.html'

    def get(self, request, *args, **kwargs):
        # 1. Garante permissão (Apenas Recepcionista ou Admin)
        if not (request.user.is_superuser or 
                request.user.tipo_usuario == CustomUser.TipoUsuario.RECEPCIONISTA):
            return redirect('home')

        # 2. Define o período (Mês Atual)
        agora = timezone.now()
        mes_atual = agora.month
        ano_atual = agora.year

        # 3. Busca consultas PAGAS ou CONCLUÍDAS neste mês
        consultas = Consulta.objects.filter(
            data_hora__year=ano_atual,
            data_hora__month=mes_atual,
            status__in=[Consulta.StatusConsulta.PAGA, Consulta.StatusConsulta.CONCLUIDA]
        ).order_by('data_hora')

        # 4. Calcula o Total (Assumindo R$ 150,00 por consulta)
        valor_consulta = 150.00
        total_receita = consultas.count() * valor_consulta

        context = {
            'consultas': consultas,
            'total_receita': total_receita,
            'mes': agora.strftime('%B/%Y'), # Ex: Novembro/2025
            'valor_fixo': valor_consulta
        }
        
        return render(request, self.template_name, context)