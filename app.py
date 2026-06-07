from spyne import Application, rpc, ServiceBase, Integer, Unicode, Array, ComplexModel, Fault, Boolean
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
import logging
import sqlite3
import os

DB_PATH = "jiujitsu.db"

# Configuração de logs
def configure_logging():
    log_format = "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"
    
    # Obter logger raiz
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remover handlers antigos se existirem
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    
    # Handler para arquivo
    file_handler = logging.FileHandler("jiujitsu_service.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)

# Inicializar Banco de Dados
def init_db():
    logging.info("Inicializando banco de dados SQLite...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de Cursos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cursos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria TEXT NOT NULL,
        valor REAL NOT NULL
    )
    """)
    
    # Tabela de Matrículas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matriculas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_aluno TEXT NOT NULL,
        cpf TEXT NOT NULL,
        id_curso INTEGER NOT NULL,
        plano TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Ativo',
        FOREIGN KEY (id_curso) REFERENCES cursos (id)
    )
    """)
    
    # Inserir cursos padrão se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM cursos")
    if cursor.fetchone()[0] == 0:
        logging.info("Populando cursos padrão no banco de dados...")
        cursor.executemany("""
        INSERT INTO cursos (nome, categoria, valor) VALUES (?, ?, ?)
        """, [
            ("Jiu-Jitsu Iniciante", "Basico", 150.0),
            ("Jiu-Jitsu Competição", "Avançado", 200.0),
            ("Jiu-Jitsu Kids", "Infantil", 120.0)
        ])
        conn.commit()
        
    conn.close()
    logging.info("Banco de dados SQLite inicializado com sucesso.")

# Verificação de segurança WS-Security UsernameToken
def check_security(ctx):
    logging.info(f"[{ctx.method_name}] Iniciando validação de segurança SOAP Header")
    
    if ctx.in_document is None:
        logging.warning(f"[{ctx.method_name}] Falha na autenticação: Documento SOAP ausente.")
        raise Fault(
            faultcode="Client.Security",
            faultstring="Security header is missing. SOAP requests to protected operations must contain a <wsse:Security> header."
        )
        
    namespaces = {
        'wsse': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'
    }
    
    # Encontrar elemento wsse:Security
    security = ctx.in_document.xpath('//wsse:Security', namespaces=namespaces)
    if not security:
        logging.warning(f"[{ctx.method_name}] Falha na autenticação: <wsse:Security> ausente no documento.")
        raise Fault(
            faultcode="Client.Security",
            faultstring="Security header is missing. SOAP requests to protected operations must contain a <wsse:Security> header."
        )
        
    # Encontrar wsse:UsernameToken
    username_token = security[0].xpath('.//wsse:UsernameToken', namespaces=namespaces)
    if not username_token:
        logging.warning(f"[{ctx.method_name}] Falha na autenticação: <wsse:UsernameToken> ausente.")
        raise Fault(
            faultcode="Client.Security",
            faultstring="Missing <wsse:UsernameToken> inside <wsse:Security>."
        )
        
    username = username_token[0].xpath('.//wsse:Username/text()', namespaces=namespaces)
    password = username_token[0].xpath('.//wsse:Password/text()', namespaces=namespaces)
    
    if not username or not password:
        logging.warning(f"[{ctx.method_name}] Falha na autenticação: Username ou Password vazios no SOAP Header.")
        raise Fault(
            faultcode="Client.Security",
            faultstring="Invalid UsernameToken credentials structure. Username and Password must be provided."
        )
        
    user = username[0]
    pwd = password[0]
    
    # Validar credenciais
    if user == "admin" and pwd == "senha_jiujitsu_123":
        logging.info(f"[{ctx.method_name}] Autenticação bem-sucedida para o usuário: {user}")
        return True
    else:
        logging.warning(f"[{ctx.method_name}] Falha na autenticação: Credenciais inválidas para o usuário '{user}'.")
        raise Fault(
            faultcode="Client.Security",
            faultstring="Authentication failed: Invalid username or password."
        )

# Modelos do Spyne
class CursoModel(ComplexModel):
    id = Integer
    nome = Unicode
    categoria = Unicode
    valor = Unicode

class MatriculaModel(ComplexModel):
    id = Integer
    nome_aluno = Unicode
    cpf = Unicode
    id_curso = Integer
    plano = Unicode
    status = Unicode

# Serviço Spyne
class GestorMatriculasService(ServiceBase):
    
    @rpc(Unicode, Unicode, Integer, Unicode, _returns=Integer)
    def registrar_matricula(ctx, nome_aluno, cpf, id_curso, plano):
        check_security(ctx)
        
        # Anonimizar CPF para logs (ex: 111.***.***-44)
        cpf_log = cpf
        if len(cpf) >= 11:
            cpf_log = f"{cpf[:3]}.***.***-{cpf[-2:]}"
        logging.info(f"[registrar_matricula] Tentativa de registrar matrícula: Aluno='{nome_aluno}', CPF='{cpf_log}', CursoID={id_curso}, Plano='{plano}'")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            # Validar se o curso existe
            cursor.execute("SELECT id FROM cursos WHERE id = ?", (id_curso,))
            curso = cursor.fetchone()
            if not curso:
                logging.error(f"[registrar_matricula] Curso ID {id_curso} não existe.")
                raise Fault("Client.ValidationError", "Curso Invalido")
                
            cursor.execute("""
            INSERT INTO matriculas (nome_aluno, cpf, id_curso, plano, status)
            VALUES (?, ?, ?, ?, 'Ativo')
            """, (nome_aluno, cpf, id_curso, plano))
            conn.commit()
            new_id = cursor.lastrowid
            logging.info(f"[registrar_matricula] Sucesso! Matrícula registrada com ID={new_id}")
            return new_id
        except Fault:
            raise
        except Exception as e:
            logging.error(f"[registrar_matricula] Erro ao salvar matrícula: {e}")
            raise Fault("Server.DatabaseError", str(e))
        finally:
            conn.close()

    @rpc(Integer, _returns=MatriculaModel)
    def consultar_matricula(ctx, id_matricula):
        # Esta operação é pública
        logging.info(f"[consultar_matricula] Consulta pública para matrícula ID={id_matricula}")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT id, nome_aluno, cpf, id_curso, plano, status
            FROM matriculas WHERE id = ?
            """, (id_matricula,))
            row = cursor.fetchone()
            if row:
                m_model = MatriculaModel(
                    id=row[0],
                    nome_aluno=row[1],
                    cpf=row[2],
                    id_curso=row[3],
                    plano=row[4],
                    status=row[5]
                )
                logging.info(f"[consultar_matricula] Sucesso! Matricula encontrada para aluno '{row[1]}'")
                return m_model
            else:
                logging.warning(f"[consultar_matricula] Matrícula ID={id_matricula} não encontrada.")
                return None
        except Exception as e:
            logging.error(f"[consultar_matricula] Erro: {e}")
            raise Fault("Server.DatabaseError", str(e))
        finally:
            conn.close()

    @rpc(_returns=Array(MatriculaModel))
    def listar_matriculas_ativas(ctx):
        check_security(ctx)
        logging.info("[listar_matriculas_ativas] Listando matrículas com status='Ativo'")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT id, nome_aluno, cpf, id_curso, plano, status
            FROM matriculas WHERE status = 'Ativo'
            """)
            rows = cursor.fetchall()
            ativas = []
            for row in rows:
                ativas.append(MatriculaModel(
                    id=row[0],
                    nome_aluno=row[1],
                    cpf=row[2],
                    id_curso=row[3],
                    plano=row[4],
                    status=row[5]
                ))
            logging.info(f"[listar_matriculas_ativas] Sucesso! Retornando {len(ativas)} matrículas ativas.")
            return ativas
        except Exception as e:
            logging.error(f"[listar_matriculas_ativas] Erro: {e}")
            raise Fault("Server.DatabaseError", str(e))
        finally:
            conn.close()

    @rpc(Unicode, _returns=Array(CursoModel))
    def consultar_cursos(ctx, categoria):
        # Esta operação é pública
        logging.info(f"[consultar_cursos] Consulta pública de cursos para Categoria='{categoria}'")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            if categoria:
                cursor.execute("""
                SELECT id, nome, categoria, valor
                FROM cursos WHERE LOWER(categoria) = LOWER(?)
                """, (categoria,))
            else:
                cursor.execute("SELECT id, nome, categoria, valor FROM cursos")
            rows = cursor.fetchall()
            res = []
            for row in rows:
                c_model = CursoModel(id=row[0], nome=row[1], categoria=row[2], valor=str(row[3]))
                res.append(c_model)
            logging.info(f"[consultar_cursos] Retornados {len(res)} cursos cadastrados.")
            return res
        except Exception as e:
            logging.error(f"[consultar_cursos] Erro: {e}")
            raise Fault("Server.DatabaseError", str(e))
        finally:
            conn.close()

    @rpc(Integer, Unicode, _returns=Boolean)
    def atualizar_status_matricula(ctx, id_matricula, status):
        check_security(ctx)
        logging.info(f"[atualizar_status_matricula] Atualizando matricula ID={id_matricula} para Status='{status}'")
        
        # Validar status permitido
        if status not in ["Ativo", "Inativo", "Cancelado"]:
            logging.error(f"[atualizar_status_matricula] Status inválido: '{status}'")
            raise Fault("Client.ValidationError", f"Status inválido: '{status}'. Permitidos: Ativo, Inativo, Cancelado")
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE matriculas SET status = ? WHERE id = ?", (status, id_matricula))
            conn.commit()
            updated = cursor.rowcount > 0
            if updated:
                logging.info(f"[atualizar_status_matricula] Sucesso! Matricula ID={id_matricula} atualizada.")
            else:
                logging.warning(f"[atualizar_status_matricula] Matrícula ID={id_matricula} não encontrada.")
            return updated
        except Exception as e:
            logging.error(f"[atualizar_status_matricula] Erro: {e}")
            raise Fault("Server.DatabaseError", str(e))
        finally:
            conn.close()

    @rpc(Integer, _returns=Boolean)
    def deletar_matricula(ctx, id_matricula):
        check_security(ctx)
        logging.info(f"[deletar_matricula] Deletando matricula ID={id_matricula}")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM matriculas WHERE id = ?", (id_matricula,))
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logging.info(f"[deletar_matricula] Sucesso! Matricula ID={id_matricula} deletada.")
            else:
                logging.warning(f"[deletar_matricula] Matrícula ID={id_matricula} não encontrada para deleção.")
            return deleted
        except Exception as e:
            logging.error(f"[deletar_matricula] Erro: {e}")
            raise Fault("Server.DatabaseError", str(e))
        finally:
            conn.close()

# Configuração da Aplicação Spyne
application = Application([GestorMatriculasService],
    tns='jiujitsu.escola.services',
    in_protocol=Soap11(),
    out_protocol=Soap11()
)

if __name__ == '__main__':
    configure_logging()
    init_db()
    logging.info("Iniciando servidor SOAP Gestor de Matrículas em http://127.0.0.1:8000/")
    wsgi_app = WsgiApplication(application)
    server = make_server('127.0.0.1', 8000, wsgi_app)
    server.serve_forever()
