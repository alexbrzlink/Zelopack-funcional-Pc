import calendar
import datetime
import locale
from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from . import laboratorio_bp

# Configura o locale para português do Brasil
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')
    except:
        pass  # Mantém o padrão se não conseguir configurar

# Nomes dos meses em português
MESES = {
    1: 'JANEIRO',
    2: 'FEVEREIRO',
    3: 'MARÇO',
    4: 'ABRIL',
    5: 'MAIO',
    6: 'JUNHO',
    7: 'JULHO',
    8: 'AGOSTO',
    9: 'SETEMBRO',
    10: 'OUTUBRO',
    11: 'NOVEMBRO',
    12: 'DEZEMBRO'
}

@laboratorio_bp.route('/')
@login_required
def index():
    """Página principal do módulo de calendário do laboratório"""
    return redirect(url_for('laboratorio.calendario'))

@laboratorio_bp.route('/calendario')
@login_required
def calendario():
    """Exibe o calendário de atividades do laboratório"""
    # Obtém o mês e ano da query string ou usa o mês/ano atual
    ano = int(request.args.get('ano', datetime.datetime.now().year))
    mes = int(request.args.get('mes', datetime.datetime.now().month))
    
    # Obtém o primeiro dia do mês e o número de dias
    primeiro_dia = datetime.date(ano, mes, 1)
    _, dias_no_mes = calendar.monthrange(ano, mes)
    
    # Obter o mês anterior para calcular os dias em branco no começo do calendário
    mes_anterior = 12 if mes == 1 else mes - 1
    ano_anterior = ano - 1 if mes == 1 else ano
    _, dias_no_mes_anterior = calendar.monthrange(ano_anterior, mes_anterior)
    
    # Obtém o nome do mês
    mes_nome = MESES[mes]
    
    # Obtém as atividades para o mês
    atividades = gerar_atividades_mes(ano, mes)
    
    return render_template('laboratorio/calendario.html', 
                           ano=ano, 
                           mes=mes, 
                           mes_nome=mes_nome,
                           dias_no_mes=dias_no_mes,
                           dias_no_mes_anterior=dias_no_mes_anterior,
                           primeiro_dia=primeiro_dia,
                           atividades=atividades,
                           now=datetime.datetime.now)

@laboratorio_bp.route('/calendario/anual')
@login_required
def calendario_anual():
    """Exibe o calendário anual de atividades do laboratório"""
    # Obtém o ano da query string ou usa o ano atual
    ano = int(request.args.get('ano', datetime.datetime.now().year))
    
    # Gera o calendário para todos os meses do ano
    calendario_anual = {}
    for mes in range(1, 13):
        primeiro_dia = datetime.date(ano, mes, 1)
        _, dias_no_mes = calendar.monthrange(ano, mes)
        
        calendario_anual[mes] = {
            'primeiro_dia': primeiro_dia,
            'dias_no_mes': dias_no_mes,
            'atividades': gerar_atividades_mes(ano, mes)
        }
    
    return render_template('laboratorio/calendario_anual.html', 
                           ano=ano,
                           calendario=calendario_anual,
                           meses=MESES)

@laboratorio_bp.route('/calendario/imprimir')
@login_required
def imprimir_calendario():
    """Versão para impressão do calendário mensal"""
    # Obtém o mês e ano da query string ou usa o mês/ano atual
    ano = int(request.args.get('ano', datetime.datetime.now().year))
    mes = int(request.args.get('mes', datetime.datetime.now().month))
    
    # Obtém o primeiro dia do mês e o número de dias
    primeiro_dia = datetime.date(ano, mes, 1)
    _, dias_no_mes = calendar.monthrange(ano, mes)
    
    # Obter o mês anterior para calcular os dias em branco no começo do calendário
    mes_anterior = 12 if mes == 1 else mes - 1
    ano_anterior = ano - 1 if mes == 1 else ano
    _, dias_no_mes_anterior = calendar.monthrange(ano_anterior, mes_anterior)
    
    # Obtém o nome do mês
    mes_nome = MESES[mes]
    
    # Obtém as atividades para o mês
    atividades = gerar_atividades_mes(ano, mes)
    
    return render_template('laboratorio/imprimir_calendario.html', 
                           ano=ano, 
                           mes=mes, 
                           mes_nome=mes_nome,
                           dias_no_mes=dias_no_mes,
                           dias_no_mes_anterior=dias_no_mes_anterior,
                           primeiro_dia=primeiro_dia,
                           atividades=atividades)

@laboratorio_bp.route('/calendario/imprimir/anual')
@login_required
def imprimir_calendario_anual():
    """Versão para impressão do calendário anual"""
    # Obtém o ano da query string ou usa o ano atual
    ano = int(request.args.get('ano', datetime.datetime.now().year))
    
    # Gera o calendário para todos os meses do ano
    calendario_anual = {}
    for mes in range(1, 13):
        primeiro_dia = datetime.date(ano, mes, 1)
        _, dias_no_mes = calendar.monthrange(ano, mes)
        
        calendario_anual[mes] = {
            'primeiro_dia': primeiro_dia,
            'dias_no_mes': dias_no_mes,
            'atividades': gerar_atividades_mes(ano, mes)
        }
    
    return render_template('laboratorio/imprimir_calendario_anual.html', 
                           ano=ano,
                           calendario=calendario_anual,
                           meses=MESES)

def gerar_atividades_mes(ano, mes):
    """Gera as atividades para o mês conforme as regras definidas"""
    # Inicializa o dicionário de atividades
    atividades = {}
    
    # Obtém o número de dias no mês e o primeiro dia da semana (0 = segunda, 6 = domingo)
    _, dias_no_mes = calendar.monthrange(ano, mes)
    
    # Define o primeiro dia do mês para calcular dia da semana
    primeiro_dia = datetime.date(ano, mes, 1)
    
    # Inicializa o turno para o Shelf Life 10D - determina o turno inicial do mês
    # baseado na data do primeiro dia do mês
    # Faz o cálculo para descobrir o turno correto para o primeiro dia do mês
    # Vamos usar o número de dias desde uma data de referência conhecida
    data_referencia = datetime.date(2024, 1, 1)  # 1º de janeiro de 2024 começa com o 1º turno
    dias_desde_referencia = (primeiro_dia - data_referencia).days
    # Como o turno muda diariamente, o turno inicial deste mês é o resto da divisão por 3, mais 1
    turno_shelf_life = (dias_desde_referencia % 3) + 1
    
    # Gera as atividades para cada dia do mês
    for dia in range(1, dias_no_mes + 1):
        data = datetime.date(ano, mes, dia)
        dia_semana = data.weekday()  # 0=segunda, 1=terça, ..., 6=domingo
        
        # Inicializa as atividades para cada turno
        atividades_dia = {
            1: [],  # 1º turno
            2: [],  # 2º turno
            3: []   # 3º turno
        }
        
        # 1. E.T.E (Estação de Tratamento de Efluentes)
        if dia_semana == 0:  # Segunda-feira
            atividades_dia[1].append("E.T.E")
        else:  # Terça a domingo
            atividades_dia[3].append("E.T.E")
        
        # 2. Análise de Água
        if dia_semana == 0 or dia_semana == 3:  # Segunda ou Quinta
            atividades_dia[1].append("ANÁLISE DE ÁGUA")
        elif dia_semana == 1 or dia_semana == 4:  # Terça ou Sexta
            atividades_dia[2].append("ANÁLISE DE ÁGUA")
        elif dia_semana == 2 or dia_semana == 5:  # Quarta ou Sábado
            atividades_dia[3].append("ANÁLISE DE ÁGUA")
        elif dia_semana == 6:  # Domingo
            # No domingo, todos os turnos realizam análise de água (se houver expediente)
            atividades_dia[1].append("ANÁLISE DE ÁGUA*")
            atividades_dia[2].append("ANÁLISE DE ÁGUA*")
            atividades_dia[3].append("ANÁLISE DE ÁGUA*")
        
        # 3. Shelf Life 10D (alterna ciclicamente entre os turnos)
        atividades_dia[turno_shelf_life].append("SHELF LIFE 10D")
        
        # Atualiza o turno para o próximo dia
        turno_shelf_life = turno_shelf_life % 3 + 1  # Cicla entre 1, 2, 3
        
        # 4. Turbidez (Apenas às segundas-feiras, 3º turno)
        if dia_semana == 0:  # Segunda-feira
            atividades_dia[3].append("TURBIDEZ")
        
        # Armazena as atividades para este dia
        atividades[dia] = atividades_dia
    
    return atividades