import os
import re
import sys

# Configurar o caminho do projeto
project_path = 'C:\\Users\\Alex\\Documents\\ZeloPack-Industria\\ZeloPack-Industria'
sys.path.append(project_path)

# Templates padrão por tipo de página
default_templates = {
    'form': '''
{% extends 'base.html' %}

{% block title %}Formulário - ZeloPack{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="card-title mb-0">Formulário</h4>
                </div>
                <div class="card-body">
                    <form method="post">
                        {{ csrf_token() }}
                        
                        <!-- Conteúdo do formulário aqui -->
                        
                        <div class="form-group text-center">
                            <button type="submit" class="btn btn-primary">Salvar</button>
                            <a href="#" class="btn btn-secondary ml-2">Cancelar</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
    
    'list': '''
{% extends 'base.html' %}

{% block title %}Lista - ZeloPack{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-md-10 offset-md-1">
            <div class="card">
                <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                    <h4 class="card-title mb-0">Lista de Itens</h4>
                    <a href="#" class="btn btn-light btn-sm">
                        <i class="fas fa-plus"></i> Novo Item
                    </a>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped table-hover">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Nome</th>
                                    <th>Data</th>
                                    <th>Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>1</td>
                                    <td>Item de Exemplo</td>
                                    <td>01/01/2025</td>
                                    <td>
                                        <a href="#" class="btn btn-sm btn-info"><i class="fas fa-eye"></i></a>
                                        <a href="#" class="btn btn-sm btn-warning"><i class="fas fa-edit"></i></a>
                                        <a href="#" class="btn btn-sm btn-danger"><i class="fas fa-trash"></i></a>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
    
    'detail': '''
{% extends 'base.html' %}

{% block title %}Detalhes - ZeloPack{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                    <h4 class="card-title mb-0">Detalhes do Item</h4>
                    <div>
                        <a href="#" class="btn btn-light btn-sm">
                            <i class="fas fa-edit"></i> Editar
                        </a>
                        <a href="#" class="btn btn-light btn-sm">
                            <i class="fas fa-arrow-left"></i> Voltar
                        </a>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row mb-3">
                        <div class="col-md-4 font-weight-bold">ID:</div>
                        <div class="col-md-8">1</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-md-4 font-weight-bold">Nome:</div>
                        <div class="col-md-8">Item de Exemplo</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-md-4 font-weight-bold">Data:</div>
                        <div class="col-md-8">01/01/2025</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-md-4 font-weight-bold">Descrição:</div>
                        <div class="col-md-8">Descrição detalhada do item de exemplo.</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
    
    'index': '''
{% extends 'base.html' %}

{% block title %}Página Principal - ZeloPack{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="card-title mb-0">Bem-vindo ao Módulo</h4>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="card mb-3">
                                <div class="card-header bg-light">
                                    <h5 class="mb-0">Gerenciamento</h5>
                                </div>
                                <div class="card-body">
                                    <p>Gerencie os recursos deste módulo.</p>
                                    <a href="#" class="btn btn-primary btn-sm">
                                        <i class="fas fa-cog"></i> Acessar
                                    </a>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card mb-3">
                                <div class="card-header bg-light">
                                    <h5 class="mb-0">Relatórios</h5>
                                </div>
                                <div class="card-body">
                                    <p>Visualize relatórios e estatísticas.</p>
                                    <a href="#" class="btn btn-primary btn-sm">
                                        <i class="fas fa-chart-bar"></i> Acessar
                                    </a>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card mb-3">
                                <div class="card-header bg-light">
                                    <h5 class="mb-0">Configurações</h5>
                                </div>
                                <div class="card-body">
                                    <p>Configure as preferências do módulo.</p>
                                    <a href="#" class="btn btn-primary btn-sm">
                                        <i class="fas fa-wrench"></i> Acessar
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
}

def find_template_references():
    """Encontrar todas as referências a templates no código Python"""
    templates_referenced = []
    for root, dirs, files in os.walk(os.path.join(project_path, 'blueprints')):
        for file in files:
            if file.endswith('.py'):
                try:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Procurar por render_template('...',...) ou render_template("...",...)  
                        matches = re.findall(r'render_template\(['"](.*?)['\"\)]', content)
                        for match in matches:
                            # Remover parâmetros após a vírgula, se houver
                            template_path = match.strip().split(',')[0].strip('\'\"')
                            templates_referenced.append(template_path)
                except Exception as e:
                    print(f"Erro ao analisar {file_path}: {e}")
    
    return templates_referenced

def check_template_exists(template_path):
    """Verificar se o template existe"""
    full_path = os.path.join(project_path, 'templates', template_path)
    return os.path.exists(full_path)

def generate_template(template_path, template_type='form'):
    """Gerar um template com conteúdo padrão"""
    template_content = default_templates.get(template_type, default_templates['form'])
    
    # Criar diretórios se não existirem
    full_path = os.path.join(project_path, 'templates', template_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # Escrever o arquivo do template
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"Template criado: {full_path}")

def guess_template_type(template_path):
    """Tentar adivinhar o tipo de template com base no nome do arquivo"""
    filename = os.path.basename(template_path).lower()
    
    if any(x in filename for x in ['form', 'edit', 'novo', 'create', 'update']):
        return 'form'
    elif any(x in filename for x in ['list', 'index', 'lista', 'listar']):
        return 'list'
    elif any(x in filename for x in ['detail', 'view', 'detalhe', 'visualizar', 'show']):
        return 'detail'
    else:
        return 'index'

def main():
    print("Verificando templates referenciados...")
    templates_referenced = find_template_references()
    
    print(f"\nTotal de templates referenciados: {len(templates_referenced)}")
    
    missing_templates = []
    for template in templates_referenced:
        if not check_template_exists(template):
            missing_templates.append(template)
    
    print(f"\nTemplates ausentes: {len(missing_templates)}")
    
    if missing_templates:
        print("\nLista de templates ausentes:")
        for i, template in enumerate(missing_templates, 1):
            print(f"{i}. {template}")
        
        create_all = input("\nDeseja criar todos os templates ausentes? (s/n): ").lower() == 's'
        
        if create_all:
            for template in missing_templates:
                template_type = guess_template_type(template)
                generate_template(template, template_type)
            print("\nTodos os templates ausentes foram criados!")
        else:
            print("\nOperação cancelada.")
    else:
        print("\nTodos os templates referenciados existem no sistema!")

if __name__ == "__main__":
    main()
