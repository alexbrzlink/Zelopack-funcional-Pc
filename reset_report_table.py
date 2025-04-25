"""
Script para fazer backup da tabela report e recriar com o esquema correto.
Este é um script temporário para lidar com a migração da tabela report.
"""
import os
import sys
import logging
import json
from datetime import datetime
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def reset_report_table():
    """Faz backup da tabela Report e a recria com o esquema correto."""
    from app import app, db
    import models
    
    with app.app_context():
        try:
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
            
            with engine.connect() as conn:
                # Passo 1: Verificar se a tabela report existe
                try:
                    result = conn.execute(text("SELECT COUNT(*) FROM report"))
                    count = result.scalar()
                    logger.info(f"Tabela report existe com {count} registros.")
                    
                    # Passo 2: Fazer backup dos dados existentes
                    if count > 0:
                        # Criar tabela de backup se não existir
                        try:
                            conn.execute(text("""
                                CREATE TABLE IF NOT EXISTS report_backup (
                                    id SERIAL PRIMARY KEY,
                                    data JSONB,
                                    backup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """))
                            conn.commit()
                            logger.info("Tabela de backup criada ou já existe.")
                            
                            # Obter dados existentes
                            result = conn.execute(text("SELECT * FROM report"))
                            reports = []
                            for row in result:
                                report_dict = {}
                                for column in row._mapping:
                                    # Converter valores para tipos serializáveis
                                    if isinstance(row[column], datetime):
                                        report_dict[column] = row[column].isoformat()
                                    else:
                                        report_dict[column] = row[column]
                                reports.append(report_dict)
                            
                            # Salvar no backup
                            if reports:
                                for report in reports:
                                    conn.execute(
                                        text("INSERT INTO report_backup (data) VALUES (:data)"),
                                        {"data": json.dumps(report)}
                                    )
                                conn.commit()
                                logger.info(f"{len(reports)} relatórios salvos na tabela de backup.")
                        except Exception as e:
                            logger.error(f"Erro ao fazer backup: {e}")
                            conn.rollback()
                            return False
                    
                    # Passo 3: Remover tabela report
                    try:
                        conn.execute(text("DROP TABLE IF EXISTS report CASCADE"))
                        conn.commit()
                        logger.info("Tabela report removida com sucesso.")
                    except Exception as e:
                        logger.error(f"Erro ao remover tabela report: {e}")
                        conn.rollback()
                        return False
                    
                except SQLAlchemyError:
                    logger.info("Tabela report não existe, será criada.")
            
            # Passo 4: Recriar a tabela com o schema correto usando SQLAlchemy
            db.create_all()
            logger.info("Tabela report recriada com sucesso usando db.create_all().")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro geral: {e}")
            return False


if __name__ == "__main__":
    logger.debug("Iniciando reset da tabela report...")
    success = reset_report_table()
    
    if success:
        logger.debug("Reset concluído com sucesso!")
        sys.exit(0)
    else:
        logger.debug("Ocorreram erros durante o reset. Verifique os logs.")
        sys.exit(1)