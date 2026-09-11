"""
server.py - Servidor Web Cloud-Native (FastAPI + Uvicorn)
Desenvolvido para a disciplina de Aplicação Web para Nuvem.
Oferece API RESTful, Healthcheck para Cloud Load Balancers, Documentação OpenAPI/Swagger e Front-end SPA.
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv

import database
from database import get_db, Curso, Matricula, init_db

load_dotenv()

# ==============================================================================
# CONFIGURAÇÃO DE LOGS (12-Factor: Event Streams para stdout)
# ==============================================================================
LOG_FORMAT = "%(asctime)s [%(levelname)s] [API Cloud] - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, stream=sys.stdout)
logger = logging.getLogger("jiujitsu.api")

# ==============================================================================
# LIFESPAN DA APLICAÇÃO (Startup e Shutdown modernos)
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando Jiu-Jitsu Cloud Web Application...")
    init_db()
    logger.info("Banco de dados pronto para requisições.")
    yield
    logger.info("Encerrando aplicação com graça (Graceful shutdown)...")

# ==============================================================================
# VARIÁVEIS DE AMBIENTE E SEGURANÇA
# ==============================================================================
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "senha_jiujitsu_123")
SECRET_TOKEN = os.getenv("SECRET_KEY", "jiujitsu-cloud-secret-token-2026")
APP_ENV = os.getenv("APP_ENV", "production")

# ==============================================================================
# INICIALIZAÇÃO DO FASTAPI
# ==============================================================================
app = FastAPI(
    title="🥋 Jiu-Jitsu Academy - Cloud Web API",
    description="""
API Web para Nuvem desenvolvida para a disciplina **Aplicação Web para Nuvem**.
- Evolução de arquitetura SOA (SOAP 1.1) para **Cloud-Native RESTful**.
- Suporte a banco de dados agnóstico (SQLite e PostgreSQL / AWS RDS).
- Preparado para implantação em **IaaS (AWS EC2)** e **PaaS (Render, Railway, Vercel, Heroku)**.
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuração de CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# SCHEMAS PYDANTIC (Validação e Serialização)
# ==============================================================================

class CursoCreate(BaseModel):
    nome: str = Field(..., example="Jiu-Jitsu No-Gi Avançado")
    categoria: str = Field(..., example="Avançado")
    valor: float = Field(..., gt=0, example=210.0)

class CursoResponse(BaseModel):
    id: int
    nome: str
    categoria: str
    valor: float

    class Config:
        from_attributes = True

class MatriculaCreate(BaseModel):
    nome_aluno: str = Field(..., min_length=3, example="Rickson Gracie")
    cpf: str = Field(..., example="123.456.789-00")
    id_curso: int = Field(..., example=1)
    plano: str = Field(..., example="Mensal")

class MatriculaStatusUpdate(BaseModel):
    status: str = Field(..., example="Inativo")

class MatriculaResponse(BaseModel):
    id: int
    nome_aluno: str
    cpf: str
    id_curso: int
    curso_nome: Optional[str] = None
    plano: str
    status: str
    data_criacao: Optional[str] = None

class LoginRequest(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="senha_jiujitsu_123")

class TokenResponse(BaseModel):
    token: str
    message: str

def mask_cpf(cpf: str) -> str:
    """Função utilitária para mascarar CPF em logs (LGPD)."""
    clean_cpf = "".join(filter(str.isdigit, cpf))
    if len(clean_cpf) >= 11:
        return f"{clean_cpf[:3]}.***.***-{clean_cpf[-2:]}"
    return "***.***.***-**"

def verify_token(authorization: Optional[str] = Header(None)):
    """Verifica autenticação por Token Bearer para endpoints protegidos."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cabeçalho Authorization ausente. Forneça o token Bearer.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido. Use 'Bearer <token>'."
        )
        
    token = parts[1]
    if token != SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token de acesso inválido ou expirado."
        )
    return True

# ==============================================================================
# ENDPOINTS DE MONITORAMENTO E CLOUD HEALTHCHECK
# ==============================================================================

@app.get("/health", tags=["Cloud Health"])
def health_check(db: Session = Depends(get_db)):
    """
    Endpoint de Health Check para AWS Target Groups, Application Load Balancers e PaaS.
    Verifica a saúde do servidor e a conectividade com o banco de dados.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
        db_engine = database.engine.dialect.name
    except Exception as e:
        logger.error(f"Healthcheck: Falha na conexão com banco de dados: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": f"error: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    return {
        "status": "healthy",
        "service": "jiujitsu-cloud-web-app",
        "database": {
            "status": db_status,
            "engine": db_engine
        },
        "environment": APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ==============================================================================
# ENDPOINTS DE AUTENTICAÇÃO
# ==============================================================================

@app.post("/api/auth/login", response_model=TokenResponse, tags=["Autenticação"])
def login(creds: LoginRequest):
    """Realiza autenticação de administrador e retorna token de acesso."""
    if creds.username == ADMIN_USER and creds.password == ADMIN_PASSWORD:
        logger.info(f"Autenticação de administrador bem-sucedida para o usuário '{creds.username}'")
        return TokenResponse(
            token=SECRET_TOKEN,
            message="Autenticado com sucesso!"
        )
    logger.warning(f"Tentativa de login falha para o usuário '{creds.username}'")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas. Verifique usuário e senha."
    )

# ==============================================================================
# ENDPOINTS DE CURSOS
# ==============================================================================

@app.get("/api/cursos", response_model=List[CursoResponse], tags=["Cursos"])
def listar_cursos(categoria: Optional[str] = None, db: Session = Depends(get_db)):
    """Lista todos os cursos oferecidos ou filtra por categoria."""
    query = db.query(Curso)
    if categoria:
        query = query.filter(Curso.categoria.ilike(f"%{categoria}%"))
    cursos = query.all()
    logger.info(f"Consulta de cursos realizada. {len(cursos)} cursos encontrados.")
    return [CursoResponse(id=c.id, nome=c.nome, categoria=c.categoria, valor=c.valor) for c in cursos]

@app.post("/api/cursos", response_model=CursoResponse, status_code=status.HTTP_201_CREATED, tags=["Cursos"])
def criar_curso(curso_in: CursoCreate, db: Session = Depends(get_db), auth: bool = Depends(verify_token)):
    """Cadastra um novo curso (requer autenticação de administrador)."""
    novo_curso = Curso(
        nome=curso_in.nome,
        categoria=curso_in.categoria,
        valor=curso_in.valor
    )
    db.add(novo_curso)
    db.commit()
    db.refresh(novo_curso)
    logger.info(f"Novo curso cadastrado: '{novo_curso.nome}' (ID: {novo_curso.id})")
    return novo_curso

# ==============================================================================
# ENDPOINTS DE MATRÍCULAS
# ==============================================================================

@app.get("/api/matriculas", response_model=List[MatriculaResponse], tags=["Matrículas"])
def listar_matriculas(status_filtro: Optional[str] = None, curso_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Lista todas as matrículas, permitindo filtros por status ou curso."""
    query = db.query(Matricula)
    if status_filtro:
        query = query.filter(Matricula.status == status_filtro)
    if curso_id:
        query = query.filter(Matricula.id_curso == curso_id)
    
    matriculas = query.order_by(Matricula.id.desc()).all()
    logger.info(f"Consulta de matrículas realizada. {len(matriculas)} registros encontrados.")
    return [
        MatriculaResponse(
            id=m.id,
            nome_aluno=m.nome_aluno,
            cpf=m.cpf,
            id_curso=m.id_curso,
            curso_nome=m.curso.nome if m.curso else "Curso Desconhecido",
            plano=m.plano,
            status=m.status,
            data_criacao=m.data_criacao.isoformat() if m.data_criacao else None
        )
        for m in matriculas
    ]

@app.get("/api/matriculas/{id_matricula}", response_model=MatriculaResponse, tags=["Matrículas"])
def consultar_matricula(id_matricula: int, db: Session = Depends(get_db)):
    """Consulta os detalhes de uma matrícula específica por ID."""
    matricula = db.query(Matricula).filter(Matricula.id == id_matricula).first()
    if not matricula:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada.")
    return MatriculaResponse(
        id=matricula.id,
        nome_aluno=matricula.nome_aluno,
        cpf=matricula.cpf,
        id_curso=matricula.id_curso,
        curso_nome=matricula.curso.nome if matricula.curso else "Curso Desconhecido",
        plano=matricula.plano,
        status=matricula.status,
        data_criacao=matricula.data_criacao.isoformat() if matricula.data_criacao else None
    )

@app.post("/api/matriculas", response_model=MatriculaResponse, status_code=status.HTTP_201_CREATED, tags=["Matrículas"])
def registrar_matricula(mat_in: MatriculaCreate, db: Session = Depends(get_db)):
    """Registra uma nova matrícula de aluno."""
    # Validar se o curso indicado existe
    curso = db.query(Curso).filter(Curso.id == mat_in.id_curso).first()
    if not curso:
        logger.error(f"Falha ao registrar matrícula: Curso ID {mat_in.id_curso} não existe.")
        raise HTTPException(status_code=400, detail=f"Curso ID {mat_in.id_curso} não existe.")
    
    nova_mat = Matricula(
        nome_aluno=mat_in.nome_aluno,
        cpf=mat_in.cpf,
        id_curso=mat_in.id_curso,
        plano=mat_in.plano,
        status="Ativo"
    )
    db.add(nova_mat)
    db.commit()
    db.refresh(nova_mat)
    
    logger.info(f"Matrícula realizada com sucesso! ID={nova_mat.id}, Aluno='{nova_mat.nome_aluno}', CPF='{mask_cpf(nova_mat.cpf)}'")
    
    return MatriculaResponse(
        id=nova_mat.id,
        nome_aluno=nova_mat.nome_aluno,
        cpf=nova_mat.cpf,
        id_curso=nova_mat.id_curso,
        curso_nome=curso.nome,
        plano=nova_mat.plano,
        status=nova_mat.status,
        data_criacao=nova_mat.data_criacao.isoformat() if nova_mat.data_criacao else None
    )

@app.patch("/api/matriculas/{id_matricula}/status", response_model=MatriculaResponse, tags=["Matrículas"])
def atualizar_status(id_matricula: int, payload: MatriculaStatusUpdate, db: Session = Depends(get_db)):
    """Atualiza o status de uma matrícula (Ativo, Inativo, Cancelado)."""
    status_permitidos = ["Ativo", "Inativo", "Cancelado"]
    if payload.status not in status_permitidos:
        raise HTTPException(status_code=400, detail=f"Status inválido. Permitidos: {', '.join(status_permitidos)}")
    
    matricula = db.query(Matricula).filter(Matricula.id == id_matricula).first()
    if not matricula:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada.")
    
    matricula.status = payload.status
    db.commit()
    db.refresh(matricula)
    logger.info(f"Status da matrícula ID {id_matricula} atualizado para '{payload.status}'")
    
    return MatriculaResponse(
        id=matricula.id,
        nome_aluno=matricula.nome_aluno,
        cpf=matricula.cpf,
        id_curso=matricula.id_curso,
        curso_nome=matricula.curso.nome if matricula.curso else None,
        plano=matricula.plano,
        status=matricula.status,
        data_criacao=matricula.data_criacao.isoformat() if matricula.data_criacao else None
    )

@app.delete("/api/matriculas/{id_matricula}", status_code=status.HTTP_204_NO_CONTENT, tags=["Matrículas"])
def deletar_matricula(id_matricula: int, db: Session = Depends(get_db)):
    """Remove uma matrícula do sistema."""
    matricula = db.query(Matricula).filter(Matricula.id == id_matricula).first()
    if not matricula:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada.")
    
    db.delete(matricula)
    db.commit()
    logger.info(f"Matrícula ID {id_matricula} deletada com sucesso.")
    return None

# ==============================================================================
# ENDPOINT DE DASHBOARD & ESTATÍSTICAS
# ==============================================================================

@app.get("/api/dashboard/stats", tags=["Dashboard"])
def obter_metricas_dashboard(db: Session = Depends(get_db)):
    """Retorna métricas em tempo real para o dashboard do front-end."""
    total_cursos = db.query(Curso).count()
    total_matriculas = db.query(Matricula).count()
    ativas = db.query(Matricula).filter(Matricula.status == "Ativo").count()
    inativas = db.query(Matricula).filter(Matricula.status == "Inativo").count()
    canceladas = db.query(Matricula).filter(Matricula.status == "Cancelado").count()

    # Cálculo estimado de faturamento mensal baseado nas matrículas ativas
    faturamento_estimado = 0.0
    matriculas_ativas = db.query(Matricula).filter(Matricula.status == "Ativo").all()
    for m in matriculas_ativas:
        if m.curso and m.curso.valor:
            faturamento_estimado += m.curso.valor

    return {
        "total_cursos": total_cursos,
        "total_matriculas": total_matriculas,
        "matriculas_ativas": ativas,
        "matriculas_inativas": inativas,
        "matriculas_canceladas": canceladas,
        "faturamento_mensal_estimado": round(faturamento_estimado, 2),
        "taxa_retencao": round((ativas / total_matriculas * 100) if total_matriculas > 0 else 100, 1)
    }

# ==============================================================================
# ENDPOINT DE INTEROPERABILIDADE E INFORMAÇÕES ARQUITETURAIS
# ==============================================================================

@app.get("/api/architecture/info", tags=["Arquitetura & Nuvem"])
def info_arquitetura():
    """Retorna metadados pedagógicos da evolução de SOA para Nuvem."""
    return {
        "projeto": "Jiu-Jitsu Academy - Cloud Evolution",
        "disciplina": "Aplicação Web para Nuvem",
        "paradigmas": {
            "original_soa": {
                "protocolo": "SOAP 1.1 sobre HTTP",
                "contrato": "WSDL / XSD (jiujitsu_service.wsdl)",
                "seguranca": "WS-Security UsernameToken no header XML",
                "arquivo_legado": "app.py"
            },
            "evolucao_cloud": {
                "protocolo": "RESTful JSON / HTTP",
                "especificacao": "OpenAPI 3.0 / Swagger UI em /docs",
                "persistencia": "Agnóstica (SQLite para dev/IaaS simples e PostgreSQL para RDS/PaaS)",
                "aderencia": "12-Factor App (Fatores III, VI, VII, VIII, XI)",
                "observabilidade": "Health check em /health e logs estruturados em stdout"
            }
        },
        "deploys_suportados": {
            "iaas": "AWS EC2 (Ubuntu Linux + Nginx + Uvicorn + Systemd)",
            "paas": "Render.com, Railway, Heroku, Vercel"
        }
    }

# ==============================================================================
# CONFIGURAÇÃO DE ARQUIVOS ESTÁTICOS / FRONT-END
# ==============================================================================
# Garante que o diretório static existe
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=FileResponse, tags=["Front-end"])
def index():
    """Entrega a Single Page Application (SPA) principal."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse(
        content={
            "mensagem": "Front-end em construção. Acesse /docs para a API interativa.",
            "docs": "/docs",
            "health": "/health"
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    logger.info(f"Iniciando servidor Uvicorn em http://{host}:{port}")
    uvicorn.run("server:app", host=host, port=port, reload=True)
