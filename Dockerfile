# ==============================================================================
# DOCKERFILE - JIU-JITSU CLOUD WEB APPLICATION
# Otimizado para implantação em Nuvem (AWS EC2, ECS, Render, Railway)
# ==============================================================================

FROM python:3.12-slim

# Metadados
LABEL maintainer="Academia Jiu-Jitsu Cloud"
LABEL description="Aplicação Web para Nuvem - Híbrida SOA e Cloud-Native"

# Variáveis de ambiente para execução otimizada do Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HOST=0.0.0.0

# Diretório de trabalho no contêiner
WORKDIR /app

# Instalar dependências de sistema necessárias para compilação e rede
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas requirements primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código-fonte da aplicação
COPY . .

# Criar usuário não-root para segurança na nuvem
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor a porta configurada
EXPOSE 8000

# Healthcheck nativo do contêiner para orquestradores de nuvem
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Comando de inicialização do servidor Uvicorn ASGI
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT}"]
