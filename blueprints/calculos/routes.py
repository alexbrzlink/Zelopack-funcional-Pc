from flask import render_template, jsonify, request
from flask_login import login_required

from . import calculos_bp


@calculos_bp.route('/')
@login_required
def index():
    """Página principal da seção de cálculos."""
    return render_template('calculos/index.html')


@calculos_bp.route('/api/calculate', methods=['POST'])
@login_required
def calculate():
    """Endpoint para realizar cálculos via API."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400
    
    tipo_calculo = data.get('tipo_calculo')
    
    try:
        if tipo_calculo == 'producao_200':
            # Cálculo de produção 200g
            peso_bruto = float(data.get('peso_bruto', 0))
            tara = float(data.get('tara', 0))
            
            if peso_bruto <= 0:
                return jsonify({'error': 'Peso bruto deve ser maior que zero'}), 400
            if tara < 0:
                return jsonify({'error': 'Tara não pode ser negativa'}), 400
                
            resultado = peso_bruto - tara
            
            return jsonify({
                'resultado': resultado,
                'unidade': 'g'
            })
            
        elif tipo_calculo == 'producao_litro':
            # Cálculo do volume com base na densidade
            peso = float(data.get('peso', 0))
            densidade = float(data.get('densidade', 0))
            
            if peso <= 0:
                return jsonify({'error': 'Peso deve ser maior que zero'}), 400
            if densidade <= 0:
                return jsonify({'error': 'Densidade deve ser maior que zero'}), 400
                
            # Volume = Massa / Densidade
            resultado = peso / densidade
            
            return jsonify({
                'resultado': resultado,
                'unidade': 'L'
            })
            
        elif tipo_calculo == 'abaixar_brix':
            # Cálculo para abaixar Brix
            brix_atual = float(data.get('brix_atual', 0))
            brix_desejado = float(data.get('brix_desejado', 0))
            volume_inicial = float(data.get('volume_inicial', 0))
            
            if brix_atual <= 0:
                return jsonify({'error': 'Brix atual deve ser maior que zero'}), 400
            if brix_desejado <= 0:
                return jsonify({'error': 'Brix desejado deve ser maior que zero'}), 400
            if brix_desejado >= brix_atual:
                return jsonify({'error': 'Brix desejado deve ser menor que o Brix atual'}), 400
            if volume_inicial <= 0:
                return jsonify({'error': 'Volume inicial deve ser maior que zero'}), 400
            
            # Fórmula: Volume de água a adicionar = (Volume inicial * Brix atual / Brix desejado) - Volume inicial
            resultado = (volume_inicial * brix_atual / brix_desejado) - volume_inicial
            
            return jsonify({
                'resultado': resultado,
                'unidade': 'L'
            })
            
        elif tipo_calculo == 'ratio':
            # Cálculo de ratio (Brix/Acidez)
            brix = float(data.get('brix', 0))
            acidez = float(data.get('acidez', 0))
            
            if brix <= 0:
                return jsonify({'error': 'Brix deve ser maior que zero'}), 400
            if acidez <= 0:
                return jsonify({'error': 'Acidez deve ser maior que zero'}), 400
                
            resultado = brix / acidez
            
            return jsonify({
                'resultado': resultado,
                'unidade': ''
            })
            
        else:
            return jsonify({'error': f'Tipo de cálculo não reconhecido: {tipo_calculo}'}), 400
            
    except ZeroDivisionError:
        return jsonify({'error': 'Divisão por zero não permitida'}), 400
    except ValueError as e:
        return jsonify({'error': f'Erro de valor: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao realizar cálculo: {str(e)}'}), 500