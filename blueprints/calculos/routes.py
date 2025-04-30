import logging
import os
import json
import math
import numpy as np
from io import BytesIO
import base64
from flask import render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user

# Importar o blueprint do arquivo __init__.py
from . import calculos_bp

# Dicionário de fatores de conversão para diferentes tipos de cálculos
FATORES_CONVERSAO = {
    "brix": {
        "temperatura_referencia": 20.0,
        "fator_correcao": {
            "standard": 1.0,
            "citrus": 0.98,
            "nectars": 1.02,
            "concentrate": 0.95
        }
    },
    "acidez": {
        "fator_citrico": 0.064,
        "fator_malico": 0.067,
        "fator_tartarico": 0.075
    },
    "producao": {
        "tolerancia_padrao": 2.5,
        "densidade_media": {
            "suco": 1.045,
            "nectar": 1.050,
            "refresco": 1.030
        }
    },
    "solidos": {
        "fator_conversao": 1.33
    }
}

# Carregar configurações adicionais do arquivo se existir
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config_calculos.json')
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        try:
            configs = json.load(f)
            # Mesclar com as configurações padrão
            for categoria, valores in configs.items():
                if categoria in FATORES_CONVERSAO:
                    FATORES_CONVERSAO[categoria].update(valores)
                else:
                    FATORES_CONVERSAO[categoria] = valores
        except json.JSONDecodeError:
            logging.error("Erro ao carregar arquivo de configuração de cálculos")


@calculos_bp.route('/')
@login_required
def index():
    """Página principal do módulo de cálculos técnicos."""
    return render_template('calculos/index.html')


@calculos_bp.route('/tecnicos', methods=['GET', 'POST'])
@login_required
def tecnicos():
    """Calculadora técnica avançada com 29 cálculos específicos."""
    results = {}
    if request.method == 'POST':
        # Parâmetros de entrada
        peso_liquido = float(request.form.get('peso_liquido', 0) or 0)
        perdas = float(request.form.get('perdas', 0) or 0)
        densidade = float(request.form.get('densidade', 1) or 1)
        brix_atual = float(request.form.get('brix_atual', 0) or 0)
        brix_desejado = float(request.form.get('brix_desejado', 0) or 0)
        volume_atual = float(request.form.get('volume_atual', 0) or 0)
        brix_medido = float(request.form.get('brix_medido', 0) or 0)
        temperatura = float(request.form.get('temperatura', 20) or 20)
        peso_embalagem = float(request.form.get('peso_embalagem', 0) or 0)
        volume = float(request.form.get('volume', 0) or 0)
        concentracao_desejada = float(request.form.get('concentracao_desejada', 0) or 0)
        concentracao_corante = float(request.form.get('concentracao_corante', 1) or 1)
        peso = float(request.form.get('peso', 0) or 0)
        acidez = float(request.form.get('acidez', 0) or 0)
        ratio = float(request.form.get('ratio', 0) or 0)
        volume_titulante = float(request.form.get('volume_titulante', 0) or 0)
        normalidade = float(request.form.get('normalidade', 0.1) or 0.1)
        volume_amostra = float(request.form.get('volume_amostra', 10) or 10)
        acidez_atual = float(request.form.get('acidez_atual', 0) or 0)
        concentracao_soda = float(request.form.get('concentracao_soda', 1) or 1)
        fator = float(request.form.get('fator', 1) or 1)
        volume_inicial = float(request.form.get('volume_inicial', 0) or 0)
        volume_final = float(request.form.get('volume_final', 0) or 0)
        brix1 = float(request.form.get('brix1', 0) or 0)
        vol1 = float(request.form.get('vol1', 0) or 0)
        brix2 = float(request.form.get('brix2', 0) or 0)
        vol2 = float(request.form.get('vol2', 0) or 0)
        acidez1 = float(request.form.get('acidez1', 0) or 0)
        acidez2 = float(request.form.get('acidez2', 0) or 0)
        vazao = float(request.form.get('vazao', 1) or 1)
        acidez_desejada = float(request.form.get('acidez_desejada', 0) or 0)
        brix_inicial = float(request.form.get('brix_inicial', 0) or 0)
        acucar_cristal = float(request.form.get('acucar_cristal', 0) or 0)
        volume_solucao = float(request.form.get('volume_solucao', 0) or 0)
        percentual_acucar = float(request.form.get('percentual_acucar', 0) or 0)
        peso_bruto = float(request.form.get('peso_bruto', 0) or 0)
        tara = float(request.form.get('tara', 0) or 0)
        peso_total = float(request.form.get('peso_total', 0) or 0)
        embalagem = float(request.form.get('embalagem', 0) or 0)

        # Cálculos
        # 1. Produção Final (200)
        producao_final = peso_liquido - perdas

        # 2. Produção (Litro)
        producao_l = peso_liquido / densidade if densidade != 0 else 0

        # 3. Abaixar Brix
        qtd_agua_l = ((brix_atual - brix_desejado) * volume_atual) / brix_desejado if brix_desejado != 0 else 0

        # 4. Brix Corrigido
        fator_correcao = 0.002 * (temperatura - 20)  # Fator típico baseado na temperatura
        brix_corrigido = brix_medido + fator_correcao

        # 5. Peso Bruto
        peso_bruto_calc = peso_liquido + peso_embalagem

        # 6. Corantes
        qtd_corante = (volume * concentracao_desejada) / concentracao_corante if concentracao_corante != 0 else 0

        # 7. Densidade
        densidade_calc = peso / volume if volume != 0 else 0

        # 8. Ratio
        ratio_calc = brix_atual / acidez if acidez != 0 else 0

        # 9. Ratio - Brix
        brix_from_ratio = ratio * acidez

        # 10. Ratio - Acidez
        acidez_from_ratio = brix_atual / ratio if ratio != 0 else 0

        # 11. Acidez (%)
        acidez_calc = (volume_titulante * normalidade * 0.064) / volume_amostra if volume_amostra != 0 else 0

        # 12. Cálculo de Soda
        qtd_soda = (volume * acidez_atual) / (concentracao_soda * 100) if concentracao_soda != 0 else 0

        # 13. Vitamina C
        vitamina_c = (volume_titulante * fator) / volume_amostra if volume_amostra != 0 else 0

        # 14. Soda-Antigo / Soda-Diversey (mesma fórmula, fatores distintos)
        qtd_soda_diversey = (volume * acidez_atual) / (concentracao_soda * 100) if concentracao_soda != 0 else 0

        # 15. Ácido-Diversey / Ácido-Antigo (mesma fórmula que Acidez, tabelas distintas)
        acidez_diversey = (volume_titulante * normalidade * 0.064) / volume_amostra if volume_amostra != 0 else 0

        # 16. Saber Perda de Base (%)
        perda = ((volume_inicial - volume_final) / volume_inicial) * 100 if volume_inicial != 0 else 0

        # 17. Quantidade de Açúcar a Puxar
        qtd_acucar_puxar = ((brix_desejado - brix_atual) * volume * densidade) / 100

        # 18. Aumentar Brix Açúcar Batido (mesma fórmula que Qtd Açúcar a Puxar)
        qtd_acucar_batido = ((brix_desejado - brix_atual) * volume * densidade) / 100

        # 19. Previsão Brix
        brix_previsto = (brix1 * vol1 + brix2 * vol2) / (vol1 + vol2) if (vol1 + vol2) != 0 else 0

        # 20. Previsão Acidez
        acidez_prevista = (acidez1 * vol1 + acidez2 * vol2) / (vol1 + vol2) if (vol1 + vol2) != 0 else 0

        # 21. Tempo de Finalização
        tempo_final = volume / vazao if vazao != 0 else 0

        # 22. Aumentar Acidez
        qtd_acido = (acidez_desejada - acidez_atual) * volume * fator

        # 23. Diminuir Acidez
        novo_volume_acidez = (volume_atual * acidez_atual) / acidez_desejada if acidez_desejada != 0 else 0

        # 24. Correção de Brix
        novo_volume_brix = (brix_inicial * volume_inicial) / brix_desejado if brix_desejado != 0 else 0

        # 25. Conversão Cristal Líquido
        volume_solucao_calc = acucar_cristal / densidade if densidade != 0 else 0

        # 26. Correção Açúcar Cristal
        qtd_acucar_cristal = (brix_desejado - brix_atual) * volume / 100

        # 27. Conversão Líquido - Cristal
        peso_cristal = volume_solucao * densidade * (percentual_acucar / 100)

        # 28. Peso Líquido 200
        peso_liquido_200 = peso_bruto - tara

        # 29. Peso Líquido Litro / Zeragem de Embalagem
        volume_liquido = peso_liquido / densidade if densidade != 0 else 0
        peso_liquido_zeragem = peso_total - embalagem

        results = {
            "Produção Final (kg)": producao_final,
            "Produção (Litro)": producao_l,
            "Abaixar Brix (L)": qtd_agua_l,
            "Brix Corrigido": brix_corrigido,
            "Peso Bruto (kg)": peso_bruto_calc,
            "Quantidade de Corante (L)": qtd_corante,
            "Densidade (g/mL)": densidade_calc,
            "Ratio": ratio_calc,
            "Brix (via Ratio)": brix_from_ratio,
            "Acidez (via Ratio)": acidez_from_ratio,
            "Acidez (%)": acidez_calc,
            "Quantidade de Soda (L)": qtd_soda,
            "Vitamina C (mg/L)": vitamina_c,
            "Quantidade de Soda Diversey (L)": qtd_soda_diversey,
            "Acidez Diversey (%)": acidez_diversey,
            "Perda de Base (%)": perda,
            "Quantidade de Açúcar a Puxar (kg)": qtd_acucar_puxar,
            "Quantidade de Açúcar Batido (kg)": qtd_acucar_batido,
            "Brix Previsto": brix_previsto,
            "Acidez Prevista (%)": acidez_prevista,
            "Tempo de Finalização (min)": tempo_final,
            "Quantidade de Ácido (L)": qtd_acido,
            "Novo Volume (Diminuir Acidez) (L)": novo_volume_acidez,
            "Novo Volume (Correção Brix) (L)": novo_volume_brix,
            "Volume Solução (Cristal Líquido) (L)": volume_solucao_calc,
            "Quantidade de Açúcar Cristal (kg)": qtd_acucar_cristal,
            "Peso Cristal (Líquido - Cristal) (kg)": peso_cristal,
            "Peso Líquido 200 (kg)": peso_liquido_200,
            "Volume Líquido (Peso Líquido Litro) (L)": volume_liquido,
            "Peso Líquido (Zeragem de Embalagem) (kg)": peso_liquido_zeragem,
        }

    return render_template('calculos/technical_abas_new.html', results=results)


@calculos_bp.route('/tempo-tq')
# Temporariamente removendo a restrição de login para fins de teste
def tempo_tq():
    """Rota específica para cálculo de tempo de finalização do TQ."""
    # Verificar se o usuário está logado
    if not current_user.is_authenticated:
        from flask import flash
        flash('Esta página requer autenticação. Por favor, faça login com "admin" e "admin123".', 'warning')
    return render_template('calculos/technical_tempo_original.html')


@calculos_bp.route('/api/calcular/producao-200g', methods=['POST'])
@login_required
def api_calcular_producao_200g():
    """API para cálculo de produção 200g."""
    data = request.get_json()
    
    try:
        peso_bruto = float(data.get('peso_bruto', 0))
        peso_tara = float(data.get('peso_tara', 0))
        peso_especificado = float(data.get('peso_especificado', 200))
        tolerancia = float(data.get('tolerancia', FATORES_CONVERSAO['producao']['tolerancia_padrao']))
        
        # Validar dados
        if peso_bruto <= 0 or peso_tara <= 0:
            return jsonify({
                'success': False,
                'message': 'Valores de peso bruto e tara devem ser positivos.'
            }), 400
        
        # Calcular peso líquido
        peso_liquido = peso_bruto - peso_tara
        
        # Calcular limites de tolerância
        tolerancia_min = peso_especificado * (1 - (tolerancia / 100))
        tolerancia_max = peso_especificado * (1 + (tolerancia / 100))
        desvio = ((peso_liquido - peso_especificado) / peso_especificado) * 100
        
        # Determinar status
        if peso_liquido < tolerancia_min:
            status = 'Abaixo da tolerância'
            status_class = 'alert-danger'
        elif peso_liquido > tolerancia_max:
            status = 'Acima da tolerância'
            status_class = 'alert-warning'
        else:
            status = 'Dentro da tolerância'
            status_class = 'alert-success'
        
        # Dados a retornar
        resultado = {
            'success': True,
            'peso_liquido': peso_liquido,
            'status': status,
            'status_class': status_class,
            'desvio': desvio,
            'tolerancia_min': tolerancia_min,
            'tolerancia_max': tolerancia_max,
            'diferenca_abs': peso_liquido - peso_especificado
        }
        
        # Registrar o cálculo no histórico (opcional)
        registrar_historico_calculo('producao-200g', {
            'peso_bruto': peso_bruto,
            'peso_tara': peso_tara,
            'peso_especificado': peso_especificado,
            'tolerancia': tolerancia,
            'resultado': resultado
        })
        
        return jsonify(resultado)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'Erro de formato nos valores informados: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao calcular produção 200g: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Ocorreu um erro ao processar o cálculo.'
        }), 500


# Rota removida conforme solicitação do usuário para remover a calculadora padrão
# A funcionalidade de cálculo de Brix está disponível na calculadora avançada


@calculos_bp.route('/api/calcular/producao-litro', methods=['POST'])
@login_required
def api_calcular_producao_litro():
    """API para cálculo de produção em litros baseado em peso e densidade."""
    data = request.get_json()
    
    try:
        peso_total = float(data.get('peso_total', 0))
        densidade = float(data.get('densidade', 1.0))
        
        # Validar dados
        if peso_total <= 0 or densidade <= 0:
            return jsonify({
                'success': False,
                'message': 'Valores de peso total e densidade devem ser positivos.'
            }), 400
        
        # Cálculo do volume produzido
        volume_produzido = peso_total / densidade
        
        resultado = {
            'success': True,
            'volume_produzido': volume_produzido,
            'peso_total': peso_total,
            'densidade': densidade,
            'formula': f'Volume = {peso_total} ÷ {densidade} = {volume_produzido:.2f} L'
        }
        
        # Registrar o cálculo no histórico
        registrar_historico_calculo('producao-litro', {
            'peso_total': peso_total,
            'densidade': densidade,
            'resultado': resultado
        })
        
        return jsonify(resultado)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'Erro de formato nos valores informados: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao calcular produção em litros: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Ocorreu um erro ao processar o cálculo.'
        }), 500


@calculos_bp.route('/api/calcular/densidade', methods=['POST'])
@login_required
def api_calcular_densidade():
    """API para cálculo de densidade baseado em massa e volume."""
    data = request.get_json()
    
    try:
        massa = float(data.get('massa', 0))
        volume = float(data.get('volume', 0))
        
        # Validar dados
        if massa <= 0 or volume <= 0:
            return jsonify({
                'success': False,
                'message': 'Valores de massa e volume devem ser positivos.'
            }), 400
        
        # Cálculo da densidade
        densidade = massa / volume
        
        resultado = {
            'success': True,
            'densidade': densidade,
            'massa': massa,
            'volume': volume,
            'formula': f'Densidade = {massa} ÷ {volume} = {densidade:.4f} g/mL'
        }
        
        # Registrar o cálculo no histórico
        registrar_historico_calculo('densidade', {
            'massa': massa,
            'volume': volume,
            'resultado': resultado
        })
        
        return jsonify(resultado)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'Erro de formato nos valores informados: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao calcular densidade: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Ocorreu um erro ao processar o cálculo.'
        }), 500


@calculos_bp.route('/api/calcular/ratio', methods=['POST'])
@login_required
def api_calcular_ratio():
    """API para cálculo de ratio (razão entre Brix e Acidez)."""
    data = request.get_json()
    
    try:
        brix = float(data.get('brix', 0))
        acidez = float(data.get('acidez', 0))
        
        # Validar dados
        if brix <= 0:
            return jsonify({
                'success': False,
                'message': 'O valor de Brix deve ser positivo.'
            }), 400
            
        if acidez <= 0:
            return jsonify({
                'success': False,
                'message': 'O valor de Acidez deve ser positivo.'
            }), 400
        
        # Cálculo do ratio
        ratio = brix / acidez
        
        resultado = {
            'success': True,
            'ratio': ratio,
            'brix': brix,
            'acidez': acidez,
            'formula': f'Ratio = {brix} ÷ {acidez} = {ratio:.2f}'
        }
        
        # Classificação do ratio
        if ratio < 12:
            classificacao = "Ácido"
        elif ratio >= 12 and ratio < 16:
            classificacao = "Equilibrado"
        else:
            classificacao = "Doce"
        
        resultado['classificacao'] = classificacao
        
        # Registrar o cálculo no histórico
        registrar_historico_calculo('ratio', {
            'brix': brix,
            'acidez': acidez,
            'resultado': resultado
        })
        
        return jsonify(resultado)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'Erro de formato nos valores informados: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao calcular ratio: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Ocorreu um erro ao processar o cálculo.'
        }), 500


@calculos_bp.route('/api/calcular/acidez', methods=['POST'])
@login_required
def api_calcular_acidez():
    """API para cálculo padrão de acidez."""
    data = request.get_json()
    
    try:
        volume_amostra = float(data.get('volume_amostra', 0))
        fator_titulacao = float(data.get('fator_titulacao', 0))
        volume_naoh = float(data.get('volume_naoh', 0))
        
        # Validar dados
        if volume_amostra <= 0 or fator_titulacao <= 0 or volume_naoh < 0:
            return jsonify({
                'success': False,
                'message': 'Todos os valores devem ser positivos (volume NaOH pode ser zero).'
            }), 400
        
        # Cálculo da acidez
        acidez = (volume_naoh * fator_titulacao * 100) / volume_amostra
        
        resultado = {
            'success': True,
            'acidez': acidez,
            'volume_amostra': volume_amostra,
            'fator_titulacao': fator_titulacao,
            'volume_naoh': volume_naoh,
            'formula': f'Acidez (%) = ({volume_naoh} × {fator_titulacao} × 100) ÷ {volume_amostra} = {acidez:.4f}%'
        }
        
        # Registrar o cálculo no histórico
        registrar_historico_calculo('acidez', {
            'volume_amostra': volume_amostra,
            'fator_titulacao': fator_titulacao,
            'volume_naoh': volume_naoh,
            'resultado': resultado
        })
        
        return jsonify(resultado)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'Erro de formato nos valores informados: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao calcular acidez: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Ocorreu um erro ao processar o cálculo.'
        }), 500


@calculos_bp.route('/api/calcular/finalizacao-tanque', methods=['POST'])
@login_required
def api_calcular_finalizacao_tanque():
    """API para cálculo de finalização de tanque."""
    data = request.get_json()
    
    try:
        brix_atual = float(data.get('brix_atual', 0))
        brix_desejado = float(data.get('brix_desejado', 0))
        volume_atual = float(data.get('volume_atual', 0))
        tipo_ajuste = data.get('tipo_ajuste', 'diluicao')
        
        # Validações
        if brix_atual <= 0 or brix_desejado <= 0 or volume_atual <= 0:
            return jsonify({
                'success': False,
                'message': 'Todos os valores devem ser positivos.'
            }), 400
        
        resultado = {
            'success': True,
            'tipo_ajuste': tipo_ajuste,
            'brix_atual': brix_atual,
            'brix_desejado': brix_desejado,
            'volume_atual': volume_atual
        }
        
        # Cálculos específicos para cada tipo de ajuste
        if tipo_ajuste == 'diluicao':
            # Verificar se é possível diluir
            if brix_atual <= brix_desejado:
                resultado.update({
                    'possivel': False,
                    'mensagem': "O Brix atual já é menor ou igual ao desejado. Não é possível diluir.",
                    'formula': "Não aplicável"
                })
            else:
                # Fórmula: V2 = V1 * (B1 / B2 - 1)
                volume_agua = volume_atual * (brix_atual / brix_desejado - 1)
                volume_final = volume_atual + volume_agua
                
                resultado.update({
                    'possivel': True,
                    'volume_agua': volume_agua,
                    'volume_final': volume_final,
                    'reducao_brix': brix_atual - brix_desejado,
                    'formula': f"V2 = {volume_atual} × ({brix_atual} / {brix_desejado} - 1) = {volume_agua:.2f} L"
                })
                
        elif tipo_ajuste == 'concentracao':
            brix_concentrado = float(data.get('brix_concentrado', 65.0))
            
            # Verificar se é necessário concentrar
            if brix_atual >= brix_desejado:
                resultado.update({
                    'possivel': False,
                    'mensagem': "O Brix atual já é maior ou igual ao desejado. Não é necessário adicionar concentrado.",
                    'formula': "Não aplicável"
                })
            # Verificar se o concentrado é adequado
            elif brix_concentrado <= brix_desejado:
                resultado.update({
                    'possivel': False,
                    'mensagem': "O Brix do concentrado deve ser maior que o Brix desejado.",
                    'formula': "Não aplicável"
                })
            else:
                # Fórmula: V2 = V1 * (B2 - B1) / (B3 - B2)
                volume_concentrado = volume_atual * (brix_desejado - brix_atual) / (brix_concentrado - brix_desejado)
                volume_final = volume_atual + volume_concentrado
                
                resultado.update({
                    'possivel': True,
                    'volume_concentrado': volume_concentrado,
                    'volume_final': volume_final,
                    'aumento_brix': brix_desejado - brix_atual,
                    'brix_concentrado': brix_concentrado,
                    'formula': f"V2 = {volume_atual} × ({brix_desejado} - {brix_atual}) / ({brix_concentrado} - {brix_desejado}) = {volume_concentrado:.2f} L"
                })
        
        # Registrar cálculo no histórico
        registrar_historico_calculo('finalizacao-tanque', {
            'brix_atual': brix_atual,
            'brix_desejado': brix_desejado,
            'volume_atual': volume_atual,
            'tipo_ajuste': tipo_ajuste,
            'brix_concentrado': data.get('brix_concentrado') if tipo_ajuste == 'concentracao' else None,
            'resultado': resultado
        })
        
        return jsonify(resultado)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'Erro de formato nos valores informados: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao calcular finalização de tanque: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Ocorreu um erro ao processar o cálculo.'
        }), 500


@calculos_bp.route('/api/salvar-configuracao', methods=['POST'])
@login_required
def api_salvar_configuracao():
    """API para salvar configurações de fatores de conversão customizados."""
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
    data = request.get_json()
    
    try:
        categoria = data.get('categoria')
        subcategoria = data.get('subcategoria')
        valor = data.get('valor')
        
        if not categoria or not subcategoria or valor is None:
            return jsonify({
                'success': False,
                'message': 'Dados incompletos para salvar configuração.'
            }), 400
            
        # Atualizar o dicionário de fatores
        if categoria in FATORES_CONVERSAO:
            if isinstance(FATORES_CONVERSAO[categoria], dict):
                if subcategoria in FATORES_CONVERSAO[categoria]:
                    FATORES_CONVERSAO[categoria][subcategoria] = valor
                else:
                    FATORES_CONVERSAO[categoria][subcategoria] = valor
            else:
                FATORES_CONVERSAO[categoria] = {subcategoria: valor}
        else:
            FATORES_CONVERSAO[categoria] = {subcategoria: valor}
            
        # Salvar no arquivo de configuração
        with open(CONFIG_FILE, 'w') as f:
            json.dump(FATORES_CONVERSAO, f, indent=4)
            
        return jsonify({
            'success': True,
            'message': 'Configuração salva com sucesso'
        })
            
    except Exception as e:
        logging.error(f"Erro ao salvar configuração: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Ocorreu um erro ao salvar a configuração.'
        }), 500


@calculos_bp.route('/api/obter-configuracoes', methods=['GET'])
@login_required
def api_obter_configuracoes():
    """API para obter todas as configurações de fatores de conversão."""
    return jsonify({
        'success': True,
        'configuracoes': FATORES_CONVERSAO
    })


@calculos_bp.route('/historico')
@login_required
def historico_calculos():
    """Página de histórico de cálculos realizados."""
    return render_template('calculos/historico.html')


# Função auxiliar para registrar histórico de cálculos
def registrar_historico_calculo(tipo_calculo, dados):
    """
    Registra um cálculo no histórico para referência futura.
    Futuramente pode ser expandido para salvar no banco de dados.
    """
    # Por enquanto, apenas registra no log
    usuario = current_user.username if current_user.is_authenticated else "Anônimo"
    logging.info(f"Cálculo [{tipo_calculo}] realizado por {usuario}: {dados}")
    
    # Implementação futura: salvar no banco de dados
    # from app import db
    # from models import HistoricoCalculo
    # 
    # historico = HistoricoCalculo(
    #     tipo_calculo=tipo_calculo,
    #     usuario_id=current_user.id,
    #     dados=json.dumps(dados)
    # )
    # db.session.add(historico)
    # db.session.commit()