#!/usr/bin/env python3
"""
Script de teste completo para o sistema Zelopack
Simula testes manuais em um ambiente de máquina virtual
"""
import os
import sys
import time
import logging
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Configuração de logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('zelopack_tester')

# Configuração do ambiente de teste
BASE_URL = 'http://localhost:5000'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
HEADERS = {'User-Agent': USER_AGENT}
SESSION = requests.Session()

def log_separator():
    logger.info("=" * 80)

def extract_csrf_token(html_content):
    """Extrai o token CSRF da página"""
    soup = BeautifulSoup(html_content, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        return csrf_input.get('value')
    return None

def test_login():
    """Testa o sistema de login"""
    log_separator()
    logger.info("TESTE 1: SISTEMA DE LOGIN")
    
    # 1.1 Acessar página de login
    login_url = urljoin(BASE_URL, '/auth/login')
    try:
        response = SESSION.get(login_url, headers=HEADERS)
        logger.info(f"1.1 Acesso à página de login: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Falha ao acessar página de login: {response.status_code}")
            return False
        
        # Extrair token CSRF
        csrf_token = extract_csrf_token(response.text)
        if not csrf_token:
            logger.error("Token CSRF não encontrado na página de login")
            return False
        
        logger.info("Token CSRF extraído com sucesso")
        
        # 1.2 Efetuar login com credenciais padrão
        login_data = {
            'username': 'admin',
            'password': 'Alex',
            'csrf_token': csrf_token
        }
        
        response = SESSION.post(login_url, data=login_data, headers=HEADERS, allow_redirects=True)
        logger.info(f"1.2 Login com credenciais admin/Alex: {response.status_code}")
        
        # Verificar se login foi bem-sucedido (redirecionamento para dashboard)
        if 'dashboard' in response.url:
            logger.info("✓ Login bem-sucedido, redirecionado para dashboard")
            return True
        else:
            logger.error(f"❌ Login falhou, URL após login: {response.url}")
            return False
    
    except Exception as e:
        logger.error(f"Erro durante teste de login: {str(e)}")
        return False

def test_navigation():
    """Testa a navegação básica pelo sistema"""
    log_separator()
    logger.info("TESTE 2: NAVEGAÇÃO PELO SISTEMA")
    
    routes_to_test = [
        '/dashboard',
        '/forms',
        '/reports',
        '/editor'
    ]
    
    success = True
    for route in routes_to_test:
        url = urljoin(BASE_URL, route)
        try:
            response = SESSION.get(url, headers=HEADERS)
            if response.status_code == 200:
                logger.info(f"✓ Acesso à rota {route}: OK")
            else:
                logger.error(f"❌ Acesso à rota {route} falhou: {response.status_code}")
                success = False
        except Exception as e:
            logger.error(f"Erro ao acessar rota {route}: {str(e)}")
            success = False
    
    return success

def test_forms_listing():
    """Testa a listagem de formulários"""
    log_separator()
    logger.info("TESTE 3: LISTAGEM DE FORMULÁRIOS")
    
    url = urljoin(BASE_URL, '/forms')
    try:
        response = SESSION.get(url, headers=HEADERS)
        if response.status_code != 200:
            logger.error(f"❌ Acesso à página de formulários falhou: {response.status_code}")
            return False
        
        # Verificar se a página contém categorias de formulários
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.select('.category-card')
        
        if not categories:
            logger.error("❌ Nenhuma categoria de formulário encontrada")
            return False
        
        logger.info(f"✓ Encontradas {len(categories)} categorias de formulários")
        
        # Testar acesso à primeira categoria
        first_category_link = categories[0].find('a')
        if not first_category_link:
            logger.error("❌ Link para categoria não encontrado")
            return False
        
        category_url = urljoin(BASE_URL, first_category_link['href'])
        category_name = first_category_link.text.strip()
        
        logger.info(f"Testando acesso à categoria: {category_name}")
        response = SESSION.get(category_url, headers=HEADERS)
        
        if response.status_code != 200:
            logger.error(f"❌ Acesso à categoria {category_name} falhou: {response.status_code}")
            return False
        
        logger.info(f"✓ Acesso à categoria {category_name}: OK")
        
        # Verificar se há formulários listados
        soup = BeautifulSoup(response.text, 'html.parser')
        forms = soup.select('.form-card')
        
        if not forms:
            logger.warning(f"⚠️ Nenhum formulário encontrado na categoria {category_name}")
        else:
            logger.info(f"✓ Encontrados {len(forms)} formulários na categoria {category_name}")
        
        return True
    
    except Exception as e:
        logger.error(f"Erro durante teste de listagem de formulários: {str(e)}")
        return False

def test_editor():
    """Testa o editor universal"""
    log_separator()
    logger.info("TESTE 4: EDITOR UNIVERSAL")
    
    editor_url = urljoin(BASE_URL, '/editor')
    try:
        # 4.1 Acessar página principal do editor
        response = SESSION.get(editor_url, headers=HEADERS)
        logger.info(f"4.1 Acesso à página do editor: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"❌ Acesso ao editor falhou: {response.status_code}")
            return False
        
        # 4.2 Verificar se existem categorias no editor
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.select('.category-card')
        
        if not categories:
            logger.error("❌ Nenhuma categoria encontrada no editor")
            return False
        
        logger.info(f"✓ Encontradas {len(categories)} categorias no editor")
        
        # 4.3 Testar acesso à primeira categoria
        first_category_link = categories[0].find('a')
        if not first_category_link:
            logger.error("❌ Link para categoria do editor não encontrado")
            return False
        
        category_url = urljoin(BASE_URL, first_category_link['href'])
        category_name = first_category_link.text.strip()
        
        logger.info(f"Testando acesso à categoria do editor: {category_name}")
        response = SESSION.get(category_url, headers=HEADERS)
        
        if response.status_code != 200:
            logger.error(f"❌ Acesso à categoria {category_name} do editor falhou: {response.status_code}")
            return False
        
        # 4.4 Verificar se há formulários para editar
        soup = BeautifulSoup(response.text, 'html.parser')
        forms = soup.select('.form-card')
        
        if not forms:
            logger.warning(f"⚠️ Nenhum formulário para editar encontrado na categoria {category_name}")
            return True
        
        logger.info(f"✓ Encontrados {len(forms)} formulários para editar na categoria {category_name}")
        
        # 4.5 Testar acesso ao primeiro formulário
        first_form_link = forms[0].find('a')
        if not first_form_link:
            logger.error("❌ Link para formulário do editor não encontrado")
            return False
        
        form_url = urljoin(BASE_URL, first_form_link['href'])
        form_name = first_form_link.text.strip()
        
        logger.info(f"Testando acesso ao formulário no editor: {form_name}")
        response = SESSION.get(form_url, headers=HEADERS)
        
        if response.status_code != 200:
            # Verifique se há um erro específico no response
            logger.error(f"❌ Acesso ao formulário {form_name} no editor falhou: {response.status_code}")
            if response.status_code == 500:
                logger.error("❌ Erro interno do servidor ao acessar o formulário no editor")
                # Verificar logs para mais detalhes sobre o erro
            return False
        
        logger.info(f"✓ Acesso ao formulário {form_name} no editor: OK")
        return True
    
    except Exception as e:
        logger.error(f"Erro durante teste do editor universal: {str(e)}")
        return False

def test_predefined_fields():
    """Testa funcionalidade de campos predefinidos"""
    log_separator()
    logger.info("TESTE 5: CAMPOS PREDEFINIDOS")
    
    fields_url = urljoin(BASE_URL, '/forms/standard-fields')
    try:
        response = SESSION.get(fields_url, headers=HEADERS)
        logger.info(f"5.1 Acesso à página de campos padronizados: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"❌ Acesso aos campos padronizados falhou: {response.status_code}")
            return False
        
        # Verificar se existem campos padronizados listados
        soup = BeautifulSoup(response.text, 'html.parser')
        fields_cards = soup.select('.standard-fields-card')
        
        if not fields_cards:
            logger.warning("⚠️ Nenhum conjunto de campos padronizados encontrado")
            
            # Criar um novo conjunto de campos padronizados
            logger.info("Tentando criar um novo conjunto de campos padronizados")
            
            # Obter o token CSRF
            csrf_token = extract_csrf_token(response.text)
            if not csrf_token:
                logger.error("❌ Token CSRF não encontrado na página de campos padronizados")
                return False
            
            # Dados para criação do novo conjunto
            new_fields_data = {
                'name': 'Teste Automatizado',
                'description': 'Conjunto de campos criado pelo teste automatizado',
                'empresa': 'Zelopack Teste',
                'produto': 'Produto de Teste',
                'marca': 'Marca de Teste',
                'lote': 'LOT123456',
                'csrf_token': csrf_token
            }
            
            create_url = urljoin(BASE_URL, '/forms/standard-fields/create')
            response = SESSION.post(create_url, data=new_fields_data, headers=HEADERS, allow_redirects=True)
            
            if '/forms/campos-padronizados' in response.url and response.status_code == 200:
                logger.info("✓ Conjunto de campos padronizados criado com sucesso")
            else:
                logger.error(f"❌ Falha ao criar conjunto de campos padronizados: {response.status_code}")
                return False
        else:
            logger.info(f"✓ Encontrados {len(fields_cards)} conjuntos de campos padronizados")
        
        return True
    
    except Exception as e:
        logger.error(f"Erro durante teste de campos predefinidos: {str(e)}")
        return False

def test_api_endpoints():
    """Testa endpoints da API interna"""
    log_separator()
    logger.info("TESTE 6: ENDPOINTS DA API")
    
    # Lista de endpoints da API para testar
    api_endpoints = [
        '/editor/api/get-presets',
        '/editor/api/get-standard-fields'
    ]
    
    success = True
    for endpoint in api_endpoints:
        url = urljoin(BASE_URL, endpoint)
        try:
            response = SESSION.get(url, headers=HEADERS)
            
            # Alguns endpoints podem exigir parâmetros adicionais
            if response.status_code == 404:
                logger.warning(f"⚠️ Endpoint {endpoint} não encontrado ou requer parâmetros adicionais")
            elif response.status_code == 200:
                logger.info(f"✓ Acesso ao endpoint {endpoint}: OK")
                # Verificar se resposta é JSON válido
                try:
                    json_data = response.json()
                    logger.info(f"✓ Resposta JSON válida recebida de {endpoint}")
                except:
                    logger.error(f"❌ Resposta de {endpoint} não é JSON válido")
                    success = False
            else:
                logger.error(f"❌ Acesso ao endpoint {endpoint} falhou: {response.status_code}")
                success = False
        except Exception as e:
            logger.error(f"Erro ao acessar endpoint {endpoint}: {str(e)}")
            success = False
    
    return success

def test_url_fixes():
    """Testa se as correções de URL estão funcionando"""
    log_separator()
    logger.info("TESTE 7: CORREÇÕES DE URL")
    
    # Testar acesso direto às rotas de API
    api_routes = [
        '/editor/api/get-preset/1',
        '/editor/api/get-standard-fields/1'
    ]
    
    for route in api_routes:
        url = urljoin(BASE_URL, route)
        try:
            response = SESSION.get(url, headers=HEADERS)
            # Não importa se retorna 404 (item não encontrado) ou 200 (sucesso)
            # O importante é que não retorne 500 (erro interno do servidor)
            if response.status_code != 500:
                logger.info(f"✓ Rota {route} não gera erro interno: {response.status_code}")
            else:
                logger.error(f"❌ Rota {route} gera erro interno: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Erro ao acessar rota {route}: {str(e)}")
            return False
    
    return True

def run_all_tests():
    """Executa todos os testes e retorna o resultado"""
    log_separator()
    logger.info("INICIANDO TESTES COMPLETOS DO SISTEMA ZELOPACK")
    log_separator()
    
    tests = [
        ("Login", test_login),
        ("Navegação", test_navigation),
        ("Listagem de Formulários", test_forms_listing),
        ("Editor Universal", test_editor),
        ("Campos Predefinidos", test_predefined_fields),
        ("API Endpoints", test_api_endpoints),
        ("Correções de URL", test_url_fixes)
    ]
    
    results = []
    for name, test_func in tests:
        logger.info(f"Executando teste: {name}")
        
        # Tentativa 1
        success = test_func()
        
        if not success:
            logger.warning(f"Teste {name} falhou na primeira tentativa. Tentando novamente...")
            time.sleep(1)
            
            # Tentativa 2
            success = test_func()
            
            if not success:
                logger.warning(f"Teste {name} falhou na segunda tentativa. Última tentativa...")
                time.sleep(2)
                
                # Tentativa 3
                success = test_func()
        
        results.append((name, success))
        
        log_separator()
    
    # Exibir resumo dos resultados
    logger.info("RESUMO DOS TESTES:")
    
    all_passed = True
    for name, success in results:
        status = "✓ PASSOU" if success else "❌ FALHOU"
        logger.info(f"{status} - {name}")
        if not success:
            all_passed = False
    
    log_separator()
    if all_passed:
        logger.info("TODOS OS TESTES PASSARAM COM SUCESSO!")
    else:
        logger.warning("ALGUNS TESTES FALHARAM. VERIFIQUE OS LOGS PARA MAIS DETALHES.")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)