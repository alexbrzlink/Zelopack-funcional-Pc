"""
Utilitários para operações de banco de dados otimizadas.
Funções de alto desempenho para consultas comuns, caching e bulk operations.
"""

import logging
from functools import wraps
from flask import current_app
from sqlalchemy import func, text
from sqlalchemy.orm import joinedload, contains_eager, load_only
from sqlalchemy.exc import SQLAlchemyError
import time
import json

# Configuração de logging
logger = logging.getLogger('zelopack.database')

# Cache simples em memória
_query_cache = {}
_cache_timeout = 300  # 5 minutos em segundos

def clear_cache():
    """Limpa todo o cache de consultas."""
    global _query_cache
    _query_cache = {}
    logger.info("Cache de consultas limpo.")

def cached_query(timeout=None):
    """
    Decorator para cache de consultas.
    
    Args:
        timeout: Tempo de expiração do cache em segundos (None para usar o padrão)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave de cache baseada na função e argumentos
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Verificar se resultado está em cache e dentro da validade
            if cache_key in _query_cache:
                entry = _query_cache[cache_key]
                if time.time() - entry['timestamp'] < (timeout or _cache_timeout):
                    logger.debug(f"Cache hit para {cache_key}")
                    return entry['data']
            
            # Se não estiver em cache ou expirado, executar consulta
            result = func(*args, **kwargs)
            
            # Armazenar resultado no cache
            _query_cache[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }
            
            return result
        return wrapper
    return decorator

def optimize_query(query, model_class, only_fields=None, join_models=None, prefetch_models=None):
    """
    Otimiza uma consulta SQLAlchemy com carregamento seletivo ou eagerly.
    
    Args:
        query: Consulta SQLAlchemy inicial
        model_class: Classe do modelo principal
        only_fields: Lista de campos a carregar (None para todos)
        join_models: Lista de modelos para carregamento via join
        prefetch_models: Lista de modelos para pré-carregamento
        
    Returns:
        Consulta SQLAlchemy otimizada
    """
    # Aplicar carregamento seletivo de campos
    if only_fields:
        query = query.options(load_only(*only_fields))
    
    # Aplicar joins para eager loading
    if join_models:
        for model in join_models:
            query = query.options(contains_eager(getattr(model_class, model)))
    
    # Aplicar prefetch para relacionamentos
    if prefetch_models:
        for model in prefetch_models:
            query = query.options(joinedload(getattr(model_class, model)))
    
    return query

def execute_with_retry(session, operation, max_retries=3, retry_delay=1):
    """
    Executa uma operação de banco de dados com retry automático.
    
    Args:
        session: Sessão SQLAlchemy
        operation: Função contendo a operação a ser executada
        max_retries: Número máximo de tentativas
        retry_delay: Tempo de espera entre tentativas (segundos)
        
    Returns:
        Resultado da operação
    """
    attempt = 0
    last_error = None
    
    while attempt < max_retries:
        try:
            result = operation()
            session.commit()
            return result
        except SQLAlchemyError as e:
            session.rollback()
            last_error = e
            attempt += 1
            logger.warning(f"Tentativa {attempt}/{max_retries} falhou: {str(e)}")
            
            if attempt < max_retries:
                time.sleep(retry_delay)
    
    # Se chegou aqui, todas as tentativas falharam
    logger.error(f"Todas as {max_retries} tentativas falharam. Último erro: {str(last_error)}")
    raise last_error

def bulk_insert(session, objects, batch_size=100):
    """
    Insere uma lista de objetos em lote para maior performance.
    
    Args:
        session: Sessão SQLAlchemy
        objects: Lista de objetos para inserir
        batch_size: Tamanho de cada lote
        
    Returns:
        Número de objetos inseridos
    """
    total = 0
    
    for i in range(0, len(objects), batch_size):
        batch = objects[i:i+batch_size]
        try:
            session.bulk_save_objects(batch)
            session.commit()
            total += len(batch)
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Erro ao inserir lote {i//batch_size}: {str(e)}")
            raise
    
    return total

def get_table_stats(session, table_name):
    """
    Obtém estatísticas de uma tabela do banco de dados.
    
    Args:
        session: Sessão SQLAlchemy
        table_name: Nome da tabela
        
    Returns:
        Dict com estatísticas da tabela
    """
    try:
        # Contar registros
        count_query = text(f"SELECT COUNT(*) FROM {table_name}")
        count = session.execute(count_query).scalar()
        
        # Tamanho da tabela (PostgreSQL)
        size_query = text(f"""
            SELECT pg_size_pretty(pg_total_relation_size('{table_name}')) AS size,
                   pg_size_pretty(pg_relation_size('{table_name}')) AS table_size,
                   pg_size_pretty(pg_total_relation_size('{table_name}') - pg_relation_size('{table_name}')) AS index_size
        """)
        
        # Executar consulta de tamanho se for PostgreSQL
        try:
            size_result = session.execute(size_query).fetchone()
            size_stats = {
                'total_size': size_result.size,
                'table_size': size_result.table_size, 
                'index_size': size_result.index_size
            }
        except Exception:
            # Se falhar (SQLite ou outro), pular estatísticas de tamanho
            size_stats = {'total_size': 'N/A', 'table_size': 'N/A', 'index_size': 'N/A'}
        
        # Combinar resultados
        stats = {
            'table_name': table_name,
            'row_count': count,
            **size_stats
        }
        
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas da tabela {table_name}: {str(e)}")
        return {
            'table_name': table_name,
            'error': str(e)
        }

@cached_query(timeout=3600)  # Cache por 1 hora
def get_database_stats(session):
    """
    Obtém estatísticas gerais do banco de dados.
    
    Args:
        session: Sessão SQLAlchemy
        
    Returns:
        Dict com estatísticas do banco
    """
    # Lista de tabelas principais
    main_tables = ['user', 'reports', 'supplier', 'category']
    
    stats = {
        'tables': {},
        'timestamp': time.time()
    }
    
    for table in main_tables:
        stats['tables'][table] = get_table_stats(session, table)
    
    return stats