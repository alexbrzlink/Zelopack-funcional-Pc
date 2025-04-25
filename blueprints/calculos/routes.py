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


@calculos_bp.route('/api/calcular/brix-padrao', methods=['POST'])
@login_required
def api_calcular_brix_padrao():
    """API para cálculo de Brix Padrão com correção de temperatura."""
    data = request.get_json()
    
    try:
        brix_medido = float(data.get('brix_medido', 0))
        temperatura = float(data.get('temperatura', FATORES_CONVERSAO['brix']['temperatura_referencia']))
        fator_correcao = data.get('fator_correcao', 'standard')
        
        if fator_correcao == 'custom':
            fator = float(data.get('custom_factor', 1.0))
        else:
            fator = FATORES_CONVERSAO['brix']['fator_correcao'].get(fator_correcao, 1.0)
        
        # Validar dados
        if brix_medido <= 0:
            return jsonify({
                'success': False,
                'message': 'O valor de Brix medido deve ser positivo.'
            }), 400
        
        # Cálculo da correção de temperatura
        temp_ref = FATORES_CONVERSAO['brix']['temperatura_referencia']
        delta_temp = temperatura - temp_ref
        
        # Correção aproximada: a cada 1°C acima de 20°C, adicionar 0.06 ao Brix
        correcao_temp = delta_temp * 0.06
        
        # Aplicar correção de temperatura
        if temperatura != temp_ref:
            brix_corrigido_temp = (
                brix_medido - correcao_temp if temperatura > temp_ref 
                else brix_medido + abs(correcao_temp)
            )
        else:
            brix_corrigido_temp = brix_medido
        
        # Aplicar fator de correção do tipo de produto
        brix_final = brix_corrigido_temp * fator
        
        resultado = {
            'success': True,
            'brix_original': brix_medido,
            'brix_corrigido_temp': brix_corrigido_temp,
            'brix_final': brix_final,
            'correcao_aplicada': correcao_temp,
            'fator_aplicado': fator,
            'temp_ref': temp_ref,
            'temperatura': temperatura
        }
        
        # Registrar cálculo no histórico
        registrar_historico_calculo('brix-padrao', {
            'brix_medido': brix_medido,
            'temperatura': temperatura,
            'fator_correcao': fator_correcao,
            'fator_personalizado': fator if fator_correcao == 'custom' else None,
            'resultado': resultado
        })
        
        return jsonify(resultado)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'Erro de formato nos valores informados: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao calcular Brix padrão: {str(e)}")
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