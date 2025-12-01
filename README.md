<p align="center">
  <h1 align="center">🏥 SIGM - Sistema Integrado de Gestão Médica</h1>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" />
  <img src="https://img.shields.io/badge/Stripe-Payment-008CDD?style=for-the-badge&logo=stripe&logoColor=white" />
  <img src="https://img.shields.io/badge/Architecture-MVC%2FMVT-orange?style=for-the-badge" />
</p>

<p align="center">
  Uma solução web completa para clínicas médicas, focada na jornada digital do paciente, prontuário eletrônico e processamento financeiro automatizado.
</p>

<hr>

## 📖 Sobre o Projeto

O **SIGM** é um sistema desenvolvido com rigorosos princípios de **Engenharia de Software**. O projeto partiu da modelagem conceitual (UML, Casos de Uso) para uma implementação robusta em **Django**.

O diferencial deste sistema é a simulação de um ambiente de produção real, eliminando processos manuais através de:
* **Pagamentos via Cartão de Crédito** (Integração Stripe com Webhooks).
* **Geração Dinâmica de Documentos** (Receitas e Atestados em PDF).
* **Controle de Acesso Baseado em Papéis** (RBAC para Médicos, Pacientes e Recepção).

---

## 🚀 Funcionalidades Principais

### 🩺 Módulo Médico
* **Agenda Inteligente:** Visualização de consultas do dia e agendamentos futuros.
* **Prontuário Eletrônico:** Acesso ao histórico clínico completo do paciente.
* **Painel de Atendimento:** Registro de anamnese (queixas, alergias, medicamentos).
* **Documentos Dinâmicos:** Geração automática de **Receitas e Atestados em PDF** prontos para impressão ou envio digital.

### 👤 Módulo Paciente
* **Autenticação Moderna:** Login simplificado via e-mail (sem necessidade de username).
* **Agendamento:** Marcação de consultas com validação automática de conflitos de horário e regras de negócio (ex: cancelamento 24h).
* **Pagamentos:** Checkout transparente com **Stripe**. O status da consulta muda automaticamente após a confirmação bancária.
* **Histórico:** Acesso a consultas passadas, download de documentos médicos e visualização de laudos de exames.

### 🏥 Módulo Administrativo (Recepção)
* **Painel de Controle:** Visão geral da agenda de todos os médicos do dia.
* **Financeiro:** Geração de relatórios de faturamento mensal consolidados.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3.12, Django Framework.
* **Banco de Dados:** SQLite (Modelagem Relacional Otimizada).
* **Frontend:** Bootstrap 5 (Responsivo, UI/UX Limpa).
* **Pagamentos:** Stripe API & Stripe Webhooks (Processamento Assíncrono).
* **Relatórios/PDF:** WeasyPrint (HTML to PDF).
* **Integração Sistema:** PyGObject, Cairo, Pango (Dependências gráficas para PDF).

---

## 💻 Guia de Instalação e Configuração

Siga os passos abaixo rigorosamente para configurar o ambiente de desenvolvimento.

### 1. Clone o Repositório
```bash
git clone [https://github.com/seu-usuario/clinica-medica.git](https://github.com/seu-usuario/clinica-medica.git)
cd clinica-medica
```

---

### 2. Configuração do Ambiente Virtual
```bash
python3 -m venv venv

# Ativa o ambiente
# No macOS/Linux:
source venv/bin/activate
# No Windows:
venv\Scripts\activate
```

---


### 3. Instalação de Dependências Python
```bash
pip install django stripe weasyprint PyGObject
```

---

### 4. Configuração das Chaves de API (Stripe)
Você precisa de uma conta no Stripe para processar pagamentos.

- Obtenha suas chaves de teste (pk_test_... e sk_test_...) no Dashboard.
- Abra o arquivo clinica_medica/settings.py.
- Configure as variáveis no final do arquivo:

```bash
# Em clinica_medica/settings.py

STRIPE_PUBLIC_KEY = 'sua_chave_publica_aqui' # Começa com pk_test_
STRIPE_SECRET_KEY = 'sua_chave_secreta_aqui' # Começa com sk_test_
# STRIPE_WEBHOOK_SECRET = será obtida no passo de execução abaixo
```

---


### 5. Preparação do Banco de Dados

```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
```

---

### COMO EXECUTAR 

```bash
python3 manage.py runserver
stripe listen --events checkout.session.completed --forward-to [http://127.0.0.1:8000/pagamentos/stripe-webhook/](http://127.0.0.1:8000/pagamentos/stripe-webhook/)
```

### NO NAVEGADOR
```bash
http://127.0.0.1:8000/cadastro/
```


### IMPORTANTE 

Ao rodar o comando acima, o terminal exibirá uma mensagem como: > Ready! Your webhook signing secret is whsec_...

- Copie essa chave (whsec_...).
- Vá no seu settings.py.
- Atualize a variável STRIPE_WEBHOOK_SECRET com ela. Se você reiniciar o Stripe Listener, essa chave mudará e você precisará atualizar novamente.




