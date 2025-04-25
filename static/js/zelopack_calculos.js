/**
 * ZeloPack - Biblioteca de Cálculos Técnicos
 * Implementação de todos os cálculos laboratoriais e de produção
 */

// Inicialização
console.log("ZeloCalc: Inicializando módulo de cálculos técnicos 2.0...");

document.addEventListener('DOMContentLoaded', function() {
    // Configurações e constantes
    const CONFIG = {
        // Tolerâncias padrão
        tolerancias: {
            peso200g: 2.5, // ±2.5%
            brix: 0.2,     // ±0.2 Brix
            acidez: 0.05   // ±0.05% acidez
        },
        
        // Valores de referência
        referencias: {
            densidadeSucos: 1.045,  // g/mL
            pesoEmbalagem200g: 19.0 // g
        },
        
        // Fatores de conversão
        fatores: {
            // Fator de correção de Brix por tipo de produto
            brix: {
                padrao: 1.0,
                citrus: 0.98,
                nectar: 1.02,
                concentrado: 0.95
            },
            
            // Conversão açúcar
            acucar: {
                cristalParaLiquido: 0.85, // 1kg cristal = 0.85L líquido
                liquidoParaCristal: 1.18  // 1L líquido = 1.18kg cristal
            }
        }
    };
    
    // ======== FUNÇÕES DE UTILIDADE ========
    
    /**
     * Formata um número com casas decimais específicas
     * @param {number} valor - O valor a ser formatado
     * @param {number} casas - Número de casas decimais
     * @returns {string} - Valor formatado
     */
    function formatarNumero(valor, casas = 2) {
        return Number(valor).toFixed(casas);
    }
    
    /**
     * Valida se todas as entradas de um formulário estão preenchidas
     * @param {Array} campos - Array com IDs dos campos a validar
     * @returns {boolean} - true se todos os campos estiverem válidos
     */
    function validarCampos(campos) {
        let valido = true;
        campos.forEach(id => {
            const elemento = document.getElementById(id);
            if (!elemento) return;
            
            const valor = elemento.value.trim();
            if (!valor || isNaN(parseFloat(valor))) {
                elemento.classList.add('is-invalid');
                valido = false;
            } else {
                elemento.classList.remove('is-invalid');
            }
        });
        
        return valido;
    }
    
    // ======== IMPLEMENTAÇÃO DOS CÁLCULOS ========
    
    // -------- 1. PRODUÇÃO 200g --------
    window.calculoProducao200g = {
        calcular: function() {
            // Obter valores
            const pesoBruto = parseFloat(document.getElementById('peso_bruto_200g').value) || 0;
            const tara = parseFloat(document.getElementById('tara_200g').value) || CONFIG.referencias.pesoEmbalagem200g;
            const tolerancia = parseFloat(document.getElementById('tolerancia_200g').value) || CONFIG.tolerancias.peso200g;
            const pesoEspecificado = parseFloat(document.getElementById('peso_especificado_200g').value) || 200.0;
            
            // Validar entradas
            if (!validarCampos(['peso_bruto_200g'])) {
                alert('Por favor, preencha ao menos o Peso Bruto para realizar o cálculo.');
                return;
            }
            
            // Calcular peso líquido
            const pesoLiquido = pesoBruto - tara;
            
            // Verificar tolerância
            const limiteInferior = pesoEspecificado * (1 - (tolerancia / 100));
            const limiteSuperior = pesoEspecificado * (1 + (tolerancia / 100));
            const desvio = ((pesoLiquido - pesoEspecificado) / pesoEspecificado) * 100;
            
            // Determinar status
            let status, statusClass;
            
            if (pesoLiquido < limiteInferior) {
                status = 'Abaixo da tolerância';
                statusClass = 'alert-danger';
            } else if (pesoLiquido > limiteSuperior) {
                status = 'Acima da tolerância';
                statusClass = 'alert-warning';
            } else {
                status = 'Dentro da tolerância';
                statusClass = 'alert-success';
            }
            
            // Atualizar resultados na interface
            document.getElementById('resultado_peso_liquido_200g').textContent = formatarNumero(pesoLiquido) + ' g';
            document.getElementById('resultado_status_200g').textContent = status;
            document.getElementById('resultado_desvio_200g').textContent = formatarNumero(desvio) + '%';
            
            // Atualizar detalhes adicionais
            document.getElementById('resultado_limite_inferior_200g').textContent = formatarNumero(limiteInferior) + ' g';
            document.getElementById('resultado_limite_superior_200g').textContent = formatarNumero(limiteSuperior) + ' g';
            document.getElementById('resultado_diferenca_200g').textContent = formatarNumero(pesoLiquido - pesoEspecificado) + ' g';
            
            // Atualizar classe de status
            const statusElement = document.getElementById('status_alerta_200g');
            statusElement.className = 'alert ' + statusClass;
            
            // Mostrar área de resultado
            document.getElementById('resultado_area_200g').style.display = 'block';
        }
    };
    
    // -------- 2. PRODUÇÃO LITRO --------
    window.calculoProducaoLitro = {
        calcular: function() {
            // Obter valores
            const peso = parseFloat(document.getElementById('peso_total').value) || 0;
            const unidadePeso = document.getElementById('unidade_peso').value || 'kg';
            const densidade = parseFloat(document.getElementById('densidade_producao').value) || CONFIG.referencias.densidadeSucos;
            
            // Validar entradas
            if (!validarCampos(['peso_total', 'densidade_producao'])) {
                alert('Por favor, preencha todos os campos necessários.');
                return;
            }
            
            // Converter para unidades consistentes (kg)
            const pesoEmKg = unidadePeso === 'g' ? peso / 1000 : peso;
            
            // Calcular volume em litros (kg ÷ kg/L = L)
            const volumeLitros = pesoEmKg / densidade;
            
            // Atualizar resultados na interface
            document.getElementById('resultado_volume').textContent = formatarNumero(volumeLitros) + ' L';
            document.getElementById('resultado_formula_volume').textContent = 
                `${formatarNumero(pesoEmKg)} kg ÷ ${formatarNumero(densidade)} kg/L = ${formatarNumero(volumeLitros)} L`;
            
            // Mostrar área de resultado
            document.getElementById('resultado_area_volume').style.display = 'block';
        }
    };
    
    // -------- 3. ABAIXAR BRIX --------
    window.calculoAbaixarBrix = {
        calcular: function() {
            // Obter valores
            const brixAtual = parseFloat(document.getElementById('brix_atual_abaixar').value) || 0;
            const brixDesejado = parseFloat(document.getElementById('brix_desejado_abaixar').value) || 0;
            const volumeInicial = parseFloat(document.getElementById('volume_inicial_abaixar').value) || 0;
            
            // Validar entradas
            if (!validarCampos(['brix_atual_abaixar', 'brix_desejado_abaixar', 'volume_inicial_abaixar'])) {
                alert('Por favor, preencha todos os campos necessários.');
                return;
            }
            
            // Validar que brixAtual > brixDesejado
            if (brixAtual <= brixDesejado) {
                alert('O Brix atual já é menor ou igual ao desejado. Não é possível diluir mais.');
                return;
            }
            
            // Calcular água necessária
            const volumeAgua = volumeInicial * (brixAtual / brixDesejado - 1);
            const volumeFinal = volumeInicial + volumeAgua;
            
            // Atualizar resultados na interface
            document.getElementById('resultado_agua').textContent = formatarNumero(volumeAgua) + ' L';
            document.getElementById('resultado_volume_final').textContent = formatarNumero(volumeFinal) + ' L';
            document.getElementById('resultado_formula_brix').textContent = 
                `${formatarNumero(volumeInicial)} × (${formatarNumero(brixAtual)} ÷ ${formatarNumero(brixDesejado)} - 1) = ${formatarNumero(volumeAgua)} L`;
            
            // Mostrar área de resultado
            document.getElementById('resultado_area_abaixar_brix').style.display = 'block';
        }
    };
    
    // -------- 4. BRIX CORRIGIDO --------
    window.calculoBrixCorrigido = {
        calcular: function() {
            // Obter valores
            const brixMedido = parseFloat(document.getElementById('brix_medido').value) || 0;
            const temperatura = parseFloat(document.getElementById('temperatura_brix').value) || 20;
            const tipoCorrecao = document.getElementById('tipo_correcao').value || 'padrao';
            
            // Validar entradas
            if (!validarCampos(['brix_medido'])) {
                alert('Por favor, informe ao menos o Brix medido.');
                return;
            }
            
            // Calcular correção de temperatura
            const temperaturaRef = 20.0; // Temperatura de referência
            const deltaTempRef = temperatura - temperaturaRef;
            
            // Fator aproximado: a cada 1°C acima de 20°C, adicionar 0.06 ao Brix
            const correcaoTemp = deltaTempRef * 0.06;
            
            // Aplicar correção de temperatura
            let brixCorrigidoTemp = brixMedido;
            
            if (temperatura !== temperaturaRef) {
                brixCorrigidoTemp = temperatura > temperaturaRef 
                    ? brixMedido - correcaoTemp 
                    : brixMedido + Math.abs(correcaoTemp);
            }
            
            // Aplicar fator de correção do tipo de produto
            const fator = CONFIG.fatores.brix[tipoCorrecao] || 1.0;
            const brixFinal = brixCorrigidoTemp * fator;
            
            // Atualizar resultados na interface
            document.getElementById('resultado_brix_corrigido').textContent = formatarNumero(brixFinal, 1);
            document.getElementById('resultado_correcao_temp').textContent = formatarNumero(correcaoTemp, 2);
            document.getElementById('resultado_fator_produto').textContent = formatarNumero(fator, 2);
            
            // Mostrar como a correção foi feita
            let explicacao = '';
            if (temperatura !== temperaturaRef) {
                const operacao = temperatura > temperaturaRef ? 'subtraído' : 'adicionado';
                explicacao += `Correção de temperatura (${temperatura}°C): ${operacao} ${formatarNumero(Math.abs(correcaoTemp), 2)}<br>`;
            }
            
            if (fator !== 1.0) {
                explicacao += `Aplicado fator de produto ${tipoCorrecao}: ${formatarNumero(fator, 2)}<br>`;
            }
            
            document.getElementById('resultado_explicacao_brix').innerHTML = explicacao || 'Nenhuma correção significativa aplicada.';
            
            // Mostrar área de resultado
            document.getElementById('resultado_area_brix').style.display = 'block';
        }
    };
    
    // -------- 5. PESO BRUTO --------
    window.calculoPesoBruto = {
        calcular: function() {
            // Obter valores
            const pesoLiquido = parseFloat(document.getElementById('peso_liquido_calc').value) || 0;
            const tara = parseFloat(document.getElementById('tara_calc').value) || 0;
            
            // Validar entradas
            if (!validarCampos(['peso_liquido_calc', 'tara_calc'])) {
                alert('Por favor, preencha todos os campos necessários.');
                return;
            }
            
            // Calcular peso bruto
            const pesoBruto = pesoLiquido + tara;
            
            // Atualizar resultados na interface
            document.getElementById('resultado_peso_bruto').textContent = formatarNumero(pesoBruto) + ' g';
            document.getElementById('resultado_formula_peso_bruto').textContent = 
                `${formatarNumero(pesoLiquido)} g + ${formatarNumero(tara)} g = ${formatarNumero(pesoBruto)} g`;
            
            // Mostrar área de resultado
            document.getElementById('resultado_area_peso_bruto').style.display = 'block';
        }
    };
    
    // -------- 6. CORANTES --------
    window.calculoCorantes = {
        calcular: function() {
            // Obter valores
            const volumeTotal = parseFloat(document.getElementById('volume_corante').value) || 0;
            const dosagem = parseFloat(document.getElementById('dosagem_corante').value) || 0;
            const unidadeDosagem = document.getElementById('unidade_dosagem').value || 'mL/L';
            
            // Validar entradas
            if (!validarCampos(['volume_corante', 'dosagem_corante'])) {
                alert('Por favor, preencha todos os campos necessários.');
                return;
            }
            
            // Calcular quantidade de corante
            const quantidadeCorante = volumeTotal * dosagem;
            
            // Determinar unidade de saída
            let unidadeSaida = 'mL';
            if (unidadeDosagem === 'g/L') {
                unidadeSaida = 'g';
            }
            
            // Atualizar resultados na interface
            document.getElementById('resultado_corante').textContent = formatarNumero(quantidadeCorante) + ' ' + unidadeSaida;
            document.getElementById('resultado_formula_corante').textContent = 
                `${formatarNumero(volumeTotal)} L × ${formatarNumero(dosagem)} ${unidadeDosagem} = ${formatarNumero(quantidadeCorante)} ${unidadeSaida}`;
            
            // Mostrar área de resultado
            document.getElementById('resultado_area_corante').style.display = 'block';
        }
    };
    
    // -------- 7. DENSIDADE --------
    window.calculoDensidade = {
        calcular: function() {
            // Obter valores
            const massa = parseFloat(document.getElementById('massa_densidade').value) || 0;
            const volume = parseFloat(document.getElementById('volume_densidade').value) || 0;
            
            // Validar entradas
            if (!validarCampos(['massa_densidade', 'volume_densidade'])) {
                alert('Por favor, preencha todos os campos necessários.');
                return;
            }
            
            // Calcular densidade
            const densidade = massa / volume;
            
            // Atualizar resultados na interface
            document.getElementById('resultado_densidade').textContent = formatarNumero(densidade, 3) + ' g/mL';
            document.getElementById('resultado_formula_densidade').textContent = 
                `${formatarNumero(massa)} g ÷ ${formatarNumero(volume)} mL = ${formatarNumero(densidade, 3)} g/mL`;
            
            // Mostrar área de resultado
            document.getElementById('resultado_area_densidade').style.display = 'block';
        }
    };
    
    // -------- 8. RATIO --------
    window.calculoRatio = {
        calcular: function() {
            // Obter valores
            const brix = parseFloat(document.getElementById('brix_ratio').value) || 0;
            const acidez = parseFloat(document.getElementById('acidez_ratio').value) || 0;
            
            // Validar entradas
            if (!validarCampos(['brix_ratio', 'acidez_ratio'])) {
                alert('Por favor, preencha todos os campos necessários.');
                return;
            }
            
            // Validar que acidez não é zero
            if (acidez === 0) {
                alert('A acidez não pode ser zero. Divisão por zero não é permitida.');
                return;
            }
            
            // Calcular ratio
            const ratio = brix / acidez;
            
            // Atualizar resultados na interface
            document.getElementById('resultado_ratio').textContent = formatarNumero(ratio, 1);
            document.getElementById('resultado_formula_ratio').textContent = 
                `${formatarNumero(brix, 1)} ÷ ${formatarNumero(acidez, 2)} = ${formatarNumero(ratio, 1)}`;
            
            // Mostrar área de resultado
            document.getElementById('resultado_area_ratio').style.display = 'block';
        }
    };
    
    // -------- 9. ACIDEZ --------
    window.calculoAcidez = {
        calcular: function() {
            // Obter valores
            const volumeAmostra = parseFloat(document.getElementById('volume_amostra_acidez').value) || 0;
            const fatorNaOH = parseFloat(document.getElementById('fator_naoh').value) || 0;
            const volumeNaOH = parseFloat(document.getElementById('volume_naoh').value) || 0;
            
            // Validar entradas
            if (!validarCampos(['volume_amostra_acidez', 'fator_naoh', 'volume_naoh'])) {
                alert('Por favor, preencha todos os campos necessários.');
                return;
            }
            
            // Calcular acidez
            const acidez = (volumeNaOH * fatorNaOH * 100) / volumeAmostra;
            
            // Atualizar resultados na interface
            document.getElementById('resultado_acidez').textContent = formatarNumero(acidez, 2) + '%';
            document.getElementById('resultado_formula_acidez').textContent = 
                `(${formatarNumero(volumeNaOH)} × ${formatarNumero(fatorNaOH)} × 100) ÷ ${formatarNumero(volumeAmostra)} = ${formatarNumero(acidez, 2)}%`;
            
            // Mostrar área de resultado
            document.getElementById('resultado_area_acidez').style.display = 'block';
        }
    };

    // Inicialização de event listeners para botões de cálculo
    function inicializarEventListeners() {
        // Produção 200g
        const btnCalculo200g = document.getElementById('calcular_200g');
        if (btnCalculo200g) {
            btnCalculo200g.addEventListener('click', window.calculoProducao200g.calcular);
        }
        
        // Produção Litro
        const btnCalculoLitro = document.getElementById('calcular_volume');
        if (btnCalculoLitro) {
            btnCalculoLitro.addEventListener('click', window.calculoProducaoLitro.calcular);
        }
        
        // Abaixar Brix
        const btnAbaixarBrix = document.getElementById('calcular_abaixar_brix');
        if (btnAbaixarBrix) {
            btnAbaixarBrix.addEventListener('click', window.calculoAbaixarBrix.calcular);
        }
        
        // Brix Corrigido
        const btnBrixCorrigido = document.getElementById('calcular_brix_corrigido');
        if (btnBrixCorrigido) {
            btnBrixCorrigido.addEventListener('click', window.calculoBrixCorrigido.calcular);
        }
        
        // Peso Bruto
        const btnPesoBruto = document.getElementById('calcular_peso_bruto');
        if (btnPesoBruto) {
            btnPesoBruto.addEventListener('click', window.calculoPesoBruto.calcular);
        }
        
        // Corantes
        const btnCorantes = document.getElementById('calcular_corante');
        if (btnCorantes) {
            btnCorantes.addEventListener('click', window.calculoCorantes.calcular);
        }
        
        // Densidade
        const btnDensidade = document.getElementById('calcular_densidade');
        if (btnDensidade) {
            btnDensidade.addEventListener('click', window.calculoDensidade.calcular);
        }
        
        // Ratio
        const btnRatio = document.getElementById('calcular_ratio');
        if (btnRatio) {
            btnRatio.addEventListener('click', window.calculoRatio.calcular);
        }
        
        // Acidez
        const btnAcidez = document.getElementById('calcular_acidez');
        if (btnAcidez) {
            btnAcidez.addEventListener('click', window.calculoAcidez.calcular);
        }
        
        // Botões para limpar formulários
        document.querySelectorAll('.btn-limpar').forEach(btn => {
            btn.addEventListener('click', function() {
                const area = this.closest('.calculo-area');
                const inputs = area.querySelectorAll('input:not([type="hidden"])');
                inputs.forEach(input => {
                    input.value = '';
                    input.classList.remove('is-invalid');
                });
                
                // Esconder área de resultado
                const resultadoArea = area.querySelector('.resultado-area');
                if (resultadoArea) {
                    resultadoArea.style.display = 'none';
                }
            });
        });
    }
    
    // Inicializar quando o DOM estiver carregado
    inicializarEventListeners();
    
    console.log("ZeloCalc: Módulo de cálculos técnicos carregado com sucesso!");
});