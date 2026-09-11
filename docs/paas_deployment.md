# Guia Comparativo e Passo a Passo: Implantação em Plataformas PaaS
## Plataformas Analisadas: Render, Railway, Vercel e Heroku
**Requisito Atendido:** *"PaaS: Usar uma plataforma que automatize parte da infraestrutura para publicar uma aplicação web simples, com back-end, front-end, acesso a banco de dados e link público de acesso."*

---

## 1. RENDER.COM (Opção Recomendada para o Trabalho)

O **Render** é atualmente a plataforma PaaS mais recomendada para trabalhos acadêmicos de computação em nuvem, pois oferece deploy nativo do GitHub, suporte a Docker, banco de dados PostgreSQL gerenciado gratuito e certificado SSL automático sem exigir cartão de crédito.

### 1.1 Pré-requisitos
- Conta no [Render.com](https://render.com) (cadastre-se usando sua conta do GitHub).
- Repositório público no GitHub com os arquivos do projeto (`server.py`, `Dockerfile`, `requirements.txt`, etc.).

### 1.2 Passo a Passo: Criando o Banco de Dados PostgreSQL Gratuito
1. No dashboard do Render, clique em **New +** e selecione **PostgreSQL**.
2. Preencha os campos:
   - **Name:** `jiujitsu-postgres`
   - **Database:** `jiujitsudb`
   - **User:** `jiuuser`
   - **Region:** Ohio (US East) ou Frankfurt (escolha a mesma para a aplicação).
   - **Plan Type:** Selecione **Free** (1 GB de armazenamento, 90 dias de persistência contínua).
3. Clique em **Create Database**.
4. Quando o banco estiver criado, copie o campo **Internal Database URL** (exemplo: `postgres://jiuuser:senha@dpg-xxxx-a.render.com/jiujitsudb`).

### 1.3 Passo a Passo: Criando o Web Service (Back-end + Front-end)
1. No dashboard do Render, clique em **New +** e selecione **Web Service**.
2. Conecte o repositório GitHub: `lucasbombev/jiujitsu-soa`.
3. Configure as opções:
   - **Name:** `jiujitsu-cloud-app`
   - **Language / Environment:** Selecione **Docker** (o Render usará o nosso `Dockerfile` automaticamente) OU selecione **Python 3**.
   - Se selecionar Python:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Selecione **Free**.
4. Adicione as **Environment Variables** (Variáveis de Ambiente):
   - `DATABASE_URL`: Cole a *Internal Database URL* obtida no passo anterior.
   - `PORT`: `10000` (ou deixe a porta padrão do Render).
   - `ADMIN_USER`: `admin`
   - `ADMIN_PASSWORD`: `senha_jiujitsu_123`
   - `SECRET_KEY`: `render-secret-key-jiujitsu-2026`
5. Clique em **Create Web Service**.
6. O Render iniciará o build da imagem, executará os testes e inicializará o serviço. Em 2 a 3 minutos, um link público HTTPS estará disponível no topo da página:
   ```
   https://jiujitsu-cloud-app.onrender.com
   ```

### 1.4 Limitações, Vantagens e Desvantagens do Render
- **Limitações do Plano Free:** O contêiner entra em modo de hibernação (*spin-down*) após 15 minutos de inatividade. A primeira requisição após a hibernação pode levar cerca de 40 a 50 segundos para responder (cold-start). O PostgreSQL gratuito é renovável a cada 90 dias.
- **Vantagens:** Não exige cartão de crédito, suporte total a Docker, SSL automático, interface limpa, logs em tempo real na tela.
- **Desvantagens:** Cold-start perceptível após inatividade.

---

## 2. RAILWAY.APP

O **Railway** é uma plataforma PaaS extremamente moderna e ágil, muito popular pelo provisionamento visual em grafo e detecção automática de Docker.

### 2.1 Pré-requisitos
- Conta no [Railway.app](https://railway.app) com login do GitHub.

### 2.2 Passo a Passo: Deploy Completo
1. No dashboard, clique em **New Project**.
2. Selecione **Provision PostgreSQL**. Em 10 segundos, o Railway cria um contêiner PostgreSQL gerenciado.
3. No mesmo projeto, clique no botão **+ Create** e selecione **GitHub Repo** -> selecione `jiujitsu-soa`.
4. Clique no card do serviço da aplicação e acesse a aba **Variables**:
   - Clique em **Add Reference** e selecione a variável `DATABASE_URL` do PostgreSQL criado.
   - Adicione `ADMIN_USER=admin` e `ADMIN_PASSWORD=senha_jiujitsu_123`.
5. Acesse a aba **Settings** do serviço web:
   - Na seção **Networking**, clique em **Generate Domain**.
   - O Railway gerará uma URL pública com HTTPS automático (ex.: `https://jiujitsu-soa-production.up.railway.app`).
6. O build iniciará imediatamente usando o `Dockerfile`.

### 2.3 Limitações, Vantagens e Desvantagens do Railway
- **Limitações:** O plano Hobby oferece um crédito inicial (US$ 5,00) gratuito ou período de trial. Para uso continuado após os créditos, exige cadastro de cartão.
- **Vantagens:** Sem *cold start* (a aplicação não dorme como no Render), provisionamento de PostgreSQL instantâneo, métricas de CPU/Memória em tempo real, interface intuitiva.
- **Desvantagens:** Requer cartão para manutenção além do trial gratuito.

---

## 3. VERCEL

A **Vercel** é a plataforma líder mundial para hospedar front-ends estáticos e aplicações Serverless (Next.js, React, Node.js).

### 3.1 Arquitetura na Vercel
Como a Vercel foi desenhada primariamente para Front-ends e funções Serverless (Edge/Node/Python via Serverless Functions em `/api`), o Uvicorn de longa duração não roda no formato tradicional de daemon. No entanto, ela é perfeita caso você queira hospedar o **Front-end SPA** de forma 100% estática e ultra-rápida (na CDN global) e apontar para a API no Render ou AWS EC2!

### 3.2 Passo a Passo (Front-end SPA na Vercel)
1. Crie uma conta em [vercel.com](https://vercel.com).
2. Clique em **Add New...** -> **Project** e importe o repositório `jiujitsu-soa`.
3. Em **Framework Preset**, selecione **Other**.
4. Em **Root Directory**, selecione `static` (ou configure `vercel.json` na raiz).
5. Clique em **Deploy**. A Vercel entrega uma URL global ultra-rápida (ex.: `https://jiujitsu-soa.vercel.app`).

### 3.3 Limitações, Vantagens e Desvantagens da Vercel
- **Vantagens:** O melhor CDN global do mercado, deploy em menos de 10 segundos, plano gratuito generoso e eterno para front-end, sem hibernação.
- **Desvantagens:** Não gerencia banco de dados PostgreSQL clássico diretamente (exige banco serverless como Neon ou Supabase) e não suporta daemons ASGI contínuos no plano básico sem reestruturação para Serverless.

---

## 4. HEROKU

O **Heroku** foi o pioneiro do conceito PaaS (criador do padrão *Procfile* e do manifesto dos *12-Factor Apps*).

### 4.1 Pré-requisitos
- Conta no [Heroku.com](https://heroku.com) e Heroku CLI instalado (`curl https://cli-assets.heroku.com/install.sh | sh`).

### 4.2 Passo a Passo: Deploy via Heroku CLI
```bash
# 1. Login no Heroku
heroku login

# 2. Criar a aplicação
heroku create jiujitsu-cloud-app

# 3. Adicionar o addon do PostgreSQL
heroku addons:create heroku-postgresql:mini

# 4. Configurar as variáveis de ambiente
heroku config:set ADMIN_USER=admin ADMIN_PASSWORD=senha_jiujitsu_123 SECRET_KEY=heroku-secret

# 5. Criar arquivo Procfile na raiz do projeto
echo "web: uvicorn server:app --host 0.0.0.0 --port \$PORT" > Procfile

# 6. Realizar o deploy via Git
git add Procfile
git commit -m "Adiciona Procfile para Heroku"
git push heroku main

# 7. Abrir a aplicação no navegador
heroku open
```

### 4.3 Limitações, Vantagens e Desvantagens do Heroku
- **Limitações:** O Heroku **descontinuou seu plano gratuito em novembro de 2022**. O plano básico (Eco Dyno) custa a partir de US$ 5 a US$ 7 por mês e exige cartão de crédito.
- **Vantagens:** Maturidade gigantesca de mercado, ecossistema de Add-ons incomparável, documentação exemplar.
- **Desvantagens:** Não é mais gratuito para estudantes.

---

## 5. TABELA COMPARATIVA COMPLETA DAS PLATAFORMAS PAAS

| Critério de Comparação | Render.com | Railway.app | Vercel | Heroku |
| :--- | :--- | :--- | :--- | :--- |
| **Plano Gratuito Real?** | **Sim (Sem Cartão)** | Trial / Créditos | **Sim (Para Front/Serverless)** | Não (Pago desde 2022) |
| **Banco de Dados Gratuito** | PostgreSQL (1 GB incluso) | PostgreSQL (Trial) | Via parceiros (Neon/Supabase) | Pago (a partir de $5/mês) |
| **Suporte Nativo a Docker** | **Sim (Detecta Dockerfile)** | **Sim (Detecta Dockerfile)** | Não | Sim (via Container Registry) |
| **Deploy Automático Git** | Sim (Automático) | Sim (Automático) | Sim (Automático) | Sim (Git push) |
| **Certificado SSL / HTTPS** | Automático (Let's Encrypt) | Automático | Automático | Automático |
| **Comportamento Inativo** | Hiberna após 15 min | Não hiberna no crédito | Não hiberna | Hiberna se dyno eco |
| **Complexidade de Setup** | **Muito Baixa (Web UI)** | **Muito Baixa (Canvas)** | Média para Back-end | Média (Uso de CLI) |

---

## 6. RECOMENDAÇÃO DO PROFESSOR / ARQUITETO PARA A DISCIPLINA

> 🏆 **Recomendação Principal: RENDER.COM**
> 
> Para o escopo acadêmico da disciplina **"Aplicação Web para Nuvem"**, o **Render.com** é a melhor escolha absoluta:
> 1. **Custo Zero:** Permite criar o Web Service (FastAPI + Front-end SPA) e a instância do PostgreSQL sem exigir cartão de crédito internacional.
> 2. **Docker First:** Ele lê o mesmo `Dockerfile` que você utiliza localmente e na AWS EC2, garantindo consistência total entre ambientes (*Dev/Prod Parity* - Princípio X do 12-Factor).
> 3. **Link Público HTTPS Imediato:** Gera um endereço seguro oficial (ex.: `https://jiujitsu-cloud-app.onrender.com`) pronto para ser colocado no relatório da disciplina e no vídeo.
