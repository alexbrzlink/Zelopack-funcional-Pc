"""
Módulo para gerenciamento de backup e restauração do sistema.
"""
import os
import shutil
import json
import logging
import tempfile
from datetime import datetime
import sqlite3
import zipfile
import psycopg2
import subprocess
from flask import current_app

# Configuração do logger
logger = logging.getLogger(__name__)

class BackupManager:
    """Sistema de gerenciamento de backup e restauração."""
    
    def __init__(self, app=None):
        """Inicializa o gerenciador de backup."""
        self.app = app
        self.backup_dir = self._get_backup_dir()
        
        # Criar diretório de backup se não existir
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir, exist_ok=True)
    
    def _get_backup_dir(self):
        """Retorna o diretório para armazenar backups."""
        if self.app:
            # Obter do app config
            return os.path.join(self.app.instance_path, 'backups')
        else:
            # Fallback para o diretório atual
            return os.path.join(os.getcwd(), 'instance', 'backups')
    
    def create_system_backup(self, include_uploads=True, include_logs=False):
        """
        Cria um backup completo do sistema, incluindo o banco de dados e 
        opcionalmente os arquivos de upload e logs.
        
        Args:
            include_uploads: Se deve incluir arquivos de upload
            include_logs: Se deve incluir arquivos de log
            
        Returns:
            dict: Informações sobre o backup criado
        """
        try:
            # Criar diretório temporário para o backup
            temp_dir = tempfile.mkdtemp()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"zelopack_backup_{timestamp}"
            backup_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
            
            # Informações do backup
            backup_info = {
                'name': backup_name,
                'timestamp': timestamp,
                'created_at': datetime.now().isoformat(),
                'version': self._get_system_version(),
                'includes_uploads': include_uploads,
                'includes_logs': include_logs
            }
            
            # Salvar arquivo de informações
            info_path = os.path.join(temp_dir, 'backup_info.json')
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2)
            
            # Backup do banco de dados
            db_backup_path = os.path.join(temp_dir, 'database')
            os.makedirs(db_backup_path, exist_ok=True)
            
            # Identificar tipo de banco de dados e fazer backup
            db_type, db_uri = self._get_db_info()
            if db_type == 'sqlite':
                self._backup_sqlite_db(db_uri, db_backup_path)
            elif db_type == 'postgresql':
                self._backup_postgres_db(db_uri, db_backup_path)
            else:
                logger.warning(f"Tipo de banco de dados não suportado para backup: {db_type}")
            
            # Backup de configurações
            config_backup_path = os.path.join(temp_dir, 'configs')
            os.makedirs(config_backup_path, exist_ok=True)
            self._backup_configurations(config_backup_path)
            
            # Backup de uploads
            if include_uploads:
                uploads_backup_path = os.path.join(temp_dir, 'uploads')
                os.makedirs(uploads_backup_path, exist_ok=True)
                self._backup_uploads(uploads_backup_path)
            
            # Backup de logs
            if include_logs:
                logs_backup_path = os.path.join(temp_dir, 'logs')
                os.makedirs(logs_backup_path, exist_ok=True)
                self._backup_logs(logs_backup_path)
            
            # Criar arquivo ZIP com todo o conteúdo
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname=rel_path)
            
            # Limpar diretório temporário
            shutil.rmtree(temp_dir)
            
            logger.info(f"Backup completo criado em: {backup_path}")
            
            return {
                'success': True,
                'file_path': backup_path,
                'file_name': os.path.basename(backup_path),
                'size': os.path.getsize(backup_path),
                'created_at': datetime.now().isoformat(),
                'info': backup_info
            }
        
        except Exception as e:
            logger.error(f"Erro ao criar backup: {str(e)}")
            # Limpar diretório temporário em caso de erro
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def restore_system_from_backup(self, backup_file_path, restore_uploads=True, restore_logs=False):
        """
        Restaura o sistema a partir de um arquivo de backup.
        
        Args:
            backup_file_path: Caminho para o arquivo de backup
            restore_uploads: Se deve restaurar arquivos de upload
            restore_logs: Se deve restaurar arquivos de log
            
        Returns:
            dict: Informações sobre a restauração
        """
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(backup_file_path):
                return {'success': False, 'error': 'Arquivo de backup não encontrado.'}
            
            # Criar diretório temporário para extração
            temp_dir = tempfile.mkdtemp()
            
            # Extrair arquivo ZIP
            with zipfile.ZipFile(backup_file_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Verificar informações do backup
            info_path = os.path.join(temp_dir, 'backup_info.json')
            if not os.path.exists(info_path):
                shutil.rmtree(temp_dir)
                return {'success': False, 'error': 'Arquivo de backup inválido (informações não encontradas).'}
            
            with open(info_path, 'r', encoding='utf-8') as f:
                backup_info = json.load(f)
            
            # Verificar compatibilidade de versão
            current_version = self._get_system_version()
            backup_version = backup_info.get('version', '0.0.0')
            
            logger.info(f"Restaurando backup versão {backup_version} para sistema versão {current_version}")
            
            # Restaurar banco de dados
            db_backup_path = os.path.join(temp_dir, 'database')
            if os.path.exists(db_backup_path):
                db_type, db_uri = self._get_db_info()
                if db_type == 'sqlite':
                    self._restore_sqlite_db(db_uri, db_backup_path)
                elif db_type == 'postgresql':
                    self._restore_postgres_db(db_uri, db_backup_path)
                else:
                    logger.warning(f"Tipo de banco de dados não suportado para restauração: {db_type}")
            else:
                logger.warning("Backup do banco de dados não encontrado.")
            
            # Restaurar configurações
            config_backup_path = os.path.join(temp_dir, 'configs')
            if os.path.exists(config_backup_path):
                self._restore_configurations(config_backup_path)
            else:
                logger.warning("Backup de configurações não encontrado.")
            
            # Restaurar uploads
            if restore_uploads and backup_info.get('includes_uploads', False):
                uploads_backup_path = os.path.join(temp_dir, 'uploads')
                if os.path.exists(uploads_backup_path):
                    self._restore_uploads(uploads_backup_path)
                else:
                    logger.warning("Backup de uploads não encontrado.")
            
            # Restaurar logs
            if restore_logs and backup_info.get('includes_logs', False):
                logs_backup_path = os.path.join(temp_dir, 'logs')
                if os.path.exists(logs_backup_path):
                    self._restore_logs(logs_backup_path)
                else:
                    logger.warning("Backup de logs não encontrado.")
            
            # Limpar diretório temporário
            shutil.rmtree(temp_dir)
            
            logger.info(f"Sistema restaurado com sucesso a partir do backup: {backup_file_path}")
            
            return {
                'success': True,
                'backup_info': backup_info,
                'restored_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {str(e)}")
            # Limpar diretório temporário em caso de erro
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_backups(self):
        """
        Retorna a lista de backups disponíveis.
        
        Returns:
            list: Lista de backups disponíveis
        """
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        # Listar todos os arquivos ZIP no diretório de backup
        for file_name in os.listdir(self.backup_dir):
            if not file_name.endswith('.zip'):
                continue
            
            file_path = os.path.join(self.backup_dir, file_name)
            
            try:
                # Extrair informações do backup
                with zipfile.ZipFile(file_path, 'r') as zipf:
                    if 'backup_info.json' in zipf.namelist():
                        with zipf.open('backup_info.json') as f:
                            backup_info = json.load(f)
                            
                            backups.append({
                                'file_name': file_name,
                                'file_path': file_path,
                                'size': os.path.getsize(file_path),
                                'info': backup_info
                            })
                    else:
                        # Backup sem informações, adicionar informações básicas
                        stat = os.stat(file_path)
                        created_at = datetime.fromtimestamp(stat.st_ctime)
                        
                        backups.append({
                            'file_name': file_name,
                            'file_path': file_path,
                            'size': stat.st_size,
                            'info': {
                                'name': file_name.replace('.zip', ''),
                                'timestamp': created_at.strftime('%Y%m%d_%H%M%S'),
                                'created_at': created_at.isoformat()
                            }
                        })
            except Exception as e:
                logger.error(f"Erro ao ler backup {file_name}: {str(e)}")
        
        # Ordenar por data de criação (mais recente primeiro)
        backups.sort(key=lambda x: x['info'].get('created_at', ''), reverse=True)
        
        return backups
    
    def delete_backup(self, backup_file_name):
        """
        Exclui um backup específico.
        
        Args:
            backup_file_name: Nome do arquivo de backup
            
        Returns:
            bool: True se o backup foi excluído com sucesso
        """
        try:
            backup_path = os.path.join(self.backup_dir, backup_file_name)
            
            if not os.path.exists(backup_path):
                logger.warning(f"Backup não encontrado: {backup_file_name}")
                return False
            
            os.remove(backup_path)
            logger.info(f"Backup excluído: {backup_file_name}")
            
            return True
        
        except Exception as e:
            logger.error(f"Erro ao excluir backup: {str(e)}")
            return False
    
    def _get_system_version(self):
        """Retorna a versão atual do sistema."""
        # Tentar obter de configurações do app
        if self.app:
            return self.app.config.get('VERSION', '1.0.0')
        
        # Tentar obter de arquivo de configuração ou variável de ambiente
        # Fallback para versão padrão
        return os.environ.get('SYSTEM_VERSION', '1.0.0')
    
    def _get_db_info(self):
        """Retorna informações sobre o banco de dados."""
        if self.app:
            db_uri = self.app.config.get('SQLALCHEMY_DATABASE_URI', '')
        else:
            db_uri = os.environ.get('DATABASE_URL', '')
        
        # Identificar tipo de banco
        if 'sqlite' in db_uri:
            return 'sqlite', db_uri
        elif 'postgresql' in db_uri or 'postgres' in db_uri:
            return 'postgresql', db_uri
        else:
            return 'unknown', db_uri
    
    def _backup_sqlite_db(self, db_uri, backup_path):
        """Faz backup de um banco de dados SQLite."""
        # Extrair caminho do arquivo do URI
        db_file = db_uri.replace('sqlite:///', '')
        db_file = os.path.abspath(db_file)
        
        if not os.path.exists(db_file):
            logger.warning(f"Arquivo de banco de dados SQLite não encontrado: {db_file}")
            return
        
        # Caminho para o arquivo de backup
        backup_file = os.path.join(backup_path, 'zelopack_db.sqlite')
        
        # Fazer backup - para SQLite, basta copiar o arquivo
        shutil.copy2(db_file, backup_file)
        logger.info(f"Backup do banco de dados SQLite concluído: {backup_file}")
    
    def _backup_postgres_db(self, db_uri, backup_path):
        """Faz backup de um banco de dados PostgreSQL."""
        try:
            # Extrair credenciais do URI
            # URI formato: postgresql://user:password@host:port/dbname
            from urllib.parse import urlparse
            
            parsed_uri = urlparse(db_uri)
            dbname = parsed_uri.path.lstrip('/')
            user = parsed_uri.username
            password = parsed_uri.password
            host = parsed_uri.hostname
            port = parsed_uri.port or 5432
            
            # Caminho para o arquivo de backup
            backup_file = os.path.join(backup_path, 'zelopack_db.sql')
            
            # Ambiente para pg_dump
            env = os.environ.copy()
            if password:
                env['PGPASSWORD'] = password
            
            # Comando pg_dump
            cmd = [
                'pg_dump',
                '-h', host,
                '-p', str(port),
                '-U', user,
                '-F', 'c',  # Formato custom
                '-b',       # Incluir blobs
                '-v',       # Modo verbose
                '-f', backup_file,
                dbname
            ]
            
            logger.info(f"Executando backup do PostgreSQL: {' '.join(cmd)}")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Erro ao fazer backup do PostgreSQL: {result.stderr}")
                
                # Tentar abordagem alternativa com conexão direta
                self._backup_postgres_db_direct(db_uri, backup_path)
            else:
                logger.info(f"Backup do banco de dados PostgreSQL concluído: {backup_file}")
        
        except Exception as e:
            logger.error(f"Erro ao fazer backup do PostgreSQL: {str(e)}")
            # Tentar abordagem alternativa
            self._backup_postgres_db_direct(db_uri, backup_path)
    
    def _backup_postgres_db_direct(self, db_uri, backup_path):
        """Faz backup direto com psycopg2 extraindo dados em formato SQL."""
        try:
            # Conectar ao banco
            conn = psycopg2.connect(db_uri)
            cursor = conn.cursor()
            
            # Caminho para o arquivo de backup
            backup_file = os.path.join(backup_path, 'zelopack_db_tables.sql')
            
            # Obter lista de tabelas
            cursor.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'")
            tables = cursor.fetchall()
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                # Cabeçalho
                f.write("-- Zelopack Database Backup\n")
                f.write(f"-- Generated: {datetime.now().isoformat()}\n\n")
                
                # Para cada tabela
                for table, in tables:
                    f.write(f"\n-- Table: {table}\n")
                    
                    # Estrutura da tabela
                    cursor.execute(f"SELECT pg_catalog.pg_get_tabledef('{table}'::regclass::oid)")
                    create_stmt = cursor.fetchone()[0]
                    f.write(f"{create_stmt};\n\n")
                    
                    # Dados da tabela
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    
                    if rows:
                        # Nomes das colunas
                        colnames = [desc[0] for desc in cursor.description]
                        
                        for row in rows:
                            values = []
                            for val in row:
                                if val is None:
                                    values.append("NULL")
                                elif isinstance(val, (int, float)):
                                    values.append(str(val))
                                else:
                                    # Escapar strings
                                    values.append(f"'{str(val).replace(''', ''''''')}'")
                            
                            f.write(f"INSERT INTO {table} ({', '.join(colnames)}) VALUES ({', '.join(values)});\n")
            
            cursor.close()
            conn.close()
            
            logger.info(f"Backup direto do banco de dados PostgreSQL concluído: {backup_file}")
        
        except Exception as e:
            logger.error(f"Erro ao fazer backup direto do PostgreSQL: {str(e)}")
            
            # Criar arquivo de erro
            error_file = os.path.join(backup_path, 'db_backup_error.txt')
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"Erro ao fazer backup do banco de dados: {str(e)}\n")
                f.write(f"URI: {db_uri}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
    
    def _restore_sqlite_db(self, db_uri, backup_path):
        """Restaura um banco de dados SQLite."""
        # Extrair caminho do arquivo do URI
        db_file = db_uri.replace('sqlite:///', '')
        db_file = os.path.abspath(db_file)
        
        # Caminho para o arquivo de backup
        backup_file = os.path.join(backup_path, 'zelopack_db.sqlite')
        
        if not os.path.exists(backup_file):
            logger.warning(f"Arquivo de backup SQLite não encontrado: {backup_file}")
            return
        
        # Fazer backup do banco atual antes de sobrescrever
        current_backup = f"{db_file}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if os.path.exists(db_file):
            shutil.copy2(db_file, current_backup)
            logger.info(f"Backup do banco atual criado: {current_backup}")
        
        # Restaurar - para SQLite, basta copiar o arquivo
        shutil.copy2(backup_file, db_file)
        logger.info(f"Banco de dados SQLite restaurado: {db_file}")
    
    def _restore_postgres_db(self, db_uri, backup_path):
        """Restaura um banco de dados PostgreSQL."""
        try:
            # Extrair credenciais do URI
            from urllib.parse import urlparse
            
            parsed_uri = urlparse(db_uri)
            dbname = parsed_uri.path.lstrip('/')
            user = parsed_uri.username
            password = parsed_uri.password
            host = parsed_uri.hostname
            port = parsed_uri.port or 5432
            
            # Caminho para o arquivo de backup
            backup_file = os.path.join(backup_path, 'zelopack_db.sql')
            
            if not os.path.exists(backup_file):
                backup_file = os.path.join(backup_path, 'zelopack_db_tables.sql')
                if not os.path.exists(backup_file):
                    logger.warning(f"Arquivo de backup PostgreSQL não encontrado: {backup_path}")
                    return
            
            # Ambiente para pg_restore
            env = os.environ.copy()
            if password:
                env['PGPASSWORD'] = password
            
            # Conexão para desconectar outros usuários
            conn_string = f"host={host} port={port} dbname={dbname} user={user} password={password}"
            conn = psycopg2.connect(conn_string)
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Desconectar outros usuários
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{dbname}'
                AND pid <> pg_backend_pid()
            """)
            
            # Comando pg_restore para restaurar
            if backup_file.endswith('.sql'):
                # Arquivo SQL - usar psql
                cmd = [
                    'psql',
                    '-h', host,
                    '-p', str(port),
                    '-U', user,
                    '-d', dbname,
                    '-f', backup_file
                ]
            else:
                # Arquivo formato custom - usar pg_restore
                cmd = [
                    'pg_restore',
                    '-h', host,
                    '-p', str(port),
                    '-U', user,
                    '-d', dbname,
                    '-c',       # Limpar objetos antes de recriar
                    '-v',       # Modo verbose
                    backup_file
                ]
            
            logger.info(f"Executando restauração do PostgreSQL: {' '.join(cmd)}")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Erro ao restaurar o PostgreSQL: {result.stderr}")
                
                # Se estiver usando arquivo SQL, tentar executar com psycopg2
                if backup_file.endswith('.sql'):
                    self._restore_postgres_db_direct(db_uri, backup_file)
            else:
                logger.info(f"Banco de dados PostgreSQL restaurado com sucesso")
        
        except Exception as e:
            logger.error(f"Erro ao restaurar o PostgreSQL: {str(e)}")
            
            # Tentar abordagem alternativa
            if backup_file.endswith('.sql'):
                self._restore_postgres_db_direct(db_uri, backup_file)
    
    def _restore_postgres_db_direct(self, db_uri, backup_file):
        """Restaura um banco de dados PostgreSQL diretamente com psycopg2."""
        try:
            # Conectar ao banco
            conn = psycopg2.connect(db_uri)
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Ler arquivo SQL
            with open(backup_file, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # Executar comandos SQL
            cursor.execute(sql_script)
            
            cursor.close()
            conn.close()
            
            logger.info(f"Banco de dados PostgreSQL restaurado diretamente com sucesso")
        
        except Exception as e:
            logger.error(f"Erro ao restaurar diretamente o PostgreSQL: {str(e)}")
    
    def _backup_configurations(self, backup_path):
        """Faz backup das configurações do sistema."""
        if not self.app:
            logger.warning("App não disponível para backup de configurações")
            return
        
        try:
            # Criar arquivo de configurações
            config_file = os.path.join(backup_path, 'system_configs.json')
            
            # Obter configurações do banco de dados
            with self.app.app_context():
                from models import SystemConfig
                
                configs = SystemConfig.query.all()
                config_data = {config.key: config.value for config in configs}
            
            # Salvar configurações
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Backup de configurações concluído: {config_file}")
        
        except Exception as e:
            logger.error(f"Erro ao fazer backup de configurações: {str(e)}")
    
    def _restore_configurations(self, backup_path):
        """Restaura as configurações do sistema."""
        if not self.app:
            logger.warning("App não disponível para restauração de configurações")
            return
        
        try:
            # Caminho do arquivo de configurações
            config_file = os.path.join(backup_path, 'system_configs.json')
            
            if not os.path.exists(config_file):
                logger.warning(f"Arquivo de configurações não encontrado: {config_file}")
                return
            
            # Carregar configurações
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Restaurar configurações
            with self.app.app_context():
                from models import SystemConfig, db
                
                for key, value in config_data.items():
                    # Verificar se a configuração já existe
                    config = SystemConfig.query.filter_by(key=key).first()
                    
                    if config:
                        config.value = value
                    else:
                        # Criar nova configuração
                        config = SystemConfig(key=key, value=value)
                        db.session.add(config)
                
                db.session.commit()
            
            logger.info(f"Configurações restauradas com sucesso")
        
        except Exception as e:
            logger.error(f"Erro ao restaurar configurações: {str(e)}")
    
    def _backup_uploads(self, backup_path):
        """Faz backup dos arquivos de upload."""
        try:
            # Identificar diretório de uploads
            if self.app:
                upload_dir = self.app.config.get('UPLOAD_FOLDER')
            else:
                upload_dir = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.getcwd(), 'uploads')
            
            if not os.path.exists(upload_dir):
                logger.warning(f"Diretório de uploads não encontrado: {upload_dir}")
                return
            
            # Copiar arquivos
            for item in os.listdir(upload_dir):
                item_path = os.path.join(upload_dir, item)
                
                if os.path.isfile(item_path):
                    # Copiar arquivo
                    shutil.copy2(item_path, os.path.join(backup_path, item))
                elif os.path.isdir(item_path):
                    # Copiar diretório
                    shutil.copytree(
                        item_path, 
                        os.path.join(backup_path, item),
                        dirs_exist_ok=True
                    )
            
            logger.info(f"Backup de uploads concluído")
        
        except Exception as e:
            logger.error(f"Erro ao fazer backup de uploads: {str(e)}")
    
    def _restore_uploads(self, backup_path):
        """Restaura os arquivos de upload."""
        try:
            # Identificar diretório de uploads
            if self.app:
                upload_dir = self.app.config.get('UPLOAD_FOLDER')
            else:
                upload_dir = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.getcwd(), 'uploads')
            
            # Criar diretório se não existir
            os.makedirs(upload_dir, exist_ok=True)
            
            # Copiar arquivos
            for item in os.listdir(backup_path):
                item_path = os.path.join(backup_path, item)
                
                if os.path.isfile(item_path):
                    # Copiar arquivo
                    shutil.copy2(item_path, os.path.join(upload_dir, item))
                elif os.path.isdir(item_path):
                    # Copiar diretório
                    shutil.copytree(
                        item_path, 
                        os.path.join(upload_dir, item),
                        dirs_exist_ok=True
                    )
            
            logger.info(f"Uploads restaurados com sucesso")
        
        except Exception as e:
            logger.error(f"Erro ao restaurar uploads: {str(e)}")
    
    def _backup_logs(self, backup_path):
        """Faz backup dos arquivos de log."""
        try:
            # Identificar diretório de logs
            if self.app:
                log_dir = self.app.config.get('LOG_FOLDER')
            else:
                log_dir = os.environ.get('LOG_FOLDER') or os.path.join(os.getcwd(), 'logs')
            
            if not os.path.exists(log_dir):
                logger.warning(f"Diretório de logs não encontrado: {log_dir}")
                return
            
            # Copiar arquivos
            for item in os.listdir(log_dir):
                if not item.endswith('.log'):
                    continue
                    
                item_path = os.path.join(log_dir, item)
                
                if os.path.isfile(item_path):
                    # Copiar arquivo
                    shutil.copy2(item_path, os.path.join(backup_path, item))
            
            logger.info(f"Backup de logs concluído")
        
        except Exception as e:
            logger.error(f"Erro ao fazer backup de logs: {str(e)}")
    
    def _restore_logs(self, backup_path):
        """Restaura os arquivos de log."""
        try:
            # Identificar diretório de logs
            if self.app:
                log_dir = self.app.config.get('LOG_FOLDER')
            else:
                log_dir = os.environ.get('LOG_FOLDER') or os.path.join(os.getcwd(), 'logs')
            
            # Criar diretório se não existir
            os.makedirs(log_dir, exist_ok=True)
            
            # Copiar arquivos
            for item in os.listdir(backup_path):
                if not item.endswith('.log'):
                    continue
                    
                item_path = os.path.join(backup_path, item)
                
                if os.path.isfile(item_path):
                    # Copiar arquivo
                    shutil.copy2(item_path, os.path.join(log_dir, item))
            
            logger.info(f"Logs restaurados com sucesso")
        
        except Exception as e:
            logger.error(f"Erro ao restaurar logs: {str(e)}")