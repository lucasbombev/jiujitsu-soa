"""
tests/test_api.py - Testes Automatizados da Web API Cloud-Native
Executa validação completa dos endpoints REST, autenticação, persistência e health checks.
"""

import os
import pytest
from fastapi.testclient import TestClient

# Garante uso de banco de teste SQLite em memória ou arquivo isolado
os.environ["DATABASE_URL"] = "sqlite:///./test_jiujitsu.db"
os.environ["ADMIN_USER"] = "admin"
os.environ["ADMIN_PASSWORD"] = "senha_jiujitsu_123"
os.environ["SECRET_KEY"] = "test-secret-token"

from server import app
from database import init_db

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Inicializa banco limpo para testes."""
    init_db()
    yield
    if os.path.exists("test_jiujitsu.db"):
        try:
            os.remove("test_jiujitsu.db")
        except Exception:
            pass


def test_health_check():
    """Valida o endpoint de Health Check de nuvem."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"]["status"] == "connected"
    assert "sqlite" in data["database"]["engine"].lower()


def test_listar_cursos():
    """Verifica se os cursos padrão foram populados pelo seed."""
    response = client.get("/api/cursos")
    assert response.status_code == 200
    cursos = response.json()
    assert len(cursos) >= 3
    nomes = [c["nome"] for c in cursos]
    assert any("Iniciante" in n for n in nomes)


def test_registrar_matricula_valida():
    """Testa criação de nova matrícula com sucesso."""
    payload = {
        "nome_aluno": "Royce Gracie",
        "cpf": "999.888.777-66",
        "id_curso": 1,
        "plano": "Anual"
    }
    response = client.post("/api/matriculas", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nome_aluno"] == "Royce Gracie"
    assert data["status"] == "Ativo"
    assert data["id"] is not None


def test_registrar_matricula_curso_invalido():
    """Valida rejeição de matrícula quando o ID do curso não existe."""
    payload = {
        "nome_aluno": "Aluno Fantasma",
        "cpf": "000.111.222-33",
        "id_curso": 99999,
        "plano": "Mensal"
    }
    response = client.post("/api/matriculas", json=payload)
    assert response.status_code == 400
    assert "não existe" in response.json()["detail"]


def test_atualizar_status_matricula():
    """Testa transição de status (Ativo -> Inativo)."""
    # Cria uma matrícula para testar
    res_cria = client.post("/api/matriculas", json={
        "nome_aluno": "Aluno Status Test",
        "cpf": "123.123.123-12",
        "id_curso": 1,
        "plano": "Mensal"
    })
    mat_id = res_cria.json()["id"]

    # Altera status
    res_patch = client.patch(f"/api/matriculas/{mat_id}/status", json={"status": "Inativo"})
    assert res_patch.status_code == 200
    assert res_patch.json()["status"] == "Inativo"


def test_deletar_matricula():
    """Testa exclusão de matrícula."""
    res_cria = client.post("/api/matriculas", json={
        "nome_aluno": "Aluno Para Deletar",
        "cpf": "555.555.555-55",
        "id_curso": 1,
        "plano": "Mensal"
    })
    mat_id = res_cria.json()["id"]

    # Deleta
    res_del = client.delete(f"/api/matriculas/{mat_id}")
    assert res_del.status_code == 204

    # Consulta novamente para verificar se sumiu
    res_get = client.get(f"/api/matriculas/{mat_id}")
    assert res_get.status_code == 404


def test_dashboard_stats():
    """Verifica se as métricas do dashboard são calculadas corretamente."""
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_matriculas" in stats
    assert "matriculas_ativas" in stats
    assert "faturamento_mensal_estimado" in stats
    assert stats["total_cursos"] >= 1


def test_autenticacao_admin():
    """Testa login com credenciais corretas e incorretas."""
    # Falha
    res_fail = client.post("/api/auth/login", json={"username": "admin", "password": "senha_errada"})
    assert res_fail.status_code == 401

    # Sucesso
    res_ok = client.post("/api/auth/login", json={"username": "admin", "password": "senha_jiujitsu_123"})
    assert res_ok.status_code == 200
    assert "token" in res_ok.json()
    assert res_ok.json()["token"] == "test-secret-token"


def test_criar_curso_protegido_por_token():
    """Verifica proteção de rota de criação de cursos."""
    payload = {
        "nome": "Jiu-Jitsu Judô Integrado",
        "categoria": "Avançado",
        "valor": 190.0
    }
    # Sem token deve falhar
    res_no_auth = client.post("/api/cursos", json=payload)
    assert res_no_auth.status_code == 401

    # Com token válido
    headers = {"Authorization": "Bearer test-secret-token"}
    res_auth = client.post("/api/cursos", json=payload, headers=headers)
    assert res_auth.status_code == 201
    assert res_auth.json()["nome"] == "Jiu-Jitsu Judô Integrado"
