# Roteiro Completo para Vídeo de Apresentação Acadêmica
## Disciplina: Aplicação Web para Nuvem
**Projeto:** Jiu-Jitsu Academy - Da Arquitetura SOA à Aplicação Web Cloud-Native  
**Tempo Recomendado:** 10 minutos *(com notas de ajuste para 5 ou 15 minutos)*  
**Apresentador:** [Seu Nome Completo]  

---

## Estrutura do Roteiro e Cronograma

| Bloco | Conteúdo | Duração (10 min) | Duração (5 min) | Duração (15 min) |
| :--- | :--- | :--- | :--- | :--- |
| **Bloco 1** | Abertura, Contexto e Arquitetura SOA Original | 00:00 - 02:00 | 00:00 - 01:00 | 00:00 - 03:00 |
| **Bloco 2** | Evolução para a Nuvem e Arquitetura-Alvo | 02:00 - 03:30 | 01:00 - 01:45 | 03:00 - 05:30 |
| **Bloco 3** | Demonstração Prática (Front, Back, Swagger, DB) | 03:30 - 06:30 | 01:45 - 03:30 | 05:30 - 10:00 |
| **Bloco 4** | Deploys em Nuvem: IaaS (AWS EC2) e PaaS (Render) | 06:30 - 08:30 | 03:30 - 04:30 | 10:00 - 13:00 |
| **Bloco 5** | Segurança, 12-Factor, Desafios e Encerramento | 08:30 - 10:00 | 04:30 - 05:00 | 13:00 - 15:00 |

---

## BLOCO 1: Abertura e Apresentação do Projeto SOA Original (00:00 - 02:00)

### 🎬 Ação de Tela:
- Câmera aberta no seu rosto com a tela de fundo exibindo o slide inicial ou a página principal do GitHub do projeto (`https://github.com/lucasbombev/jiujitsu-soa`).
- Em seguida, transicionar a tela para o VS Code / IDE mostrando o arquivo `app.py` e o arquivo `jiujitsu_service.wsdl`.

### 🗣️ Fala Sugerida:
> "Olá, professor(a) e colegas! Meu nome é **[Seu Nome]**, e estou apresentando o projeto final da disciplina de **Aplicação Web para Nuvem**."
> 
> "O objetivo deste trabalho é demonstrar a transformação e implantação em nuvem de uma aplicação pré-existente. Como base, escolhi o sistema **Jiu-Jitsu Academy**, que desenvolvi originalmente sob o paradigma **SOA — Service-Oriented Architecture**."
> 
> "Na versão SOA original, o sistema foi construído como um serviço web **SOAP 1.1** em Python usando a biblioteca Spyne. Como vocês podem ver aqui na minha tela no arquivo `app.py`, ele possui contratos formais de interface definidos em WSDL e tipos em XSD. As operações protegidas, como o registro e cancelamento de matrículas, utilizavam segurança a nível de mensagem com o padrão da OASIS: **WS-Security UsernameToken**, inspecionando o cabeçalho XML via XPath."
> 
> "Essa arquitetura era perfeita para integrações corporativas fechadas, testada via SoapUI e scripts com a biblioteca Zeep. Porém, para o ecossistema de nuvem e aplicações voltadas ao usuário final, tínhamos alguns desafios fundamentais: a ausência de um front-end web interativo, a dificuldade dos navegadores em consumir envelopes SOAP nativamente e a violação de princípios de aplicações modernas para nuvem."

---

## BLOCO 2: A Evolução Arquitetural para Nuvem (02:00 - 03:30)

### 🎬 Ação de Tela:
- Abrir o navegador na aplicação rodando e clicar no botão **"Arquitetura Cloud"** na barra superior para exibir o modal de comparação, ou abrir o diagrama Mermaid no `README.md`.

### 🗣️ Fala Sugerida:
> "Para atender aos requisitos da disciplina, evoluímos a aplicação para uma **arquitetura híbrida Cloud-Native**."
> 
> "Preservamos o núcleo de negócio, mas desacoplamos e expandimos as camadas em três pilares essenciais:
> 1. **Back-end Web RESTful assíncrono**: Implementado com FastAPI e servidor ASGI Uvicorn, gerando documentação automática OpenAPI/Swagger.
> 2. **Front-end Single Page Application (SPA)**: Construído com HTML5 semântico, CSS3 moderno com tema Dark/Glassmorphism e Vanilla JavaScript consumindo a API de forma assíncrona.
> 3. **Camada de Dados Agnóstica**: Utilizando SQLAlchemy com suporte nativo tanto a SQLite (para desenvolvimento local e testes rápidos) quanto a PostgreSQL (para os bancos gerenciados na nuvem, como o AWS RDS e o PostgreSQL do Render).
> 
> "Além disso, adaptamos o projeto aos princípios do **12-Factor App**: configurações extraídas para variáveis de ambiente com arquivo `.env`, logs estruturados enviados diretamente para `stdout` e endpoints de observabilidade como o `/health` para os balanceadores de carga da nuvem."

---

## BLOCO 3: Demonstração Prática Local (03:30 - 06:30)

### 🎬 Ação de Tela 1: Terminal Local e Inicialização
- Abrir o terminal limpo no VS Code e executar:
  ```bash
  python -m pytest tests/test_api.py -v
  ```
- Mostrar todos os 9 testes passando em verde.
- Em seguida, rodar o servidor:
  ```bash
  python server.py
  ```
- Apontar no terminal o log: `Iniciando Jiu-Jitsu Cloud Web Application...` e o bind em `http://0.0.0.0:8000`.

### 🗣️ Fala Sugerida:
> "Vejam aqui no terminal: primeiro executei nossa suíte automatizada de testes com Pytest, cobrindo endpoints de cursos, matrículas, filtros, cálculos de faturamento e healthcheck. Todos os testes passaram com sucesso."
> "Agora, inicio o servidor Uvicorn escutando na porta 8000."

---

### 🎬 Ação de Tela 2: Navegador Web - Front-end SPA
- Alternar para o navegador em `http://localhost:8000`.
- Mostrar o design: Badge de status verde no topo com `Cloud Online • SQLITE`, os 4 cards de KPIs (Total de Alunos, Ativos, Cursos, Faturamento Mensal).
- Rolar até o catálogo de cursos.
- Clicar em **"+ Nova Matrícula"**.
- Preencher:
  - Nome: `Royce Gracie`
  - CPF: digitar apenas números (mostrar a máscara automática formatando `999.888.777-66`).
  - Curso: `Jiu-Jitsu Competição`.
  - Plano: `Anual`.
  - Clicar em **Confirmar Matrícula**.
- Mostrar o Toast verde de sucesso e a nova linha aparecendo instantaneamente na tabela com status **ATIVO**.
- Apontar para os cards de KPI no topo que se atualizaram em tempo real (o faturamento e o total de alunos aumentaram).
- Na tabela, clicar no botão **"Inativar"** da matrícula criada e depois filtrar pelo dropdown de status para mostrar apenas os alunos ativos.

### 🗣️ Fala Sugerida:
> "Aqui está o front-end moderno que desenvolvemos. Ele é 100% responsivo e possui uma estética imersiva de artes marciais. No topo, temos o monitoramento de saúde do backend em tempo real."
> "Quando realizo uma nova matrícula, observem a validação e a máscara automática de CPF. Ao confirmar, o front-end envia um POST assíncrono para a nossa API REST, que persiste no banco relacional e atualiza os indicadores de faturamento e alunos ativos instantaneamente."
> "Na tabela de gestão, temos busca em tempo real, filtros por status e botões de ação imediata, tudo com tratamento de feedback visual para o usuário."

---

### 🎬 Ação de Tela 3: Swagger UI e Healthcheck
- Abrir uma nova aba em `http://localhost:8000/docs`.
- Passar rapidamente pelas rotas `/health`, `/api/cursos`, `/api/matriculas`, `/api/dashboard/stats`.
- Abrir a rota `/health`, clicar em **"Try it out"** -> **"Execute"** e mostrar o retorno JSON: `status: healthy`, `database: connected`.

### 🗣️ Fala Sugerida:
> "Para os desenvolvedores e integradores, a API expõe a especificação OpenAPI através do Swagger em `/docs`. Aqui podemos testar todos os contratos REST, autenticação por Bearer Token e o endpoint `/health`, que informa a saúde do serviço e o dialeto do banco de dados conectado."

---

## BLOCO 4: Deploy em Nuvem - IaaS e PaaS (06:30 - 08:30)

### 🎬 Ação de Tela 1: Demonstração do Deploy em IaaS (AWS EC2)
- Abrir a aba com o console da AWS (EC2) ou terminal SSH conectado na instância EC2 (`ssh ubuntu@ec2-public-ip`).
- Mostrar a aplicação rodando com seu IP público da AWS (exemplo: `http://54.232.xxx.xxx` ou domínio associado).
- Abrir o navegador no IP público da AWS e recarregar a página, mostrando que está online no ar.

### 🗣️ Fala Sugerida:
> "Agora vamos ao ponto central da disciplina: a implantação em nuvem pública."
> 
> "Para o requisito de **IaaS (Infraestrutura como Serviço)**, criei uma máquina virtual na **AWS usando o Amazon EC2** no plano Free Tier (instância t2.micro com Ubuntu Server 22.04 LTS)."
> 
> "A configuração foi feita manualmente via SSH:
> 1. Atualizamos os pacotes do Linux e configuramos o ambiente Python.
> 2. O servidor Uvicorn roda como um serviço do sistema operacional gerenciado pelo **systemd**, garantindo que ele reinicie automaticamente caso ocorra alguma falha.
> 3. Na frente da aplicação, configuramos o **Nginx como Reverse Proxy**, escutando na porta 80 padrão e repassando o tráfego localmente para o Uvicorn na porta 8000.
> 4. Configuramos o **Security Group** da AWS liberando as portas 22 (SSH restrito) e 80 (HTTP público)."
> 
> "Vejam aqui no navegador: ao acessar o IP público fornecido pela AWS, a aplicação responde perfeitamente, acessível para qualquer usuário na internet."

---

### 🎬 Ação de Tela 2: Demonstração do Deploy em PaaS (Render / Railway)
- Abrir a aba do painel do **Render.com** (ou Railway) mostrando o Web Service e o PostgreSQL Database criados.
- Mostrar a URL pública HTTPS gerada pelo Render (ex.: `https://jiujitsu-cloud-app.onrender.com`).
- Clicar no link e navegar na aplicação rodando em HTTPS com certificado SSL válido.
- Mostrar os logs no dashboard do Render demonstrando os commits e o deploy contínuo (CI/CD via Git).

### 🗣️ Fala Sugerida:
> "Para o requisito de **PaaS (Plataforma como Serviço)**, escolhi o **Render.com**."
> 
> "No modelo PaaS, não precisamos gerenciar o sistema operacional, patches ou servidores web manualmente. Conectamos o repositório do GitHub diretamente na plataforma. A cada `git push` na branch main, o Render detecta o nosso `Dockerfile`, compila a imagem, executa as migrações e sobe o serviço com certificado HTTPS/SSL configurado automaticamente."
> 
> "Além disso, provisionei uma instância gerenciada de **PostgreSQL** no Render, configurando a variável `DATABASE_URL` no painel. O SQLAlchemy conecta de forma transparente, permitindo que a aplicação seja totalmente stateless."

---

## BLOCO 5: Pontos Técnicos, Desafios e Conclusão (08:30 - 10:00)

### 🎬 Ação de Tela:
- Retornar a câmera para você ou mostrar o slide final / README com os links públicos.

### 🗣️ Fala Sugerida:
> "Para concluir, gostaria de destacar os principais aprendizados técnicos e desafios superados neste projeto:
> 
> 1. **Diferença prática entre IaaS e PaaS**: No IaaS (EC2), temos controle total sobre o sistema operacional, firewall e proxy reverso, mas a responsabilidade de manutenção é 100% nossa. No PaaS (Render), a produtividade e a automação do CI/CD são muito superiores, embora com menor controle granular de baixo nível.
> 2. **Segurança e Privacidade**: No transporte, usamos HTTPS/TLS e autenticação por Bearer Token. Na privacidade de dados (LGPD), implementamos mascaramento de CPF tanto nos logs estruturados quanto na visualização da tabela.
> 3. **Observabilidade**: O endpoint `/health` garante que balanceadores e orquestradores saibam exatamente se a aplicação e a conexão com o banco continuam ativas."
> 
> "Todo o código-fonte, a documentação com os comandos de deploy passo a passo e os links de acesso público estão disponíveis no repositório do GitHub no link da descrição."
> 
> "Agradeço a atenção do professor e de todos. Muito obrigado e até a próxima!"

---

## Dicas Práticas para a Gravação
- **Ferramentas Gratuitas de Gravação:** Recomendamos usar o **OBS Studio** (gratuito e open-source) com duas cenas:
  - Cena 1: Câmera + Tela Inteira (para demonstrações no navegador e terminal).
  - Cena 2: Câmera cheia (para abertura e encerramento).
- **Resolução Recomendada:** 1080p (1920x1080) a 30fps.
- **Áudio:** Use um fone com microfone razoável ou microfone de lapela. Faça um teste de 15 segundos antes de gravar tudo.
- **Preparação:** Deixe as abas do navegador já abertas antes de começar (Localhost, Swagger, AWS Console e Render Dashboard) para não perder tempo com logins ou carregamentos lentos.
