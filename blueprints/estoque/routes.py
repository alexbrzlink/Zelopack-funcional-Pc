from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from app import db
from models import CategoriaEstoque, ItemEstoque, MovimentacaoEstoque
from . import estoque_bp

# Página principal do estoque - Lista todos os itens
@estoque_bp.route('/')
@login_required
def index():
    """Página principal do estoque com lista de itens."""
    itens = ItemEstoque.query.all()
    categorias = CategoriaEstoque.query.all()
    
    # Filtrar reagentes, se solicitado
    filtro = request.args.get('filtro')
    if filtro == 'reagentes':
        itens = [item for item in itens if item.e_reagente]
    elif filtro == 'baixo_estoque':
        itens = [item for item in itens if item.verificar_estoque_baixo()]
    elif filtro == 'proximos_vencimento':
        itens = [item for item in itens if item.data_validade and 
                 item.dias_ate_vencimento() is not None and 
                 item.dias_ate_vencimento() <= 30]
    elif filtro and filtro.isdigit():
        # Filtrar por categoria
        categoria_id = int(filtro)
        itens = [item for item in itens if item.categoria_id == categoria_id]
        
    return render_template('estoque/index.html', 
                         itens=itens, 
                         categorias=categorias,
                         filtro_atual=filtro)

# Página de detalhes de um item específico
@estoque_bp.route('/item/<int:item_id>')
@login_required
def detalhe_item(item_id):
    """Exibe detalhes de um item específico."""
    item = ItemEstoque.query.get_or_404(item_id)
    movimentacoes = MovimentacaoEstoque.query.filter_by(item_id=item_id).order_by(MovimentacaoEstoque.data_movimentacao.desc()).all()
    return render_template('estoque/detalhe_item.html', 
                         item=item, 
                         movimentacoes=movimentacoes)

# Página para adicionar novo item
@estoque_bp.route('/item/novo', methods=['GET', 'POST'])
@login_required
def novo_item():
    """Formulário para adicionar novo item ao estoque."""
    categorias = CategoriaEstoque.query.all()
    
    if request.method == 'POST':
        try:
            # Criar novo item
            item = ItemEstoque(
                codigo=request.form['codigo'],
                nome=request.form['nome'],
                descricao=request.form['descricao'],
                categoria_id=int(request.form['categoria_id']),
                unidade_medida=request.form['unidade_medida'],
                quantidade_minima=float(request.form['quantidade_minima']) if request.form['quantidade_minima'] else 0,
                quantidade_atual=0,  # Inicialmente zero, será atualizado com movimentação
                localizacao=request.form['localizacao'],
                observacoes=request.form['observacoes'],
                
                # Campos específicos para reagentes
                formula_quimica=request.form.get('formula_quimica'),
                cas_number=request.form.get('cas_number'),
                concentracao=request.form.get('concentracao'),
                data_validade=datetime.strptime(request.form['data_validade'], '%Y-%m-%d') if request.form.get('data_validade') else None,
                fabricante=request.form.get('fabricante'),
                
                # Marcadores
                e_reagente=bool(request.form.get('e_reagente')),
                e_perigoso=bool(request.form.get('e_perigoso'))
            )
            
            db.session.add(item)
            db.session.commit()
            
            # Se houver quantidade inicial, registrar como uma entrada
            quantidade_inicial = float(request.form.get('quantidade_inicial', 0))
            if quantidade_inicial > 0:
                movimentacao = MovimentacaoEstoque(
                    item_id=item.id,
                    tipo='entrada',
                    quantidade=quantidade_inicial,
                    lote=request.form.get('lote_inicial'),
                    responsavel=current_user.name,
                    motivo='Estoque inicial',
                    observacoes='Cadastro inicial do item'
                )
                db.session.add(movimentacao)
                
                # Atualizar quantidade atual
                item.quantidade_atual = quantidade_inicial
                db.session.commit()
            
            flash(f'Item "{item.nome}" adicionado com sucesso!', 'success')
            return redirect(url_for('estoque.index'))
        
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Erro ao adicionar item: {str(e)}', 'danger')
    
    return render_template('estoque/form_item.html', 
                         categorias=categorias,
                         item=None,
                         acao='novo')

# Página para editar item existente
@estoque_bp.route('/item/<int:item_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_item(item_id):
    """Formulário para editar item existente."""
    item = ItemEstoque.query.get_or_404(item_id)
    categorias = CategoriaEstoque.query.all()
    
    if request.method == 'POST':
        try:
            # Atualizar item
            item.codigo = request.form['codigo']
            item.nome = request.form['nome']
            item.descricao = request.form['descricao']
            item.categoria_id = int(request.form['categoria_id'])
            item.unidade_medida = request.form['unidade_medida']
            item.quantidade_minima = float(request.form['quantidade_minima']) if request.form['quantidade_minima'] else 0
            item.localizacao = request.form['localizacao']
            item.observacoes = request.form['observacoes']
            
            # Campos específicos para reagentes
            item.formula_quimica = request.form.get('formula_quimica')
            item.cas_number = request.form.get('cas_number')
            item.concentracao = request.form.get('concentracao')
            item.data_validade = datetime.strptime(request.form['data_validade'], '%Y-%m-%d') if request.form.get('data_validade') else None
            item.fabricante = request.form.get('fabricante')
            
            # Marcadores
            item.e_reagente = bool(request.form.get('e_reagente'))
            item.e_perigoso = bool(request.form.get('e_perigoso'))
            
            db.session.commit()
            flash(f'Item "{item.nome}" atualizado com sucesso!', 'success')
            return redirect(url_for('estoque.detalhe_item', item_id=item.id))
        
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Erro ao atualizar item: {str(e)}', 'danger')
    
    return render_template('estoque/form_item.html', 
                         categorias=categorias,
                         item=item,
                         acao='editar')

# Rota para registrar entrada de estoque
@estoque_bp.route('/item/<int:item_id>/entrada', methods=['GET', 'POST'])
@login_required
def registrar_entrada(item_id):
    """Formulário para registrar entrada de estoque."""
    item = ItemEstoque.query.get_or_404(item_id)
    
    if request.method == 'POST':
        try:
            quantidade = float(request.form['quantidade'])
            
            if quantidade <= 0:
                flash('A quantidade deve ser maior que zero.', 'warning')
                return redirect(url_for('estoque.registrar_entrada', item_id=item.id))
            
            # Criar nova movimentação
            movimentacao = MovimentacaoEstoque(
                item_id=item.id,
                tipo='entrada',
                quantidade=quantidade,
                lote=request.form.get('lote'),
                nota_fiscal=request.form.get('nota_fiscal'),
                responsavel=current_user.name,
                motivo=request.form.get('motivo'),
                observacoes=request.form.get('observacoes')
            )
            
            db.session.add(movimentacao)
            
            # Atualizar quantidade atual
            item.quantidade_atual += quantidade
            
            db.session.commit()
            flash(f'Entrada de {quantidade} {item.unidade_medida} registrada com sucesso!', 'success')
            return redirect(url_for('estoque.detalhe_item', item_id=item.id))
        
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            flash(f'Erro ao registrar entrada: {str(e)}', 'danger')
    
    return render_template('estoque/form_movimentacao.html', 
                         item=item,
                         tipo='entrada')

# Rota para registrar saída de estoque
@estoque_bp.route('/item/<int:item_id>/saida', methods=['GET', 'POST'])
@login_required
def registrar_saida(item_id):
    """Formulário para registrar saída de estoque."""
    item = ItemEstoque.query.get_or_404(item_id)
    
    if request.method == 'POST':
        try:
            quantidade = float(request.form['quantidade'])
            
            if quantidade <= 0:
                flash('A quantidade deve ser maior que zero.', 'warning')
                return redirect(url_for('estoque.registrar_saida', item_id=item.id))
            
            if quantidade > item.quantidade_atual:
                flash(f'Quantidade insuficiente em estoque. Disponível: {item.quantidade_atual} {item.unidade_medida}', 'danger')
                return redirect(url_for('estoque.registrar_saida', item_id=item.id))
            
            # Criar nova movimentação
            movimentacao = MovimentacaoEstoque(
                item_id=item.id,
                tipo='saida',
                quantidade=quantidade,
                lote=request.form.get('lote'),
                responsavel=current_user.name,
                motivo=request.form.get('motivo'),
                observacoes=request.form.get('observacoes')
            )
            
            db.session.add(movimentacao)
            
            # Atualizar quantidade atual
            item.quantidade_atual -= quantidade
            
            db.session.commit()
            flash(f'Saída de {quantidade} {item.unidade_medida} registrada com sucesso!', 'success')
            return redirect(url_for('estoque.detalhe_item', item_id=item.id))
        
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            flash(f'Erro ao registrar saída: {str(e)}', 'danger')
    
    return render_template('estoque/form_movimentacao.html', 
                         item=item,
                         tipo='saida')

# Rotas para gerenciar categorias de estoque
@estoque_bp.route('/categorias')
@login_required
def listar_categorias():
    """Lista todas as categorias de estoque."""
    categorias = CategoriaEstoque.query.all()
    return render_template('estoque/categorias.html', categorias=categorias)

@estoque_bp.route('/categoria/nova', methods=['GET', 'POST'])
@login_required
def nova_categoria():
    """Formulário para adicionar nova categoria."""
    if request.method == 'POST':
        try:
            # Criar nova categoria
            categoria = CategoriaEstoque(
                nome=request.form['nome'],
                descricao=request.form.get('descricao')
            )
            
            db.session.add(categoria)
            db.session.commit()
            flash(f'Categoria "{categoria.nome}" adicionada com sucesso!', 'success')
            return redirect(url_for('estoque.listar_categorias'))
        
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Erro ao adicionar categoria: {str(e)}', 'danger')
    
    return render_template('estoque/form_categoria.html', categoria=None)

@estoque_bp.route('/categoria/<int:categoria_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_categoria(categoria_id):
    """Formulário para editar categoria existente."""
    categoria = CategoriaEstoque.query.get_or_404(categoria_id)
    
    if request.method == 'POST':
        try:
            # Atualizar categoria
            categoria.nome = request.form['nome']
            categoria.descricao = request.form.get('descricao')
            
            db.session.commit()
            flash(f'Categoria "{categoria.nome}" atualizada com sucesso!', 'success')
            return redirect(url_for('estoque.listar_categorias'))
        
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Erro ao atualizar categoria: {str(e)}', 'danger')
    
    return render_template('estoque/form_categoria.html', categoria=categoria)

# Rota para relatórios de estoque
@estoque_bp.route('/relatorios')
@login_required
def relatorios():
    """Página de relatórios de estoque."""
    # Itens com estoque baixo
    itens_estoque_baixo = ItemEstoque.query.filter(ItemEstoque.quantidade_atual < ItemEstoque.quantidade_minima).all()
    
    # Itens próximos ao vencimento (30 dias)
    hoje = datetime.utcnow().date()
    itens_vencimento = []
    for item in ItemEstoque.query.filter(ItemEstoque.data_validade != None).all():
        if item.data_validade and (item.data_validade.date() - hoje).days <= 30:
            itens_vencimento.append(item)
    
    # Itens por categoria (para gráfico)
    categorias = CategoriaEstoque.query.all()
    dados_categorias = []
    for cat in categorias:
        count = ItemEstoque.query.filter_by(categoria_id=cat.id).count()
        dados_categorias.append({
            'nome': cat.nome,
            'total': count
        })
    
    return render_template('estoque/relatorios.html',
                         itens_estoque_baixo=itens_estoque_baixo,
                         itens_vencimento=itens_vencimento,
                         dados_categorias=dados_categorias)

# Rotas para controle específico de luvas

@estoque_bp.route('/luvas')
@login_required
def estoque_luvas():
    """Página específica para gerenciamento de estoque de luvas."""
    try:
        # Buscar categoria de luvas (criar se não existir)
        categoria_luvas = CategoriaEstoque.query.filter_by(nome='Luvas').first()
        if not categoria_luvas:
            categoria_luvas = CategoriaEstoque(nome='Luvas', descricao='Luvas de proteção em diversos tamanhos')
            db.session.add(categoria_luvas)
            db.session.commit()
            
        # Buscar itens de luvas por tamanho
        luvas_p = ItemEstoque.query.filter_by(nome='Luvas Tamanho P', categoria_id=categoria_luvas.id).first()
        luvas_m = ItemEstoque.query.filter_by(nome='Luvas Tamanho M', categoria_id=categoria_luvas.id).first()
        luvas_g = ItemEstoque.query.filter_by(nome='Luvas Tamanho G', categoria_id=categoria_luvas.id).first()
        luvas_xg = ItemEstoque.query.filter_by(nome='Luvas Tamanho XG', categoria_id=categoria_luvas.id).first()
        
        # Criar itens de luvas se não existirem
        if not luvas_p:
            luvas_p = ItemEstoque(
                codigo='LUVAS-P',
                nome='Luvas Tamanho P',
                categoria_id=categoria_luvas.id,
                unidade_medida='pares',
                quantidade_minima=10,
                quantidade_atual=0,
                e_reagente=False
            )
            db.session.add(luvas_p)
            
        if not luvas_m:
            luvas_m = ItemEstoque(
                codigo='LUVAS-M',
                nome='Luvas Tamanho M',
                categoria_id=categoria_luvas.id,
                unidade_medida='pares',
                quantidade_minima=20,
                quantidade_atual=0,
                e_reagente=False
            )
            db.session.add(luvas_m)
            
        if not luvas_g:
            luvas_g = ItemEstoque(
                codigo='LUVAS-G',
                nome='Luvas Tamanho G',
                categoria_id=categoria_luvas.id,
                unidade_medida='pares',
                quantidade_minima=20,
                quantidade_atual=0,
                e_reagente=False
            )
            db.session.add(luvas_g)
            
        if not luvas_xg:
            luvas_xg = ItemEstoque(
                codigo='LUVAS-XG',
                nome='Luvas Tamanho XG',
                categoria_id=categoria_luvas.id,
                unidade_medida='pares',
                quantidade_minima=10,
                quantidade_atual=0,
                e_reagente=False
            )
            db.session.add(luvas_xg)
            
        db.session.commit()
        
        # Obter histórico de movimentações para cada tamanho
        items_luvas = [luvas_p, luvas_m, luvas_g, luvas_xg]
        
        # Montar dicionário com dados para a view
        dados_luvas = []
        
        for item in items_luvas:
            # Obter as últimas 10 movimentações para este item
            movimentacoes = MovimentacaoEstoque.query.filter_by(item_id=item.id).order_by(
                MovimentacaoEstoque.data_movimentacao.desc()).limit(10).all()
                
            # Adicionar à lista
            dados_luvas.append({
                'id': item.id,
                'tamanho': item.nome.split('Tamanho ')[1],
                'codigo': item.codigo,
                'quantidade_atual': item.quantidade_atual,
                'quantidade_minima': item.quantidade_minima,
                'status': 'baixo' if item.verificar_estoque_baixo() else 'ok',
                'movimentacoes': movimentacoes
            })
        
        return render_template('estoque/luvas.html', dados_luvas=dados_luvas)
        
    except Exception as e:
        flash(f'Erro ao carregar estoque de luvas: {str(e)}', 'danger')
        return redirect(url_for('estoque.index'))

@estoque_bp.route('/luvas/registrar', methods=['POST'])
@login_required
def registrar_movimentacao_luvas():
    """Registra movimentação no estoque de luvas."""
    try:
        item_id = request.form.get('item_id')
        tipo = request.form.get('tipo')
        quantidade = float(request.form.get('quantidade', 1))
        tamanho_luva = request.form.get('tamanho_luva')
        
        # Validações
        if not all([item_id, tipo, quantidade, tamanho_luva]):
            flash('Todos os campos são obrigatórios.', 'warning')
            return redirect(url_for('estoque.estoque_luvas'))
            
        if tipo not in ['entrada', 'saida']:
            flash('Tipo de movimentação inválido.', 'warning')
            return redirect(url_for('estoque.estoque_luvas'))
            
        if quantidade <= 0:
            flash('A quantidade deve ser maior que zero.', 'warning')
            return redirect(url_for('estoque.estoque_luvas'))
            
        # Buscar o item
        item = ItemEstoque.query.get_or_404(item_id)
        
        # Verificar disponibilidade para saída
        if tipo == 'saida' and quantidade > item.quantidade_atual:
            flash(f'Quantidade insuficiente em estoque. Disponível: {item.quantidade_atual} pares.', 'danger')
            return redirect(url_for('estoque.estoque_luvas'))
            
        # Criar a movimentação
        pessoa = request.form.get('pessoa', '')
        observacoes = request.form.get('observacoes', '')
        
        movimentacao = MovimentacaoEstoque(
            item_id=item.id,
            tipo=tipo,
            quantidade=quantidade,
            responsavel=current_user.name,
            motivo=f"{'Entrada' if tipo == 'entrada' else 'Retirada'} de luvas {tamanho_luva}",
            observacoes=observacoes,
            
            # Campos específicos para luvas
            tamanho_luva=tamanho_luva,
            pessoa_entrega=pessoa if tipo == 'entrada' else None,
            pessoa_retirada=pessoa if tipo == 'saida' else None
        )
        
        db.session.add(movimentacao)
        
        # Atualizar quantidade
        if tipo == 'entrada':
            item.quantidade_atual += quantidade
        else:
            item.quantidade_atual -= quantidade
            
        db.session.commit()
        
        flash(f"{'Entrada' if tipo == 'entrada' else 'Retirada'} de {quantidade} pares de luvas tamanho {tamanho_luva} registrada com sucesso!", 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao registrar movimentação: {str(e)}', 'danger')
        
    return redirect(url_for('estoque.estoque_luvas'))

@estoque_bp.route('/luvas/historico/<tamanho>')
@login_required
def historico_luvas(tamanho):
    """Exibe histórico completo de movimentações de um tamanho específico de luvas."""
    try:
        # Validar tamanho
        if tamanho not in ['P', 'M', 'G', 'XG']:
            flash('Tamanho de luva inválido.', 'warning')
            return redirect(url_for('estoque.estoque_luvas'))
            
        # Buscar item correspondente
        item = ItemEstoque.query.filter_by(nome=f'Luvas Tamanho {tamanho}').first()
        
        if not item:
            flash('Item não encontrado.', 'warning')
            return redirect(url_for('estoque.estoque_luvas'))
            
        # Buscar todas as movimentações
        movimentacoes = MovimentacaoEstoque.query.filter_by(item_id=item.id).order_by(
            MovimentacaoEstoque.data_movimentacao.desc()).all()
            
        return render_template('estoque/historico_luvas.html', 
                             item=item,
                             tamanho=tamanho,
                             movimentacoes=movimentacoes)
                             
    except Exception as e:
        flash(f'Erro ao carregar histórico: {str(e)}', 'danger')
        return redirect(url_for('estoque.estoque_luvas'))

# Rota para excluir item (via AJAX)
@estoque_bp.route('/item/<int:item_id>/excluir', methods=['POST'])
@login_required
def excluir_item(item_id):
    """Exclui um item do estoque."""
    try:
        item = ItemEstoque.query.get_or_404(item_id)
        nome_item = item.nome
        
        # Excluir movimentações relacionadas
        MovimentacaoEstoque.query.filter_by(item_id=item.id).delete()
        
        # Excluir o item
        db.session.delete(item)
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=True, message=f'Item "{nome_item}" excluído com sucesso!')
        
        flash(f'Item "{nome_item}" excluído com sucesso!', 'success')
        return redirect(url_for('estoque.index'))
        
    except SQLAlchemyError as e:
        db.session.rollback()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, message=f'Erro ao excluir item: {str(e)}'), 500
        
        flash(f'Erro ao excluir item: {str(e)}', 'danger')
        return redirect(url_for('estoque.index'))

# Rota para excluir categoria
@estoque_bp.route('/categoria/<int:categoria_id>/excluir', methods=['POST'])
@login_required
def excluir_categoria(categoria_id):
    """Exclui uma categoria de estoque."""
    try:
        categoria = CategoriaEstoque.query.get_or_404(categoria_id)
        
        # Verificar se existem itens nesta categoria
        itens = ItemEstoque.query.filter_by(categoria_id=categoria.id).first()
        if itens:
            flash('Não é possível excluir categoria que possui itens vinculados.', 'warning')
            return redirect(url_for('estoque.listar_categorias'))
        
        nome_categoria = categoria.nome
        db.session.delete(categoria)
        db.session.commit()
        
        flash(f'Categoria "{nome_categoria}" excluída com sucesso!', 'success')
        return redirect(url_for('estoque.listar_categorias'))
        
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Erro ao excluir categoria: {str(e)}', 'danger')
        return redirect(url_for('estoque.listar_categorias'))