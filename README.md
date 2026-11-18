# 🥋 Jiu-Jitsu Academy — Cloud Web App

[![CI/CD](https://github.com/lucasbombev/jiujitsu-soa/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/lucasbombev/jiujitsu-soa/actions/workflows/ci-cd.yml)

Aplicação web acadêmica para gestão de uma academia de Jiu-Jitsu, construída como
evolução de um serviço legado **SOA/SOAP 1.1** para uma arquitetura
**Cloud-Native RESTful**. O projeto reúne backend FastAPI, frontend SPA em
JavaScript puro, banco relacional, testes automatizados, pipeline de CI/CD e
deploy no Render.

> **Disciplina:** Aplicação Web para Nuvem
> **Repositório:** https://github.com/lucasbombev/jiujitsu-soa

---

## 📖 Descrição

O sistema permite:

- Consultar o catálogo de cursos da academia.
- Registrar, consultar, filtrar e excluir matrículas de alunos.
- Alterar o status de uma matrícula (`Ativo`, `Inativo`, `Cancelado`).
- Visualizar métricas do dashboard (total de matrículas, ativas, cursos e
  faturamento mensal estimado).
- Autenticar um administrador para cadastrar novos cursos.
- Acompanhar a saúde da aplicação em nuvem pelo endpoint `/health`.
- Consumir a API documentada automaticamente via Swagger/OpenAPI em `/docs`.

O CPF é mascarado na interface e nos logs, em conformidade com a LGPD.

---

## 🧰 Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12, FastAPI, Uvicorn |
| Validação | Pydantic v2 |
| Persistência | SQLAlchemy 2 + SQLite (dev/Render free) ou PostgreSQL |
| Frontend | HTML5, CSS3 e JavaScript puro (SPA) |
| Testes backend | Pytest + FastAPI TestClient |
| Testes frontend | Vitest + jsdom + Testing Library (`@testing-library/dom`) |
| CI/CD | GitHub Actions |
| Deploy | Render (`render.yaml` + Deploy Hook) |
| Container | Docker + Docker Compose (opcional) |
| Legado | SOAP 1.1 com Spyne/WSDL (mantido em `app.py`) |

---

## 🚀 Como rodar localmente

### Pré-requisitos

- Python **3.12** (recomendado; o CI usa essa versão)
- Node.js **20+** (apenas para os testes de frontend)
- Git

### 1. Clonar e criar o ambiente Python

```bash
git clone https://github.com/lucasbombev/jiujitsu-soa.git
cd jiujitsu-soa

python3.12 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

> O `requirements.txt` inclui o Spyne (instalado a partir do GitHub) porque o
> serviço SOAP legado continua no repositório. A instalação pode levar alguns
> minutos na primeira execução.

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Para desenvolvimento local, o padrão do `.env.example` já funciona:

```env
PORT=8000
HOST=0.0.0.0
APP_ENV=production
DATABASE_URL=sqlite:///./jiujitsu.db
ADMIN_USER=admin
ADMIN_PASSWORD=senha_jiujitsu_123
SECRET_KEY=jiujitsu-cloud-secret-token-2026-super-segura
CORS_ORIGINS=*
```

> Troque `ADMIN_PASSWORD` e `SECRET_KEY` em qualquer ambiente publicado.

### 3. Subir a aplicação

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Acesse:

- Aplicação: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Na primeira inicialização, o banco SQLite é criado e populado com cursos e
matrículas de demonstração (`database.py`).

### 4. Rodar com Docker (opcional)

```bash
docker compose up --build
```

Isso sobe a aplicação e um PostgreSQL local. A aplicação fica disponível em
http://localhost:8000.

---

## 🧪 Como rodar os testes

### Backend — Pytest

```bash
source .venv/bin/activate
pytest -v
```

Para rodar somente os testes de unidade:

```bash
pytest tests/test_unit.py -v
```

**O que é coberto:**

| Arquivo | Tipo | Casos |
|---|---|---|
| `tests/test_api.py` | Integração (TestClient) | health check, cursos, matrícula válida/inválida, status, exclusão, dashboard, login, rota protegida |
| `tests/test_unit.py` | Unidade | mascaramento de CPF, validação Pydantic, token Bearer, serialização dos modelos |

Total atual: **22 testes de backend**.

### Frontend — Vitest

```bash
npm ci
npm test
```

Para cobertura:

```bash
npm run test:coverage
```

**O que é coberto:**

| Arquivo | Tipo | Casos |
|---|---|---|
| `tests/frontend/utils.test.js` | Unidade | `escapeHtml`, `maskDisplayCpf`, `formatCurrency`, `statusClass`, `filterMatriculas` |
| `tests/frontend/matricula-row.test.js` | Componente/DOM | render da linha da tabela, proteção XSS, botões por status |
| `tests/frontend/app-bootstrap.test.js` | Fumaça/integração | carrega `index.html`, `utils.js` e `app.js` no jsdom e valida o dashboard renderizado |

Total atual: **20 testes de frontend** (cobertura de 100% dos statements de
`static/utils.js`).

### Rodar tudo de uma vez

```bash
source .venv/bin/activate
pytest -v
npm ci
npm test
```

---

## 🔁 Como funciona o CI/CD

O workflow está em
[`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml).

```
push/PR na main
      │
      ├── backend-tests  (Python 3.12 + pip cache + pytest)
      │
      └── frontend-tests (Node 22 + npm cache + npm ci + vitest)
                    │
                    └── deploy (somente push na main e se os dois passarem)
                              │
                              ├── POST no RENDER_DEPLOY_HOOK_URL
                              └── aguarda GET /health responder HTTP 200
```

**Gatilhos:**

- `push` na branch `main`;
- `pull_request` para a `main` (apenas testes, sem deploy);
- `workflow_dispatch` (execução manual, apenas testes).

**Secrets e variáveis necessários no GitHub**
(`Settings → Secrets and variables → Actions`):

| Nome | Tipo | Para que serve |
|---|---|---|
| `RENDER_DEPLOY_HOOK_URL` | Secret | Disparar o deploy no Render após os testes passarem |
| `RENDER_APP_URL` | Variable | URL pública usada no health check pós-deploy (opcional) |

O `render.yaml` usa `autoDeploy: false`: o Render **não** publica sozinho a cada
push. O deploy só acontece pelo job do GitHub Actions, depois dos testes. Isso
garante o requisito de "deploy automático em caso de sucesso".

### Configurar o deploy (resumo)

1. No Render, crie um **Blueprint** apontando para este repositório (o
   `render.yaml` já descreve o serviço), ou crie um **Web Service** manual com:
   - Build: `pip install --upgrade pip && pip install -r requirements.txt`
   - Start: `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - Health check: `/health`
2. Copie a URL pública do serviço.
3. Em **Settings → Deploy Hook**, crie e copie a URL do hook.
4. No GitHub, cadastre o secret `RENDER_DEPLOY_HOOK_URL` e a variable
   `RENDER_APP_URL`.
5. Faça um push na `main` e acompanhe em **Actions**.

O passo a passo detalhado, com prints e roteiro de vídeo, está no
[`GUIA.md`](GUIA.md).

### Link do deploy

> **Placeholder:** `https://SEU-SERVICO.onrender.com`
>
> Substitua pela URL real após criar o serviço no Render.

---

## 🗂️ Estrutura de pastas

```text
jiujitsu-soa/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # Pipeline: testes + deploy Render
├── static/
│   ├── app.js                 # Lógica da SPA (consome a API REST)
│   ├── utils.js               # Funções puras testadas pelo Vitest
│   ├── index.html             # Interface
│   └── style.css              # Estilos
├── tests/
│   ├── conftest.py            # Ambiente isolado de testes (SQLite)
│   ├── test_api.py            # Testes de integração dos endpoints
│   ├── test_unit.py           # Testes de unidade do backend
│   └── frontend/
│       ├── utils.test.js      # Testes das funções utilitárias
│       ├── matricula-row.test.js  # Teste de componente/DOM
│       └── app-bootstrap.test.js  # Teste de fumaça da SPA
├── app.py                     # Serviço SOAP legado (Spyne/WSDL)
├── database.py                # Engine, modelos e seed SQLAlchemy
├── server.py                  # Aplicação FastAPI + SPA
├── test_soap.py               # Teste manual do serviço SOAP (opcional)
├── test_and_dump.py           # Extração manual do WSDL/XSD (opcional)
├── jiujitsu_service.wsdl      # Contrato SOAP
├── jiujitsu_service.xsd       # Schema SOAP
├── jiujitsu-soapui-project.xml
├── Dockerfile                 # Imagem da aplicação
├── docker-compose.yml         # App + PostgreSQL local
├── render.yaml                # Blueprint de deploy no Render
├── package.json               # Dependências e scripts dos testes frontend
├── package-lock.json          # Lockfile usado pelo npm ci
├── vitest.config.mjs          # Configuração do Vitest (jsdom)
├── pytest.ini                 # Configuração do Pytest
├── requirements.txt           # Dependências Python
├── .env.example               # Variáveis de ambiente de exemplo
├── README.md                  # Este arquivo
├── GUIA.md                    # Passo a passo manual da entrega
├── RELATORIO.md               # Template do relatório final
└── docs/
    └── evidencias/            # Prints do CI/CD e do deploy
```

---

## 🔐 Segurança e LGPD

- CPF mascarado nos logs (`mask_cpf`, backend) e na tabela (`maskDisplayCpf`,
  frontend).
- Rotas de criação de curso e operações administrativas exigem token Bearer.
- Credenciais e chave secreta vêm de variáveis de ambiente, nunca do código.
- Em produção, troque `ADMIN_PASSWORD` e `SECRET_KEY` e não versione o `.env`.
- O CORS está aberto (`*`) por ser um projeto acadêmico; restrinja as origens em
  um ambiente real.

---

## 📝 Observações sobre o deploy

- O `render.yaml` usa **SQLite no disco efêmero** do plano free. A cada
  deploy/restart, o banco volta ao seed inicial. Para persistência real,
  configure um PostgreSQL no Render e altere `DATABASE_URL` para
  `postgresql://...` (o `database.py` já aceita esse formato).
- O plano free do Render hiberna após inatividade. O primeiro acesso pode
  demorar; o job de deploy aguarda até 10 minutos pelo `/health`.
- O serviço SOAP legado (`app.py`) não é iniciado no deploy; o deploy sobe
  apenas o FastAPI (`server.py`).

---

## 📚 Documentação da entrega

- [`GUIA.md`](GUIA.md): checklist, comandos, configuração de secrets, deploy,
  roteiro do vídeo e sugestão de relatório.
- [`RELATORIO.md`](RELATORIO.md): estrutura pronta para preencher.
- [`jiujitsu_service.wsdl`](jiujitsu_service.wsdl): contrato do serviço SOAP
  original.
- `/docs`: documentação OpenAPI gerada automaticamente pelo FastAPI.

---

## 👤 Autor

**Lucas Gabriel** — curso de Sistemas para Internet.

Projeto desenvolvido para fins acadêmicos.
