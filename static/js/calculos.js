/**
 * ZELOPACK - Sistema de Cálculos de Laboratório
 * Este arquivo contém todas as funções JavaScript para os cálculos interativos
 */

// Namespace para os cálculos
window.ZelopackCalculos = {
    // Constantes e fatores de conversão padrão
    fatores: {
        cristal_to_liquido: 0.85,  // 1kg de açúcar cristal equivale a 0.85L de açúcar líquido
        liquido_to_cristal: 1.18,  // 1L de açúcar líquido equivale a 1.18kg de açúcar cristal
        acido_citrico_fator: 1.0,  // Fator para ácido cítrico
        brix_correcao_temp: {
            "20": 1.000,  // Fatores de correção de Brix por temperatura
            "25": 0.990,
            "30": 0.980
        }
    },
    
    // Inicialização das funcionalidades de cálculo
    init: function() {
        console.log('Zelopack Cálculos: Inicializando módulo...');
        
        // Carregar fatores de conversão do servidor
        this.carregarFatoresConversao();
        
        // Inicializar gráficos interativos
        this.inicializarGraficos();
        
        // Configurar interatividade nas calculadoras
        this.configurarCalculadoras();
        
        // Aplicar efeitos visuais nos formulários de cálculo
        this.aplicarEfeitosVisuais();
        
        // Configurar comportamento de campos dependentes
        this.configurarCamposDependentes();
        
        console.log('Zelopack Cálculos: Inicialização concluída!');
    },
    
    // Carregar fatores de conversão do servidor via API
    carregarFatoresConversao: function() {
        fetch('/calculos/api/conversion_factors')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao obter fatores de conversão!');
                }
                return response.json();
            })
            .then(data => {
                this.fatores = data;
                console.log('Fatores de conversão carregados com sucesso:', this.fatores);
                
                // Atualizar formulários com os fatores carregados
                this.atualizarFormsComFatores();
            })
            .catch(error => {
                console.error('Erro ao carregar fatores de conversão:', error);
                ZelopackAnimations.showMessage('Não foi possível carregar os fatores de conversão. Usando valores padrão.', 'warning');
            });
    },
    
    // Atualizar formulários de cálculos com os fatores carregados
    atualizarFormsComFatores: function() {
        // Atualizar interface de configuração de fatores, se existir
        const fatores_form = document.getElementById('form-fatores');
        if (fatores_form) {
            const inputs = fatores_form.querySelectorAll('input[data-fator]');
            inputs.forEach(input => {
                const fator = input.getAttribute('data-fator');
                if (fator && this.fatores[fator] !== undefined) {
                    input.value = this.fatores[fator];
                }
            });
        }
        
        // Atualizar seletores de temperatura para correção de Brix
        const tempSelects = document.querySelectorAll('select[data-brix-temp]');
        if (tempSelects.length && this.fatores.brix_correcao_temp) {
            tempSelects.forEach(select => {
                // Limpar opções existentes
                select.innerHTML = '';
                
                // Adicionar novas opções
                Object.keys(this.fatores.brix_correcao_temp).forEach(temp => {
                    const option = document.createElement('option');
                    option.value = temp;
                    option.textContent = `${temp}°C (fator: ${this.fatores.brix_correcao_temp[temp]})`;
                    select.appendChild(option);
                });
            });
        }
    },
    
    // Inicializar gráficos interativos
    inicializarGraficos: function() {
        // Buscar containers de gráficos
        const graphContainers = document.querySelectorAll('.graph-container');
        
        if (!graphContainers.length) return;
        
        graphContainers.forEach(container => {
            const graphType = container.getAttribute('data-graph-type');
            const graphId = container.getAttribute('id');
            
            if (!graphType || !graphId) return;
            
            switch (graphType) {
                case 'ratio-comparacao':
                    this.criarGraficoRatioComparacao(graphId);
                    break;
                case 'brix-acidez':
                    this.criarGraficoBrixAcidez(graphId);
                    break;
                case 'rendimento':
                    this.criarGraficoRendimento(graphId);
                    break;
                // Adicionar mais tipos de gráficos conforme necessário
            }
        });
    },
    
    // Criar gráfico de comparação de ratio para diferentes frutas
    criarGraficoRatioComparacao: function(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Usar biblioteca Chart.js para criar gráfico
        // Verificar se Chart.js está disponível
        if (typeof Chart === 'undefined') {
            console.error('Chart.js não encontrado. O gráfico não será renderizado.');
            container.innerHTML = '<div class="alert alert-warning">Biblioteca de gráficos não encontrada.</div>';
            return;
        }
        
        // Verificar se já existe um canvas no container
        let canvas = container.querySelector('canvas');
        if (!canvas) {
            canvas = document.createElement('canvas');
            container.appendChild(canvas);
        }
        
        // Dados para o gráfico
        const frutas = ['Laranja', 'Uva', 'Maçã', 'Abacaxi', 'Manga'];
        const ratioIdeal = [10, 20, 25, 15, 45];  // Valores ideais médios
        const ratioMin = [8, 15, 20, 10, 30];     // Valores mínimos aceitáveis
        const ratioMax = [12, 25, 30, 20, 60];    // Valores máximos aceitáveis
        
        // Criação do gráfico
        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: frutas,
                datasets: [{
                    label: 'Ratio Ideal',
                    data: ratioIdeal,
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }, {
                    label: 'Mínimo Aceitável',
                    data: ratioMin,
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    type: 'line',
                    fill: false
                }, {
                    label: 'Máximo Aceitável',
                    data: ratioMax,
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    type: 'line',
                    fill: false
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Comparativo de Ratio por Tipo de Fruta'
                    },
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                return `Faixa ideal: ${ratioMin[context.dataIndex]} - ${ratioMax[context.dataIndex]}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Ratio (Brix/Acidez)'
                        }
                    }
                }
            }
        });
    },
    
    // Criar gráfico Brix x Acidez
    criarGraficoBrixAcidez: function(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Verificar se Chart.js está disponível
        if (typeof Chart === 'undefined') {
            console.error('Chart.js não encontrado. O gráfico não será renderizado.');
            container.innerHTML = '<div class="alert alert-warning">Biblioteca de gráficos não encontrada.</div>';
            return;
        }
        
        // Verificar se já existe um canvas no container
        let canvas = container.querySelector('canvas');
        if (!canvas) {
            canvas = document.createElement('canvas');
            container.appendChild(canvas);
        }
        
        // Dados para o gráfico
        const brixValues = [8, 9, 10, 11, 12, 13, 14, 15];
        const datasets = [];
        
        // Gerar linhas de ratio para diferentes valores de acidez
        for (let acidez of [0.5, 0.75, 1.0, 1.25, 1.5]) {
            const ratioValues = brixValues.map(brix => brix / acidez);
            
            datasets.push({
                label: `Acidez ${acidez}%`,
                data: ratioValues,
                borderColor: this.getColorForAcidez(acidez),
                backgroundColor: 'transparent',
                borderWidth: 2,
                tension: 0.1
            });
        }
        
        // Criação do gráfico
        new Chart(canvas, {
            type: 'line',
            data: {
                labels: brixValues,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Ratio em Função do Brix e Acidez'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Ratio: ${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: 'Ratio (Brix/Acidez)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Brix (°Bx)'
                        }
                    }
                }
            }
        });
    },
    
    // Criar gráfico de rendimento
    criarGraficoRendimento: function(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Verificar se Chart.js está disponível
        if (typeof Chart === 'undefined') {
            console.error('Chart.js não encontrado. O gráfico não será renderizado.');
            container.innerHTML = '<div class="alert alert-warning">Biblioteca de gráficos não encontrada.</div>';
            return;
        }
        
        // Verificar se já existe um canvas no container
        let canvas = container.querySelector('canvas');
        if (!canvas) {
            canvas = document.createElement('canvas');
            container.appendChild(canvas);
        }
        
        // Dados simulados de rendimento
        const labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'];
        const rendimentoReal = [92, 88, 95, 91, 94, 97];
        const rendimentoEsperado = [90, 90, 90, 90, 90, 90];
        
        // Criação do gráfico
        new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Rendimento Real',
                    data: rendimentoReal,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Rendimento Esperado',
                    data: rendimentoEsperado,
                    borderColor: 'rgba(153, 102, 255, 1)',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Histórico de Rendimento da Produção'
                    }
                },
                scales: {
                    y: {
                        min: 80,
                        title: {
                            display: true,
                            text: 'Rendimento (%)'
                        }
                    }
                }
            }
        });
    },
    
    // Obter cor com base no valor de acidez para visualização
    getColorForAcidez: function(acidez) {
        const colors = {
            0.5: 'rgba(54, 162, 235, 1)',   // Azul
            0.75: 'rgba(75, 192, 192, 1)',  // Verde-água
            1.0: 'rgba(255, 206, 86, 1)',   // Amarelo
            1.25: 'rgba(255, 159, 64, 1)',  // Laranja
            1.5: 'rgba(255, 99, 132, 1)'    // Vermelho
        };
        
        return colors[acidez] || 'rgba(128, 128, 128, 1)';
    },
    
    // Configurar interatividade nas calculadoras
    configurarCalculadoras: function() {
        // Configurar comportamento de todas as calculadoras
        this.configurarAberturaCalculadoras();
        this.configurarBotoesCalcular();
        this.configurarResetCalculadoras();
        this.configurarValidacaoInputs();
        this.configurarAnimacoesResultados();
        
        // Interceptar eventos de submit em formulários
        const forms = document.querySelectorAll('form[id^="form-"]');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
            });
        });
    },
    
    // Configurar abertura/fechamento de calculadoras ao clicar no título
    configurarAberturaCalculadoras: function() {
        const calculatorTitles = document.querySelectorAll('.calculator-title, .card-header-calculator');
        
        calculatorTitles.forEach(title => {
            title.addEventListener('click', function() {
                // Encontrar o corpo associado com esta calculadora
                let body = null;
                if (this.classList.contains('calculator-title')) {
                    body = this.nextElementSibling;
                    if (body && body.classList.contains('calculator-body')) {
                        body.classList.toggle('active');
                        
                        // Animar ícone de seta, se existir
                        const icon = this.querySelector('.fa-chevron-down, .fa-chevron-up');
                        if (icon) {
                            icon.classList.toggle('fa-chevron-down');
                            icon.classList.toggle('fa-chevron-up');
                        }
                    }
                } else if (this.classList.contains('card-header-calculator')) {
                    // Para novo estilo de card
                    const card = this.closest('.card-calculator');
                    if (card) {
                        body = card.querySelector('.card-body-calculator');
                        if (body) {
                            if (body.style.display === 'none') {
                                // Abrir com animação
                                $(body).slideDown(300);
                                // Atualizar ícone
                                const icon = this.querySelector('.fa-chevron-down, .fa-chevron-up');
                                if (icon) icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
                            } else {
                                // Fechar com animação
                                $(body).slideUp(300);
                                // Atualizar ícone
                                const icon = this.querySelector('.fa-chevron-down, .fa-chevron-up');
                                if (icon) icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
                            }
                        }
                    }
                }
                
                // Efeito de "destaque" ao clicar
                ZelopackAnimations.pulse(this);
            });
        });
    },
    
    // Configurar botões de calcular
    configurarBotoesCalcular: function() {
        const btnCalculate = document.querySelectorAll('.btn-calculate');
        
        btnCalculate.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tipoCalculo = btn.getAttribute('data-tipo') || '';
                
                if (tipoCalculo) {
                    // Executar função de cálculo específica
                    this.executarCalculo(tipoCalculo);
                }
            });
        });
    },
    
    // Configurar botões de reset das calculadoras
    configurarResetCalculadoras: function() {
        const resetButtons = document.querySelectorAll('.action-button.reset');
        
        resetButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const formId = btn.getAttribute('data-form-id');
                const resultId = btn.getAttribute('data-result-id');
                
                if (formId) {
                    const form = document.getElementById(formId);
                    if (form) {
                        form.reset();
                        
                        // Limpar mensagens de erro
                        const errorMessages = form.querySelectorAll('.error-message');
                        errorMessages.forEach(msg => {
                            msg.style.display = 'none';
                        });
                        
                        // Limpar formatação de erros nos inputs
                        const inputs = form.querySelectorAll('input, select');
                        inputs.forEach(input => {
                            input.classList.remove('is-invalid');
                        });
                    }
                }
                
                if (resultId) {
                    const resultBox = document.getElementById(resultId);
                    if (resultBox) {
                        resultBox.style.display = 'none';
                    }
                }
                
                // Efeito visual
                ZelopackAnimations.pulse(btn);
            });
        });
    },
    
    // Validação de campos de formulário
    configurarValidacaoInputs: function() {
        const numericInputs = document.querySelectorAll('input[type="number"], input[data-tipo="numero"]');
        
        numericInputs.forEach(input => {
            // Validar quando o valor mudar
            input.addEventListener('input', () => {
                this.validarCampoNumerico(input);
            });
            
            // Validar também quando perder o foco
            input.addEventListener('blur', () => {
                this.validarCampoNumerico(input);
            });
        });
    },
    
    // Validar campo numérico
    validarCampoNumerico: function(input) {
        const value = input.value.trim();
        const min = parseFloat(input.getAttribute('min') || '-Infinity');
        const max = parseFloat(input.getAttribute('max') || 'Infinity');
        const required = input.hasAttribute('required');
        
        // Limpar estado anterior
        input.classList.remove('is-invalid', 'is-valid');
        
        // Buscar elemento de mensagem de erro associado
        const errorMsgId = 'error-' + input.id;
        const errorMsg = document.getElementById(errorMsgId);
        
        // Verificar se está vazio
        if (required && value === '') {
            input.classList.add('is-invalid');
            if (errorMsg) {
                errorMsg.textContent = 'Este campo é obrigatório.';
                errorMsg.style.display = 'block';
            }
            return false;
        }
        
        // Verificar se é um número válido
        const numValue = parseFloat(value);
        if (isNaN(numValue)) {
            input.classList.add('is-invalid');
            if (errorMsg) {
                errorMsg.textContent = 'Digite um número válido.';
                errorMsg.style.display = 'block';
            }
            return false;
        }
        
        // Verificar limites
        if (numValue < min) {
            input.classList.add('is-invalid');
            if (errorMsg) {
                errorMsg.textContent = `O valor mínimo é ${min}.`;
                errorMsg.style.display = 'block';
            }
            return false;
        }
        
        if (numValue > max) {
            input.classList.add('is-invalid');
            if (errorMsg) {
                errorMsg.textContent = `O valor máximo é ${max}.`;
                errorMsg.style.display = 'block';
            }
            return false;
        }
        
        // Se chegou aqui, o valor é válido
        input.classList.add('is-valid');
        if (errorMsg) {
            errorMsg.style.display = 'none';
        }
        
        return true;
    },
    
    // Configurar animações para resultados
    configurarAnimacoesResultados: function() {
        // Definir animações para as caixas de resultado quando são exibidas
        const resultBoxes = document.querySelectorAll('.result-box');
        
        resultBoxes.forEach(box => {
            // Armazenar o observador original
            const originalDisplay = box.style.display;
            
            // Configurar MutationObserver para detectar mudanças no estilo "display"
            const observer = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.attributeName === 'style') {
                        const newDisplay = box.style.display;
                        
                        if (newDisplay !== 'none' && newDisplay !== originalDisplay) {
                            // Adicionar animação quando o resultado é mostrado
                            box.classList.add('animate-fade-in');
                            // Animar o valor do resultado, se existir
                            const resultValue = box.querySelector('.result-value');
                            if (resultValue) {
                                ZelopackAnimations.pulse(resultValue);
                            }
                            
                            // Remover a classe de animação após a conclusão
                            setTimeout(() => {
                                box.classList.remove('animate-fade-in');
                            }, 1000);
                        }
                    }
                });
            });
            
            // Iniciar observação da caixa de resultado
            observer.observe(box, { attributes: true });
        });
    },
    
    // Aplicar efeitos visuais nos formulários de cálculo
    aplicarEfeitosVisuais: function() {
        // Adicionar efeitos de hover em cards e calculadoras
        const cards = document.querySelectorAll('.card-calculator');
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
                this.style.boxShadow = '0 12px 20px rgba(0, 0, 0, 0.15)';
                this.style.transition = 'all 0.3s ease';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = '';
                this.style.boxShadow = '';
            });
        });
        
        // Adicionar tooltips explicativos
        const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
        tooltipTriggers.forEach(trigger => {
            trigger.addEventListener('mouseenter', function() {
                const tooltip = this.getAttribute('data-tooltip');
                if (tooltip) {
                    ZelopackAnimations.showTooltip(this, tooltip);
                }
            });
        });
        
        // Animar abas quando clicadas
        const tabButtons = document.querySelectorAll('.nav-link[data-bs-toggle="tab"]');
        tabButtons.forEach(tab => {
            tab.addEventListener('click', function() {
                ZelopackAnimations.pulse(this);
            });
        });
    },
    
    // Configurar comportamento de campos dependentes
    configurarCamposDependentes: function() {
        // Encontrar pares de campos onde um depende do outro
        const dependentFields = document.querySelectorAll('[data-depends-on]');
        
        dependentFields.forEach(field => {
            const sourceFieldId = field.getAttribute('data-depends-on');
            const sourceField = document.getElementById(sourceFieldId);
            
            if (sourceField) {
                // Adicionar listener para o campo fonte
                sourceField.addEventListener('input', () => {
                    this.atualizarCampoDependente(sourceField, field);
                });
                
                // Fazer atualização inicial
                this.atualizarCampoDependente(sourceField, field);
            }
        });
    },
    
    // Atualizar campo dependente com base no valor de outro campo
    atualizarCampoDependente: function(sourceField, dependentField) {
        const dependencyType = dependentField.getAttribute('data-dependency-type') || '';
        const sourceValue = parseFloat(sourceField.value);
        
        // Não fazer nada se o valor fonte não for um número válido
        if (isNaN(sourceValue)) return;
        
        // Aplicar transformação adequada com base no tipo de dependência
        switch (dependencyType) {
            case 'multiplicar':
                const factor = parseFloat(dependentField.getAttribute('data-factor') || '1');
                dependentField.value = (sourceValue * factor).toFixed(2);
                break;
                
            case 'inverso':
                // Evitar divisão por zero
                if (sourceValue === 0) {
                    dependentField.value = '';
                } else {
                    dependentField.value = (1 / sourceValue).toFixed(4);
                }
                break;
                
            case 'diferenca':
                const referenceValue = parseFloat(dependentField.getAttribute('data-reference') || '0');
                dependentField.value = (referenceValue - sourceValue).toFixed(2);
                break;
                
            // Adicionar mais tipos de dependência conforme necessário
        }
        
        // Disparar evento para que validadores ou outros listeners sejam notificados
        dependentField.dispatchEvent(new Event('input'));
    },
    
    // Executar um cálculo com base no tipo
    executarCalculo: function(tipoCalculo) {
        // Coletar dados do formulário correspondente
        const formId = 'form-' + tipoCalculo;
        const resultId = 'result-' + tipoCalculo;
        const form = document.getElementById(formId);
        
        if (!form) {
            console.error(`Formulário não encontrado: ${formId}`);
            return;
        }
        
        // Validar todos os campos antes de prosseguir
        const inputs = form.querySelectorAll('input[type="number"], input[data-tipo="numero"]');
        let formValido = true;
        
        // Verificar se todos os campos são válidos
        inputs.forEach(input => {
            if (!this.validarCampoNumerico(input)) {
                formValido = false;
            }
        });
        
        if (!formValido) {
            ZelopackAnimations.showMessage('Por favor, corrija os erros no formulário antes de calcular.', 'warning');
            return;
        }
        
        // Coletar todos os valores dos inputs
        const inputData = {};
        inputs.forEach(input => {
            inputData[input.id.replace(tipoCalculo + '_', '')] = parseFloat(input.value);
        });
        
        // Adicionar tipo de cálculo aos dados
        inputData.tipo_calculo = tipoCalculo;
        
        // Exibir animação de carregamento durante o cálculo
        ZelopackAnimations.showLoading('Calculando...');
        
        // Enviar dados para a API e processar resultado
        fetch('/calculos/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(inputData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na requisição: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            // Esconder animação de carregamento
            ZelopackAnimations.hideLoading();
            
            if (data.error) {
                // Mostrar mensagem de erro
                ZelopackAnimations.showMessage(data.error, 'danger');
                return;
            }
            
            // Atualizar e exibir o resultado
            this.exibirResultado(tipoCalculo, data.resultado, data);
        })
        .catch(error => {
            console.error('Erro ao calcular:', error);
            ZelopackAnimations.hideLoading();
            ZelopackAnimations.showMessage('Erro ao processar o cálculo. Tente novamente.', 'danger');
        });
    },
    
    // Exibir o resultado de um cálculo na interface
    exibirResultado: function(tipoCalculo, resultado, dadosCompletos) {
        const resultBox = document.getElementById('result-' + tipoCalculo);
        const resultValue = document.getElementById('result-value-' + tipoCalculo);
        
        if (!resultBox || !resultValue) {
            console.error(`Elementos de resultado não encontrados para ${tipoCalculo}`);
            return;
        }
        
        // Atualizar valor do resultado
        resultValue.textContent = this.formatarResultado(resultado, tipoCalculo);
        
        // Se houver informações adicionais no resultado (como classificação), atualizá-las
        if (dadosCompletos.classificacao) {
            const classElement = document.getElementById('result-classificacao-' + tipoCalculo);
            if (classElement) {
                classElement.textContent = dadosCompletos.classificacao;
                
                // Aplicar classes de estilo baseado no status
                if (dadosCompletos.status) {
                    // Limpar classes anteriores
                    classElement.className = classElement.className.replace(/text-\w+/g, '').trim();
                    // Adicionar nova classe
                    classElement.classList.add(dadosCompletos.status);
                }
            }
        }
        
        // Exibir a caixa de resultado com efeito de fadein
        resultBox.style.display = 'block';
        
        // Gerar um gráfico dinâmico, se aplicável
        if (tipoCalculo === 'ratio_fruta' || tipoCalculo === 'rendimento') {
            this.gerarGraficoDinamico(tipoCalculo, dadosCompletos);
        }
    },
    
    // Formatar o resultado de acordo com o tipo de cálculo
    formatarResultado: function(valor, tipoCalculo) {
        // Formatação padrão com 2 casas decimais
        let formatado = parseFloat(valor).toFixed(2);
        
        // Formatações específicas com base no tipo
        switch (tipoCalculo) {
            case 'producao_200':
            case 'producao_litro':
                formatado = parseFloat(valor).toFixed(1);
                break;
                
            case 'ratio':
            case 'ratio_fruta':
                formatado = parseFloat(valor).toFixed(1);
                break;
                
            case 'rendimento':
                formatado = parseFloat(valor).toFixed(2) + '%';
                break;
                
            case 'ph':
            case 'acidez':
                formatado = parseFloat(valor).toFixed(3);
                break;
                
            // Formatos para outros tipos específicos
        }
        
        return formatado;
    },
    
    // Gerar um gráfico dinâmico baseado no resultado do cálculo
    gerarGraficoDinamico: function(tipoCalculo, dadosCompletos) {
        const graphContainer = document.getElementById('graph-' + tipoCalculo);
        if (!graphContainer) return;
        
        // Verificar se Chart.js está disponível
        if (typeof Chart === 'undefined') {
            graphContainer.innerHTML = '<div class="alert alert-warning">Biblioteca de gráficos não encontrada.</div>';
            return;
        }
        
        // Limpar gráfico anterior, se existir
        while (graphContainer.firstChild) {
            graphContainer.removeChild(graphContainer.firstChild);
        }
        
        // Criar novo canvas para o gráfico
        const canvas = document.createElement('canvas');
        graphContainer.appendChild(canvas);
        
        // Configurar o gráfico de acordo com o tipo de cálculo
        let chart;
        
        switch(tipoCalculo) {
            case 'ratio_fruta':
                // Gráfico para ratio de fruta
                const tipoFruta = dadosCompletos.tipo_fruta || 'laranja';
                const valor = dadosCompletos.resultado;
                
                // Definir faixas de referência com base no tipo de fruta
                let faixas = {};
                
                switch(tipoFruta) {
                    case 'laranja':
                        faixas = {
                            baixo: 8,
                            ideal_min: 8,
                            ideal_max: 12,
                            alto: 18
                        };
                        break;
                    case 'uva':
                        faixas = {
                            baixo: 15,
                            ideal_min: 15,
                            ideal_max: 25,
                            alto: 35
                        };
                        break;
                    case 'maca':
                        faixas = {
                            baixo: 20,
                            ideal_min: 20,
                            ideal_max: 30,
                            alto: 40
                        };
                        break;
                    case 'abacaxi':
                        faixas = {
                            baixo: 10,
                            ideal_min: 10,
                            ideal_max: 20,
                            alto: 30
                        };
                        break;
                    default:
                        faixas = {
                            baixo: 30,
                            ideal_min: 30,
                            ideal_max: 60,
                            alto: 90
                        };
                }
                
                // Criar gráfico de gauge para visualização do ratio
                chart = new Chart(canvas, {
                    type: 'gauge',
                    data: {
                        datasets: [{
                            value: valor,
                            data: [faixas.baixo, faixas.ideal_min, faixas.ideal_max, faixas.alto, 100],
                            backgroundColor: ['#dc3545', '#28a745', '#dc3545', '#dc3545'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        needle: {
                            radiusPercentage: 2,
                            widthPercentage: 3.2,
                            lengthPercentage: 80,
                            color: 'rgba(0, 0, 0, 1)'
                        },
                        valueLabel: {
                            formatter: function(value) {
                                return value.toFixed(1);
                            }
                        }
                    }
                });
                break;
                
            case 'rendimento':
                // Gráfico para rendimento
                const rendimento = dadosCompletos.resultado;
                
                chart = new Chart(canvas, {
                    type: 'doughnut',
                    data: {
                        labels: ['Rendimento', 'Perda'],
                        datasets: [{
                            data: [rendimento, 100 - rendimento],
                            backgroundColor: [
                                'rgba(75, 192, 192, 0.8)',
                                'rgba(255, 99, 132, 0.8)'
                            ],
                            borderColor: [
                                'rgba(75, 192, 192, 1)',
                                'rgba(255, 99, 132, 1)'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Rendimento da Produção'
                            },
                            legend: {
                                position: 'bottom'
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return `${context.label}: ${context.raw.toFixed(2)}%`;
                                    }
                                }
                            }
                        },
                        cutout: '70%'
                    }
                });
                break;
                
            // Adicionar outros tipos de gráficos conforme necessário
        }
        
        // Exibir container de gráfico
        graphContainer.style.display = 'block';
    }
};

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se ZelopackAnimations está disponível
    if (typeof ZelopackAnimations === 'undefined') {
        console.error('ZelopackAnimations não está disponível. Algumas animações podem não funcionar.');
    }
    
    // Inicializar módulo de cálculos
    if (document.querySelector('.calculation-tabs')) {
        ZelopackCalculos.init();
    }
    
    // Função global para calcular (para compatibilidade com código existente)
    window.calculate = function(tipoCalculo) {
        ZelopackCalculos.executarCalculo(tipoCalculo);
    };
});

// Função global para copiar resultado
function copyResult(resultId, unit) {
    const resultElement = document.getElementById(resultId);
    if (!resultElement) return;
    
    const value = resultElement.textContent;
    const textToCopy = unit ? value + ' ' + unit : value;
    
    // Criar elemento temporário
    const tempInput = document.createElement('input');
    tempInput.value = textToCopy;
    document.body.appendChild(tempInput);
    
    // Selecionar e copiar
    tempInput.select();
    document.execCommand('copy');
    
    // Remover elemento temporário
    document.body.removeChild(tempInput);
    
    // Animação de feedback
    ZelopackAnimations.pulse(resultElement);
    
    // Mostrar mensagem de sucesso
    ZelopackAnimations.showTooltip(resultElement, 'Copiado para a área de transferência!');
}

// Função global para resetar calculadora
function resetCalculator(formId, resultId) {
    const form = document.getElementById(formId);
    const result = document.getElementById(resultId);
    
    if (form) {
        form.reset();
    }
    
    if (result) {
        result.style.display = 'none';
    }
}