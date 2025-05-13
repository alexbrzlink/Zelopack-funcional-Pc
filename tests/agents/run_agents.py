#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import time
import datetime
import logging
from pathlib import Path

# Adicionar diretório pai ao path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Importar o gerenciador de agentes
from tests.ai_agents import AgentsManager

# Configurações de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("zelopack_agents_scheduler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("zelopack_agents_scheduler")

def main():
    # Carregar configuração
    config_file = os.path.join(os.path.dirname(__file__), "scheduler_config.json")
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        if not config.get("enabled", True):
            logger.info("Agendamento desativado. Saindo.")
            return
        
        # Executar agentes
        logger.info("Iniciando execução agendada dos agentes")
        manager = AgentsManager()
        summary = manager.run_all_agents(apply_fixes=config.get("apply_fixes", True))
        
        # Atualizar configuração com a última execução
        config["last_run"] = datetime.datetime.now().isoformat()
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Execução agendada concluída. Próxima execução em {config.get('interval_minutes', 5)} minutos")
    except Exception as e:
        logger.error(f"Erro na execução agendada: {e}")

if __name__ == "__main__":
    main()
