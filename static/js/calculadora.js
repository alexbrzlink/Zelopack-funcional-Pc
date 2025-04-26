/**
 * ZeloCalc - Módulo de cálculos técnicos para o Zelopack
 * Versão 3.0 - Implementação otimizada e corrigida dos cálculos
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('ZeloCalc 3.0: Inicializando módulo de cálculos técnicos...');
    
    // Configuração geral da interface
    setupInterface();
    
    // Configuração dos handlers dos botões de cálculo
    setupCalculos();
    
    // Tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    console.log('ZeloCalc 3.0: Módulo inicializado com sucesso!');
});

/**
 * Configura a interface geral do módulo de cálculos
 */
function setupInterface() {
    // Expandir/colapsar categorias
    document.querySelectorAll('.calculo-category').forEach(category => {
        category.addEventListener('click', function() {
            const items = document.querySelectorAll('.calculo-item[data-target^="' + this.dataset.category + '"]');
            items.forEach(item => {
                item.classList.toggle('collapsed');
            });
            this.querySelector('.fa-chevron-down').classList.toggle('fa-rotate-180');
        });
    });
    
    // Troca de cálculos ao clicar nos itens da lista
    document.querySelectorAll('.calculo-item').forEach(item => {
        item.addEventListener('click', function() {
            // Remover classe ativa de todos os itens
            document.querySelectorAll('.calculo-item').forEach(i => i.classList.remove('active'));
            // Adicionar classe ativa ao item clicado
            this.classList.add('active');
            
            // Esconder todas as áreas de cálculo
            document.querySelectorAll('.calculo-area').forEach(area => area.classList.remove('active'));
            
            // Mostrar a área correspondente ao item clicado
            const targetArea = document.getElementById(this.dataset.target + '-area');
            if (targetArea) {
                targetArea.classList.add('active');
                // Garantir que a área de resultado esteja oculta
                const resultadoArea = targetArea.querySelector('.resultado-area');
                if (resultadoArea) {
                    resultadoArea.style.display = 'none';
                }
            } else {
                console.warn('Área de cálculo não encontrada para: ' + this.dataset.target);
                // Mostrar mensagem de área em construção
                const emptyState = document.getElementById('calculo-empty-state');
                if (emptyState) {
                    emptyState.innerHTML = `
                        <div class="empty-state-content">
                            <i class="fas fa-tools fa-3x mb-3 text-primary"></i>
                            <h4>Cálculo em Implementação</h4>
                            <p>O cálculo "${this.textContent.trim()}" está sendo desenvolvido e estará disponível em breve.</p>
                        </div>
                    `;
                    emptyState.classList.add('active');
                }
            }
        });
    });
    
    // Configurar botões de limpar
    document.querySelectorAll('.btn-clear').forEach(btn => {
        btn.addEventListener('click', function() {
            const area = this.closest('.calculo-area');
            const inputs = area.querySelectorAll('input:not([type="hidden"])');
            inputs.forEach(input => {
                if (input.classList.contains('preserve-on-clear')) {
                    return;
                }
                input.value = '';
            });
            // Ocultar área de resultado
            const resultadoArea = area.querySelector('.resultado-area');
            if (resultadoArea) {
                resultadoArea.style.display = 'none';
            }
        });
    });
    
    // Busca de cálculos
    const searchInput = document.getElementById('searchCalculo');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            
            document.querySelectorAll('.calculo-item').forEach(item => {
                const name = item.textContent.toLowerCase();
                if (name.includes(query)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
            
            // Mostrar/ocultar categorias adequadamente
            if (query === '') {
                document.querySelectorAll('.calculo-category').forEach(cat => {
                    cat.style.display = '';
                });
            } else {
                document.querySelectorAll('.calculo-category').forEach(category => {
                    const categoryName = category.dataset.category;
                    const hasVisibleItems = Array.from(
                        document.querySelectorAll(`.calculo-item[data-target^="${categoryName}"]`)
                    ).some(item => item.style.display !== 'none');
                    
                    category.style.display = hasVisibleItems ? '' : 'none';
                });
            }
        });
    }
}

/**
 * Configura os handlers para todos os cálculos
 */
function setupCalculos() {
    // Produção 200g
    const btnCalculaPeso200g = document.getElementById('calculaPeso200g');
    if (btnCalculaPeso200g) {
        btnCalculaPeso200g.addEventListener('click', function() {
            calcularPeso200g();
        });
    }
    
    // Ratio
    const btnCalcularRatio = document.getElementById('calcularRatio');
    if (btnCalcularRatio) {
        btnCalcularRatio.addEventListener('click', function() {
            calcularRatio();
        });
    }
    
    // Ratio Simples
    const btnCalcularRatioSimples = document.getElementById('calcularRatioSimples');
    if (btnCalcularRatioSimples) {
        btnCalcularRatioSimples.addEventListener('click', function() {
            calcularRatioAlt();
        });
    }
    
    // Densidade
    const btnCalcularDensidade = document.getElementById('calculaDensidade');
    if (btnCalcularDensidade) {
        btnCalcularDensidade.addEventListener('click', function() {
            calcularDensidade();
        });
    }
    
    // Acidez
    const btnCalcularAcidez = document.getElementById('calcularAcidez');
    if (btnCalcularAcidez) {
        btnCalcularAcidez.addEventListener('click', function() {
            calcularAcidez();
        });
    }
    
    // Produção Litro
    const btnCalcularProducaoLitro = document.getElementById('calcularProducaoLitro');
    if (btnCalcularProducaoLitro) {
        btnCalcularProducaoLitro.addEventListener('click', function() {
            calcularProducaoLitro();
        });
    }
}

/**
 * Implementação do cálculo de Produção 200g
 */
function calcularPeso200g() {
    const pesoBruto = parseFloat(document.getElementById('peso_bruto').value) || 0;
    const tara = parseFloat(document.getElementById('peso_tara').value) || 0;
    const pesoEspecificado = parseFloat(document.getElementById('peso_especificado').value) || 200;
    const tolerancia = parseFloat(document.getElementById('tolerancia').value) || 2.5;
    
    if (pesoBruto <= 0 || tara <= 0) {
        alert('Por favor, preencha o peso bruto e a tara corretamente.');
        return;
    }
    
    // Calcular peso líquido
    const pesoLiquido = pesoBruto - tara;
    
    // Verificar tolerância
    const limiteInferior = pesoEspecificado * (1 - (tolerancia / 100));
    const limiteSuperior = pesoEspecificado * (1 + (tolerancia / 100));
    const desvio = ((pesoLiquido - pesoEspecificado) / pesoEspecificado) * 100;
    const diferencaAbsoluta = pesoLiquido - pesoEspecificado;
    
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
    
    // Exibir resultados
    document.getElementById('valor-peso-liquido').textContent = pesoLiquido.toFixed(2) + ' g';
    document.getElementById('status-peso').textContent = status;
    document.getElementById('desvio-peso').textContent = desvio.toFixed(2) + '%';
    
    // Atualizar fórmula
    document.getElementById('formula-bruto').textContent = pesoBruto.toFixed(2);
    document.getElementById('formula-tara').textContent = tara.toFixed(2);
    document.getElementById('formula-liquido').textContent = pesoLiquido.toFixed(2);
    
    // Atualizar detalhes
    document.getElementById('tolerancia-min').textContent = limiteInferior.toFixed(2) + ' g';
    document.getElementById('tolerancia-max').textContent = limiteSuperior.toFixed(2) + ' g';
    document.getElementById('diferenca-abs').textContent = diferencaAbsoluta.toFixed(2) + ' g';
    
    // Exibir área de resultado
    document.getElementById('resultado-peso200g').style.display = 'block';
    
    // Aplicar estilo conforme status
    const pesoStatus = document.querySelector('.peso-status');
    pesoStatus.className = 'alert peso-status';
    pesoStatus.classList.add(statusClass);
    
    const pesoDesvio = document.querySelector('.peso-desvio');
    pesoDesvio.className = 'alert peso-desvio';
    pesoDesvio.classList.add(statusClass);
}

/**
 * Implementação do cálculo de Ratio
 */
function calcularRatio() {
    const brix = parseFloat(document.getElementById('ratio_brix').value) || 0;
    const acidez = parseFloat(document.getElementById('ratio_acidez').value) || 0;
    
    if (brix <= 0 || acidez <= 0) {
        alert('Por favor, preencha o Brix e a acidez corretamente.');
        return;
    }
    
    // Calcular ratio
    const ratio = brix / acidez;
    
    // Exibir resultado
    const resultadoArea = document.getElementById('resultado-ratio');
    if (resultadoArea) {
        resultadoArea.innerHTML = `
            <div class="resultado-header">
                <h4><i class="fas fa-check-circle"></i> Resultado do Cálculo</h4>
                <button class="btn btn-sm btn-primary print-btn">
                    <i class="fas fa-print"></i> Imprimir
                </button>
            </div>
            
            <div class="resultado-value" id="resultado_ratio_valor">${ratio.toFixed(1)}</div>
            
            <div class="resultado-formula">
                <div>Ratio = Brix / Acidez</div>
                <div>Ratio = ${brix.toFixed(1)} / ${acidez.toFixed(3)} = ${ratio.toFixed(1)}</div>
            </div>
            
            <div class="resultado-interpretation">
                <div class="alert ${ratio < 12 ? 'alert-warning' : (ratio > 18 ? 'alert-info' : 'alert-success')}">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong>Interpretação:</strong> 
                    ${ratio < 12 ? 'Produto com predominância ácida.' : 
                      (ratio > 18 ? 'Produto com predominância doce.' : 
                       'Ratio ideal (balanceado).')}
                </div>
            </div>
        `;
        
        resultadoArea.style.display = 'block';
    }
}

/**
 * Implementação do cálculo de Ratio Alternativo (para o segundo botão)
 */
function calcularRatioAlt() {
    const brix = parseFloat(document.getElementById('brix_ratio').value) || 0;
    const acidez = parseFloat(document.getElementById('acidez_ratio').value) || 0;
    
    if (brix <= 0 || acidez <= 0) {
        alert('Por favor, preencha o Brix e a acidez corretamente.');
        return;
    }
    
    // Calcular ratio
    const ratio = brix / acidez;
    
    // Exibir resultado
    const resultadoArea = document.getElementById('resultado-ratio-simples');
    if (resultadoArea) {
        resultadoArea.innerHTML = `
            <div class="resultado-header">
                <h4><i class="fas fa-check-circle"></i> Resultado do Cálculo</h4>
                <button class="btn btn-sm btn-primary print-btn">
                    <i class="fas fa-print"></i> Imprimir
                </button>
            </div>
            
            <div class="resultado-value">${ratio.toFixed(1)}</div>
            
            <div class="resultado-formula">
                <div>Ratio = Brix / Acidez</div>
                <div>Ratio = ${brix.toFixed(1)} / ${acidez.toFixed(2)} = ${ratio.toFixed(1)}</div>
            </div>
            
            <div class="resultado-interpretation">
                <div class="alert ${ratio < 12 ? 'alert-warning' : (ratio > 18 ? 'alert-info' : 'alert-success')}">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong>Interpretação:</strong> 
                    ${ratio < 12 ? 'Produto com predominância ácida.' : 
                      (ratio > 18 ? 'Produto com predominância doce.' : 
                       'Ratio ideal (balanceado).')}
                </div>
            </div>
        `;
        
        resultadoArea.style.display = 'block';
    }
}

/**
 * Implementação do cálculo de Densidade
 */
function calcularDensidade() {
    const massa = parseFloat(document.getElementById('densidade_massa').value) || 0;
    const volume = parseFloat(document.getElementById('densidade_volume').value) || 0;
    
    if (massa <= 0 || volume <= 0) {
        alert('Por favor, preencha a massa e o volume corretamente.');
        return;
    }
    
    // Calcular densidade
    const densidade = massa / volume;
    
    // Exibir resultado
    const resultadoArea = document.getElementById('resultado-densidade');
    if (resultadoArea) {
        resultadoArea.innerHTML = `
            <div class="resultado-header">
                <h4><i class="fas fa-check-circle"></i> Resultado do Cálculo</h4>
                <button class="btn btn-sm btn-primary print-btn">
                    <i class="fas fa-print"></i> Imprimir
                </button>
            </div>
            
            <div class="resultado-value" id="resultado_densidade_valor">${densidade.toFixed(3)} g/mL</div>
            
            <div class="resultado-formula">
                <div>Densidade = Massa / Volume</div>
                <div>Densidade = ${massa.toFixed(1)} g / ${volume.toFixed(1)} mL = ${densidade.toFixed(3)} g/mL</div>
            </div>
            
            <div class="resultado-interpretation">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong>Equivalente a:</strong> ${(densidade * 1000).toFixed(1)} kg/m³
                </div>
            </div>
        `;
        
        resultadoArea.style.display = 'block';
    }
}

/**
 * Implementação do cálculo de Acidez
 */
function calcularAcidez() {
    const volumeAmostra = parseFloat(document.getElementById('volume_amostra').value) || 0;
    const fatorTitulacao = parseFloat(document.getElementById('fator_titulacao').value) || 0;
    const volumeNaoh = parseFloat(document.getElementById('volume_naoh').value) || 0;
    
    if (volumeAmostra <= 0 || fatorTitulacao <= 0 || volumeNaoh <= 0) {
        alert('Por favor, preencha todos os campos corretamente.');
        return;
    }
    
    // Calcular acidez
    const acidez = (volumeNaoh * fatorTitulacao * 100) / volumeAmostra;
    
    // Exibir resultado
    const resultadoArea = document.getElementById('resultado-acidez');
    if (resultadoArea) {
        resultadoArea.innerHTML = `
            <div class="resultado-header">
                <h4><i class="fas fa-check-circle"></i> Resultado do Cálculo</h4>
                <button class="btn btn-sm btn-primary print-btn">
                    <i class="fas fa-print"></i> Imprimir
                </button>
            </div>
            
            <div class="resultado-value" id="resultado_acidez_valor">${acidez.toFixed(3)}%</div>
            
            <div class="resultado-formula">
                <div>Acidez (%) = (Volume NaOH × Fator × 100) / Volume da Amostra</div>
                <div>Acidez = (${volumeNaoh.toFixed(1)} × ${fatorTitulacao.toFixed(3)} × 100) / ${volumeAmostra.toFixed(1)} = ${acidez.toFixed(3)}%</div>
            </div>
        `;
        
        resultadoArea.style.display = 'block';
    }
}

/**
 * Implementação do cálculo de Produção em Litros
 */
function calcularProducaoLitro() {
    const pesoTotal = parseFloat(document.getElementById('peso_total').value) || 0;
    const densidade = parseFloat(document.getElementById('densidade_pl').value) || 1.045;
    
    if (pesoTotal <= 0) {
        alert('Por favor, preencha o peso total corretamente.');
        return;
    }
    
    // Calcular volume em litros
    const volumeLitros = pesoTotal / densidade;
    
    // Exibir resultado
    const resultadoArea = document.getElementById('resultado-producao-litro');
    if (resultadoArea) {
        resultadoArea.innerHTML = `
            <div class="resultado-header">
                <h4><i class="fas fa-check-circle"></i> Resultado do Cálculo</h4>
                <button class="btn btn-sm btn-primary print-btn">
                    <i class="fas fa-print"></i> Imprimir
                </button>
            </div>
            
            <div class="resultado-value" id="resultado_volume_valor">${volumeLitros.toFixed(1)} L</div>
            
            <div class="resultado-formula">
                <div>Volume (L) = Peso Total (kg) / Densidade (kg/L)</div>
                <div>Volume = ${pesoTotal.toFixed(1)} / ${densidade.toFixed(3)} = ${volumeLitros.toFixed(1)} L</div>
            </div>
            
            <div class="resultado-equivalente">
                <div>Equivalente a: ${(volumeLitros * 1000).toFixed(0)} mL ou ${(volumeLitros / 1000).toFixed(3)} m³</div>
            </div>
        `;
        
        resultadoArea.style.display = 'block';
    }
}