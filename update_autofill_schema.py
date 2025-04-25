"""
Script para atualizar o esquema da tabela form_presets.
Adiciona o campo fields_json para compatibilidade com a API de autofill.
"""

import logging
import os
import sys
from app import app, db
from models import FormPreset

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def adicionar_coluna_fields_json():
    """Adiciona a coluna fields_json à tabela form_presets"""
    try:
        with app.app_context():
            # Verificar se a coluna já existe
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            colunas = [coluna['name'] for coluna in inspector.get_columns('form_presets')]
            
            if 'fields_json' not in colunas:
                logger.info("Adicionando coluna 'fields_json' à tabela 'form_presets'...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE form_presets ADD COLUMN fields_json TEXT'))
                    conn.commit()
                logger.info("Coluna 'fields_json' adicionada com sucesso!")
                
                # Atualizar dados existentes - copiando de 'data' para 'fields_json'
                logger.info("Atualizando dados existentes...")
                presets = FormPreset.query.all()
                for preset in presets:
                    if preset.data and not preset.fields_json:
                        preset.fields_json = preset.data
                db.session.commit()
                logger.info(f"Dados atualizados para {len(presets)} registros.")
            else:
                logger.info("A coluna 'fields_json' já existe. Nenhuma alteração necessária.")
                
            return True
    except Exception as e:
        logger.error(f"Erro ao adicionar coluna 'fields_json': {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando atualização do esquema da tabela form_presets...")
    resultado = adicionar_coluna_fields_json()
    
    if resultado:
        logger.info("Atualização concluída com sucesso!")
        sys.exit(0)
    else:
        logger.error("Falha na atualização do esquema. Verifique os logs para mais informações.")
        sys.exit(1)