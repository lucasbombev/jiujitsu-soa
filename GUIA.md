# 📘 GUIA — Conclusão da Entrega

> **Projeto:** Jiu-Jitsu Academy — Cloud Web App
> **Repositório:** https://github.com/lucasbombev/jiujitsu-soa
> **Branch principal:** `main`
> **Stack:** Python 3.12 + FastAPI + SQLAlchemy + Vanilla JS
> **Deploy escolhido:** Render (plano free, SQLite)
>
> Este guia separa o que **já foi implementado no código** do que **você ainda
> precisa fazer manualmente** (GitHub, Render, prints, vídeo e relatório).

---

## 1. Checklist do trabalho

Marque conforme for concluindo. Os itens ✅ já estão no repositório local; os
itens ☐ dependem de ações suas em serviços externos.

| # | Requisito | Status | Evidência |
|---|---|---|---|
| 1 | Projeto web com backend e frontend | ✅ | `server.py`, `static/index.html`, `static/app.js` |
| 2 | Testes de unidade no backend | ✅ | `tests/test_unit.py` (13 testes) |
| 2.1 | Testes de integração no backend | ✅ | `tests/test_api.py` (9 testes) |
| 3 | Testes simples no frontend | ✅ | `tests/frontend/utils.test.js`, `matricula-row.test.js` e `app-bootstrap.test.js` (20 testes) |
| 4 | Pipeline com instalação + testes | ✅ | `.github/workflows/ci-cd.yml` (jobs `backend-tests` e `frontend-tests`) |
| 5 | Deploy automático após sucesso | ✅ (configurado) | Job `deploy` + `render.yaml` |
| 6 | Pipeline executado com sucesso no GitHub | ☐ | Aba **Actions** do repositório |
| 7 | Serviço criado e no ar no Render | ☐ | URL `https://SEU-SERVICO.onrender.com` |
| 8 | Repositório público | ✅ | https://github.com/lucasbombev/jiujitsu-soa |
| 9 | README atualizado | ✅ | `README.md` |
| 10 | GUIA da entrega | ✅ | Este arquivo |
| 11 | Print do CI/CD funcionando | ☐ | Você vai capturar após o push |
| 12 | Vídeo curto (3–5 min) | ☐ | Roteiro na seção 3.9 |
| 13 | Relatório final preenchido | ☐ | Template em `RELATORIO.md` |

> **Importante:** o pipeline e o deploy estão **implementados**, mas ainda não
> foram executados porque dependem de um push para o GitHub e da criação do
> serviço no Render. Não considere os itens 6, 7, 11, 12 e 13 concluídos antes
> de fazer os passos abaixo.

---

## 2. O que já foi feito (IA)

### 2.1 Resumo

- Auditei o projeto existente sem apagar funcionalidades.
- Mantive os **9 testes de API** que já existiam.
- Adicionei **13 testes de unidade** no backend.
- Extraí funções puras do frontend para `static/utils.js` e criei **20 testes**
  com Vitest + jsdom + Testing Library.
- Criei o workflow de CI/CD com dois jobs de teste e um job de deploy
  condicionado à `main` e ao sucesso dos testes.
- Criei o `render.yaml` com `autoDeploy: false` para que o deploy só ocorra pelo
  GitHub Actions.
- Atualizei o README e criei este guia + template de relatório.

### 2.2 Resultados dos testes (executados localmente)

```text
Backend  (pytest): 22 passed
Frontend (vitest): 20 passed
Cobertura de static/utils.js: 100% dos statements
```

### 2.3 Arquivos criados

| Arquivo | Para que serve |
|---|---|
| `.github/workflows/ci-cd.yml` | Pipeline: checkout → runtime → cache → install → testes → deploy |
| `render.yaml` | Blueprint do serviço web no Render |
| `package.json` | Scripts e dependências dos testes de frontend |
| `package-lock.json` | Versões travadas; usado pelo `npm ci` no CI |
| `vitest.config.mjs` | Configuração do Vitest com ambiente `jsdom` |
| `static/utils.js` | Funções puras do frontend (escape, CPF, moeda, filtros, linha da tabela) |
| `tests/test_unit.py` | 13 testes de unidade do backend |
| `tests/conftest.py` | Isola o banco de testes antes de importar a aplicação |
| `tests/frontend/utils.test.js` | 15 testes das funções utilitárias |
| `tests/frontend/matricula-row.test.js` | 4 testes de componente/DOM da linha da tabela |
| `tests/frontend/app-bootstrap.test.js` | 1 teste de fumaça que carrega a SPA real no jsdom |
| `pytest.ini` | Configuração do Pytest (`testpaths`, `pythonpath` e warnings) |
| `README.md` | Documentação completa do projeto |
| `GUIA.md` | Este guia |
| `RELATORIO.md` | Template do relatório final |

### 2.4 Arquivos alterados (mudanças preservam o comportamento)

| Arquivo | Mudança |
|---|---|
| `static/app.js` | Passou a usar as funções de `static/utils.js`; a renderização da tabela foi extraída para `buildMatriculaRow` |
| `static/index.html` | Carrega `static/utils.js` antes de `static/app.js` |
| `.gitignore` | Ignora `node_modules/`, `coverage/` e `.vitest/` |

Nenhuma funcionalidade foi removida. As funções continuam com o mesmo
comportamento visual; a diferença é que agora são testáveis isoladamente.

### 2.5 O que **não** foi feito por mim

- Não criei conta nem serviço no Render.
- Não cadastrei secrets no GitHub.
- Não executei o workflow no GitHub (não tenho acesso às suas credenciais).
- Não gravei o vídeo nem preenchi o relatório com seus dados pessoais.

---

## 3. O que você precisa fazer manualmente

### 3.1 Revisar as mudanças antes de commitar

No diretório do projeto:

```bash
cd ~/Documents/jiujitsu-soa

git status
git diff --stat
git diff -- static/app.js static/index.html .gitignore
```

Confira se o `package-lock.json`, `package.json`, `render.yaml` e a pasta
`.github/` aparecem como novos arquivos.

> **Atenção:** `.venv/`, `node_modules/`, `.env`, `coverage/` e bancos locais não
> devem ser commitados — eles já estão no `.gitignore`.

### 3.2 Conferir o repositório público

O repositório já está público:

- https://github.com/lucasbombev/jiujitsu-soa

Se por acaso ele estiver privado, vá em **Settings → General → Danger Zone →
Change repository visibility → Public**. O requisito pede repositório público.

### 3.3 Commitar e fazer o push

```bash
git add .
git commit -m "ci: adiciona testes unitários, testes de frontend e pipeline CI/CD"
git push origin main
```

Se o push for rejeitado porque o remoto tem commits novos:

```bash
git pull --rebase origin main
git push origin main
```

O push na `main` já dispara o workflow. Antes de fazer o push, porém, eu
recomendo configurar o Render e os secrets (passos 3.4 a 3.6), para que o job de
deploy não falhe na primeira execução.

### 3.4 Criar o serviço no Render

Você tem dois caminhos. O **Blueprint** é o mais rápido porque usa o
`render.yaml` que já está no repositório.

#### Opção A — Blueprint (recomendado)

1. Acesse https://dashboard.render.com e faça login com o GitHub.
2. Clique em **New → Blueprint**.
3. Conecte/selecione o repositório `lucasbombev/jiujitsu-soa`.
4. Confirme a branch `main` e o arquivo `render.yaml`.
5. O Render mostrará o serviço `jiujitsu-academy`.
6. Quando pedir o valor de `ADMIN_PASSWORD`, informe uma senha forte
   (diferente da senha padrão do código) e guarde-a.
7. Clique em **Apply** e aguarde o primeiro deploy.
8. Copie a URL pública gerada, algo como:
   `https://jiujitsu-academy.onrender.com`
   (o nome pode ganhar um sufixo se já estiver em uso).

#### Opção B — Web Service manual

Se preferir criar manualmente:

1. **New → Web Service** e selecione o repositório.
2. Preencha:
   - **Name:** `jiujitsu-academy`
   - **Runtime:** Python 3
   - **Branch:** `main`
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
   - **Plan:** Free
3. Em **Environment Variables**, adicione:

   | Chave | Valor |
   |---|---|
   | `PYTHON_VERSION` | `3.12.6` |
   | `APP_ENV` | `production` |
   | `DATABASE_URL` | `sqlite:///./jiujitsu.db` |
   | `ADMIN_USER` | `admin` |
   | `ADMIN_PASSWORD` | uma senha forte sua |
   | `SECRET_KEY` | uma string aleatória longa |
   | `CORS_ORIGINS` | `*` |

4. Em **Settings → Auto-Deploy**, deixe **desligado** (`No`). O deploy será
   disparado pelo GitHub Actions, não pelo Render.
5. Clique em **Create Web Service** e aguarde o status **Live**.
6. Copie a URL pública.

> **Sobre o SQLite no Render free:** o disco é efêmero. A cada deploy/restart o
> banco volta ao seed inicial. Para um trabalho acadêmico de demonstração isso
> é aceitável. Se quiser persistência real, crie um PostgreSQL no Render e
> troque `DATABASE_URL` por `postgresql://...` (veja a seção 5.4).

### 3.5 Criar o Deploy Hook no Render

1. No painel do Render, abra o serviço `jiujitsu-academy`.
2. Vá em **Settings → Deploy Hook**.
3. Clique em **Create Deploy Hook**.
4. Copie a URL gerada (ela contém um segredo; não divulgue no vídeo/print).

Essa URL será usada pelo job `deploy` do GitHub Actions.

### 3.6 Cadastrar o secret e a variable no GitHub

Acesse:

- https://github.com/lucasbombev/jiujitsu-soa/settings/secrets/actions

#### Secret

1. Clique em **New repository secret**.
2. Nome: `RENDER_DEPLOY_HOOK_URL`
3. Valor: a URL copiada no passo 3.5.
4. Clique em **Add secret**.

#### Variable (opcional, mas recomendada)

1. Na mesma tela, abra a aba **Variables**.
2. Clique em **New repository variable**.
3. Nome: `RENDER_APP_URL`
4. Valor: a URL pública do Render, **sem barra no final**. Exemplo:
   `https://jiujitsu-academy.onrender.com`
5. Clique em **Add variable**.

> O job de deploy usa `RENDER_APP_URL` para aguardar `/health` responder HTTP
> 200. Se você não criar a variable, o deploy ainda funciona, mas o health check
> é pulado.

Se o workflow usar o environment `production` e você configurou regras de
aprovação nesse environment, será necessário aprovar o deploy em **Actions**.

### 3.7 Executar e acompanhar o workflow

O push do passo 3.3 já deve ter disparado o workflow. Para acompanhar:

1. Acesse https://github.com/lucasbombev/jiujitsu-soa/actions
2. Clique no workflow **CI/CD - Testes e Deploy**.
3. Abra a execução mais recente.
4. Você deve ver:
   - `Backend - Pytest` ✅
   - `Frontend - Vitest` ✅
   - `Deploy no Render` ✅ (somente em push para `main`)
5. Abra o job **Deploy no Render** e confira os logs:
   - `Disparando deploy hook do Render...`
   - `Resposta HTTP do Render: 200` (ou 201)
   - `Aplicação saudável (HTTP 200) na tentativa N.`

Se o primeiro push ocorreu **antes** de você cadastrar o secret, o job de deploy
vai falhar com "Secret ausente". Nesse caso:

- cadastre o secret (passo 3.6);
- volte em **Actions**, abra a execução;
- clique em **Re-run failed jobs**; ou
- faça um novo commit/push na `main`.

Para rodar apenas os testes sem deploy, use **Actions → CI/CD - Testes e
Deploy → Run workflow** (o deploy só roda em `push`).

### 3.8 Verificar o deploy

1. Abra a URL pública do Render.
2. Confira:
   - A aplicação carrega com os cursos e matrículas de demonstração;
   - O badge de status no topo mostra `Cloud Online • SQLITE`;
   - https://SEU-SERVICO.onrender.com/health retorna `"status": "healthy"`;
   - https://SEU-SERVICO.onrender.com/docs abre o Swagger;
   - O login `admin` + senha definida no Render funciona;
   - Criar uma matrícula e recarregar a página mantém os dados (até o próximo
     deploy/restart).
3. No Render, abra **Logs** e confira se não há erros de banco.

### 3.9 Tirar os prints e gravar o vídeo

#### Prints obrigatórios

1. **Actions — visão geral:** execução com os jobs de backend, frontend e deploy
   verdes (todos com ✅).
2. **Deploy — logs:** trecho com "Disparando deploy hook", "Resposta HTTP" e
   "Aplicação saudável".
3. **Render — serviço Live:** painel do Render mostrando o serviço no ar e a URL.
4. **Aplicação publicada:** navegador com a URL do Render e o dashboard.
5. **Health check:** JSON de `/health` com `"status": "healthy"`.
6. **Testes locais (opcional):** terminal com `pytest -v` e `npm test` passando.

Salve as imagens em uma pasta `docs/evidencias/` (não é obrigatório commitar) e
referencie no relatório.

#### Roteiro do vídeo (3–5 minutos)

| Tempo | O que mostrar / falar |
|---|---|
| 0:00–0:30 | Apresentação: nome, disciplina, nome do projeto e repositório público. |
| 0:30–1:00 | Visão geral da arquitetura: FastAPI + SQLite/PostgreSQL + SPA em JS puro + SOAP legado. |
| 1:00–1:45 | Backend: abrir `tests/test_unit.py` e `tests/test_api.py`, explicar 2–3 casos (máscara de CPF, validação Pydantic, matrícula com curso inválido). Rodar `pytest -v` e mostrar os 22 testes passando. |
| 1:45–2:30 | Frontend: abrir `static/utils.js` e `tests/frontend/utils.test.js`; explicar `filterMatriculas` e `buildMatriculaRow`; rodar `npm test` e mostrar os 20 testes passando. |
| 2:30–3:00 | Abrir `.github/workflows/ci-cd.yml` e explicar os jobs, o cache, a condição `if` do deploy e os secrets. |
| 3:00–3:45 | Fazer um commit pequeno (ex.: ajustar uma frase do README) e dar `git push origin main`; mostrar o workflow rodando na aba Actions. |
| 3:45–4:30 | Mostrar o job de deploy concluído e abrir a aplicação publicada; mostrar `/health` e `/docs`. |
| 4:30–5:00 | Dificuldades enfrentadas e como foram resolvidas; concluir. |

**Dicas para o vídeo:**

- Feche abas com dados pessoais, tokens, secrets e o `.env`.
- Aumente a fonte do terminal.
- Se o Render estiver hibernando, abra a URL antes de gravar para "acordar" o
  serviço.
- Se o deploy demorar, corte a espera na edição e mostre o resultado final.
- Narre em primeira pessoa e explique o **porquê** de cada escolha, não apenas
  o comando.

### 3.10 Preencher o relatório final

Use o arquivo [`RELATORIO.md`](RELATORIO.md) como base. Seções sugeridas:

1. **Capa:** nome, curso, disciplina, professor, data, link do repositório.
2. **Resumo:** 5–8 linhas sobre o projeto e os resultados.
3. **Introdução e contexto:** evolução SOA → Cloud-Native.
4. **Objetivos:** geral e específicos (testes, CI/CD, deploy).
5. **Arquitetura e stack:** diagrama simples, tecnologias e decisões.
6. **Testes implementados:** tabelas com os casos de backend e frontend,
   comandos e resultados (22 + 20).
7. **Pipeline de CI/CD:** etapas, gatilhos, secrets, condição de deploy e
   prints.
8. **Deploy:** URL, provedor, configuração, health check e limitações do SQLite
   efêmero.
9. **Dificuldades enfrentadas e soluções:** use a tabela da seção 3.11.
10. **Conclusão:** o que foi aprendido e próximos passos.
11. **Referências:** documentações oficiais.
12. **Anexos:** prints, link do vídeo e do repositório.

### 3.11 Dificuldades enfrentadas — sugestões para o relatório

Escreva com suas palavras, mas você pode usar estes fatos reais do projeto:

| Dificuldade | Como foi superada |
|---|---|
| O frontend era JavaScript puro, sem framework e sem testes. | Extraí funções puras para `static/utils.js` e testei com Vitest + jsdom + Testing Library, sem precisar reescrever a SPA. |
| As funções de renderização estavam acopladas ao DOM e à API. | Criei `buildMatriculaRow`, que recebe um objeto e devolve HTML; o teste renderiza só a linha no jsdom. |
| Os testes de API compartilhavam estado e podiam usar o banco de desenvolvimento. | Criei `tests/conftest.py` para definir `DATABASE_URL` de teste antes de importar a aplicação. |
| O `requirements.txt` instala o Spyne direto do GitHub, o que pode falhar por rede. | Usei Python 3.12 (mesma versão do CI), validei a instalação completa e documentei o troubleshoot. |
| O SQLite no Render free é efêmero. | Documentei a limitação e deixei o caminho para PostgreSQL via `DATABASE_URL`. |
| O Render poderia deployar antes dos testes. | Configurei `autoDeploy: false` no `render.yaml` e o deploy passou a ser disparado pelo job do GitHub Actions, que depende dos testes. |
| O primeiro acesso ao Render free pode demorar. | O workflow aguarda até 10 minutos pelo `/health` antes de considerar o deploy concluído. |
| O ambiente local tinha Python 3.14 sem `pip`/`venv`. | Usei `uv` para instalar Python 3.12 e criar o ambiente isolado. |
| Avisos de depreciação do Pydantic v2. | Não bloqueiam a entrega; foram documentados como melhoria futura (`json_schema_extra`/`ConfigDict`). |

> Se a sua instituição exigir declaração de uso de IA, acrescente uma seção
> informando que a IA foi usada como apoio para auditoria, implementação dos
> testes/pipeline e documentação, e que você revisou e validou o resultado.

### 3.12 Checklist final antes de entregar

- [ ] `pytest -v` passa localmente.
- [ ] `npm test` passa localmente.
- [ ] `git status` não mostra `.env`, `node_modules`, `.venv` ou banco local.
- [ ] Push feito na `main`.
- [ ] Workflow verde na aba Actions (backend + frontend + deploy).
- [ ] Serviço Live no Render.
- [ ] `/health` retorna HTTP 200.
- [ ] README com o link real do deploy (substituir o placeholder).
- [ ] Prints salvos.
- [ ] Vídeo gravado (3–5 min).
- [ ] Relatório preenchido.
- [ ] Link do repositório e do vídeo enviados conforme o professor pedir.

---

## 4. Comandos úteis

### Ambiente Python

```bash
# Criar ambiente (Python 3.12)
python3.12 -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Rodar a aplicação
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# ou
python server.py
```

Se não tiver `python3.12`/`venv` no sistema:

```bash
# Ubuntu/Debian
sudo apt install python3.12 python3.12-venv

# Alternativa: uv (instala o Python 3.12 sem sudo)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.12
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Testes

```bash
# Backend — todos
pytest -v

# Backend — somente unidade
pytest tests/test_unit.py -v

# Backend — somente API
pytest tests/test_api.py -v

# Frontend
npm ci
npm test

# Frontend — cobertura
npm run test:coverage

# Frontend — modo watch durante o desenvolvimento
npm run test:watch
```

### Docker

```bash
docker compose up --build
docker compose down
```

### Deploy e verificação

```bash
# Health check local
curl http://127.0.0.1:8000/health

# Health check em produção (troque a URL)
curl https://SEU-SERVICO.onrender.com/health

# Testar o deploy hook manualmente (não faça isso no vídeo mostrando a URL)
curl -X POST "https://api.render.com/deploy/SEU-HOOK"
```

### Git

```bash
git status
git diff --stat
git add .
git commit -m "ci: adiciona testes unitários, testes de frontend e pipeline CI/CD"
git push origin main

# Atualizar a branch local
git pull --rebase origin main
```

### Validação rápida dos arquivos

```bash
# Sintaxe do JavaScript
node --check static/app.js
node --check static/utils.js

# Sintaxe dos YAMLs (se tiver PyYAML)
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci-cd.yml')); print('workflow OK')"
python -c "import yaml; yaml.safe_load(open('render.yaml')); print('render OK')"
```

---

## 5. Solução de Problemas

> **Correção mais recente (CI):** o GitHub Actions falhou com
> `ModuleNotFoundError: No module named 'server'` na coleta do Pytest. A causa
> e a correção definitiva estão na **seção 5.15**.

### 5.1 `No module named pytest` / `No module named fastapi`

O ambiente virtual não está ativado ou as dependências não foram instaladas:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 5.2 `ensurepip is not available` ao criar a venv

Falta o pacote `python3.12-venv`:

```bash
sudo apt install python3.12-venv
```

Ou use `uv` (seção 4).

### 5.3 `pip install` falha no Spyne (download do GitHub)

O `requirements.txt` instala o Spyne de `https://github.com/arskom/spyne/archive/master.zip`.
Se o GitHub estiver instável:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Se persistir, tente novamente em alguns minutos ou use o Docker, que isola o
ambiente. No CI, o cache do pip ajuda nas execuções seguintes, mas o download
inicial ainda depende do GitHub.

### 5.4 Quero PostgreSQL em vez de SQLite no Render

1. No Render, crie um **PostgreSQL** (New → Postgres).
2. Copie a **Internal Database URL**.
3. No serviço web, altere `DATABASE_URL` para essa URL
   (`postgresql://...`; o `database.py` também aceita `postgres://`).
4. Faça um novo deploy.

O `database.py` usa SQLAlchemy e cria as tabelas automaticamente. O plano free
do PostgreSQL do Render tem prazo de expiração; verifique as condições atuais.

### 5.5 Deploy falha com "Secret ausente"

O secret `RENDER_DEPLOY_HOOK_URL` não foi cadastrado ou está com outro nome.
Confira em **Settings → Secrets and variables → Actions**. O nome deve ser
exatamente `RENDER_DEPLOY_HOOK_URL`. Depois, use **Re-run failed jobs**.

### 5.6 Deploy falha com HTTP 401/403 no Render

A URL do Deploy Hook está incorreta/revogada. Gere um novo hook em
**Render → serviço → Settings → Deploy Hook** e atualize o secret no GitHub.

### 5.7 Health check do Render falha (503/502)

- Abra os **Logs** do serviço no Render e procure erros de banco.
- Confirme `DATABASE_URL=sqlite:///./jiujitsu.db` (ou a URL do PostgreSQL).
- Confirme o start command:
  `uvicorn server:app --host 0.0.0.0 --port $PORT`.
- O plano free pode estar hibernando; aguarde o primeiro acesso.
- Se o banco PostgreSQL expirou, recrie e atualize a URL.

### 5.8 O workflow não aparece na aba Actions

- Confirme que o arquivo está em `.github/workflows/ci-cd.yml` (nome e caminho
  exatos).
- Confirme que o YAML é válido (sem tabs, indentação com espaços).
- Confirme que o push foi para a `main`.
- Verifique se Actions está habilitado em **Settings → Actions → General**.

### 5.9 `npm ci` falha

O `package-lock.json` está dessincronizado do `package.json`. Rode:

```bash
npm install
git add package-lock.json
git commit -m "chore: atualiza lockfile"
git push origin main
```

Nunca remova o `package-lock.json` do repositório: o `npm ci` depende dele.

### 5.10 Vitest reclama de `document is not defined`

Confirme que `vitest.config.mjs` tem `environment: "jsdom"` e que o arquivo de
configuração está na raiz. Rode `npm test` novamente.

### 5.11 Testes backend usam o banco errado

O `tests/conftest.py` define `DATABASE_URL=sqlite:///./test_jiujitsu.db` antes
de importar a aplicação. Se você rodar testes de outro diretório, o caminho
relativo pode mudar. Rode sempre da raiz do projeto.

Se sobrar banco de teste:

```bash
rm -f test_jiujitsu.db
```

### 5.12 Porta 8000 ocupada

```bash
# Descobrir o processo
lsof -i :8000

# Ou subir em outra porta
uvicorn server:app --reload --port 8001
```

### 5.13 Avisos de depreciação do Pydantic

Os avisos `PydanticDeprecatedSince20` são de compatibilidade e não quebram os
testes. Para eliminá-los no futuro, troque `Field(..., example=...)` por
`Field(..., json_schema_extra={"example": ...})` e `class Config` por
`model_config = ConfigDict(from_attributes=True)`.

### 5.14 O Render "dormiu" e a URL demora

É o comportamento do plano free. Abra a URL alguns segundos antes de gravar o
vídeo ou de tirar o print. O job de deploy já espera até 10 minutos.

### 5.15 `ModuleNotFoundError: No module named 'server'` no GitHub Actions

**Sintoma no log do CI:**

```text
ImportError while importing test module '.../tests/test_api.py'.
tests/test_api.py:16: in <module>
    from server import app
E   ModuleNotFoundError: No module named 'server'

ImportError while importing test module '.../tests/test_unit.py'.
tests/test_unit.py:14: in <module>
    import server
E   ModuleNotFoundError: No module named 'server'

collected 0 items / 2 errors
```

**Causa:** o `server.py` está na raiz do projeto, mas o comando `pytest`
(console script usado no CI) não coloca o diretório atual no `sys.path`. O
Pytest adiciona ao caminho a pasta do arquivo de teste (`tests/`), não a raiz.
Localmente o erro pode não aparecer se você rodar `python -m pytest`, porque o
`python -m` insere o cwd no `sys.path`; por isso a diferença entre “passa na
minha máquina” e “falha no Actions”.

**Correção aplicada — `pytest.ini` na raiz:**

```ini
[pytest]
testpaths = tests
pythonpath = .
python_files = test_*.py
addopts = -ra
filterwarnings =
    ignore::pydantic.PydanticDeprecatedSince20
```

A linha `pythonpath = .` é relativa ao `rootdir` (a raiz, onde está o
`pytest.ini`) e faz o Pytest inserir a raiz no `sys.path` antes de importar os
módulos de teste. Com isso, `from server import app`, `import server` e
`import database` funcionam tanto no seu terminal quanto no runner do GitHub.

**Como validar localmente do mesmo jeito que o CI:**

```bash
cd ~/Documents/jiujitsu-soa
source .venv/bin/activate

# Use o console script, não `python -m pytest`; é assim que o CI executa.
pytest -v

# Deve coletar e executar 22 testes:
# 22 passed
```

Para conferir a configuração que o Pytest está usando:

```bash
pytest --trace-config 2>&1 | grep -E "rootdir|inifile"
```

**Não foi necessário alterar imports nos testes.** `tests/test_api.py` e
`tests/test_unit.py` continuam com `from server import app` / `import server`,
porque o problema era de caminho de importação, não de nome de módulo.

**Se o `server.py` estiver em uma subpasta** (ex.: `app/server.py`), o valor
correto seria `pythonpath = app` (ou o caminho da pasta que contém o módulo).
No nosso projeto ele está na raiz, então `pythonpath = .` é o correto.

**Alternativas (não necessárias agora):**

- Criar um `conftest.py` vazio na raiz: o Pytest insere a pasta do conftest no
  `sys.path`. Funciona, mas é menos explícito que `pythonpath = .`.
- Definir `PYTHONPATH: .` no step do workflow. Também funciona, mas duplica a
  configuração; preferimos deixar a regra no `pytest.ini`, que vale para
  qualquer execução (local, CI, IDE).

**Checklist rápido para esse erro:**

- [ ] `pytest.ini` está na raiz, não dentro de `tests/`.
- [ ] Contém `pythonpath = .`.
- [ ] `server.py` está na raiz (ou ajuste o caminho).
- [ ] O step do CI roda `pytest -v` a partir da raiz do repositório.
- [ ] O log mostra `22 tests collected` antes de executar.

---

## 6. Resumo do que falta (ordem recomendada)

1. Revisar o diff (3.1).
2. Criar o serviço no Render (3.4).
3. Criar o Deploy Hook (3.5).
4. Cadastrar `RENDER_DEPLOY_HOOK_URL` e `RENDER_APP_URL` (3.6).
5. Commit + push (3.3).
6. Acompanhar o workflow (3.7).
7. Validar a aplicação publicada (3.8).
8. Substituir o placeholder do deploy no README pelo link real.
9. Tirar prints e gravar o vídeo (3.9).
10. Preencher o relatório (3.10) e revisar o checklist final (3.12).
