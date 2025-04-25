from sqlalchemy import or_, and_, func
from datetime import datetime

from models import Report

def search_reports(query=None, category=None, supplier=None, date_from=None, date_to=None, order_by_title=False):
    """
    Realiza busca flexível de laudos com suporte a termos parciais.
    
    Args:
        query: Termo de busca geral (busca em título, descrição, etc.)
        category: Filtro por categoria
        supplier: Filtro por fornecedor
        date_from: Data inicial para filtro
        date_to: Data final para filtro
        order_by_title: Se True, ordena os resultados alfabeticamente pelo título em vez da data
        
    Returns:
        Lista de objetos Report que correspondem aos critérios
    """
    # Iniciar a consulta base
    search_query = Report.query
    
    # Aplicar filtro de texto (busca flexível)
    if query and isinstance(query, str) and query.strip():
        # Limpar query para busca parcial
        search_term = f"%{query}%"
        
        # Buscar em vários campos com OR
        search_query = search_query.filter(
            or_(
                Report.title.ilike(search_term),
                Report.description.ilike(search_term),
                Report.original_filename.ilike(search_term),
                Report.batch_number.ilike(search_term)
            )
        )
    
    # Filtrar por categoria se fornecida
    if category and isinstance(category, str) and category.strip():
        search_query = search_query.filter(Report.category == category)
    
    # Filtrar por fornecedor se fornecido
    if supplier and isinstance(supplier, str) and supplier.strip():
        search_query = search_query.filter(Report.supplier == supplier)
    
    # Filtrar por data de início se fornecida
    if date_from:
        search_query = search_query.filter(Report.report_date >= date_from)
    
    # Filtrar por data final se fornecida
    if date_to:
        search_query = search_query.filter(Report.report_date <= date_to)
    
    # Ordenar resultados com base no parâmetro order_by_title
    if order_by_title:
        # Ordenar alfabeticamente pelo título
        search_query = search_query.order_by(Report.title)
    else:
        # Ordenar do mais recente para o mais antigo (padrão)
        search_query = search_query.order_by(Report.upload_date.desc())
    
    return search_query.all()
