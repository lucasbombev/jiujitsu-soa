"""
Testes de unidade do backend.

Diferentemente de `test_api.py` (que sobe a aplicação com TestClient e valida
os endpoints de ponta a ponta), estes testes exercitam funções isoladas:
mascaramento de CPF, validação dos schemas Pydantic e serialização dos modelos
SQLAlchemy. São rápidos e não dependem de banco de dados.
"""

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

import server
from database import Curso, Matricula
from server import (
    CursoCreate,
    MatriculaCreate,
    MatriculaStatusUpdate,
    mask_cpf,
    verify_token,
)


class TestMaskCpf:
    """Testes da função utilitária de mascaramento de CPF (LGPD)."""

    def test_mascara_cpf_formatado(self):
        assert mask_cpf("123.456.789-00") == "123.***.***-00"

    def test_mascara_cpf_somente_digitos(self):
        assert mask_cpf("12345678900") == "123.***.***-00"

    def test_cpf_curto_retorna_mascara_generica(self):
        assert mask_cpf("123") == "***.***.***-**"
        assert mask_cpf("") == "***.***.***-**"


class TestValidacaoSchemas:
    """Testes de unidade das regras de validação dos schemas Pydantic."""

    def test_matricula_com_nome_curto_e_rejeitada(self):
        with pytest.raises(ValidationError):
            MatriculaCreate(
                nome_aluno="Jo",
                cpf="123.456.789-00",
                id_curso=1,
                plano="Mensal",
            )

    def test_curso_com_valor_zero_e_rejeitado(self):
        with pytest.raises(ValidationError):
            CursoCreate(nome="Jiu-Jitsu", categoria="Básico", valor=0)

    def test_matricula_valida_e_aceita(self):
        matricula = MatriculaCreate(
            nome_aluno="Rickson Gracie",
            cpf="123.456.789-00",
            id_curso=1,
            plano="Anual",
        )
        assert matricula.nome_aluno == "Rickson Gracie"
        assert matricula.plano == "Anual"

    def test_status_update_aceita_valor(self):
        payload = MatriculaStatusUpdate(status="Inativo")
        assert payload.status == "Inativo"


class TestAutenticacao:
    """Testes de unidade da verificação do token Bearer."""

    def test_token_ausente_retorna_401(self):
        with pytest.raises(HTTPException) as exc:
            verify_token(None)
        assert exc.value.status_code == 401

    def test_formato_invalido_retorna_401(self):
        with pytest.raises(HTTPException) as exc:
            verify_token("Basic abc123")
        assert exc.value.status_code == 401

    def test_token_incorreto_retorna_403(self):
        with pytest.raises(HTTPException) as exc:
            verify_token("Bearer token-errado")
        assert exc.value.status_code == 403

    def test_token_correto_e_aceito(self):
        assert verify_token(f"Bearer {server.SECRET_TOKEN}") is True


class TestSerializacaoModelos:
    """Testes de unidade da conversão dos modelos SQLAlchemy para dicionário."""

    def test_curso_to_dict(self):
        curso = Curso(id=1, nome="Jiu-Jitsu Iniciante", categoria="Básico", valor=150.0)
        assert curso.to_dict() == {
            "id": 1,
            "nome": "Jiu-Jitsu Iniciante",
            "categoria": "Básico",
            "valor": 150.0,
        }

    def test_matricula_to_dict_sem_curso_carregado(self):
        matricula = Matricula(
            id=10,
            nome_aluno="Kyra Gracie",
            cpf="222.333.444-55",
            id_curso=2,
            plano="Semestral",
            status="Ativo",
        )
        data = matricula.to_dict()
        assert data["id"] == 10
        assert data["nome_aluno"] == "Kyra Gracie"
        assert data["curso_nome"] is None
        assert data["status"] == "Ativo"
