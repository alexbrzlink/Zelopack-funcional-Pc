from sqlalchemy import or_, and_, func
from datetime import datetime

from models import Report

def search_reports(query='', category='', supplier='', date_from=None, date_to=None):
    """
    Realiza busca flexível de laudos com suporte a termos parciais.
    
    Args:
        query: Termo de busca geral (busca em título, descrição, etc.)
        category: Filtro por categoria
        supplier: Filtro por fornecedor
        date_from: Data inicial para filtro
        date_to: Data final para filtro
        
    Returns:
        Lista de objetos Report que correspondem aos critérios
    """
    # Iniciar a consulta base
    search_query = Report.query
    
    # Aplicar filtro de texto (busca flexível)
    if query:
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
    if category:
        search_query = search_query.filter(Report.category == category)
    
    # Filtrar por fornecedor se fornecido
    if supplier:
        search_query = search_query.filter(Report.supplier == supplier)
    
    # Filtrar por data de início se fornecida
    if date_from:
        search_query = search_query.filter(Report.report_date >= date_from)
    
    # Filtrar por data final se fornecida
    if date_to:
        search_query = search_query.filter(Report.report_date <= date_to)
    
    # Ordenar resultados do mais recente para o mais antigo
    search_query = search_query.order_by(Report.upload_date.desc())
    
    return search_query.all()
