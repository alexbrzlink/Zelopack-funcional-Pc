from flask import render_template, request, jsonify
from flask_login import login_required
from blueprints.calculos import calculos_bp

@calculos_bp.route('/')
@login_required
def index():
    """Página principal da seção de cálculos."""
    return render_template('calculos/index.html', title="Calculadora de Produção")

@calculos_bp.route('/api/calculate', methods=['POST'])
@login_required
def calculate():
    """Endpoint para realizar cálculos via API."""
    data = request.get_json()
    
    if not data or 'tipo_calculo' not in data:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    tipo_calculo = data.get('tipo_calculo')
    resultado = None
    
    try:
        # Processamento dos diferentes tipos de cálculos
        if tipo_calculo == 'producao_200':
            peso_bruto = float(data.get('peso_bruto', 0))
            tara = float(data.get('tara', 0))
            resultado = peso_bruto - tara
            
        elif tipo_calculo == 'producao_litro':
            peso = float(data.get('peso', 0))
            densidade = float(data.get('densidade', 1))
            resultado = peso / densidade
            
        elif tipo_calculo == 'abaixar_brix':
            brix_atual = float(data.get('brix_atual', 0))
            brix_desejado = float(data.get('brix_desejado', 1))
            volume_inicial = float(data.get('volume_inicial', 0))
            resultado = volume_inicial * ((brix_atual / brix_desejado) - 1)
            
        elif tipo_calculo == 'brix_corrigido':
            brix_medido = float(data.get('brix_medido', 0))
            fator = float(data.get('fator', 1))
            resultado = brix_medido * fator
            
        elif tipo_calculo == 'peso_bruto':
            peso_liquido = float(data.get('peso_liquido', 0))
            tara = float(data.get('tara', 0))
            resultado = peso_liquido + tara
            
        elif tipo_calculo == 'corantes':
            volume_total = float(data.get('volume_total', 0))
            dosagem = float(data.get('dosagem', 0))
            resultado = volume_total * dosagem
            
        elif tipo_calculo == 'densidade':
            massa = float(data.get('massa', 0))
            volume = float(data.get('volume', 1))
            resultado = massa / volume
            
        elif tipo_calculo == 'ratio':
            brix = float(data.get('brix', 0))
            acidez = float(data.get('acidez', 1))
            resultado = brix / acidez
            
        elif tipo_calculo == 'acidez':
            volume_amostra = float(data.get('volume_amostra', 1))
            fator = float(data.get('fator', 0))
            volume_naoh = float(data.get('volume_naoh', 0))
            resultado = (volume_naoh * fator * 100) / volume_amostra
            
        elif tipo_calculo == 'calculo_soda':
            acidez_inicial = float(data.get('acidez_inicial', 0))
            acidez_final = float(data.get('acidez_final', 0))
            volume = float(data.get('volume', 0))
            fator = float(data.get('fator', 1))
            resultado = (acidez_final - acidez_inicial) * volume * fator
            
        elif tipo_calculo == 'vitamina_c':
            volume_reagente = float(data.get('volume_reagente', 0))
            fator_reagente = float(data.get('fator_reagente', 0))
            volume_amostra = float(data.get('volume_amostra', 1))
            resultado = (volume_reagente * fator_reagente) / volume_amostra
            
        elif tipo_calculo == 'perda_base':
            peso_inicial = float(data.get('peso_inicial', 0))
            peso_final = float(data.get('peso_final', 0))
            resultado = ((peso_inicial - peso_final) / peso_inicial) * 100
            
        elif tipo_calculo == 'acucar_puxar':
            brix_atual = float(data.get('brix_atual', 0))
            brix_desejado = float(data.get('brix_desejado', 0))
            volume = float(data.get('volume', 0))
            resultado = (brix_desejado - brix_atual) * volume * 10
            
        elif tipo_calculo == 'aumentar_acidez':
            acidez_atual = float(data.get('acidez_atual', 0))
            acidez_desejada = float(data.get('acidez_desejada', 0))
            volume = float(data.get('volume', 0))
            resultado = (acidez_desejada - acidez_atual) * volume
            
        elif tipo_calculo == 'diminuir_acidez':
            acidez_atual = float(data.get('acidez_atual', 0))
            acidez_desejada = float(data.get('acidez_desejada', 0))
            volume = float(data.get('volume', 0))
            # Fórmula baseada no fator de diluição
            fator_diluicao = acidez_desejada / acidez_atual
            resultado = volume * ((1 / fator_diluicao) - 1)
            
        elif tipo_calculo == 'conversao_acucar':
            tipo_conversao = data.get('tipo_conversao', 'cristal_para_liquido')
            quantidade = float(data.get('quantidade', 0))
            
            if tipo_conversao == 'cristal_para_liquido':
                # Fator de conversão aproximado
                resultado = quantidade * 0.85  # Valor exemplo, ajustar conforme necessidade
            else:  # liquido_para_cristal
                resultado = quantidade / 0.85  # Valor exemplo, ajustar conforme necessidade
                
        elif tipo_calculo == 'zeragem_embalagem':
            pesos = data.get('pesos', [])
            if not pesos:
                return jsonify({'error': 'Lista de pesos vazia'}), 400
            
            pesos_float = [float(p) for p in pesos]
            resultado = sum(pesos_float) / len(pesos_float)
            
        elif tipo_calculo == 'ratio_brix':
            brix1 = float(data.get('brix1', 0))
            brix2 = float(data.get('brix2', 1))
            resultado = brix1 / brix2
            
        elif tipo_calculo == 'ratio_acidez':
            acidez1 = float(data.get('acidez1', 0))
            acidez2 = float(data.get('acidez2', 1))
            resultado = acidez1 / acidez2
            
        elif tipo_calculo == 'soda_dosagem':
            volume_tanque = float(data.get('volume_tanque', 0))
            dosagem = float(data.get('dosagem', 0))
            resultado = volume_tanque * dosagem
            
        elif tipo_calculo == 'acido_dosagem':
            volume_lote = float(data.get('volume_lote', 0))
            dosagem = float(data.get('dosagem', 0))
            resultado = volume_lote * dosagem
            
        elif tipo_calculo == 'aumentar_brix_acucar_batido':
            brix_atual = float(data.get('brix_atual', 0))
            brix_desejado = float(data.get('brix_desejado', 0))
            volume_lote = float(data.get('volume_lote', 0))
            concentracao = float(data.get('concentracao', 100))
            
            # Calcular baseado na diferença de Brix e concentração da solução
            delta_brix = brix_desejado - brix_atual
            resultado = (delta_brix * volume_lote * 10) / (concentracao / 100)
            
        elif tipo_calculo == 'previsao_brix':
            volume1 = float(data.get('volume1', 0))
            brix1 = float(data.get('brix1', 0))
            volume2 = float(data.get('volume2', 0))
            brix2 = float(data.get('brix2', 0))
            
            resultado = (brix1 * volume1 + brix2 * volume2) / (volume1 + volume2)
            
        elif tipo_calculo == 'previsao_acidez':
            volume1 = float(data.get('volume1', 0))
            acidez1 = float(data.get('acidez1', 0))
            volume2 = float(data.get('volume2', 0))
            acidez2 = float(data.get('acidez2', 0))
            
            resultado = (acidez1 * volume1 + acidez2 * volume2) / (volume1 + volume2)
            
        elif tipo_calculo == 'tempo_finalizacao':
            volume_total = float(data.get('volume_total', 0))
            vazao = float(data.get('vazao', 1))
            resultado = volume_total / vazao
            
        elif tipo_calculo == 'correcao_brix':
            brix_atual = float(data.get('brix_atual', 0))
            brix_desejado = float(data.get('brix_desejado', 0))
            volume_inicial = float(data.get('volume_inicial', 0))
            
            if brix_atual > brix_desejado:
                # Abaixar Brix com água
                resultado = volume_inicial * ((brix_atual / brix_desejado) - 1)
            else:
                # Aumentar Brix (aproximação)
                resultado = (brix_desejado - brix_atual) * volume_inicial * 0.01
                
        elif tipo_calculo == 'correcao_acucar_cristal':
            brix_atual = float(data.get('brix_atual', 0))
            brix_alvo = float(data.get('brix_alvo', 0))
            volume = float(data.get('volume', 0))
            
            resultado = (brix_alvo - brix_atual) * volume * 10
            
        elif tipo_calculo == 'peso_liquido_200':
            peso_bruto = float(data.get('peso_bruto', 0))
            tara = float(data.get('tara', 0))
            resultado = peso_bruto - tara
            
        elif tipo_calculo == 'peso_liquido_litro':
            volume = float(data.get('volume', 0))
            densidade = float(data.get('densidade', 1))
            resultado = volume * densidade
            
        else:
            return jsonify({'error': 'Tipo de cálculo não suportado'}), 400
        
        return jsonify({
            'resultado': round(resultado, 4),
            'tipo_calculo': tipo_calculo
        })
    
    except Exception as e:
        return jsonify({'error': f'Erro ao calcular: {str(e)}'}), 500