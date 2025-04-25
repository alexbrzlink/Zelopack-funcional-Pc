from flask import render_template, jsonify, request
from flask_login import login_required
import math

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
                
            # Fórmula: Peso Líquido = Peso Bruto - Tara
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
                
            # Fórmula: Volume = Massa / Densidade
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
                
            # Fórmula: Ratio = Brix / Acidez
            resultado = brix / acidez
            
            return jsonify({
                'resultado': resultado,
                'unidade': ''
            })
            
        elif tipo_calculo == 'diluicao':
            # Cálculo para diluição de soluções
            conc_inicial = float(data.get('conc_inicial', 0))
            vol_inicial = float(data.get('vol_inicial', 0))
            vol_final = float(data.get('vol_final', 0))
            unidade = data.get('unidade', '%')
            
            if conc_inicial <= 0:
                return jsonify({'error': 'Concentração inicial deve ser maior que zero'}), 400
            if vol_inicial <= 0:
                return jsonify({'error': 'Volume inicial deve ser maior que zero'}), 400
            if vol_final <= 0:
                return jsonify({'error': 'Volume final deve ser maior que zero'}), 400
            if vol_final < vol_inicial:
                return jsonify({'error': 'Volume final deve ser maior ou igual ao volume inicial'}), 400
                
            # Fórmula: C1 * V1 = C2 * V2, portanto C2 = (C1 * V1) / V2
            resultado = (conc_inicial * vol_inicial) / vol_final
            
            return jsonify({
                'resultado': resultado,
                'unidade': unidade
            })
            
        elif tipo_calculo == 'conversao':
            # Conversão de unidades
            valor = float(data.get('valor', 0))
            de = data.get('de', '')
            para = data.get('para', '')
            
            if valor < 0 and de != 'temperatura':
                return jsonify({'error': 'Valor não pode ser negativo para esta conversão'}), 400
                
            resultado = 0
            
            # Conversão de volume
            if de == 'volume':
                # Converter tudo para mililitros primeiro
                valor_ml = 0
                
                if para == 'mL':
                    if para == 'mL':  # mL para mL
                        return jsonify({'resultado': valor, 'unidade': 'mL'})
                    elif para == 'L':  # mL para L
                        resultado = valor / 1000
                    elif para == 'm3':  # mL para m³
                        resultado = valor / 1000000
                    elif para == 'gal':  # mL para galões (US)
                        resultado = valor / 3785.41
                
                elif para == 'L':
                    valor_ml = valor * 1000  # L para mL
                    
                    if para == 'mL':  # L para mL
                        resultado = valor_ml
                    elif para == 'L':  # L para L
                        return jsonify({'resultado': valor, 'unidade': 'L'})
                    elif para == 'm3':  # L para m³
                        resultado = valor / 1000
                    elif para == 'gal':  # L para galões (US)
                        resultado = valor / 3.78541
                
                elif para == 'm3':
                    valor_ml = valor * 1000000  # m³ para mL
                    
                    if para == 'mL':  # m³ para mL
                        resultado = valor_ml
                    elif para == 'L':  # m³ para L
                        resultado = valor * 1000
                    elif para == 'm3':  # m³ para m³
                        return jsonify({'resultado': valor, 'unidade': 'm³'})
                    elif para == 'gal':  # m³ para galões (US)
                        resultado = valor * 264.172
                
                elif para == 'gal':
                    valor_ml = valor * 3785.41  # galões para mL
                    
                    if para == 'mL':  # galões para mL
                        resultado = valor_ml
                    elif para == 'L':  # galões para L
                        resultado = valor * 3.78541
                    elif para == 'm3':  # galões para m³
                        resultado = valor * 0.00378541
                    elif para == 'gal':  # galões para galões
                        return jsonify({'resultado': valor, 'unidade': 'gal'})
            
            # Conversão de massa
            elif de == 'massa':
                # Converter tudo para gramas primeiro
                valor_g = 0
                
                if para == 'mg':
                    valor_g = valor / 1000  # mg para g
                    
                    if para == 'mg':  # mg para mg
                        return jsonify({'resultado': valor, 'unidade': 'mg'})
                    elif para == 'g':  # mg para g
                        resultado = valor / 1000
                    elif para == 'kg':  # mg para kg
                        resultado = valor / 1000000
                    elif para == 'ton':  # mg para ton
                        resultado = valor / 1000000000
                
                elif para == 'g':
                    valor_g = valor  # g para g
                    
                    if para == 'mg':  # g para mg
                        resultado = valor * 1000
                    elif para == 'g':  # g para g
                        return jsonify({'resultado': valor, 'unidade': 'g'})
                    elif para == 'kg':  # g para kg
                        resultado = valor / 1000
                    elif para == 'ton':  # g para ton
                        resultado = valor / 1000000
                
                elif para == 'kg':
                    valor_g = valor * 1000  # kg para g
                    
                    if para == 'mg':  # kg para mg
                        resultado = valor_g * 1000
                    elif para == 'g':  # kg para g
                        resultado = valor_g
                    elif para == 'kg':  # kg para kg
                        return jsonify({'resultado': valor, 'unidade': 'kg'})
                    elif para == 'ton':  # kg para ton
                        resultado = valor / 1000
                
                elif para == 'ton':
                    valor_g = valor * 1000000  # ton para g
                    
                    if para == 'mg':  # ton para mg
                        resultado = valor_g * 1000
                    elif para == 'g':  # ton para g
                        resultado = valor_g
                    elif para == 'kg':  # ton para kg
                        resultado = valor * 1000
                    elif para == 'ton':  # ton para ton
                        return jsonify({'resultado': valor, 'unidade': 'ton'})
            
            # Conversão de temperatura
            elif de == 'temperatura':
                if para == 'C':
                    if para == 'C':  # °C para °C
                        return jsonify({'resultado': valor, 'unidade': '°C'})
                    elif para == 'F':  # °C para °F
                        resultado = (valor * 9/5) + 32
                    elif para == 'K':  # °C para K
                        resultado = valor + 273.15
                
                elif para == 'F':
                    if para == 'C':  # °F para °C
                        resultado = (valor - 32) * 5/9
                    elif para == 'F':  # °F para °F
                        return jsonify({'resultado': valor, 'unidade': '°F'})
                    elif para == 'K':  # °F para K
                        resultado = (valor - 32) * 5/9 + 273.15
                
                elif para == 'K':
                    if para == 'C':  # K para °C
                        resultado = valor - 273.15
                    elif para == 'F':  # K para °F
                        resultado = (valor - 273.15) * 9/5 + 32
                    elif para == 'K':  # K para K
                        return jsonify({'resultado': valor, 'unidade': 'K'})
            
            # Conversão de concentração
            elif de == 'concentracao':
                if para == 'ppm':
                    if para == 'ppm':  # ppm para ppm
                        return jsonify({'resultado': valor, 'unidade': 'ppm'})
                    elif para == 'ppb':  # ppm para ppb
                        resultado = valor * 1000
                    elif para == 'mgL':  # ppm para mg/L (equivalente)
                        resultado = valor
                    elif para == 'gL':  # ppm para g/L
                        resultado = valor / 1000
                    elif para == 'perc':  # ppm para %
                        resultado = valor / 10000
                
                elif para == 'ppb':
                    if para == 'ppm':  # ppb para ppm
                        resultado = valor / 1000
                    elif para == 'ppb':  # ppb para ppb
                        return jsonify({'resultado': valor, 'unidade': 'ppb'})
                    elif para == 'mgL':  # ppb para mg/L
                        resultado = valor / 1000
                    elif para == 'gL':  # ppb para g/L
                        resultado = valor / 1000000
                    elif para == 'perc':  # ppb para %
                        resultado = valor / 10000000
                
                elif para == 'mgL':
                    if para == 'ppm':  # mg/L para ppm (equivalente)
                        resultado = valor
                    elif para == 'ppb':  # mg/L para ppb
                        resultado = valor * 1000
                    elif para == 'mgL':  # mg/L para mg/L
                        return jsonify({'resultado': valor, 'unidade': 'mg/L'})
                    elif para == 'gL':  # mg/L para g/L
                        resultado = valor / 1000
                    elif para == 'perc':  # mg/L para %
                        resultado = valor / 10000
                
                elif para == 'gL':
                    if para == 'ppm':  # g/L para ppm
                        resultado = valor * 1000
                    elif para == 'ppb':  # g/L para ppb
                        resultado = valor * 1000000
                    elif para == 'mgL':  # g/L para mg/L
                        resultado = valor * 1000
                    elif para == 'gL':  # g/L para g/L
                        return jsonify({'resultado': valor, 'unidade': 'g/L'})
                    elif para == 'perc':  # g/L para %
                        resultado = valor / 10
                
                elif para == 'perc':
                    if para == 'ppm':  # % para ppm
                        resultado = valor * 10000
                    elif para == 'ppb':  # % para ppb
                        resultado = valor * 10000000
                    elif para == 'mgL':  # % para mg/L
                        resultado = valor * 10000
                    elif para == 'gL':  # % para g/L
                        resultado = valor * 10
                    elif para == 'perc':  # % para %
                        return jsonify({'resultado': valor, 'unidade': '%'})
            
            else:
                return jsonify({'error': 'Grupo de conversão não reconhecido'}), 400
                
            return jsonify({
                'resultado': resultado,
                'unidade': para
            })
            
        else:
            return jsonify({'error': f'Tipo de cálculo não reconhecido: {tipo_calculo}'}), 400
            
    except ZeroDivisionError:
        return jsonify({'error': 'Divisão por zero não permitida'}), 400
    except ValueError as e:
        return jsonify({'error': f'Erro de valor: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao realizar cálculo: {str(e)}'}), 500