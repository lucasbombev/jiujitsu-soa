# 🥋 Jiu-Jitsu Academy - Aplicação Web para Nuvem & SOA

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-005571.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Projeto desenvolvido e expandido para a disciplina **Aplicação Web para Nuvem**, demonstrando a evolução de uma arquitetura legada orientada a serviços (**SOA - SOAP 1.1**) para uma **Aplicação Web Cloud-Native moderna**, com implantações nos modelos **IaaS (AWS EC2)** e **PaaS (Render.com / Railway)**.

---

## 📌 Sumário Executivo do Projeto

- **Instituição / Disciplina:** Aplicação Web para Nuvem
- **Repositório:** [lucasbombev/jiujitsu-soa](https://github.com/lucasbombev/jiujitsu-soa)
- **Autor:** Lucas Bombev
- **Requisitos Cumpridos:**
  - [x] **Back-end:** API RESTful assíncrona desenvolvida em FastAPI com documentação interativa Swagger/OpenAPI.
  - [x] **Front-end:** Single Page Application (SPA) responsiva com design moderno em Dark Mode/Glassmorphism, consumo assíncrono de dados e máscaras de validação.
  - [x] **Acesso a Banco de Dados:** Persistência relacional agnóstica via SQLAlchemy (suporta **SQLite** local e **PostgreSQL** em nuvem como AWS RDS e Render Postgres).
  - [x] **IaaS (Infraestrutura como Serviço):** Implantação manual em máquina virtual **AWS EC2 (Ubuntu Linux + Nginx + Systemd + Uvicorn)** com link público IPv4.
  - [x] **PaaS (Plataforma como Serviço):** Publicação automatizada via Git na plataforma **Render.com** com banco de dados PostgreSQL e link público HTTPS com certificado SSL.
  - [x] **Observabilidade e 12-Factor:** Endpoint `/health` para verificação de liveness de nuvem e logs estruturados em `stdout`.
  - [x] **Vídeo Explicativo:** Roteiro completo para apresentação da arquitetura e demonstração prática.

---

## 🏛️ Arquitetura do Sistema

O projeto adota uma **Arquitetura Híbrida / Modern Cloud Application**, preservando os contratos legados do SOA e expondo interfaces modernas para a nuvem:

```
                                  INTERNET
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            ▼ (HTTP / HTTPS)                                    ▼ (SOAP XML)
   ┌─────────────────────────────────┐                 ┌───────────────────┐
   │         Front-end SPA           │                 │ Clientes Legados  │
   │   (HTML5 / CSS3 / Vanilla JS)   │                 │ (SoapUI / Zeep)   │
   └────────────────┬────────────────┘                 └─────────┬─────────┘
                    │                                            │
                    ▼ RESTful JSON                               ▼ SOAP 1.1 RPC
   ┌─────────────────────────────────────────────────────────────┴─────────┐
   │                Servidor de Aplicação Web (FastAPI / Uvicorn)          │
   │                                                                       │
   │   • /health (Health Check de Nuvem)      • /api/cursos                │
   │   • /docs (Swagger / OpenAPI UI)         • /api/matriculas            │
   │   • /static (Servidor de Ativos SPA)     • /api/dashboard/stats       │
   │   • /api/auth/login                      • Core SOA Legado (app.py)   │
   └──────────────────────────────────┬────────────────────────────────────┘
                                      │ SQLAlchemy (Agnóstico)
                                      ▼
                      ┌───────────────────────────────┐
                      │        Banco de Dados         │
                      │  • SQLite (jiujitsu.db)       │
                      │  • PostgreSQL (AWS RDS / PaaS)│
                      └───────────────────────────────┘
```

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
- Python 3.10 ou superior instalado
- Git
- Docker e Docker Compose (opcional para execução em contêineres)

### Opção 1: Execução Direta com Python (Recomendada para Desenvolvimento)

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/lucasbombev/jiujitsu-soa.git
   cd jiujitsu-soa
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   ```

5. **Inicie o servidor da aplicação web:**
   ```bash
   python server.py
   ```

6. **Acesse no navegador:**
   - **Front-end SPA:** [http://localhost:8000](http://localhost:8000)
   - **Documentação Swagger (OpenAPI):** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Healthcheck:** [http://localhost:8000/health](http://localhost:8000/health)

---

### Opção 2: Execução com Docker e PostgreSQL (Ambiente Cloud Completo)

Para simular o ambiente de produção completo com banco de dados relacional PostgreSQL:

```bash
docker-compose up --build
```
A aplicação iniciará na porta `8000` conectada ao banco PostgreSQL na porta `5432`.

---

## 🧪 Testes Automatizados

O projeto conta com suítes de testes automatizados para ambas as camadas:

```bash
# 1. Executar os testes automatizados da Web API RESTful (Pytest)
python -m pytest tests/test_api.py -v

# 2. Executar os testes do serviço SOAP legado original (Zeep)
python test_soap.py
```

---

## 📡 Referência dos Endpoints REST

| Método | Endpoint | Descrição | Autenticação |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Verificação de integridade e status do banco para Cloud Load Balancers | Pública |
| `GET` | `/docs` | Interface interativa OpenAPI / Swagger UI | Pública |
| `GET` | `/api/dashboard/stats` | Métricas consolidadas (Total de alunos, ativos, faturamento mensal) | Pública |
| `GET` | `/api/cursos` | Listagem de cursos oferecidos (suporta filtro `?categoria=`) | Pública |
| `POST` | `/api/cursos` | Cadastro de novos cursos | **Bearer Token** |
| `GET` | `/api/matriculas` | Listagem de matrículas (suporta filtros de status e curso) | Pública |
| `GET` | `/api/matriculas/{id}` | Consulta detalhada de uma matrícula específica | Pública |
| `POST` | `/api/matriculas` | Registro de nova matrícula de aluno | Pública |
| `PATCH` | `/api/matriculas/{id}/status` | Alteração de status da matrícula (`Ativo`, `Inativo`, `Cancelado`) | Pública |
| `DELETE` | `/api/matriculas/{id}` | Exclusão de matrícula | Pública |
| `POST` | `/api/auth/login` | Login administrativo para obtenção de Token Bearer | Pública |

---

## 📚 Guias de Implantação e Materiais de Apoio

A documentação detalhada para os requisitos da disciplina está organizada na pasta [`docs/`](file:///home/banana/jiujitsu-soa/docs):

1. **[Guia Completo de Implantação IaaS na AWS EC2](docs/aws_ec2_guide.md)**:
   - Configuração passo a passo de VM Ubuntu Server na AWS.
   - Setup de `systemd`, `Nginx` como Reverse Proxy, Security Groups e IP público.
   - Alternativas com Free Tier e integração com AWS RDS PostgreSQL.

2. **[Guia Comparativo de Implantação em Plataformas PaaS](docs/paas_deployment.md)**:
   - Passo a passo detalhado para **Render.com**, **Railway**, **Vercel** e **Heroku**.
   - Configuração de PostgreSQL gerenciado gratuito e variáveis de ambiente.
   - Tabela comparativa e justificativa da escolha do Render.

3. **[Roteiro Completo para Vídeo de Apresentação](docs/video_script.md)**:
   - Roteiro estruturado para vídeo de 5, 10 ou 15 minutos.
   - Falas sugeridas e ações de tela para cada bloco (Localhost, Swagger, AWS EC2, Render PaaS).
   - Dicas técnicas de gravação com OBS Studio.

---

## 🔒 Segurança e Privacidade (LGPD)

- **Mascaramento de Dados:** Em conformidade com as boas práticas de privacidade e a LGPD, números de CPF são automaticamente mascarados tanto na interface do usuário quanto nos registros de logs de auditoria (`111.***.***-44`).
- **Autenticação em Camadas:** Operações administrativas requerem autenticação por Token Bearer na REST API e UsernameToken no serviço SOAP legado.
- **Configuração 12-Factor:** Nenhuma credencial ou segredo de produção é versionado em texto plano; todas as configurações sensíveis são injetadas via variáveis de ambiente (`.env`).