# Relatório Final — Jiu-Jitsu Academy Cloud Web App

> **Template pronto para preencher.** Substitua os campos entre colchetes,
> remova as instruções em itálico e anexe os prints. Mantenha o texto em
> primeira pessoa e com suas próprias palavras.

---

## Capa

| Campo | Informação |
|---|---|
| Aluno(a) | [Seu nome completo] |
| Curso | Sistemas para Internet |
| Disciplina | [Nome da disciplina] |
| Professor(a) | [Nome] |
| Instituição | [Nome da instituição] |
| Data | [dd/mm/aaaa] |
| Repositório | https://github.com/lucasbombev/jiujitsu-soa |
| Deploy | https://SEU-SERVICO.onrender.com |
| Vídeo | [Link do vídeo] |

---

## Resumo

*[5 a 8 linhas: o que o projeto faz, qual problema resolve, quais testes e
 pipeline foram implementados e qual foi o resultado final.]*

---

## 1. Introdução e contexto

*[Descreva o projeto, a disciplina e a evolução de um serviço SOA/SOAP para uma
arquitetura Cloud-Native RESTful. Explique por que testar e automatizar o deploy
é importante nesse contexto.]*

---

## 2. Objetivos

### Objetivo geral

*[Ex.: concluir a aplicação web com testes automatizados, pipeline de CI/CD,
deploy em nuvem e documentação.]*

### Objetivos específicos

- Implementar testes de unidade no backend.
- Implementar testes de funções/componentes no frontend.
- Automatizar instalação, testes e deploy em um pipeline.
- Publicar a aplicação em um provedor de nuvem.
- Documentar a execução e as dificuldades.

---

## 3. Arquitetura e stack

### Visão geral

```text
Navegador (SPA: HTML/CSS/JS)
        │  HTTP/JSON
        ▼
FastAPI (server.py) ── SQLAlchemy (database.py) ── SQLite / PostgreSQL
        │
        └── /health, /docs, /static
```

*[Inclua um diagrama ou print da arquitetura, se desejar.]*

### Tecnologias

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Backend | FastAPI + Uvicorn | API REST rápida, documentação OpenAPI automática |
| Validação | Pydantic v2 | Validação declarativa dos payloads |
| Persistência | SQLAlchemy 2 | Suporte a SQLite e PostgreSQL sem reescrever o código |
| Frontend | HTML, CSS e JavaScript puro | Simplicidade e foco no consumo da API |
| Testes backend | Pytest + TestClient | Testes de unidade e integração |
| Testes frontend | Vitest + jsdom + Testing Library | Testes rápidos sem navegador real |
| CI/CD | GitHub Actions | Integração nativa com o repositório público |
| Deploy | Render | Plano free, deploy via hook e health check |

---

## 4. Testes implementados

### 4.1 Backend — 22 testes

| Arquivo | Tipo | Principais casos |
|---|---|---|
| `tests/test_api.py` | Integração | `/health`, listagem de cursos, matrícula válida, curso inválido, atualização de status, exclusão, dashboard, login, rota protegida |
| `tests/test_unit.py` | Unidade | `mask_cpf`, validação de schemas, token Bearer, `to_dict` dos modelos |

**Comando:**

```bash
source .venv/bin/activate
pytest -v
```

**Resultado:** `22 passed`.

*[Cole aqui o print do terminal com os 22 testes passando.]*

### 4.2 Frontend — 20 testes

| Arquivo | Tipo | Principais casos |
|---|---|---|
| `tests/frontend/utils.test.js` | Unidade | `escapeHtml`, `maskDisplayCpf`, `formatCurrency`, `statusClass`, `filterMatriculas` |
| `tests/frontend/matricula-row.test.js` | Componente/DOM | render da linha, proteção XSS, botões por status |
| `tests/frontend/app-bootstrap.test.js` | Fumaça/integração | carrega a SPA real no jsdom e valida o dashboard |

**Comando:**

```bash
npm ci
npm test
```

**Resultado:** `20 passed` e 100% de cobertura dos statements de
`static/utils.js`.

*[Cole aqui o print do terminal com os 20 testes passando.]*

### 4.3 Estratégia adotada

*[Explique a diferença entre testes de unidade e de integração. Comente a
 extração das funções puras para `static/utils.js` e o uso do jsdom para testar
 o HTML gerado sem abrir um navegador.]*

---

## 5. Pipeline de CI/CD

**Arquivo:** `.github/workflows/ci-cd.yml`

| Job | O que faz | Quando roda |
|---|---|---|
| `backend-tests` | Checkout, Python 3.12, cache pip, `pip install -r requirements.txt`, `pytest -v` | Push e PR na `main` |
| `frontend-tests` | Checkout, Node 22, cache npm, `npm ci`, `npm test` | Push e PR na `main` |
| `deploy` | Envia POST para o Deploy Hook do Render e aguarda `/health` | Somente push na `main`, após os dois testes passarem |

**Secrets/variável:**

- `RENDER_DEPLOY_HOOK_URL` (secret)
- `RENDER_APP_URL` (variable)

**Por que `autoDeploy: false`?**

*[Explique que o Render não deve publicar antes dos testes; o deploy é
 disparado pelo GitHub Actions somente após o sucesso dos jobs.]*

*[Cole aqui o print da execução com os três jobs verdes e o print dos logs do
 deploy.]*

---

## 6. Deploy

| Item | Valor |
|---|---|
| Provedor | Render |
| Tipo | Web Service (Python) |
| Plano | Free |
| Build | `pip install -r requirements.txt` |
| Start | `uvicorn server:app --host 0.0.0.0 --port $PORT` |
| Health check | `/health` |
| Banco | SQLite (`sqlite:///./jiujitsu.db`) |
| URL | https://SEU-SERVICO.onrender.com |

**Limitação conhecida:** no plano free o disco é efêmero; os dados voltam ao
seed inicial a cada deploy/restart. A aplicação está preparada para PostgreSQL
via `DATABASE_URL`.

*[Cole aqui o print do serviço Live no Render e do `/health` retornando 200.]*

---

## 7. Dificuldades enfrentadas e soluções

*[Preencha com as dificuldades reais que você viveu. Sugestões baseadas no
 projeto:]*

| Dificuldade | Como foi superada |
|---|---|
| Frontend em JavaScript puro, sem framework de testes. | Extraí funções puras para `static/utils.js` e testei com Vitest + jsdom. |
| Funções de renderização acopladas ao DOM. | Criei `buildMatriculaRow` e testei a linha renderizada com Testing Library. |
| Isolamento do banco nos testes. | `tests/conftest.py` define `DATABASE_URL` de teste antes dos imports. |
| Dependência do Spyne via GitHub no `requirements.txt`. | Validei com Python 3.12 e documentei o procedimento em caso de falha de rede. |
| SQLite efêmero no Render free. | Documentei a limitação e o caminho para PostgreSQL. |
| Garantir que o deploy só ocorra após os testes. | `autoDeploy: false` + job `deploy` com `needs` e condição de branch. |
| Espera do deploy/health check. | Loop de até 10 minutos no workflow. |
| [Sua dificuldade] | [Como resolveu] |

---

## 8. Conclusão

*[Retome os objetivos, informe o que foi entregue e o que aprendeu. Sugestões de
 próximos passos: autenticação JWT, testes E2E com Playwright, PostgreSQL
 gerenciado, observabilidade e cobertura mínima obrigatória no CI.]*

---

## 9. Referências

- FastAPI — https://fastapi.tiangolo.com/
- SQLAlchemy — https://docs.sqlalchemy.org/
- Pytest — https://docs.pytest.org/
- Vitest — https://vitest.dev/
- Testing Library — https://testing-library.com/docs/dom-testing-library/
- GitHub Actions — https://docs.github.com/actions
- Render Blueprint — https://render.com/docs/blueprint-spec
- Render Deploy Hooks — https://render.com/docs/deploy-hooks

---

## 10. Anexos

- Repositório: https://github.com/lucasbombev/jiujitsu-soa
- Deploy: https://SEU-SERVICO.onrender.com
- Vídeo: [link]
- Prints: [lista ou pasta]

### Declaração de uso de IA (se exigido pela instituição)

*[Se a instituição permitir, descreva que a IA foi usada como apoio para
 auditoria, implementação dos testes/pipeline e documentação, e que você revisou,
 executou e validou todo o resultado.]*
