# Sistema Zelopack - Instruções de Instalação

Este documento contém as instruções necessárias para instalar e executar o sistema Zelopack em seu ambiente local.

## Requisitos de Sistema

- Python 3.9 ou superior
- PostgreSQL 12 ou superior (ou SQLite para desenvolvimento)
- pip (gerenciador de pacotes Python)

## Passos para Instalação

### 1. Preparar o Ambiente

1. Extraia o arquivo ZIP em uma pasta de sua preferência
2. Abra um terminal/prompt de comando e navegue até a pasta do projeto

### 2. Criar um Ambiente Virtual (Recomendado)

```bash
# No Windows
python -m venv venv
venv\Scripts\activate

# No macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r dependencies.txt
```

### 4. Configurar o Banco de Dados

#### Opção 1: Usar SQLite (mais simples, para desenvolvimento)

O sistema está configurado para usar SQLite por padrão. Não é necessária configuração adicional.

#### Opção 2: Usar PostgreSQL (recomendado para produção)

1. Crie um banco de dados PostgreSQL:
   ```sql
   CREATE DATABASE zelopack;
   CREATE USER zelopack_user WITH PASSWORD 'sua_senha';
   GRANT ALL PRIVILEGES ON DATABASE zelopack TO zelopack_user;
   ```

2. Defina a variável de ambiente `DATABASE_URL`:
   ```bash
   # No Windows
   set DATABASE_URL=postgresql://zelopack_user:sua_senha@localhost/zelopack
   
   # No macOS/Linux
   export DATABASE_URL=postgresql://zelopack_user:sua_senha@localhost/zelopack
   ```

### 5. Criar as Tabelas do Banco de Dados

```bash
python create_tables.py
```

### 6. Executar o Sistema

```bash
# Para desenvolvimento
python -m flask run --host=0.0.0.0 --port=5000

# Para produção
gunicorn --bind 0.0.0.0:5000 main:app
```

## Acessando o Sistema

Após a execução, o sistema estará disponível em:
- URL: http://localhost:5000
- Usuário padrão: admin
- Senha padrão: admin123

## Problemas Comuns

### Erro de conexão com o banco de dados PostgreSQL
- Verifique se o serviço PostgreSQL está em execução
- Confirme se as credenciais estão corretas na variável DATABASE_URL
- Verifique se o firewall permite conexões na porta do PostgreSQL

### Erro ao executar com gunicorn
- Verifique se o gunicorn está instalado: `pip install gunicorn`
- No Windows, o gunicorn não é suportado. Use `waitress` em vez disso:
  ```bash
  pip install waitress
  python -c "from waitress import serve; from main import app; serve(app, host='0.0.0.0', port=5000)"
  ```

### Dependências faltando
Se encontrar erros de importação, instale a dependência específica:
```bash
pip install nome_do_pacote
```

## Documentação Adicional

Consulte a pasta `docs` para documentação detalhada sobre o sistema e seus módulos.

## Suporte

Para obter suporte, entre em contato através do email: suporte@zelopack.com.br