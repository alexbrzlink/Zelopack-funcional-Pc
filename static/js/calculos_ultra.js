/**
 * ZeloPack Ultra Calcs 2025
 * JavaScript interativo para nova interface de calculadoras
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("ZeloPack Ultra Calcs 2025 - Inicializado!");
    
    // Configurar tema inicial com base na preferência do usuário
    setupTheme();
    
    // Configurar os eventos do header
    setupHeader();
    
    // Configurar a filtragem por tags
    setupTags();
    
    // Configurar as calculadoras
    setupCalculators();
    
    // Configurar overlay de ajuda
    setupHelp();
    
    // Exibir todos os resultados ocultos em modo de desenvolvimento
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        document.querySelectorAll('.result-container').forEach(container => {
            container.style.display = 'block';
        });
    }
});

/**
 * Configura o tema (claro/escuro) com base nas preferências
 */
function setupTheme() {
    // Verificar se existe uma preferência salva
    const darkMode = localStorage.getItem('zeloCalc_darkMode') === 'true';
    
    // Aplicar tema escuro se necessário
    if (darkMode) {
        document.body.classList.add('dark-mode');
        document.getElementById('themeBtn')?.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    // Ou usar preferência do sistema
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (prefersDarkMode && localStorage.getItem('zeloCalc_darkMode') === null) {
        document.body.classList.add('dark-mode');
        document.getElementById('themeBtn')?.innerHTML = '<i class="fas fa-sun"></i>';
    }
}

/**
 * Configura os eventos de interação do header
 */
function setupHeader() {
    // Toggle de tema claro/escuro
    const themeBtn = document.getElementById('themeBtn');
    if (themeBtn) {
        themeBtn.addEventListener('click', function() {
            const isDarkMode = document.body.classList.toggle('dark-mode');
            
            if (isDarkMode) {
                this.innerHTML = '<i class="fas fa-sun"></i>';
                localStorage.setItem('zeloCalc_darkMode', 'true');
            } else {
                this.innerHTML = '<i class="fas fa-moon"></i>';
                localStorage.setItem('zeloCalc_darkMode', 'false');
            }
        });
    }
    
    // Favoritos
    const favoritesBtn = document.getElementById('favoritesBtn');
    if (favoritesBtn) {
        favoritesBtn.addEventListener('click', function() {
            // Filtrar por favoritos
            const tagPill = document.querySelector('.tag-pill[data-tag="favorites"]');
            if (tagPill) {
                tagPill.click();
            }
        });
    }
    
    // Botão de ajuda
    const helpBtn = document.getElementById('helpBtn');
    if (helpBtn) {
        helpBtn.addEventListener('click', function() {
            document.getElementById('helpOverlay')?.classList.add('active');
        });
    }
    
    // Pesquisa
    const searchInput = document.getElementById('megaSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            
            // Se estiver vazio, mostrar tudo
            if (!query) {
                document.querySelectorAll('.calculator-card').forEach(card => {
                    card.style.display = 'flex';
                });
                return;
            }
            
            // Filtrar calculadoras
            document.querySelectorAll('.calculator-card').forEach(card => {
                const title = card.querySelector('.calculator-title h3')?.textContent.toLowerCase() || '';
                const subtitle = card.querySelector('.calculator-subtitle')?.textContent.toLowerCase() || '';
                const formulas = card.querySelector('.formula-content')?.textContent.toLowerCase() || '';
                
                if (title.includes(query) || subtitle.includes(query) || formulas.includes(query)) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });
        
        // Limpar pesquisa
        document.getElementById('clear-search')?.addEventListener('click', function() {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
        });
        
        // Pesquisa por voz (simulado)
        document.getElementById('voice-search')?.addEventListener('click', function() {
            alert('Funcionalidade de pesquisa por voz será implementada em uma atualização futura.');
        });
    }
}

/**
 * Configura a filtragem por tags/categorias
 */
function setupTags() {
    const tagPills = document.querySelectorAll('.tag-pill');
    
    tagPills.forEach(pill => {
        pill.addEventListener('click', function() {
            // Remover classe active de todas as pills
            tagPills.forEach(p => p.classList.remove('active'));
            
            // Adicionar classe active nesta pill
            this.classList.add('active');
            
            const tag = this.getAttribute('data-tag');
            
            // Filtrar calculadoras
            document.querySelectorAll('.calculator-card').forEach(card => {
                if (tag === 'all') {
                    card.style.display = 'flex';
                } else if (tag === 'favorites' && card.getAttribute('data-favorites') === 'true') {
                    card.style.display = 'flex';
                } else if (tag === 'recentes' && card.getAttribute('data-recentes') === 'true') {
                    card.style.display = 'flex';
                } else if (card.getAttribute('data-category') === tag) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

/**
 * Configura as interações das calculadoras
 */
function setupCalculators() {
    // Favoritar
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const card = this.closest('.calculator-card');
            const isFavorite = this.classList.toggle('active');
            
            if (isFavorite) {
                card.setAttribute('data-favorites', 'true');
            } else {
                card.setAttribute('data-favorites', 'false');
            }
            
            // Salvar preferência (opcional)
            const cardId = card.id;
            const favorites = JSON.parse(localStorage.getItem('zeloCalc_favorites') || '[]');
            
            if (isFavorite && !favorites.includes(cardId)) {
                favorites.push(cardId);
            } else if (!isFavorite && favorites.includes(cardId)) {
                const index = favorites.indexOf(cardId);
                favorites.splice(index, 1);
            }
            
            localStorage.setItem('zeloCalc_favorites', JSON.stringify(favorites));
        });
    });
    
    // Expandir
    const expandButtons = document.querySelectorAll('.expand-btn');
    expandButtons.forEach(button => {
        button.addEventListener('click', function() {
            const card = this.closest('.calculator-card');
            card.classList.toggle('expanded');
            
            if (card.classList.contains('expanded')) {
                card.style.position = 'fixed';
                card.style.top = '5%';
                card.style.left = '5%';
                card.style.width = '90%';
                card.style.height = '90%';
                card.style.zIndex = '1000';
                this.innerHTML = '<i class="fas fa-compress-alt"></i>';
            } else {
                card.style.position = '';
                card.style.top = '';
                card.style.left = '';
                card.style.width = '';
                card.style.height = '';
                card.style.zIndex = '';
                this.innerHTML = '<i class="fas fa-expand-alt"></i>';
            }
        });
    });
    
    // Configurar calculadora 1: Finalização de Tanque
    setupFinalizacaoTanque();
    
    // Configurar calculadora 2: Brix Padrão
    setupBrixPadrao();
    
    // Configurar calculadora 3: Peso Líquido
    setupPesoLiquido();
    
    // Configurar calculadora 4: Mistura de Tanques
    setupMisturaTanques();
    
    // Configurar calculadora 5: Rendimento
    setupRendimento();
    
    // Configurar calculadora 6: Diluição
    setupDiluicao();
    
    // Configurar todos os botões de reset
    document.querySelectorAll('.btn-reset').forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            if (form) {
                form.querySelectorAll('input[type="number"]').forEach(input => {
                    input.value = '';
                });
                
                // Ocultar resultado se visível
                const resultContainer = form.parentElement.querySelector('.result-container');
                if (resultContainer) {
                    resultContainer.style.display = 'none';
                }
            }
        });
    });
}

/**
 * Configuração da calculadora de Finalização de Tanque
 */
function setupFinalizacaoTanque() {
    const calcBtn = document.getElementById('calc-ft-btn');
    
    if (!calcBtn) return;
    
    calcBtn.addEventListener('click', function() {
        const volumeConcentrado = parseFloat(document.getElementById('volume_concentrado').value);
        const brixConcentrado = parseFloat(document.getElementById('brix_concentrado').value);
        const brixDesejado = parseFloat(document.getElementById('brix_desejado').value);
        
        if (isNaN(volumeConcentrado) || isNaN(brixConcentrado) || isNaN(brixDesejado) || brixDesejado === 0) {
            alert('Por favor, preencha todos os campos corretamente.');
            return;
        }
        
        // Calcular
        const aguaNecessaria = volumeConcentrado * ((brixConcentrado / brixDesejado) - 1);
        const volumeFinal = volumeConcentrado + aguaNecessaria;
        
        // Exibir resultados
        document.getElementById('ft-agua').textContent = aguaNecessaria.toFixed(2);
        document.getElementById('ft-vol-final').textContent = volumeFinal.toFixed(2);
        
        // Exibir container de resultados
        document.getElementById('result-finalizacao-tanque').style.display = 'block';
        
        // Criar gráfico
        createTanqueChart(volumeConcentrado, aguaNecessaria);
    });
}

/**
 * Criação do gráfico para Finalização de Tanque
 */
function createTanqueChart(volumeConcentrado, aguaNecessaria) {
    const ctx = document.getElementById('chart-finalizacao-tanque');
    
    if (!ctx) return;
    
    // Destruir gráfico existente se houver
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
                    'rgba(109, 40, 217, 0.8)',
                    'rgba(6, 182, 212, 0.8)'
                ],
                borderColor: [
                    'rgba(109, 40, 217, 1)',
                    'rgba(6, 182, 212, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw.toFixed(2);
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.raw / total) * 100).toFixed(1);
                            return `${label}: ${value} L (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true
            }
        }
    });
}

/**
 * Configuração da calculadora de Brix Padrão
 */
function setupBrixPadrao() {
    const calcBtn = document.getElementById('calc-bp-btn');
    
    if (!calcBtn) return;
    
    calcBtn.addEventListener('click', function() {
        const brixLeitura = parseFloat(document.getElementById('brix_leitura').value);
        const temperatura = parseFloat(document.getElementById('temperatura_amostra').value);
        const fatorCorrecao = parseFloat(document.getElementById('fator_correcao').value);
        
        if (isNaN(brixLeitura) || isNaN(temperatura) || isNaN(fatorCorrecao)) {
            alert('Por favor, preencha todos os campos corretamente.');
            return;
        }
        
        // Calcular
        // Fórmula simplificada: Brix Corrigido = Leitura × Fator + (0.055 × (Temperatura - 20))
        const brixCorrigido = (brixLeitura * fatorCorrecao) + (0.055 * (temperatura - 20));
        
        // Exibir resultados
        document.getElementById('bp-brix-corrigido').textContent = brixCorrigido.toFixed(2);
        
        // Exibir container de resultados
        document.getElementById('result-brix-padrao').style.display = 'block';
    });
}

/**
 * Configuração da calculadora de Peso Líquido
 */
function setupPesoLiquido() {
    const calcBtn = document.getElementById('calc-pl-btn');
    
    if (!calcBtn) return;
    
    calcBtn.addEventListener('click', function() {
        const pesoBruto = parseFloat(document.getElementById('peso_bruto').value);
        const tara = parseFloat(document.getElementById('peso_tara').value);
        
        if (isNaN(pesoBruto) || isNaN(tara)) {
            alert('Por favor, preencha todos os campos corretamente.');
            return;
        }
        
        // Calcular
        const pesoLiquido = pesoBruto - tara;
        
        // Exibir resultados
        document.getElementById('pl-peso-liquido').textContent = pesoLiquido.toFixed(2);
        
        // Exibir container de resultados
        document.getElementById('result-peso-liquido').style.display = 'block';
    });
}

/**
 * Configuração da calculadora de Mistura de Tanques
 */
function setupMisturaTanques() {
    const calcBtn = document.getElementById('calc-mt-btn');
    
    if (!calcBtn) return;
    
    calcBtn.addEventListener('click', function() {
        const volumeTanque1 = parseFloat(document.getElementById('volume_tanque1').value);
        const brixTanque1 = parseFloat(document.getElementById('brix_tanque1').value);
        const volumeTanque2 = parseFloat(document.getElementById('volume_tanque2').value);
        const brixTanque2 = parseFloat(document.getElementById('brix_tanque2').value);
        
        if (isNaN(volumeTanque1) || isNaN(brixTanque1) || isNaN(volumeTanque2) || isNaN(brixTanque2)) {
            alert('Por favor, preencha todos os campos corretamente.');
            return;
        }
        
        // Calcular
        const volumeTotal = volumeTanque1 + volumeTanque2;
        const brixFinal = ((volumeTanque1 * brixTanque1) + (volumeTanque2 * brixTanque2)) / volumeTotal;
        
        // Exibir resultados
        document.getElementById('mt-brix-final').textContent = brixFinal.toFixed(2);
        document.getElementById('mt-vol-total').textContent = volumeTotal.toFixed(2);
        
        // Exibir container de resultados
        document.getElementById('result-mistura-tanques').style.display = 'block';
        
        // Criar gráfico
        createMisturaChart(volumeTanque1, brixTanque1, volumeTanque2, brixTanque2);
    });
}

/**
 * Criação do gráfico para Mistura de Tanques
 */
function createMisturaChart(volumeTanque1, brixTanque1, volumeTanque2, brixTanque2) {
    const ctx = document.getElementById('chart-mistura-tanques');
    
    if (!ctx) return;
    
    // Destruir gráfico existente se houver
    if (window.misturaChart) {
        window.misturaChart.destroy();
    }
    
    // Criar novo gráfico
    window.misturaChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Tanque 1', 'Tanque 2', 'Mistura Final'],
            datasets: [
                {
                    label: 'Volume (L)',
                    data: [volumeTanque1, volumeTanque2, volumeTanque1 + volumeTanque2],
                    backgroundColor: ['rgba(109, 40, 217, 0.5)', 'rgba(6, 182, 212, 0.5)', 'rgba(244, 63, 94, 0.5)'],
                    borderColor: ['rgba(109, 40, 217, 1)', 'rgba(6, 182, 212, 1)', 'rgba(244, 63, 94, 1)'],
                    borderWidth: 1
                },
                {
                    label: 'Brix (°Bx)',
                    data: [brixTanque1, brixTanque2, ((volumeTanque1 * brixTanque1) + (volumeTanque2 * brixTanque2)) / (volumeTanque1 + volumeTanque2)],
                    backgroundColor: ['rgba(109, 40, 217, 0.2)', 'rgba(6, 182, 212, 0.2)', 'rgba(244, 63, 94, 0.2)'],
                    borderColor: ['rgba(109, 40, 217, 1)', 'rgba(6, 182, 212, 1)', 'rgba(244, 63, 94, 1)'],
                    borderWidth: 1,
                    type: 'line',
                    yAxisID: 'y1',
                    order: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Volume (L)'
                    }
                },
                y1: {
                    beginAtZero: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false
                    },
                    title: {
                        display: true,
                        text: 'Brix (°Bx)'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Configuração da calculadora de Rendimento
 */
function setupRendimento() {
    const calcBtn = document.getElementById('calc-rend-btn');
    
    if (!calcBtn) return;
    
    calcBtn.addEventListener('click', function() {
        const entradaMaterial = parseFloat(document.getElementById('entrada_material').value);
        const saidaMaterial = parseFloat(document.getElementById('saida_material').value);
        
        if (isNaN(entradaMaterial) || isNaN(saidaMaterial) || entradaMaterial === 0) {
            alert('Por favor, preencha todos os campos corretamente.');
            return;
        }
        
        // Calcular
        const rendimento = (saidaMaterial / entradaMaterial) * 100;
        
        // Exibir resultados
        document.getElementById('rend-percentual').textContent = rendimento.toFixed(2);
        
        // Exibir container de resultados
        document.getElementById('result-rendimento').style.display = 'block';
    });
}

/**
 * Configuração da calculadora de Diluição
 */
function setupDiluicao() {
    const calcBtn = document.getElementById('calc-dil-btn');
    
    if (!calcBtn) return;
    
    calcBtn.addEventListener('click', function() {
        const concentracaoInicial = parseFloat(document.getElementById('concentracao_inicial').value);
        const volumeInicial = parseFloat(document.getElementById('volume_inicial').value);
        const concentracaoFinal = parseFloat(document.getElementById('concentracao_final').value);
        
        if (isNaN(concentracaoInicial) || isNaN(volumeInicial) || isNaN(concentracaoFinal) || concentracaoFinal === 0) {
            alert('Por favor, preencha todos os campos corretamente.');
            return;
        }
        
        // Calcular
        const volumeFinal = (concentracaoInicial * volumeInicial) / concentracaoFinal;
        const volumeDiluente = volumeFinal - volumeInicial;
        
        // Exibir resultados
        document.getElementById('dil-volume-final').textContent = volumeFinal.toFixed(2);
        document.getElementById('dil-volume-diluente').textContent = volumeDiluente.toFixed(2);
        
        // Exibir container de resultados
        document.getElementById('result-diluicao').style.display = 'block';
    });
}

/**
 * Configuração do overlay de ajuda
 */
function setupHelp() {
    // Fechar ajuda
    const closeHelp = document.getElementById('closeHelp');
    const helpOverlay = document.getElementById('helpOverlay');
    
    if (closeHelp && helpOverlay) {
        closeHelp.addEventListener('click', function() {
            helpOverlay.classList.remove('active');
        });
        
        // Fechar ao clicar fora do diálogo
        helpOverlay.addEventListener('click', function(e) {
            if (e.target === helpOverlay) {
                helpOverlay.classList.remove('active');
            }
        });
    }
}