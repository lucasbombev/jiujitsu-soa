# Guia de Implantação na AWS EC2 (IaaS Manual)
## Disciplina: Aplicação Web para Nuvem
**Requisito Atendido:** *"IaaS: Criar e configurar uma máquina virtual (ex: AWS EC2, Google Cloud Compute Engine, Azure VM) e implantar manualmente uma aplicação web, gerando um link público de acesso."*

---

## 1. Arquitetura Recomendada e Estimativa de Custos

### Por que Amazon EC2?
Para cumprir o critério explícito de **IaaS (Infraestrutura como Serviço)**, a escolha mandatória é o **Amazon EC2 (Elastic Compute Cloud)**. Diferente de serviços PaaS (como Elastic Beanstalk) ou CaaS (como ECS Fargate), no EC2 o estudante provisiona a máquina virtual bruta (computação, memória, disco e rede) e é responsável por configurar o sistema operacional, o runtime (Python), o servidor de aplicação (Uvicorn) e o servidor web/proxy reverso (Nginx).

### Topologia de IaaS Escolhida
```
Internet (Usuário / Professor)
           │
           ▼ Porta 80 (HTTP)
   ┌──────────────────────────────────────────────────────────────┐
   │ AWS EC2 (Ubuntu 22.04 LTS - t2.micro Free Tier)              │
   │                                                              │
   │   Security Group (Firewall): Porta 22 (SSH) + Porta 80 (HTTP)│
   │                                                              │
   │   ┌───────────────┐     Proxy Pass     ┌──────────────────┐  │
   │   │ Nginx (Proxy) │ ─────────────────> │ Uvicorn (Systemd)│  │
   │   │ Porta 80      │   127.0.0.1:8000   │ FastAPI App      │  │
   │   └───────────────┘                    └─────────┬────────┘  │
   │                                                  │           │
   │                                                  ▼           │
   │                                     ┌─────────────────────┐  │
   │                                     │ SQLite jiujitsu.db  │  │
   │                                     │ (ou RDS PostgreSQL) │  │
   │                                     └─────────────────────┘  │
   └──────────────────────────────────────────────────────────────┘
```

### Análise de Custos no AWS Free Tier (Nível Gratuito)
- **Instância EC2:** `t2.micro` (ou `t3.micro` em regiões mais novas): 750 horas gratuitas por mês durante os primeiros 12 meses de conta AWS.
- **Armazenamento EBS:** Até 30 GB de disco General Purpose SSD (gp2/gp3) gratuitos.
- **IP Público IPv4:** A AWS oferece IPs públicos associados à instância sem custo enquanto a instância estiver em execução.
- **Custo Total para o Trabalho:** **R$ 0,00 (100% Gratuito)** se respeitados os limites do Free Tier.

---

## 2. Passo a Passo Completo: Provisionamento da Instância

### Método A: Pelo Console Web da AWS (Recomendado para Iniciantes)

1. **Acesse o Console AWS:**
   - Entre em [aws.amazon.com/console](https://aws.amazon.com/console) e selecione a região mais próxima (ex.: `us-east-1` Virgínia do Norte ou `sa-east-1` São Paulo).
2. **Navegue até o EC2:**
   - No campo de busca superior, digite `EC2` e clique no serviço.
   - Clique no botão laranja **"Launch Instance"** (Executar Instância).
3. **Configure os Parâmetros:**
   - **Name:** `jiujitsu-cloud-ec2`
   - **AMI (Amazon Machine Image):** Selecione **Ubuntu Server 22.04 LTS (HVM), SSD Volume Type** (Certifique-se de que tenha a tag *"Free tier eligible"*).
   - **Architecture:** `64-bit (x86)`.
   - **Instance Type:** `t2.micro` (1 vCPU, 1 GiB de memória).
4. **Par de Chaves (Key Pair - Acesso SSH):**
   - Em *Key pair (login)*, clique em **"Create new key pair"**.
   - Nome: `jiujitsu-key`.
   - Tipo de chave: `RSA`.
   - Formato do arquivo: `.pem` (para OpenSSH / Linux / Mac / Windows Terminal).
   - Clique em **Create key pair** e salve o arquivo `jiujitsu-key.pem` no seu computador (guarde com cuidado!).
5. **Configurações de Rede (Security Group - Firewall):**
   - Marque as opções:
     - [x] **Allow SSH traffic from:** Selecione *My IP* (por segurança) ou *Anywhere (0.0.0.0/0)*.
     - [x] **Allow HTTP traffic from the internet** (Porta 80 obrigatória para a aplicação web).
     - [x] **Allow HTTPS traffic from the internet** (Porta 443 opcional para SSL).
6. **Armazenamento:**
   - Deixe o padrão: `1x 8 GiB gp3`.
7. **Lançamento:**
   - Clique no botão **"Launch instance"**.
   - Em instantes, a máquina estará com o status *"Running"*.

---

### Método B: Pela Linha de Comando (AWS CLI)

Se preferir fazer tudo via terminal:
```bash
# 1. Criar o Par de Chaves
aws ec2 create-key-pair \
  --key-name jiujitsu-key \
  --query 'KeyMaterial' \
  --output text > jiujitsu-key.pem
chmod 400 jiujitsu-key.pem

# 2. Criar Security Group
SG_ID=$(aws ec2 create-security-group \
  --group-name jiujitsu-web-sg \
  --description "Security Group para App Web Jiu-Jitsu" \
  --query 'GroupId' \
  --output text)

# 3. Liberar Portas 22 (SSH) e 80 (HTTP)
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0

# 4. Lançar a Instância EC2 (AMI Ubuntu 22.04 na us-east-1)
aws ec2 run-instances \
  --image-id ami-0c7217cdde317cfec \
  --instance-type t2.micro \
  --key-name jiujitsu-key \
  --security-group-ids $SG_ID \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=jiujitsu-cloud-ec2}]'
```

---

## 3. Conexão SSH e Configuração Manual do Servidor

### 3.1 Conectar na Instância
Localize o **Endereço IPv4 Público** da sua instância no console da AWS (exemplo: `54.232.120.45`).

No seu terminal local:
```bash
# Ajustar permissões da chave SSH
chmod 400 jiujitsu-key.pem

# Conectar via SSH
ssh -i "jiujitsu-key.pem" ubuntu@SEU_IP_PUBLICO_AWS
```

---

### 3.2 Atualizar o Sistema e Instalar Pacotes Essenciais
Dentro da máquina virtual EC2, execute:
```bash
# Atualizar repositórios
sudo apt update && sudo apt upgrade -y

# Instalar Python, pip, ambiente virtual, Nginx e Git
sudo apt install -y python3-pip python3-venv git nginx curl
```

---

### 3.3 Clonar o Repositório e Configurar a Aplicação
```bash
# Navegar para o diretório padrão de aplicações web
cd /var/www

# Clonar o repositório do projeto
sudo git clone https://github.com/lucasbombev/jiujitsu-soa.git
sudo chown -R ubuntu:ubuntu /var/www/jiujitsu-soa
cd /var/www/jiujitsu-soa

# Criar e ativar o ambiente virtual Python
python3 -m venv venv
source venv/bin/activate

# Instalar as dependências do projeto
pip install --upgrade pip
pip install fastapi uvicorn pydantic sqlalchemy python-dotenv

# Criar arquivo de configuração de produção .env
cat << 'EOF' > .env
PORT=8000
HOST=127.0.0.1
APP_ENV=production
DATABASE_URL=sqlite:///./jiujitsu.db
ADMIN_USER=admin
ADMIN_PASSWORD=senha_jiujitsu_123
SECRET_KEY=chave-secreta-aws-ec2-producao-2026
CORS_ORIGINS=*
EOF

# Inicializar o banco de dados e aplicar os seeds
python3 -c "import database; database.init_db()"
```

---

## 4. Configurar o Uvicorn como Serviço no `systemd`

Para garantir que a aplicação rode como um daemon em background e reinicie automaticamente caso o servidor reinicie:

```bash
sudo bash -c 'cat << "EOF" > /etc/systemd/system/jiujitsu.service
[Unit]
Description=Jiu-Jitsu Cloud Web Application (FastAPI + Uvicorn)
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/jiujitsu-soa
Environment="PATH=/var/www/jiujitsu-soa/venv/bin"
EnvironmentFile=/var/www/jiujitsu-soa/.env
ExecStart=/var/www/jiujitsu-soa/venv/bin/uvicorn server:app --host 127.0.0.1 --port 8000 --workers 2

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF'
```

Ative e inicie o serviço:
```bash
# Recarregar as configurações do systemd
sudo systemctl daemon-reload

# Habilitar para iniciar no boot da máquina
sudo systemctl enable jiujitsu

# Iniciar o serviço
sudo systemctl start jiujitsu

# Verificar o status (deve exibir "active (running)" em verde)
sudo systemctl status jiujitsu
```

---

## 5. Configurar o Nginx como Reverse Proxy (Porta 80)

O Nginx receberá o tráfego HTTP na porta 80 pública da internet e repassará de forma eficiente para o Uvicorn na porta interna 8000:

```bash
sudo bash -c 'cat << "EOF" > /etc/nginx/sites-available/jiujitsu
server {
    listen 80;
    server_name _;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF'
```

Ativar a configuração e reiniciar o Nginx:
```bash
# Remover o site padrão do Nginx
sudo rm -f /etc/nginx/sites-enabled/default

# Criar link simbólico para a nova configuração
sudo ln -s /etc/nginx/sites-available/jiujitsu /etc/nginx/sites-enabled/

# Testar a sintaxe do Nginx
sudo nginx -t

# Reiniciar o Nginx
sudo systemctl restart nginx
```

---

## 6. Teste de Acesso Público e Validação

1. Abra o navegador web no seu computador.
2. Digite o IP público da sua instância AWS:
   ```
   http://SEU_IP_PUBLICO_AWS
   ```
3. A interface SPA do Jiu-Jitsu Academy deve carregar instantaneamente!
4. Teste o endpoint de Healthcheck:
   ```
   http://SEU_IP_PUBLICO_AWS/health
   ```
5. Acesse a documentação interativa Swagger:
   ```
   http://SEU_IP_PUBLICO_AWS/docs
   ```

---

## 7. Alternativa com Docker na EC2

Caso prefira implantar via Docker na própria EC2:
```bash
# Instalar Docker e Docker Compose na EC2
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
newgrp docker

# Na pasta do projeto:
cd /var/www/jiujitsu-soa
docker-compose up -d --build

# Verificar contêineres ativos
docker ps
```

---

## 8. Integração Opcional com Banco Relacional Gerenciado (AWS RDS)

Se desejar demonstrar ao professor a separação completa da camada de dados usando o **Amazon RDS (PostgreSQL)**:
1. No console AWS, crie uma instância do **RDS**:
   - Engine: PostgreSQL.
   - Template: **Free Tier**.
   - DB instance class: `db.t4g.micro` ou `db.t3.micro`.
   - Master username: `postgres`.
   - Master password: `SuaSenhaSegura123`.
   - Em *Connectivity*, vincule à mesma VPC da sua EC2 e permita tráfego na porta 5432 vindo do Security Group da EC2.
2. Na EC2, edite o arquivo `/var/www/jiujitsu-soa/.env`:
   ```bash
   DATABASE_URL=postgresql://postgres:SuaSenhaSegura123@seu-endpoint-rds.amazonaws.com:5432/jiujitsudb
   ```
3. Reinicie o serviço:
   ```bash
   sudo systemctl restart jiujitsu
   ```
4. Ao acessar `/health`, o status do banco reportará `"engine": "postgresql"`.

---

## 9. Comandos Úteis de Monitoramento e Troubleshooting

```bash
# Ver logs da aplicação em tempo real
sudo journalctl -u jiujitsu -f

# Ver logs de acesso e erros do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Reiniciar a aplicação após alterações de código
sudo systemctl restart jiujitsu

# Atualizar o código a partir do Git
cd /var/www/jiujitsu-soa
git pull origin main
sudo systemctl restart jiujitsu
```

---

## 10. Checklist de Entrega IaaS
- [ ] Instância EC2 provisionada no Free Tier (`t2.micro`).
- [ ] Security Group com portas 22 (SSH) e 80 (HTTP) abertas.
- [ ] Aplicação configurada com `systemd` e `nginx`.
- [ ] Link público HTTP gerado e funcionando na internet (`http://IP_DA_EC2`).
- [ ] Endpoint `/health` retornando `status: healthy`.
- [ ] Prints do console AWS e terminal guardados para o relatório/vídeo.
