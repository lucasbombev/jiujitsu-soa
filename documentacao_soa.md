# 2. Modelagem do Sistema Orientado a Serviços (SOA)

Este documento contém a modelagem da arquitetura SOA para o sistema de "Gestor de Inscrições ou Matrículas para uma escola de jiu-jitsu", contemplando a especificação dos serviços principais do domínio.

## 2.1 Descrição do Domínio e dos Serviços

**Contextualização do Problema:**
O sistema objetiva automatizar e organizar o gerenciamento administrativo de uma academia de Jiu-Jitsu. Muitas escolas tradicionais sofrem com o controle manual ou fragmentado de fichas de alunos, pacotes de planos (mensal, semestral, anual) e turmas por níveis (iniciante, avançado) e faixas. A adoção de uma arquitetura orientada a serviços (SOA) promove a integração das matrículas a outras futuras plataformas do negócio (como aplicativo móvel para o aluno e catracas de acesso), garantindo flexibilidade e escalabilidade.

**Atores:**
- **Sistema Integrador / Frente de Caixa:** Aplicação ou interface de balcão utilizada na recepção.
- **Recepcionista / Administrador:** Usuário que lança dados e gerencia as matrículas.
- **Aluno (Cliente final):** Alvo da matrícula que necessita ser alocado em turmas e cursos/planos do sistema.

**Serviços Lógicos do Domínio:**
Para garantir um ecossistema desacoplado, dividimos a solução no mínimo em três serviços lógicos básicos:

1. **Serviço de Modalidades (Cursos):** Responsável por expor o catálogo e gerenciar cursos/produtos.
   - Retorna as modalidades de Jiu-Jitsu disponíveis, detalhes de cada item, e permite a pesquisa por categoria (ex: Jiu-Jitsu Infantil, Competição, Defesa Pessoal).
2. **Serviço de Pagamento / Faturamento:** Responsável pela orquestração financeira.
   - Embora não seja o escopo total de implementação nesta fase, esse serviço atua lógicamente validando o pagamento das faturas geradas pelos planos no momento da matrícula.
3. **Serviço de Matrículas (Gestor de Inscrições):** Serviço central responsável pelo ciclo de vida da relação do Aluno com a Escola. 
   - Cria o vínculo (matrícula) entre o Aluno e a Modalidade/Curso. Gerencia o status (Ativo/Inativo) e permite consultas dos dados da inscrição feita.

---

## 2.2 Arquitetura de Serviços

A arquitetura atual se concentra em expor operações sobre o Web Service SOAP, desenhado como serviço *bottom-up* na camada de integração da escola de Jiu-Jitsu.

**Serviços Expostos:**
Através do *endpoint* SOAP `GestorMatriculasService`, exporemos os seguintes métodos:
- `<RegistrarMatricula>`
- `<ConsultarMatricula>`
- `<ListarMatriculasAtivas>`
- `<ConsultarCursos>`

**Interfaces de Serviços e Operações:**
1. **`RegistrarMatricula`**
   - **Parâmetros de Entrada:** `Nome (string)`, `CPF (string)`, `IdCurso (int)`, `TipoPlano (string - ex: MENSAL, ANUAL)`.
   - **Retorno:** `IdMatriculaGerada (int)` e `MensagemStatus (string)`.
2. **`ConsultarMatricula`**
   - **Parâmetros de Entrada:** `IdMatricula (int)`.
   - **Retorno:** Detalhes consolidados da Matrícula (`Nome`, `CPF`, `Curso`, `Status`, `Data`).
3. **`ListarMatriculasAtivas`**
   - **Parâmetros de Entrada:** *Nenhum* (ou token lógico).
   - **Retorno:** Lista/Array de todos os registros (Inscrições) com *Status = "Ativo"*.
4. **`ConsultarCursos`**
   - **Parâmetros de Entrada:** `Categoria (string)`.
   - **Retorno:** Lista de Cursos/Planos disponíveis para a categoria informada.

**Linguagem e Protocolo:**
- **Protocolo de Comunicação:** HTTP (estudos de caso não-produtivos) / HTTPS em produção transportando envelopes estruturados via **SOAP 1.1**.
- **Linguagem de Definição e Mensageria:** O contrato e dados trocarão mensagens codificadas em **XML**, com validação embutida utilizando esquemas **XSD**.
- **Frame de Implementação:** A camada de servidor foi feita em **Python** utilizando o middleware de web services **Spyne**, servido por WSGI (Werkzeug).

---

## 2.3 Especificação dos Contratos de Serviço (WSDL/XML)

Abaixo está a representação dos principais trechos do arquivo **WSDL** abstrato modelado para o serviço do Gestor de Matrículas.

```xml
<!-- TYPES: Define os tipos de dados básicos utilizados (XSD embutido) -->
<wsdl:types>
    <xs:schema targetNamespace="jiujitsu.escola.services" elementFormDefault="qualified">
        <xs:element name="RegistrarMatricula">
            <xs:complexType>
                <xs:sequence>
                    <xs:element name="nome_aluno" type="xs:string" />
                    <xs:element name="cpf" type="xs:string" />
                    <xs:element name="id_curso" type="xs:integer" />
                    <xs:element name="plano" type="xs:string" />
                </xs:sequence>
            </xs:complexType>
        </xs:element>
        <xs:element name="RegistrarMatriculaResponse">
            <xs:complexType>
                <xs:sequence>
                    <xs:element name="RegistrarMatriculaResult" type="xs:integer" />
                </xs:sequence>
            </xs:complexType>
        </xs:element>
        <!-- Retornos Complexos omitidos para brevidade (ex: ConsultarMatriculaResponse) -->
    </xs:schema>
</wsdl:types>

<!-- MESSAGES: Define a estrutura da mensagem que vai e vem na rede -->
<wsdl:message name="RegistrarMatriculaSoapIn">
    <wsdl:part name="parameters" element="tns:RegistrarMatricula" />
</wsdl:message>
<wsdl:message name="RegistrarMatriculaSoapOut">
    <wsdl:part name="parameters" element="tns:RegistrarMatriculaResponse" />
</wsdl:message>

<!-- PORTTYPE (Interface): Agrupamento abstrato das operações e as mensagens de In / Out -->
<wsdl:portType name="GestorMatriculasPortType">
    <wsdl:operation name="RegistrarMatricula">
        <wsdl:input message="tns:RegistrarMatriculaSoapIn" />
        <wsdl:output message="tns:RegistrarMatriculaSoapOut" />
    </wsdl:operation>
    <!-- Outras operações: ConsultarMatricula, ListarMatriculasAtivas, etc. -->
</wsdl:portType>

<!-- BINDING: Ligar o envelope ao protocolo físico HTTP via SOAP -->
<wsdl:binding name="GestorMatriculasSoapBinding" type="tns:GestorMatriculasPortType">
    <soap:binding transport="http://schemas.xmlsoap.org/soap/http" style="document" />
    <wsdl:operation name="RegistrarMatricula">
        <soap:operation soapAction="RegistrarMatricula" style="document" />
        <wsdl:input>
            <soap:body use="literal" />
        </wsdl:input>
        <wsdl:output>
            <soap:body use="literal" />
        </wsdl:output>
    </wsdl:operation>
</wsdl:binding>

<!-- SERVICE: Endpoint final listado para consumo do cliente -->
<wsdl:service name="GestorMatriculasService">
    <wsdl:port name="GestorMatriculasPort" binding="tns:GestorMatriculasSoapBinding">
        <soap:address location="http://localhost:8000/matriculas" />
    </wsdl:port>
</wsdl:service>
```
