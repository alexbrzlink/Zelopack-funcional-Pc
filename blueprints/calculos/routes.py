from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
import os
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Importar o blueprint do arquivo __init__.py
from . import calculos_bp

# Carregar configurações de fatores de conversão de um arquivo JSON
def load_conversion_factors():
    try:
        factors_path = os.path.join(os.path.dirname(__file__), 'conversion_factors.json')
        if os.path.exists(factors_path):
            with open(factors_path, 'r', encoding='utf-8') as f:
                factors = json.load(f)
            return factors
        else:
            # Valores padrão se o arquivo não existir
            return {
                "cristal_to_liquido": 0.85,  # 1kg de açúcar cristal equivale a 0.85L de açúcar líquido
                "liquido_to_cristal": 1.18,  # 1L de açúcar líquido equivale a 1.18kg de açúcar cristal
                "acido_citrico_fator": 1.0,  # Fator para ácido cítrico na correção de acidez
                "brix_correcao_temp": {
                    "20": 1.000,  # Fatores de correção de Brix por temperatura
                    "25": 0.990,
                    "30": 0.980
                }
            }
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar fatores de conversão: {e}")
        return {
            "cristal_to_liquido": 0.85,
            "liquido_to_cristal": 1.18,
            "acido_citrico_fator": 1.0,
            "brix_correcao_temp": {"20": 1.000, "25": 0.990, "30": 0.980}
        }

@calculos_bp.route('/')
@login_required
def index():
    """Página principal da seção de cálculos."""
    return render_template('calculos/index.html')

@calculos_bp.route('/api/calculate', methods=['POST'])
@login_required
def calculate():
    """API para processar os diferentes tipos de cálculos."""
    try:
        data = request.json
        tipo_calculo = data.get('tipo_calculo')
        
        # Carregar fatores de conversão
        factors = load_conversion_factors()
        
        if tipo_calculo == 'producao_200':
            peso_bruto = float(data.get('peso_bruto', 0))
            tara = float(data.get('tara', 0))
            
            # Verificar se as unidades estão corretas (ambos em gramas)
            if peso_bruto < tara:
                return jsonify({'error': 'O peso bruto deve ser maior que a tara!'})
                
            peso_liquido = peso_bruto - tara
            return jsonify({'resultado': peso_liquido})
            
        elif tipo_calculo == 'producao_litro':
            peso = float(data.get('peso', 0))
            densidade = float(data.get('densidade', 0))
            
            if densidade <= 0:
                return jsonify({'error': 'A densidade deve ser maior que zero!'})
                
            volume = peso / densidade
            return jsonify({'resultado': volume})
            
        elif tipo_calculo == 'abaixar_brix':
            brix_atual = float(data.get('brix_atual', 0))
            brix_desejado = float(data.get('brix_desejado', 0))
            volume_inicial = float(data.get('volume_inicial', 0))
            
            if brix_desejado >= brix_atual:
                return jsonify({'error': 'O Brix desejado deve ser menor que o Brix atual!'})
                
            if brix_desejado <= 0:
                return jsonify({'error': 'O Brix desejado deve ser maior que zero!'})
                
            agua_adicionar = volume_inicial * ((brix_atual / brix_desejado) - 1)
            return jsonify({'resultado': agua_adicionar})
            
        elif tipo_calculo == 'ratio':
            brix = float(data.get('brix', 0))
            acidez = float(data.get('acidez', 0))
            
            if acidez <= 0:
                return jsonify({'error': 'A acidez deve ser maior que zero!'})
                
            ratio = brix / acidez
            return jsonify({'resultado': ratio})
            
        elif tipo_calculo == 'diluicao':
            conc_inicial = float(data.get('conc_inicial', 0))
            vol_inicial = float(data.get('vol_inicial', 0))
            vol_final = float(data.get('vol_final', 0))
            unidade = data.get('unidade', '%')
            
            if vol_final <= vol_inicial:
                return jsonify({'error': 'O volume final deve ser maior que o volume inicial!'})
                
            # C1 * V1 = C2 * V2
            conc_final = (conc_inicial * vol_inicial) / vol_final
            return jsonify({'resultado': conc_final})
            
        elif tipo_calculo == 'conversao':
            valor = float(data.get('valor', 0))
            de = data.get('de', '')
            para = data.get('para', '')
            
            # Conversão de volume
            if de == 'volume':
                if para == 'mL' and de == 'L':
                    resultado = valor * 1000
                elif para == 'L' and de == 'mL':
                    resultado = valor / 1000
                elif para == 'm3' and de == 'L':
                    resultado = valor / 1000
                elif para == 'L' and de == 'm3':
                    resultado = valor * 1000
                elif para == 'gal' and de == 'L':
                    resultado = valor / 3.78541
                elif para == 'L' and de == 'gal':
                    resultado = valor * 3.78541
                else:
                    return jsonify({'error': 'Conversão de volume não suportada!'})
                    
            # Conversão de massa
            elif de == 'massa':
                if para == 'g' and de == 'mg':
                    resultado = valor / 1000
                elif para == 'mg' and de == 'g':
                    resultado = valor * 1000
                elif para == 'kg' and de == 'g':
                    resultado = valor / 1000
                elif para == 'g' and de == 'kg':
                    resultado = valor * 1000
                elif para == 'ton' and de == 'kg':
                    resultado = valor / 1000
                elif para == 'kg' and de == 'ton':
                    resultado = valor * 1000
                else:
                    return jsonify({'error': 'Conversão de massa não suportada!'})
                    
            # Conversão de temperatura
            elif de == 'temperatura':
                if para == 'F' and de == 'C':
                    resultado = (valor * 9/5) + 32
                elif para == 'C' and de == 'F':
                    resultado = (valor - 32) * 5/9
                elif para == 'K' and de == 'C':
                    resultado = valor + 273.15
                elif para == 'C' and de == 'K':
                    resultado = valor - 273.15
                else:
                    return jsonify({'error': 'Conversão de temperatura não suportada!'})
                    
            # Conversão de concentração
            elif de == 'concentracao':
                if para == 'ppb' and de == 'ppm':
                    resultado = valor * 1000
                elif para == 'ppm' and de == 'ppb':
                    resultado = valor / 1000
                elif para == 'ppm' and de == 'mgL':
                    resultado = valor
                elif para == 'mgL' and de == 'ppm':
                    resultado = valor
                elif para == 'gL' and de == 'mgL':
                    resultado = valor / 1000
                elif para == 'mgL' and de == 'gL':
                    resultado = valor * 1000
                elif para == 'perc' and de == 'ppm':
                    resultado = valor / 10000
                elif para == 'ppm' and de == 'perc':
                    resultado = valor * 10000
                else:
                    return jsonify({'error': 'Conversão de concentração não suportada!'})
            else:
                return jsonify({'error': 'Tipo de conversão não suportado!'})
                
            return jsonify({'resultado': resultado})
            
        elif tipo_calculo == 'rendimento':
            entrada = float(data.get('entrada', 0))
            saida = float(data.get('saida', 0))
            
            if entrada <= 0:
                return jsonify({'error': 'O valor de entrada deve ser maior que zero!'})
                
            rendimento = (saida / entrada) * 100
            return jsonify({'resultado': rendimento})
            
        elif tipo_calculo == 'consumo':
            quantidade_insumo = float(data.get('quantidade_insumo', 0))
            unidades_produzidas = int(data.get('unidades_produzidas', 0))
            
            if unidades_produzidas <= 0:
                return jsonify({'error': 'O número de unidades deve ser maior que zero!'})
                
            consumo_por_unidade = quantidade_insumo / unidades_produzidas
            return jsonify({'resultado': consumo_por_unidade})
            
        elif tipo_calculo == 'solucao':
            concentracao = float(data.get('concentracao', 0))
            volume = float(data.get('volume', 0))
            tipo_solucao = data.get('tipo_solucao', 'massa')
            
            # Verificar se é uma solução m/v (massa/volume) ou v/v (volume/volume)
            if tipo_solucao == 'massa':
                # Para soluções m/v (ex: g/mL)
                # Concentração em % significa g de soluto em 100 mL de solução
                soluto = (concentracao * volume) / 100
                return jsonify({'resultado': soluto})
            else:
                # Para soluções v/v (ex: mL/mL)
                # Concentração em % significa mL de soluto em 100 mL de solução
                soluto = (concentracao * volume) / 100
                return jsonify({'resultado': soluto})
                
        elif tipo_calculo == 'ratio_fruta':
            tipo_fruta = data.get('tipo_fruta', 'laranja')
            brix = float(data.get('brix', 0))
            acidez = float(data.get('acidez', 0))
            
            if acidez <= 0:
                return jsonify({'error': 'A acidez deve ser maior que zero!'})
            
            ratio = brix / acidez
            
            # Classificação baseada no tipo de fruta e seu ratio
            classificacao = ""
            status = ""
            
            if tipo_fruta == 'laranja':
                if ratio < 8:
                    classificacao = "Baixo - Muito ácida"
                    status = "text-danger"
                elif ratio >= 8 and ratio < 12:
                    classificacao = "Ideal - Bom equilíbrio"
                    status = "text-success"
                elif ratio >= 12 and ratio < 18:
                    classificacao = "Alto - Pouco ácida"
                    status = "text-warning"
                else:
                    classificacao = "Muito alto - Excessivamente doce"
                    status = "text-danger"
            elif tipo_fruta == 'uva':
                if ratio < 15:
                    classificacao = "Baixo - Muito ácida"
                    status = "text-danger"
                elif ratio >= 15 and ratio < 25:
                    classificacao = "Ideal - Bom equilíbrio"
                    status = "text-success"
                elif ratio >= 25 and ratio < 35:
                    classificacao = "Alto - Pouco ácida"
                    status = "text-warning"
                else:
                    classificacao = "Muito alto - Excessivamente doce"
                    status = "text-danger"
            elif tipo_fruta == 'maca':
                if ratio < 20:
                    classificacao = "Baixo - Muito ácida"
                    status = "text-danger"
                elif ratio >= 20 and ratio < 30:
                    classificacao = "Ideal - Bom equilíbrio"
                    status = "text-success"
                elif ratio >= 30 and ratio < 40:
                    classificacao = "Alto - Pouco ácida"
                    status = "text-warning"
                else:
                    classificacao = "Muito alto - Excessivamente doce"
                    status = "text-danger"
            elif tipo_fruta == 'abacaxi':
                if ratio < 10:
                    classificacao = "Baixo - Muito ácida"
                    status = "text-danger"
                elif ratio >= 10 and ratio < 20:
                    classificacao = "Ideal - Bom equilíbrio"
                    status = "text-success"
                elif ratio >= 20 and ratio < 30:
                    classificacao = "Alto - Pouco ácida"
                    status = "text-warning"
                else:
                    classificacao = "Muito alto - Excessivamente doce"
                    status = "text-danger"
            else:  # manga e outros
                if ratio < 30:
                    classificacao = "Baixo - Muito ácida"
                    status = "text-danger"
                elif ratio >= 30 and ratio < 60:
                    classificacao = "Ideal - Bom equilíbrio"
                    status = "text-success"
                elif ratio >= 60 and ratio < 90:
                    classificacao = "Alto - Pouco ácida"
                    status = "text-warning"
                else:
                    classificacao = "Muito alto - Excessivamente doce"
                    status = "text-danger"
                    
            return jsonify({
                'resultado': ratio,
                'classificacao': classificacao,
                'status': status
            })
            
        elif tipo_calculo == 'correcao_acidez':
            acidez_atual = float(data.get('acidez_atual', 0))
            acidez_desejada = float(data.get('acidez_desejada', 0))
            volume_suco = float(data.get('volume_suco', 0))
            
            if acidez_atual <= acidez_desejada:
                return jsonify({'error': 'A acidez atual deve ser maior que a acidez desejada!'})
            
            # Fator de conversão para ácido cítrico
            fator_acido = factors["acido_citrico_fator"]
            
            # Cálculo da quantidade de ácido cítrico necessária (em gramas)
            acido_necessario = (acidez_desejada - acidez_atual) * volume_suco * fator_acido
            
            return jsonify({'resultado': abs(acido_necessario)})
            
        elif tipo_calculo == 'pasteurizacao':
            temperatura = float(data.get('temperatura', 0))
            tempo = float(data.get('tempo', 0))
            
            # Fórmula para Unidades de Pasteurização (PU)
            # PU = t × 1.393^(T-60), onde t = tempo em minutos, T = temperatura em °C
            if temperatura < 60:
                return jsonify({'error': 'A temperatura deve ser maior ou igual a 60°C!'})
                
            pu = tempo * (1.393 ** (temperatura - 60))
            return jsonify({'resultado': pu})
            
        elif tipo_calculo == 'formulacao':
            tipo_bebida = data.get('tipo_bebida', 'nectar')
            volume = float(data.get('volume', 0))
            
            resultado = {
                'ingredientes': []
            }
            
            if tipo_bebida == 'nectar':
                resultado['ingredientes'] = [
                    {'nome': 'Polpa de fruta', 'quantidade': volume * 0.3, 'unidade': 'L'},
                    {'nome': 'Água', 'quantidade': volume * 0.58, 'unidade': 'L'},
                    {'nome': 'Açúcar', 'quantidade': volume * 0.12, 'unidade': 'kg'},
                    {'nome': 'Ácido cítrico', 'quantidade': volume * 0.002, 'unidade': 'kg'},
                ]
            elif tipo_bebida == 'refresco':
                resultado['ingredientes'] = [
                    {'nome': 'Polpa de fruta', 'quantidade': volume * 0.15, 'unidade': 'L'},
                    {'nome': 'Água', 'quantidade': volume * 0.75, 'unidade': 'L'},
                    {'nome': 'Açúcar', 'quantidade': volume * 0.10, 'unidade': 'kg'},
                    {'nome': 'Ácido cítrico', 'quantidade': volume * 0.001, 'unidade': 'kg'},
                ]
            elif tipo_bebida == 'suco':
                resultado['ingredientes'] = [
                    {'nome': 'Polpa de fruta', 'quantidade': volume * 0.98, 'unidade': 'L'},
                    {'nome': 'Água', 'quantidade': volume * 0.02, 'unidade': 'L'},
                    {'nome': 'Conservantes', 'quantidade': volume * 0.0005, 'unidade': 'kg'},
                ]
                
            return jsonify(resultado)
            
        elif tipo_calculo == 'perda_base':
            peso_inicial = float(data.get('peso_inicial', 0))
            peso_final = float(data.get('peso_final', 0))
            
            if peso_inicial <= 0:
                return jsonify({'error': 'O peso inicial deve ser maior que zero!'})
                
            perda = ((peso_inicial - peso_final) / peso_inicial) * 100
            return jsonify({'resultado': perda})
            
        elif tipo_calculo == 'acidez':
            volume_amostra = float(data.get('volume_amostra', 0))
            fator_titulacao = float(data.get('fator_titulacao', 0))
            volume_naoh = float(data.get('volume_naoh', 0))
            
            if volume_amostra <= 0:
                return jsonify({'error': 'O volume da amostra deve ser maior que zero!'})
                
            acidez = (volume_naoh * fator_titulacao * 100) / volume_amostra
            return jsonify({'resultado': acidez})
            
        elif tipo_calculo == 'densidade':
            massa = float(data.get('massa', 0))
            volume = float(data.get('volume', 0))
            
            if volume <= 0:
                return jsonify({'error': 'O volume deve ser maior que zero!'})
                
            densidade = massa / volume
            return jsonify({'resultado': densidade})
            
        elif tipo_calculo == 'vitc':
            volume_reagente = float(data.get('volume_reagente', 0))
            fator_reagente = float(data.get('fator_reagente', 0))
            volume_amostra = float(data.get('volume_amostra', 0))
            
            if volume_amostra <= 0:
                return jsonify({'error': 'O volume da amostra deve ser maior que zero!'})
                
            vitamina_c = (volume_reagente * fator_reagente) / volume_amostra
            return jsonify({'resultado': vitamina_c})
            
        elif tipo_calculo == 'brix_corrigido':
            brix_medido = float(data.get('brix_medido', 0))
            temperatura = float(data.get('temperatura', 20))
            
            # Obter o fator de correção para a temperatura
            temp_key = str(int(temperatura))
            fator = factors.get('brix_correcao_temp', {}).get(temp_key, 1.0)
            
            brix_corrigido = brix_medido * fator
            return jsonify({'resultado': brix_corrigido})
            
        elif tipo_calculo == 'peso_bruto':
            peso_liquido = float(data.get('peso_liquido', 0))
            tara = float(data.get('tara', 0))
            
            peso_bruto = peso_liquido + tara
            return jsonify({'resultado': peso_bruto})
            
        elif tipo_calculo == 'corantes':
            volume_total = float(data.get('volume_total', 0))
            dosagem = float(data.get('dosagem', 0))
            
            corante = volume_total * dosagem
            return jsonify({'resultado': corante})
            
        elif tipo_calculo == 'aumento_brix':
            brix_atual = float(data.get('brix_atual', 0))
            brix_desejado = float(data.get('brix_desejado', 0))
            volume = float(data.get('volume', 0))
            
            if brix_atual >= brix_desejado:
                return jsonify({'error': 'O Brix desejado deve ser maior que o Brix atual!'})
                
            # Quantidade de açúcar em kg para aumentar o Brix
            # 1 kg de açúcar em 10L de água aumenta o Brix em 1°
            acucar = (brix_desejado - brix_atual) * volume / 10
            return jsonify({'resultado': acucar})
            
        elif tipo_calculo == 'aumento_acidez':
            acidez_atual = float(data.get('acidez_atual', 0))
            acidez_desejada = float(data.get('acidez_desejada', 0))
            volume = float(data.get('volume', 0))
            
            if acidez_atual >= acidez_desejada:
                return jsonify({'error': 'A acidez desejada deve ser maior que a acidez atual!'})
                
            # Fator de conversão para ácido cítrico
            fator_acido = factors["acido_citrico_fator"]
            
            acido = (acidez_desejada - acidez_atual) * volume * fator_acido
            return jsonify({'resultado': acido})
            
        elif tipo_calculo == 'cristal_liquido':
            tipo_conversao = data.get('tipo_conversao', 'cristal_to_liquido')
            quantidade = float(data.get('quantidade', 0))
            
            if tipo_conversao == 'cristal_to_liquido':
                # Converter de açúcar cristal para açúcar líquido
                fator = factors["cristal_to_liquido"]
                resultado = quantidade * fator
                unidade = 'L'
            else:
                # Converter de açúcar líquido para açúcar cristal
                fator = factors["liquido_to_cristal"]
                resultado = quantidade * fator
                unidade = 'kg'
                
            return jsonify({'resultado': resultado, 'unidade': unidade})
            
        elif tipo_calculo == 'previsao_brix':
            volume1 = float(data.get('volume1', 0))
            brix1 = float(data.get('brix1', 0))
            volume2 = float(data.get('volume2', 0))
            brix2 = float(data.get('brix2', 0))
            
            if (volume1 + volume2) <= 0:
                return jsonify({'error': 'A soma dos volumes deve ser maior que zero!'})
                
            brix_final = (brix1 * volume1 + brix2 * volume2) / (volume1 + volume2)
            return jsonify({'resultado': brix_final})
            
        elif tipo_calculo == 'previsao_acidez':
            volume1 = float(data.get('volume1', 0))
            acidez1 = float(data.get('acidez1', 0))
            volume2 = float(data.get('volume2', 0))
            acidez2 = float(data.get('acidez2', 0))
            
            if (volume1 + volume2) <= 0:
                return jsonify({'error': 'A soma dos volumes deve ser maior que zero!'})
                
            acidez_final = (acidez1 * volume1 + acidez2 * volume2) / (volume1 + volume2)
            return jsonify({'resultado': acidez_final})
            
        elif tipo_calculo == 'tempo_finalizacao':
            volume_total = float(data.get('volume_total', 0))
            vazao = float(data.get('vazao', 0))
            
            if vazao <= 0:
                return jsonify({'error': 'A vazão deve ser maior que zero!'})
                
            tempo = volume_total / vazao
            return jsonify({'resultado': tempo})
            
        elif tipo_calculo == 'zeragem_embalagem':
            pesos = data.get('pesos', [])
            
            if not pesos or len(pesos) == 0:
                return jsonify({'error': 'É necessário informar pelo menos um peso!'})
                
            pesos = [float(p) for p in pesos if p]
            tara_media = sum(pesos) / len(pesos)
            return jsonify({'resultado': tara_media})
        
        else:
            return jsonify({'error': 'Tipo de cálculo não reconhecido!'})
            
    except Exception as e:
        current_app.logger.error(f"Erro no cálculo: {e}")
        return jsonify({'error': f'Erro ao processar o cálculo: {str(e)}'})

# API para obter os fatores de conversão atuais
@calculos_bp.route('/api/conversion_factors', methods=['GET'])
@login_required
def get_conversion_factors():
    """Retorna os fatores de conversão atuais."""
    factors = load_conversion_factors()
    return jsonify(factors)

# API para atualizar os fatores de conversão
@calculos_bp.route('/api/conversion_factors', methods=['POST'])
@login_required
def update_conversion_factors():
    """Atualiza os fatores de conversão."""
    try:
        data = request.json
        factors_path = os.path.join(os.path.dirname(__file__), 'conversion_factors.json')
        
        with open(factors_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        return jsonify({'success': True, 'message': 'Fatores de conversão atualizados com sucesso!'})
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar fatores de conversão: {e}")
        return jsonify({'success': False, 'error': f'Erro ao atualizar fatores de conversão: {str(e)}'})