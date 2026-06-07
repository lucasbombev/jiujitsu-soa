# Relatório Técnico - Evolução do Serviço SOAP (Unidade 3)
**Disciplina:** Arquitetura Orientada a Serviços (SOA)  
**Projeto Prático 2:** Serviço Seguro, Documentado e Monitorado  
**Domínio de Negócio:** Gestor de Inscrições/Matrículas para Escola de Jiu-Jitsu  

---

## 1. Descrição da Evolução do Serviço

Nesta Unidade 3, o serviço SOAP originalmente construído de forma básica e em memória foi evoluído para atender a requisitos corporativos de **persistência real**, **segurança a nível de mensagem**, **documentação rigorosa** e **monitoramento/auditoria**.

### Evolução da Arquitetura
1. **Camada de Persistência:** Substituição da simulação em memória (`list` do Python) por um banco de dados relacional **SQLite**.
2. **Camada de Segurança:** Implementação de controle de acesso baseado no padrão **WS-Security (UsernameToken)** no cabeçalho (Header) do envelope SOAP.
3. **Evolução do Contrato:** Adicionados os métodos para fechar o ciclo de vida completo do recurso (CRUD completo):
   - `atualizar_status_matricula` (Update)
   - `deletar_matricula` (Delete)
4. **Camada de Monitoramento:** Implementação de logging estruturado gravando em arquivo rotativo (`jiujitsu_service.log`) e no console, cobrindo tentativas de acesso, auditoria de segurança e consultas de banco de dados.

---

## 2. Persistência de Dados e CRUD Completo

O banco de dados escolhido foi o **SQLite**, por ser embutido na biblioteca padrão do Python (`sqlite3`), eliminando a necessidade de servidores externos e facilitando a portabilidade do projeto.

### 2.1 Modelo de Dados (Schema)
O banco `jiujitsu.db` contém duas tabelas com integridade referencial:

*   **Tabela `cursos`:** Catálogo de modalidades oferecidas pela escola.
*   **Tabela `matriculas`:** Registro das inscrições dos alunos vinculados a um curso.

```sql
CREATE TABLE IF NOT EXISTS cursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,
    valor REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS matriculas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_aluno TEXT NOT NULL,
    cpf TEXT NOT NULL,
    id_curso INTEGER NOT NULL,
    plano TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Ativo',
    FOREIGN KEY (id_curso) REFERENCES cursos (id)
);
```

### 2.2 Operações CRUD Disponibilizadas
*   **Create (C):** `registrar_matricula` (Insere matrícula no banco após validar a existência do `id_curso`).
*   **Read (R):** `consultar_matricula` (Busca uma inscrição por ID) e `listar_matriculas_ativas` (Retorna todas com `status = 'Ativo'`).
*   **Update (U):** `atualizar_status_matricula` (Atualiza o campo `status` da matrícula para `Ativo`, `Inativo` ou `Cancelado`).
*   **Delete (D):** `deletar_matricula` (Remove fisicamente o registro do banco de dados).

---

## 3. Segurança em Serviços SOAP (WS-Security)

### 3.1 Justificativa da Abordagem Escolhida
Para serviços SOAP, o padrão de segurança da indústria é o **WS-Security (Web Services Security)**. Optou-se por implementar a autenticação baseada em **UsernameToken** no cabeçalho SOAP (`<soapenv:Header>`), que transporta o nome de usuário e a senha criptografada ou em texto plano dentro de um elemento de segurança específico (`<wsse:Security>`).

Esta abordagem foi preferida por:
1.  **Compatibilidade Nativa:** É suportada de forma automática por ferramentas de teste corporativo como o **SoapUI**.
2.  **Desacoplamento de Protocolo:** A segurança é aplicada diretamente na mensagem (nível de aplicação), não dependendo unicamente da segurança da camada de transporte (como HTTPS/TLS), garantindo os princípios de robustez do SOA.
3.  **Segurança Específica por Operação:** Permite proteger métodos administrativos (`registrar_matricula`, `atualizar_status_matricula`, `deletar_matricula`, `listar_matriculas_ativas`) enquanto mantém consultas públicas abertas para clientes e prospectos (`consultar_cursos` e `consultar_matricula`).

### 3.2 Estrutura do Header WS-Security
Toda chamada para métodos protegidos deve conter a seguinte estrutura no cabeçalho:

```xml
<soapenv:Header>
   <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
      <wsse:UsernameToken>
         <wsse:Username>admin</wsse:Username>
         <wsse:Password>senha_jiujitsu_123</wsse:Password>
      </wsse:UsernameToken>
   </wsse:Security>
</soapenv:Header>
```

Se o cabeçalho for omitido ou as credenciais estiverem incorretas, o serviço bloqueia a execução na raiz e retorna um **SOAP Fault** padronizado com código `Client.Security`.

---

## 4. Contratos do Serviço e Documentação

### 4.1 Arquivo WSDL do Serviço
O WSDL completo está salvo na raiz do projeto como [jiujitsu_service.wsdl](file:///c:/Users/Usuario/Documents/jiujitsu-soa/jiujitsu_service.wsdl). Ele descreve o endpoint, os bindings SOAP 1.1 e as portas de comunicação.

### 4.2 Esquema XML (XSD)
Para respeitar as diretrizes de design de contratos rígidos em SOA, a definição dos tipos de dados complexos (`CursoModel`, `MatriculaModel`) foi extraída e isolada no arquivo [jiujitsu_service.xsd](file:///c:/Users/Usuario/Documents/jiujitsu-soa/jiujitsu_service.xsd).

### 4.3 Projeto de Testes SoapUI
Para fins de validação e entrega, foi gerado o arquivo [jiujitsu-soapui-project.xml](file:///c:/Users/Usuario/Documents/jiujitsu-soa/jiujitsu-soapui-project.xml). Este arquivo pode ser importado diretamente no SoapUI e contém requisições configuradas para cada operação, incluindo os headers de autenticação corretos e incorretos.

---

## 5. Evidências de Testes do Serviço SOAP

Os testes funcionais foram automatizados usando a biblioteca `zeep` (que gera envelopes SOAP idênticos aos de um cliente SoapUI) e simulam o comportamento real da API.

### 5.1 Relatório de Execução dos Testes (`test_execution.log`)
Abaixo está a saída literal do console gerada pelo script de validação de ponta a ponta (`test_soap.py`):

```text
==================================================
INICIANDO SUÍTE DE TESTES DO SERVIÇO SOAP DE JIU-JITSU
==================================================

TESTE 1: Consultar Cursos (Público, sem cabeçalho de segurança)...
Sucesso! Cursos cadastrados encontrados: 3
 - Curso ID 1: Jiu-Jitsu Iniciante (Basico) - R$ 150.0
 - Curso ID 2: Jiu-Jitsu Competição (Avançado) - R$ 200.0
 - Curso ID 3: Jiu-Jitsu Kids (Infantil) - R$ 120.0

TESTE 2: Registrar Matrícula Sem Autenticação (Deve falhar)...
Sucesso! Operação bloqueada como esperado. Erro retornado: Security header is missing. SOAP requests to protected operations must contain a <wsse:Security> header.

TESTE 3: Registrar Matrícula Com Senha Incorreta (Deve falhar)...
Sucesso! Operação bloqueada como esperado. Erro retornado: Authentication failed: Invalid username or password.

TESTE 4: Registrar Matrícula Com Credenciais Corretas (Deve funcionar)...
Sucesso! Matrícula registrada no banco de dados. ID Gerado: 1

TESTE 5: Consultar Matrícula ID 1 (Público)...
Sucesso! Detalhes da matrícula:
 - Aluno: Rickson Gracie
 - CPF: 222.333.444-55
 - Curso ID: 2
 - Plano: SEMESTRAL
 - Status: Ativo

TESTE 6: Listar Matrículas Ativas com Autenticação...
Sucesso! Matrículas ativas encontradas: 1
 - Inscrição 1: Rickson Gracie - Status: Ativo

TESTE 7: Atualizar Status da Matrícula ID 1 para 'Inativo'...
Sucesso! Status da matrícula alterado no banco de dados.
 - Novo status confirmado no banco: Inativo

TESTE 8: Deletar Matrícula ID 1 (CRUD - Delete)...
Sucesso! Matrícula deletada fisicamente do banco de dados.
 - Confirmação: Matrícula não foi mais localizada (sucesso).

==================================================
SUÍTE DE TESTES CONCLUÍDA COM SUCESSO!
==================================================
```

### 5.2 Exemplo de Mensagem SOAP de Erro (Falta de Autenticação - SOAP Fault)
Quando um cliente chama a operação `registrar_matricula` sem o cabeçalho de segurança, o servidor retorna o envelope SOAP 1.1 abaixo com código HTTP `500`:

```xml
<soap11env:Envelope xmlns:soap11env="http://schemas.xmlsoap.org/soap/envelope/">
   <soap11env:Body>
      <soap11env:Fault>
         <faultcode>Client.Security</faultcode>
         <faultstring>Security header is missing. SOAP requests to protected operations must contain a <wsse:Security> header.</faultstring>
      </soap11env:Fault>
   </soap11env:Body>
</soap11env:Envelope>
```

---

## 6. Evidências de Logs e Monitoramento

O servidor gera registros detalhados gravados no arquivo [jiujitsu_service.log](file:///c:/Users/Usuario/Documents/jiujitsu-soa/jiujitsu_service.log).

### 6.1 Extrato dos Logs do Servidor
Abaixo está o registro de atividades gerado durante a execução da suíte de testes:

```text
2026-06-07 15:09:20,601 [INFO] [app.py:35] - Inicializando banco de dados SQLite...
2026-06-07 15:09:20,605 [INFO] [app.py:76] - Banco de dados SQLite inicializado com sucesso.
2026-06-07 15:09:20,606 [INFO] [app.py:340] - Iniciando servidor SOAP Gestor de Matrículas em http://127.0.0.1:8000/
2026-06-07 15:09:20,634 [INFO] [app.py:248] - [consultar_cursos] Consulta pública de cursos para Categoria='None'
2026-06-07 15:09:20,637 [INFO] [app.py:263] - [consultar_cursos] Retornados 3 cursos cadastrados.
2026-06-07 15:09:20,642 [INFO] [app.py:80] - [registrar_matricula] Iniciando validação de segurança SOAP Header
2026-06-07 15:09:20,646 [WARNING] [app.py:96] - [registrar_matricula] Falha na autenticação: <wsse:Security> ausente no documento.
2026-06-07 15:09:20,650 [INFO] [app.py:80] - [registrar_matricula] Iniciando validação de segurança SOAP Header
2026-06-07 15:09:20,651 [WARNING] [app.py:129] - [registrar_matricula] Falha na autenticação: Credenciais inválidas para o usuário 'admin'.
2026-06-07 15:09:20,655 [INFO] [app.py:80] - [registrar_matricula] Iniciando validação de segurança SOAP Header
2026-06-07 15:09:20,655 [INFO] [app.py:126] - [registrar_matricula] Autenticação bem-sucedida para o usuário: admin
2026-06-07 15:09:20,655 [INFO] [app.py:161] - [registrar_matricula] Tentativa de registrar matrícula: Aluno='Rickson Gracie', CPF='222.***.***-55', CursoID=2, Plano='SEMESTRAL'
2026-06-07 15:09:20,659 [INFO] [app.py:179] - [registrar_matricula] Sucesso! Matrícula registrada com ID=1
2026-06-07 15:09:20,662 [INFO] [app.py:192] - [consultar_matricula] Consulta pública para matrícula ID=1
2026-06-07 15:09:20,664 [INFO] [app.py:211] - [consultar_matricula] Sucesso! Matricula encontrada para aluno 'Rickson Gracie'
2026-06-07 15:09:20,667 [INFO] [app.py:80] - [listar_matriculas_ativas] Iniciando validação de segurança SOAP Header
2026-06-07 15:09:20,667 [INFO] [app.py:126] - [listar_matriculas_ativas] Autenticação bem-sucedida para o usuário: admin
2026-06-07 15:09:20,667 [INFO] [app.py:225] - [listar_matriculas_ativas] Listando matrículas com status='Ativo'
2026-06-07 15:09:20,668 [INFO] [app.py:245] - [listar_matriculas_ativas] Sucesso! Retornando 1 matrículas ativas.
2026-06-07 15:09:20,671 [INFO] [app.py:80] - [atualizar_status_matricula] Iniciando validação de segurança SOAP Header
2026-06-07 15:09:20,671 [INFO] [app.py:126] - [atualizar_status_matricula] Autenticação bem-sucedida para o usuário: admin
2026-06-07 15:09:20,671 [INFO] [app.py:284] - [atualizar_status_matricula] Atualizando matricula ID=1 para Status='Inativo'
2026-06-07 15:09:20,676 [INFO] [app.py:298] - [atualizar_status_matricula] Sucesso! Matricula ID=1 atualizada.
2026-06-07 15:09:20,678 [INFO] [app.py:192] - [consultar_matricula] Consulta pública para matrícula ID=1
2026-06-07 15:09:20,680 [INFO] [app.py:211] - [consultar_matricula] Sucesso! Matricula encontrada para aluno 'Rickson Gracie'
2026-06-07 15:09:20,683 [INFO] [app.py:80] - [deletar_matricula] Iniciando validação de segurança SOAP Header
2026-06-07 15:09:20,683 [INFO] [app.py:126] - [deletar_matricula] Autenticação bem-sucedida para o usuário: admin
2026-06-07 15:09:20,684 [INFO] [app.py:311] - [deletar_matricula] Deletando matricula ID=1
2026-06-07 15:09:20,688 [INFO] [app.py:320] - [deletar_matricula] Sucesso! Matricula ID=1 deletada.
2026-06-07 15:09:20,692 [INFO] [app.py:192] - [consultar_matricula] Consulta pública para matrícula ID=1
2026-06-07 15:09:20,693 [WARNING] [app.py:214] - [consultar_matricula] Matrícula ID=1 não encontrada.
```

---

## 7. Conclusão

Com as evoluções realizadas, o serviço SOAP Gestor de Matrículas de Jiu-Jitsu agora atende plenamente aos requisitos de robustez exigidos para aplicações corporativas no escopo do paradigma SOA:
-   **Contrato Isolado:** Interface exposta formalmente em WSDL e modelos de dados definidos rigorosamente no XSD desacoplado.
-   **Segurança Robusta:** Autenticação padrão de mercado WS-Security UsernameToken protegendo as operações administrativas no nível da mensagem XML.
-   **Persistência Relacional:** Operações CRUD integradas com banco de dados relacional SQLite, garantindo integridade e transacionalidade de dados.
-   **Monitoramento e Auditoria:** Rastreabilidade total das transações e tentativas de acesso via logs estruturados de auditoria, facilitando a identificação rápida de anomalias ou acessos indevidos.
