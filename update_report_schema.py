#!/usr/bin/env python3
"""
Script para atualizar o esquema do banco de dados Report.
Adiciona os seguintes campos:
1. Campos para análises realizadas em laboratório
2. Validação físico-química
3. Campos adicionais de rastreabilidade
"""

import os
import sys
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from app import app, db

def execute_sql(sql):
    """Executa um comando SQL com tratamento de erro."""
    try:
        print(f"Executando: {sql}")
        db.session.execute(text(sql))
        db.session.commit()
        print("Comando executado com sucesso.")
        return True
    except (OperationalError, ProgrammingError) as e:
        print(f"Erro ao executar comando: {e}")
        db.session.rollback()
        return False

def column_exists(table, column):
    """Verifica se uma coluna existe na tabela."""
    try:
        sql = f"""
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = '{table}' AND column_name = '{column}'
        """
        result = db.session.execute(text(sql)).fetchone()
        return result is not None
    except Exception as e:
        print(f"Erro ao verificar coluna {column}: {e}")
        return False

def main():
    print("Iniciando atualização do esquema do banco de dados...")
    
    # Adicionando campos para análises realizadas em laboratório
    if not column_exists('reports', 'lab_brix'):
        execute_sql("""
        ALTER TABLE reports
        ADD COLUMN lab_brix FLOAT
        """)
    
    if not column_exists('reports', 'lab_ph'):
        execute_sql("""
        ALTER TABLE reports
        ADD COLUMN lab_ph FLOAT
        """)
    
    if not column_exists('reports', 'lab_acidity'):
        execute_sql("""
        ALTER TABLE reports
        ADD COLUMN lab_acidity FLOAT
        """)
    
    # Adicionando campo para validação físico-química
    if not column_exists('reports', 'physicochemical_validation'):
        execute_sql("""
        ALTER TABLE reports
        ADD COLUMN physicochemical_validation VARCHAR(20) DEFAULT 'não verificado'
        """)
    
    # Adicionando campos adicionais de rastreabilidade
    if not column_exists('reports', 'report_archived'):
        execute_sql("""
        ALTER TABLE reports
        ADD COLUMN report_archived BOOLEAN DEFAULT FALSE
        """)
    
    if not column_exists('reports', 'microbiology_collected'):
        execute_sql("""
        ALTER TABLE reports
        ADD COLUMN microbiology_collected BOOLEAN DEFAULT FALSE
        """)
    
    if not column_exists('reports', 'has_report_document'):
        execute_sql("""
        ALTER TABLE reports
        ADD COLUMN has_report_document BOOLEAN DEFAULT FALSE
        """)
    
    print("Atualização do esquema concluída.")

if __name__ == "__main__":
    with app.app_context():
        main()
        print("Script finalizado.")