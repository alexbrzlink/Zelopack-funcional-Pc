import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python3
"""
ZELOPACK - Sistema de Gerenciamento de Laudos
Aplicativo Principal Executável

Este arquivo serve como ponto de entrada para o aplicativo empacotado
e executa o servidor Flask em modo standalone para ambientes desktop.
"""

import os
import sys
import signal
import webbrowser
import threading
import time
import socket
from contextlib import closing

# Adicionar o diretório atual ao PATH para garantir importações corretas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar variáveis de ambiente necessárias
os.environ['FLASK_ENV'] = 'development'  # Usar modo de desenvolvimento para facilitar autenticação 
os.environ['FLASK_DEBUG'] = '1'
os.environ['WTF_CSRF_ENABLED'] = 'False'  # Desabilitar CSRF para o aplicativo desktop

# Importar a aplicação
from app import app
# Importar o arquivo main para inicializar rotas
try:
    import main  # noqa
except ImportError:
    logger.debug("Aviso: Não foi possível importar o módulo 'main'.")

# Definir o caminho base para os recursos (importante para PyInstaller)
if getattr(sys, 'frozen', False):
    # Se estiver executando como executável congelado (PyInstaller)
    # PyInstaller cria uma variável temporária e a armazena em _MEIPASS
    try:
        base_dir = sys._MEIPASS
    except AttributeError:
        base_dir = os.path.dirname(sys.executable)
else:
    # Se estiver executando em modo de desenvolvimento
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Configurar caminhos para os recursos
app.static_folder = os.path.join(base_dir, 'static')
app.template_folder = os.path.join(base_dir, 'templates')

# Encontrar porta disponível
def find_free_port():
    """Encontrar uma porta disponível no sistema."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

# Abrir o navegador com atraso para garantir que o servidor esteja funcionando
def open_browser(port):
    """Abrir o navegador apontando para a aplicação."""
    time.sleep(1.5)  # Aguardar o servidor iniciar
    
    # Usar a rota de login direto para facilitar o acesso
    url = f"http://localhost:{port}/login-direct"
    logger.debug(f"Abrindo navegador em: {url}")
    webbrowser.open(url)

# Função para encerrar a aplicação com Ctrl+C
def signal_handler(sig, frame):
    """Manipular sinais de interrupção para desligamento limpo."""
    logger.debug('\nEncerrando aplicação ZELOPACK...')
    sys.exit(0)

def main():
    """Função principal que inicia o servidor Flask."""
    # Registrar manipulador de sinal para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Encontrar porta disponível
    port = find_free_port()
    
    # Informar ao usuário
    logger.debug("=" * 60)
    logger.debug("ZELOPACK - Sistema de Gerenciamento de Laudos")
    logger.debug("=" * 60)
    logger.debug(f"Iniciando servidor em http://localhost:{port}")
    logger.debug("Pressione Ctrl+C para encerrar a aplicação")
    logger.debug("=" * 60)
    
    # Iniciar navegador em uma thread separada
    browser_thread = threading.Thread(target=open_browser, args=(port,))
    browser_thread.daemon = True
    browser_thread.start()
    
    # Iniciar a aplicação
    app.run(host='localhost', port=port, debug=False, threaded=True)

if __name__ == '__main__':
    main()