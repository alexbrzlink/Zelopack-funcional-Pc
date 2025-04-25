/**
 * ZELOPACK - JavaScript para a Seção de Cálculos Técnicos
 * Script responsável pelas animações, interatividade e funcionalidade das calculadoras
 * Versão 2.0 - Interface completamente renovada
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('ZeloCalc: Inicializando módulo de cálculos técnicos 2.0...');
    
    // Catálogo de todos os cálculos disponíveis para busca
    const calculosDisponiveis = [
        { 
            id: 'finalizar-tanque', 
            nome: 'Finalização de Tanque', 
            categoria: 'Tanques', 
            descricao: 'Diluição para Brix específico', 
            icon: 'bi-droplet-fill', 
            favorito: true,
            frequencia: 58
        },
        { 
            id: 'brix-padrao', 
            nome: 'Brix Padrão', 
            categoria: 'Laboratório', 
            descricao: 'Padronização de valores Brix', 
            icon: 'bi-thermometer-half', 
            favorito: true,
            frequencia: 42
        },
        { 
            id: 'peso-liquido', 
            nome: 'Peso Líquido', 
            categoria: 'Produção', 
            descricao: 'Cálculo de peso líquido em embalagens', 
            icon: 'bi-box-seam', 
            favorito: false,
            frequencia: 35
        },
        { 
            id: 'diluicao', 
            nome: 'Diluição', 
            categoria: 'Laboratório', 
            descricao: 'Cálculos de diluição de amostras', 
            icon: 'bi-water', 
            favorito: false,
            frequencia: 30
        },
        { 
            id: 'rendimento', 
            nome: 'Rendimento de Produção', 
            categoria: 'Produção', 
            descricao: 'Cálculo de rendimento percentual', 
            icon: 'bi-graph-up-arrow', 
            favorito: false,
            frequencia: 28
        },
        { 
            id: 'acidez', 
            nome: 'Acidez', 
            categoria: 'Laboratório', 
            descricao: 'Medição de acidez em sucos', 
            icon: 'bi-eyedropper', 
            favorito: false,
            frequencia: 25
        },
        // Adicionar outros cálculos aqui conforme forem implementados
    ];
    
    initializeApp();
    setupSidebar();
    setupSearch();
    setupHelp();
    setupCalculatorInterface();
    setupThemeToggle();
    
    // Inicializa os tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    console.log('ZeloCalc: Módulo inicializado com sucesso!');
    
    /**
     * Inicialização do aplicativo
     */
    function initializeApp() {
        // Verificar preferência de tema salvo
        if (localStorage.getItem('zeloCalc_darkMode') === 'true') {
            document.body.classList.add('dark-mode');
            document.getElementById('themeToggle').innerHTML = '<i class="bi bi-moon"></i>';
        }
        
        // Configurar a calculadora inicial
        setupCalculator('finalizar-tanque');
    }
    
    /**
     * Configuração da Interface da Calculadora
     */
    function setupCalculatorInterface() {
        // Implementar funcionalidades da calculadora ativa
        
        // Botões de expansão
        const expandButtons = document.querySelectorAll('.btn-icon[title="Expandir"]');
        expandButtons.forEach(button => {
            button.addEventListener('click', function() {
                const calculatorContainer = this.closest('.calculation-container');
                
                if (calculatorContainer.classList.contains('expanded')) {
                    // Contrai
                    calculatorContainer.classList.remove('expanded');
                    document.body.classList.remove('calculator-expanded');
                    this.innerHTML = '<i class="bi bi-arrows-fullscreen"></i>';
                    this.setAttribute('title', 'Expandir');
                } else {
                    // Expande
                    calculatorContainer.classList.add('expanded');
                    document.body.classList.add('calculator-expanded');
                    this.innerHTML = '<i class="bi bi-fullscreen-exit"></i>';
                    this.setAttribute('title', 'Contrair');
                }
            });
        });
        
        // Botões de favorito
        const favoriteButtons = document.querySelectorAll('.btn-icon[title="Favoritar"]');
        favoriteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const calculatorId = this.closest('.calculation-container').id;
                const isFavorite = this.classList.toggle('active');
                
                if (isFavorite) {
                    this.innerHTML = '<i class="bi bi-star-fill"></i>';
                    // Salvar na lista de favoritos
                    const favorites = JSON.parse(localStorage.getItem('zeloCalc_favorites') || '[]');
                    if (!favorites.includes(calculatorId)) {
                        favorites.push(calculatorId);
                        localStorage.setItem('zeloCalc_favorites', JSON.stringify(favorites));
                    }
                } else {
                    this.innerHTML = '<i class="bi bi-star"></i>';
                    // Remover da lista de favoritos
                    const favorites = JSON.parse(localStorage.getItem('zeloCalc_favorites') || '[]');
                    const index = favorites.indexOf(calculatorId);
                    if (index > -1) {
                        favorites.splice(index, 1);
                        localStorage.setItem('zeloCalc_favorites', JSON.stringify(favorites));
                    }
                }
            });
        });
        
        // Sistema de navegação dos passos (1-2-3)
        setupStepNavigation();
    }
    
    /**
     * Configuração da Navegação por Passos
     */
    function setupStepNavigation() {
        // Botão Calcular (passo 1 para 2)
        document.getElementById('btn-calculate')?.addEventListener('click', function() {
            const volumeConcentrado = parseFloat(document.getElementById('volume_concentrado').value);
            const brixConcentrado = parseFloat(document.getElementById('brix_concentrado').value);
            const brixDesejado = parseFloat(document.getElementById('brix_desejado').value);
            
            if (isNaN(volumeConcentrado) || isNaN(brixConcentrado) || isNaN(brixDesejado)) {
                alert('Por favor, preencha todos os campos corretamente.');
                return;
            }
            
            // Ativar o passo 2 (fórmula)
            goToStep(2);
            
            // Atualizar os valores na tela de fórmula
            document.getElementById('calc-volume-concentrado').textContent = volumeConcentrado;
            document.getElementById('calc-brix-concentrado').textContent = brixConcentrado;
            document.getElementById('calc-brix-desejado').textContent = brixDesejado;
            
            // Calcular os resultados para mostrar no passo 3
            const aguaNecessaria = volumeConcentrado * ((brixConcentrado / brixDesejado) - 1);
            const volumeFinal = volumeConcentrado + aguaNecessaria;
            
            document.getElementById('result-agua').textContent = aguaNecessaria.toFixed(2);
            document.getElementById('result-volume-final').textContent = volumeFinal.toFixed(2);
            
            // Criar gráfico
            createTanqueChart(volumeConcentrado, aguaNecessaria);
        });
        
        // Botão Limpar
        document.getElementById('btn-reset')?.addEventListener('click', function() {
            const form = document.querySelector('.calculation-form');
            form.querySelectorAll('input').forEach(input => {
                input.value = '';
            });
        });
        
        // Botão Voltar (passo 2 para 1)
        document.getElementById('btn-back-to-input')?.addEventListener('click', function() {
            goToStep(1);
        });
        
        // Botão Ver Resultado (passo 2 para 3)
        document.getElementById('btn-show-result')?.addEventListener('click', function() {
            goToStep(3);
        });
        
        // Botão Voltar (passo 3 para 2)
        document.getElementById('btn-back-to-formula')?.addEventListener('click', function() {
            goToStep(2);
        });
        
        // Botão Novo Cálculo (passo 3 para 1)
        document.getElementById('btn-new-calculation')?.addEventListener('click', function() {
            goToStep(1);
        });
        
        // Botão Salvar Resultado
        document.getElementById('btn-save-result')?.addEventListener('click', function() {
            const volumeConcentrado = document.getElementById('calc-volume-concentrado').textContent;
            const brixConcentrado = document.getElementById('calc-brix-concentrado').textContent;
            const brixDesejado = document.getElementById('calc-brix-desejado').textContent;
            const aguaNecessaria = document.getElementById('result-agua').textContent;
            const volumeFinal = document.getElementById('result-volume-final').textContent;
            
            const resultData = {
                data: new Date().toISOString(),
                calculo: 'Finalização de Tanque',
                parametros: {
                    volumeConcentrado,
                    brixConcentrado,
                    brixDesejado
                },
                resultados: {
                    aguaNecessaria,
                    volumeFinal
                }
            };
            
            // Salvar o resultado no histórico
            const history = JSON.parse(localStorage.getItem('zeloCalc_history') || '[]');
            history.unshift(resultData);
            localStorage.setItem('zeloCalc_history', JSON.stringify(history.slice(0, 50))); // Manter apenas os 50 mais recentes
            
            alert('Resultado salvo com sucesso!');
        });
    }
    
    /**
     * Navegação para um passo específico
     * @param {number} step - Número do passo (1, 2 ou 3)
     */
    function goToStep(step) {
        // Atualizar os indicadores de passo
        const steps = document.querySelectorAll('.step');
        const stepLines = document.querySelectorAll('.step-line');
        
        steps.forEach((s, index) => {
            if (index + 1 < step) {
                s.classList.add('completed');
                s.classList.remove('active');
            } else if (index + 1 === step) {
                s.classList.add('active');
                s.classList.remove('completed');
            } else {
                s.classList.remove('active', 'completed');
            }
        });
        
        stepLines.forEach((line, index) => {
            if (index + 1 < step) {
                line.classList.add('active');
            } else {
                line.classList.remove('active');
            }
        });
        
        // Mostrar o painel correspondente
        const panels = document.querySelectorAll('.calculation-panel');
        panels.forEach((panel, index) => {
            if (index + 1 === step) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });
    }
    
    /**
     * Função para criar o gráfico do tanque
     */
    function createTanqueChart(volumeConcentrado, aguaNecessaria) {
        const ctx = document.getElementById('tanqueChart');
        
        // Destruir o gráfico existente, se houver
        if (window.tanqueChart) {
            window.tanqueChart.destroy();
        }
        
        // Criar novo gráfico
        window.tanqueChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Concentrado', 'Água'],
                datasets: [{
                    data: [volumeConcentrado, aguaNecessaria],
                    backgroundColor: [
                        'rgba(79, 70, 229, 0.8)',
                        'rgba(14, 165, 233, 0.8)'
                    ],
                    borderColor: [
                        'rgba(79, 70, 229, 1)',
                        'rgba(14, 165, 233, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.formattedValue || '';
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${label}: ${value} L (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Configuração de uma calculadora específica
     * @param {string} calculadoraId - ID da calculadora a ser configurada
     */
    function setupCalculator(calculadoraId) {
        // Esconder todas as calculadoras
        document.querySelectorAll('.calculation-container').forEach(container => {
            container.classList.remove('active');
        });
        
        // Mostrar a calculadora selecionada
        const selectedCalculator = document.getElementById(calculadoraId);
        if (selectedCalculator) {
            selectedCalculator.classList.add('active');
            
            // Reset para o passo 1 (valores de entrada)
            goToStep(1);
            
            // Verificar se é favorito
            const favoriteButton = selectedCalculator.querySelector('.btn-icon[title="Favoritar"]');
            if (favoriteButton) {
                const favorites = JSON.parse(localStorage.getItem('zeloCalc_favorites') || '[]');
                if (favorites.includes(calculadoraId)) {
                    favoriteButton.classList.add('active');
                    favoriteButton.innerHTML = '<i class="bi bi-star-fill"></i>';
                } else {
                    favoriteButton.classList.remove('active');
                    favoriteButton.innerHTML = '<i class="bi bi-star"></i>';
                }
            }
            
            // Resetar formulário
            const form = selectedCalculator.querySelector('.calculation-form');
            if (form) {
                form.querySelectorAll('input').forEach(input => {
                    input.value = '';
                });
            }
        } else {
            // Se não encontrar a calculadora, mostrar a tela de boas-vindas
            document.getElementById('welcome-screen').style.display = 'block';
        }
    }
    
    /**
     * Configuração do Mecanismo de Busca
     */
    function setupSearch() {
        const searchInput = document.getElementById('calculatorSearch');
        const searchResults = document.getElementById('searchResults');
        const clearButton = document.getElementById('clearSearch');
        
        if (!searchInput || !searchResults || !clearButton) return;
        
        // Exibe ou esconde o botão de limpar
        searchInput.addEventListener('input', function() {
            if (this.value.length > 0) {
                clearButton.style.display = 'block';
                performSearch(this.value);
            } else {
                clearButton.style.display = 'none';
                searchResults.style.display = 'none';
            }
        });
        
        // Limpa o campo de busca ao clicar no botão
        clearButton.addEventListener('click', function() {
            searchInput.value = '';
            clearButton.style.display = 'none';
            searchResults.style.display = 'none';
        });
        
        // Fecha os resultados ao clicar fora
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
        
        // Realiza a busca e exibe os resultados
        function performSearch(query) {
            if (query.length < 2) {
                searchResults.style.display = 'none';
                return;
            }
            
            query = query.toLowerCase();
            
            // Filtra os cálculos que correspondem à busca
            const matchingCalculos = calculosDisponiveis.filter(calculo => {
                return calculo.nome.toLowerCase().includes(query) || 
                       calculo.descricao.toLowerCase().includes(query) ||
                       calculo.categoria.toLowerCase().includes(query);
            });
            
            // Exibe os resultados
            if (matchingCalculos.length > 0) {
                searchResults.innerHTML = '';
                
                matchingCalculos.forEach(calculo => {
                    const resultItem = document.createElement('div');
                    resultItem.className = 'search-result-item';
                    resultItem.dataset.calculoId = calculo.id;
                    resultItem.dataset.tab = calculo.tab;
                    resultItem.dataset.subtab = calculo.subtab;
                    
                    // Highlight do texto que corresponde à busca
                    const nameHighlighted = highlightText(calculo.nome, query);
                    const descHighlighted = highlightText(calculo.descricao, query);
                    
                    resultItem.innerHTML = `
                        <div class="search-result-icon"><i class="bi ${calculo.icon}"></i></div>
                        <div class="search-result-text">
                            <div>${nameHighlighted}</div>
                            <div style="font-size: 0.8rem; color: var(--dark-light);">${descHighlighted}</div>
                        </div>
                        <div class="search-result-category">${calculo.categoria}</div>
                    `;
                    
                    resultItem.addEventListener('click', function() {
                        navigateToCalculator(this.dataset.calculoId, this.dataset.tab, this.dataset.subtab);
                        searchResults.style.display = 'none';
                        searchInput.value = '';
                        clearButton.style.display = 'none';
                    });
                    
                    searchResults.appendChild(resultItem);
                });
                
                searchResults.style.display = 'block';
            } else {
                searchResults.innerHTML = '<div class="p-3 text-center">Nenhum cálculo encontrado</div>';
                searchResults.style.display = 'block';
            }
        }
        
        // Destaca o texto que corresponde à busca
        function highlightText(text, query) {
            const regex = new RegExp('(' + query + ')', 'gi');
            return text.replace(regex, '<span class="search-result-highlight">$1</span>');
        }
        
        // Navega até o cálculo selecionado
        function navigateToCalculator(calculoId, tabId, subtabId) {
            // Ativa a aba principal
            const tabElement = document.querySelector(`button[data-bs-target="#${tabId}"]`);
            if (tabElement) {
                const tab = new bootstrap.Tab(tabElement);
                tab.show();
                
                // Ativa a subaba, se existir
                if (subtabId) {
                    setTimeout(() => {
                        const subtabElement = document.querySelector(`button[data-bs-target="#${subtabId}"]`);
                        if (subtabElement) {
                            const subtab = new bootstrap.Tab(subtabElement);
                            subtab.show();
                        }
                        
                        // Rola até o cálculo e destaca-o
                        setTimeout(() => {
                            const calculatorCard = document.querySelector(`#form-${calculoId.replace('_', '-')}`).closest('.card-calculator');
                            
                            if (calculatorCard) {
                                calculatorCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                
                                // Destaca o card brevemente
                                calculatorCard.classList.add('animate__animated', 'animate__pulse');
                                setTimeout(() => {
                                    calculatorCard.classList.remove('animate__animated', 'animate__pulse');
                                }, 1000);
                            }
                        }, 300);
                    }, 300);
                }
            }
        }
    }
    
    /**
     * Configuração da Barra Lateral
     */
    function setupSidebar() {
        const sidebarToggle = document.getElementById('sidebarToggle');
        const calcApp = document.querySelector('.calculos-app');
        
        if (!sidebarToggle || !calcApp) return;
        
        // Verificar preferência salva
        if (localStorage.getItem('zeloCalc_sidebarCollapsed') === 'true') {
            calcApp.classList.add('sidebar-collapsed');
            sidebarToggle.innerHTML = '<i class="bi bi-chevron-right"></i>';
        }
        
        // Implementar o toggle da barra lateral
        sidebarToggle.addEventListener('click', function() {
            calcApp.classList.toggle('sidebar-collapsed');
            
            if (calcApp.classList.contains('sidebar-collapsed')) {
                this.innerHTML = '<i class="bi bi-chevron-right"></i>';
                localStorage.setItem('zeloCalc_sidebarCollapsed', 'true');
            } else {
                this.innerHTML = '<i class="bi bi-chevron-left"></i>';
                localStorage.setItem('zeloCalc_sidebarCollapsed', 'false');
            }
        });
        
        // Itens de navegação
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('click', function() {
                // Se for uma categoria, mostrar lista de calculadoras dessa categoria
                if (this.dataset.category) {
                    const categoria = this.dataset.category;
                    console.log(`Mostrando calculadoras da categoria: ${categoria}`);
                    // Implementar a lógica de navegação para categoria
                    // TODO...
                    return;
                }
                
                // Se for uma calculadora específica, mostrar ela
                if (this.dataset.calc) {
                    // Remover a classe "active" de todos os itens
                    navItems.forEach(i => i.classList.remove('active'));
                    
                    // Adicionar a classe "active" neste item
                    this.classList.add('active');
                    
                    // Configurar a calculadora selecionada
                    setupCalculator(this.dataset.calc);
                }
            });
        });
    }
    
    /**
     * Configuração da Ajuda
     */
    function setupHelp() {
        const helpToggle = document.getElementById('helpToggle');
        const helpOverlay = document.getElementById('helpOverlay');
        const helpClose = document.getElementById('helpClose');
        
        if (!helpToggle || !helpOverlay || !helpClose) return;
        
        helpToggle.addEventListener('click', function() {
            helpOverlay.classList.add('active');
        });
        
        helpClose.addEventListener('click', function() {
            helpOverlay.classList.remove('active');
        });
        
        // Fecha ao clicar fora do diálogo
        helpOverlay.addEventListener('click', function(e) {
            if (!e.target.closest('.help-dialog')) {
                helpOverlay.classList.remove('active');
            }
        });
    }
    
    /**
     * Configuração do Alternador de Tema
     */
    function setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        
        if (!themeToggle) return;
        
        themeToggle.addEventListener('click', function() {
            const isDarkMode = document.body.classList.toggle('dark-mode');
            
            if (isDarkMode) {
                this.innerHTML = '<i class="bi bi-moon"></i>';
                localStorage.setItem('zeloCalc_darkMode', 'true');
            } else {
                this.innerHTML = '<i class="bi bi-sun"></i>';
                localStorage.setItem('zeloCalc_darkMode', 'false');
            }
        });
    }
    
    /**
     * Configuração das Calculadoras
     */
    function setupCalculators() {
        // Implementa os expandidores para as calculadoras
        const expandButtons = document.querySelectorAll('.expand-calculator');
        
        expandButtons.forEach(button => {
            button.addEventListener('click', function() {
                const card = this.closest('.card-calculator');
                
                if (card.classList.contains('expanded')) {
                    // Contrai
                    card.classList.remove('expanded');
                    card.style.width = '';
                    card.style.position = '';
                    card.style.zIndex = '';
                    card.style.left = '';
                    card.style.top = '';
                    this.innerHTML = '<i class="bi bi-arrows-fullscreen"></i>';
                } else {
                    // Expande
                    card.classList.add('expanded');
                    const rect = card.getBoundingClientRect();
                    card.style.width = '80%';
                    card.style.position = 'fixed';
                    card.style.zIndex = '1050';
                    card.style.left = '10%';
                    card.style.top = '5%';
                    this.innerHTML = '<i class="bi bi-fullscreen-exit"></i>';
                }
            });
        });
    }
    
    /**
     * Configuração dos Atalhos Rápidos
     */
    function setupQuickAccess() {
        const quickAccessItems = document.querySelectorAll('.quick-access-item:not(.show-all)');
        
        quickAccessItems.forEach(item => {
            item.addEventListener('click', function() {
                const calculoId = this.dataset.calculator;
                
                // Encontrar o cálculo no catálogo
                const calculo = calculosDisponiveis.find(c => c.id === calculoId);
                
                if (calculo) {
                    // Navegar até o cálculo
                    const tabElement = document.querySelector(`button[data-bs-target="#${calculo.tab}"]`);
                    if (tabElement) {
                        const tab = new bootstrap.Tab(tabElement);
                        tab.show();
                        
                        setTimeout(() => {
                            if (calculo.subtab) {
                                const subtabElement = document.querySelector(`button[data-bs-target="#${calculo.subtab}"]`);
                                if (subtabElement) {
                                    const subtab = new bootstrap.Tab(subtabElement);
                                    subtab.show();
                                }
                            }
                            
                            setTimeout(() => {
                                const calculatorCard = document.querySelector(`#form-${calculoId.replace('_', '-')}`).closest('.card-calculator');
                                
                                if (calculatorCard) {
                                    calculatorCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                    calculatorCard.classList.add('animate__animated', 'animate__pulse');
                                    
                                    setTimeout(() => {
                                        calculatorCard.classList.remove('animate__animated', 'animate__pulse');
                                    }, 1000);
                                }
                            }, 300);
                        }, 300);
                    }
                }
            });
        });
        
        // Ação para o botão "Ver Todos"
        const showAllButton = document.querySelector('.quick-access-item.show-all');
        if (showAllButton) {
            showAllButton.addEventListener('click', function() {
                // Implementar um modal ou dropdown com todos os cálculos
                alert('Esta funcionalidade mostrará uma lista completa dos 36 cálculos disponíveis.');
            });
        }
    }
});

/**
 * Funções para cálculos específicos
 * Cada calculadora precisa implementar sua própria função de cálculo
 */
function calculate(calculatorType) {
    console.log(`Calculando: ${calculatorType}`);
    
    switch(calculatorType) {
        case 'producao_200':
            calculatePesoLiquido();
            break;
        case 'producao_litro':
            calculateVolume();
            break;
        case 'rendimento':
            calculateRendimento();
            break;
        case 'eficiencia':
            calculateEficiencia();
            break;
        case 'controle':
            calculateControle();
            break;
        case 'finalizacao_tanque':
            calculateFinalizacaoTanque();
            break;
        case 'mistura_tanques':
            calculateMisturaTanques();
            break;
        default:
            console.warn('Tipo de cálculo não implementado:', calculatorType);
    }
}

// Cálculo do Peso Líquido
function calculatePesoLiquido() {
    const pesoBruto = parseFloat(document.getElementById('peso_bruto_200').value);
    const tara = parseFloat(document.getElementById('tara_200').value);
    
    if (isNaN(pesoBruto) || isNaN(tara)) {
        showError('error-peso_bruto_200', true);
        showError('error-tara_200', true);
        return;
    }
    
    const pesoLiquido = pesoBruto - tara;
    document.getElementById('result-value-producao_200').textContent = pesoLiquido.toFixed(2);
    document.getElementById('result-producao_200').style.display = 'block';
}

// Cálculo do Volume
function calculateVolume() {
    const pesoTotal = parseFloat(document.getElementById('peso_total').value);
    const densidade = parseFloat(document.getElementById('densidade').value);
    
    if (isNaN(pesoTotal) || isNaN(densidade) || densidade === 0) {
        showError('error-peso_total', true);
        showError('error-densidade', true);
        return;
    }
    
    const volume = pesoTotal / densidade;
    document.getElementById('result-value-producao_litro').textContent = volume.toFixed(2);
    document.getElementById('result-producao_litro').style.display = 'block';
}

// Cálculo do Rendimento
function calculateRendimento() {
    const entrada = parseFloat(document.getElementById('entrada_material').value);
    const saida = parseFloat(document.getElementById('saida_material').value);
    
    if (isNaN(entrada) || isNaN(saida) || entrada === 0) {
        showError('error-entrada_material', true);
        showError('error-saida_material', true);
        return;
    }
    
    const rendimento = (saida / entrada) * 100;
    document.getElementById('result-value-rendimento').textContent = rendimento.toFixed(2);
    document.getElementById('result-rendimento').style.display = 'block';
}

// Cálculo da Eficiência
function calculateEficiencia() {
    const tempoPadrao = parseFloat(document.getElementById('tempo_padrao').value);
    const tempoReal = parseFloat(document.getElementById('tempo_real').value);
    
    if (isNaN(tempoPadrao) || isNaN(tempoReal) || tempoReal === 0) {
        showError('error-tempo_padrao', true);
        showError('error-tempo_real', true);
        return;
    }
    
    const eficiencia = (tempoPadrao / tempoReal) * 100;
    document.getElementById('result-value-eficiencia').textContent = eficiencia.toFixed(2);
    document.getElementById('result-eficiencia').style.display = 'block';
}

// Cálculo do Controle Estatístico
function calculateControle() {
    const media = parseFloat(document.getElementById('media').value);
    const desvioPadrao = parseFloat(document.getElementById('desvio_padrao').value);
    
    if (isNaN(media) || isNaN(desvioPadrao)) {
        showError('error-media', true);
        showError('error-desvio_padrao', true);
        return;
    }
    
    const limiteSuperior = media + (3 * desvioPadrao);
    const limiteInferior = media - (3 * desvioPadrao);
    
    document.getElementById('result-value-lcs').textContent = limiteSuperior.toFixed(3);
    document.getElementById('result-value-lci').textContent = limiteInferior.toFixed(3);
    document.getElementById('result-controle').style.display = 'block';
}

// Cálculo da Finalização de Tanque
function calculateFinalizacaoTanque() {
    const volumeConcentrado = parseFloat(document.getElementById('volume_concentrado').value);
    const brixConcentrado = parseFloat(document.getElementById('brix_concentrado').value);
    const brixDesejado = parseFloat(document.getElementById('brix_desejado').value);
    
    if (isNaN(volumeConcentrado) || isNaN(brixConcentrado) || isNaN(brixDesejado) || brixDesejado === 0) {
        showError('error-volume_concentrado', true);
        showError('error-brix_concentrado', true);
        showError('error-brix_desejado', true);
        return;
    }
    
    if (brixConcentrado <= brixDesejado) {
        alert("O Brix do concentrado deve ser maior que o Brix desejado para fazer a diluição.");
        return;
    }
    
    const aguaNecessaria = volumeConcentrado * ((brixConcentrado / brixDesejado) - 1);
    const volumeFinal = volumeConcentrado + aguaNecessaria;
    
    document.getElementById('result-value-agua').textContent = aguaNecessaria.toFixed(2);
    document.getElementById('result-value-volume-final').textContent = volumeFinal.toFixed(2);
    document.getElementById('result-finalizacao_tanque').style.display = 'block';
}

// Cálculo da Mistura de Tanques
function calculateMisturaTanques() {
    const volumeTanque1 = parseFloat(document.getElementById('volume_tanque1').value);
    const brixTanque1 = parseFloat(document.getElementById('brix_tanque1').value);
    const volumeTanque2 = parseFloat(document.getElementById('volume_tanque2').value);
    const brixTanque2 = parseFloat(document.getElementById('brix_tanque2').value);
    
    if (isNaN(volumeTanque1) || isNaN(brixTanque1) || isNaN(volumeTanque2) || isNaN(brixTanque2)) {
        showError('error-volume_tanque1', true);
        showError('error-brix_tanque1', true);
        showError('error-volume_tanque2', true);
        showError('error-brix_tanque2', true);
        return;
    }
    
    const volumeTotal = volumeTanque1 + volumeTanque2;
    const brixFinal = ((volumeTanque1 * brixTanque1) + (volumeTanque2 * brixTanque2)) / volumeTotal;
    
    document.getElementById('result-value-brix-mistura').textContent = brixFinal.toFixed(2);
    document.getElementById('result-value-volume-mistura').textContent = volumeTotal.toFixed(2);
    document.getElementById('result-mistura_tanques').style.display = 'block';
}

/**
 * Funções Utilitárias
 */
function showError(errorId, show) {
    const errorElement = document.getElementById(errorId);
    if (errorElement) {
        errorElement.style.display = show ? 'block' : 'none';
    }
}

function resetCalculator(formId, resultId) {
    const form = document.getElementById(formId);
    const result = document.getElementById(resultId);
    
    if (form) form.reset();
    if (result) result.style.display = 'none';
    
    // Limpa todas as mensagens de erro
    const errorMessages = form.querySelectorAll('.error-message');
    errorMessages.forEach(error => {
        error.style.display = 'none';
    });
}

function copyResult(resultId, unit) {
    const resultElement = document.getElementById(resultId);
    const text = resultElement.textContent + ' ' + unit;
    
    navigator.clipboard.writeText(text).then(() => {
        // Feedback visual de cópia bem-sucedida
        const originalText = resultElement.textContent;
        resultElement.innerHTML = '<i class="bi bi-check2"></i> Copiado!';
        
        setTimeout(() => {
            resultElement.textContent = originalText;
        }, 1500);
    }).catch(err => {
        console.error('Erro ao copiar texto: ', err);
    });
}

/**
 * Efeitos visuais adicionais
 */
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('zelopack_dark_mode', isDarkMode);
}

// Verificar preferência de tema ao carregar
document.addEventListener('DOMContentLoaded', function() {
    const prefersDarkMode = localStorage.getItem('zelopack_dark_mode') === 'true';
    if (prefersDarkMode) {
        document.body.classList.add('dark-mode');
    }
});