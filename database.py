"""
database.py - Camada de Persistência e Acesso a Dados Agnóstica
Compatível com SQLite (desenvolvimento local/IaaS) e PostgreSQL (AWS RDS / Render / Railway)
"""

import os
import logging
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()

# Logger
logger = logging.getLogger("jiujitsu.database")

# Obter URL de conexão das variáveis de ambiente
raw_db_url = os.getenv("DATABASE_URL", "sqlite:///./jiujitsu.db")

# Ajuste automático para o formato exigido pelo SQLAlchemy
# Plataformas como Heroku e Render frequentemente fornecem postgres:// em vez de postgresql://
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

# Configurar argumentos do motor
connect_args = {}
if raw_db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    raw_db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==============================================================================
# MODELOS DE DADOS
# ==============================================================================

class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(120), nullable=False)
    categoria = Column(String(60), nullable=False)
    valor = Column(Float, nullable=False)

    matriculas = relationship("Matricula", back_populates="curso", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "categoria": self.categoria,
            "valor": float(self.valor)
        }


class Matricula(Base):
    __tablename__ = "matriculas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome_aluno = Column(String(150), nullable=False)
    cpf = Column(String(20), nullable=False)
    id_curso = Column(Integer, ForeignKey("cursos.id"), nullable=False)
    plano = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="Ativo")
    data_criacao = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    curso = relationship("Curso", back_populates="matriculas")

    def to_dict(self):
        return {
            "id": self.id,
            "nome_aluno": self.nome_aluno,
            "cpf": self.cpf,
            "id_curso": self.id_curso,
            "curso_nome": self.curso.nome if self.curso else None,
            "plano": self.plano,
            "status": self.status,
            "data_criacao": self.data_criacao.isoformat() if self.data_criacao else None
        }


# ==============================================================================
# INICIALIZAÇÃO E SEEDS
# ==============================================================================

def init_db():
    """Cria tabelas se não existirem e popula cursos e matrículas iniciais."""
    logger.info("Verificando/Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Verifica se a tabela de cursos está vazia
        if db.query(Curso).count() == 0:
            logger.info("Populando cursos padrão no banco...")
            cursos_iniciais = [
                Curso(nome="Jiu-Jitsu Iniciante (Fundamentos)", categoria="Básico", valor=150.0),
                Curso(nome="Jiu-Jitsu Competição (No-Gi & Gi)", categoria="Avançado", valor=220.0),
                Curso(nome="Jiu-Jitsu Kids & Teens", categoria="Infantil", valor=120.0),
                Curso(nome="Defesa Pessoal & Jiu-Jitsu Master", categoria="Master", valor=160.0),
            ]
            db.add_all(cursos_iniciais)
            db.commit()
            
            # Popula matrículas de demonstração para exibição imediata no front-end
            logger.info("Populando matrículas padrão para demonstração acadêmica...")
            matriculas_iniciais = [
                Matricula(nome_aluno="Rickson Gracie", cpf="111.222.333-44", id_curso=2, plano="Anual", status="Ativo"),
                Matricula(nome_aluno="Kyra Gracie", cpf="222.333.444-55", id_curso=1, plano="Semestral", status="Ativo"),
                Matricula(nome_aluno="Carlos Alcantara", cpf="333.444.555-66", id_curso=3, plano="Mensal", status="Ativo"),
                Matricula(nome_aluno="Rodrigo Minotauro", cpf="444.555.666-77", id_curso=4, plano="Anual", status="Inativo"),
            ]
            db.add_all(matriculas_iniciais)
            db.commit()
            logger.info("Cursos e Matrículas padrão criados com sucesso.")
    except Exception as e:
        logger.error(f"Erro durante inicialização/seed do banco de dados: {e}")
        db.rollback()
    finally:
        db.close()


def get_db():
    """Gerador de sessão de banco para injeção de dependência no FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
