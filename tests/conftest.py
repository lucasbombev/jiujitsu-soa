"""
Configuração compartilhada do Pytest.

Define variáveis de ambiente antes de qualquer módulo da aplicação ser
importado. Isso garante que os testes usem um banco SQLite isolado e
credenciais previsíveis, sem tocar no banco de desenvolvimento/produção.
"""

import os

os.environ["DATABASE_URL"] = "sqlite:///./test_jiujitsu.db"
os.environ["ADMIN_USER"] = "admin"
os.environ["ADMIN_PASSWORD"] = "senha_jiujitsu_123"
os.environ["SECRET_KEY"] = "test-secret-token"
