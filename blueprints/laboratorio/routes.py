import calendar
import datetime
from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from . import laboratorio_bp

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
    
    # Obtém o nome do mês
    mes_nome = calendar.month_name[mes]
    
    # Obtém as atividades para o mês
    atividades = gerar_atividades_mes(ano, mes)
    
    return render_template('laboratorio/calendario.html', 
                           ano=ano, 
                           mes=mes, 
                           mes_nome=mes_nome,
                           dias_no_mes=dias_no_mes,
                           primeiro_dia=primeiro_dia,
                           atividades=atividades)

def gerar_atividades_mes(ano, mes):
    """Gera as atividades para o mês conforme as regras definidas"""
    # Inicializa o dicionário de atividades
    atividades = {}
    
    # Obtém o número de dias no mês e o primeiro dia da semana (0 = segunda, 6 = domingo)
    _, dias_no_mes = calendar.monthrange(ano, mes)
    
    # Inicializa o turno para o Shelf Life 10D (começa com o 1º turno)
    turno_shelf_life = 1
    
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
            atividades_dia[1].append("Análise de Água")
        elif dia_semana == 1 or dia_semana == 4:  # Terça ou Sexta
            atividades_dia[2].append("Análise de Água")
        elif dia_semana == 2 or dia_semana == 5:  # Quarta ou Sábado
            atividades_dia[3].append("Análise de Água")
        elif dia_semana == 6:  # Domingo
            # No domingo, todos os turnos realizam análise de água (se houver expediente)
            atividades_dia[1].append("Análise de Água (todos os pontos)*")
            atividades_dia[2].append("Análise de Água (todos os pontos)*")
            atividades_dia[3].append("Análise de Água (todos os pontos)*")
        
        # 3. Shelf Life 10D (alterna ciclicamente entre os turnos)
        atividades_dia[turno_shelf_life].append("Shelf Life 10D")
        
        # Atualiza o turno para o próximo dia
        turno_shelf_life = turno_shelf_life % 3 + 1  # Cicla entre 1, 2, 3
        
        # 4. Turbidez (Apenas às segundas-feiras, 3º turno)
        if dia_semana == 0:  # Segunda-feira
            atividades_dia[3].append("Turbidez")
        
        # Armazena as atividades para este dia
        atividades[dia] = atividades_dia
    
    return atividades