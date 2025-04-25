/**
 * Script para funcionalidades de busca e filtro de laudos
 */

document.addEventListener('DOMContentLoaded', function() {
    // Verificar se estamos na página de busca
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        setupSearchForm();
    }
    
    // Configurar busca rápida
    setupQuickSearch();
});

/**
 * Configura o formulário de busca avançada
 */
function setupSearchForm() {
    const searchForm = document.getElementById('searchForm');
    const resultsContainer = document.getElementById('searchResults');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    // Adicionar evento para envio via AJAX
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Mostrar indicador de carregamento
        if (loadingIndicator) {
            loadingIndicator.classList.remove('d-none');
        }
        
        // Obter valores do formulário
        const formData = new FormData(searchForm);
        const searchParams = new URLSearchParams();
        
        // Converter FormData para URLSearchParams
        for (const [key, value] of formData.entries()) {
            if (value) { // Só adicionar parâmetros com valor
                searchParams.append(key, value);
            }
        }
        
        // Fazer requisição AJAX
        fetch('/reports/api/search?' + searchParams.toString())
            .then(response => response.json())
            .then(data => {
                // Esconder indicador de carregamento
                if (loadingIndicator) {
                    loadingIndicator.classList.add('d-none');
                }
                
                // Renderizar resultados
                renderSearchResults(data, resultsContainer);
            })
            .catch(error => {
                console.error('Erro na busca:', error);
                
                // Esconder indicador de carregamento
                if (loadingIndicator) {
                    loadingIndicator.classList.add('d-none');
                }
                
                // Mostrar mensagem de erro
                resultsContainer.innerHTML = `
                    <div class="alert alert-danger">
                        Ocorreu um erro ao processar sua busca. Por favor, tente novamente.
                    </div>
                `;
            });
    });
    
    // Configurar limpeza de formulário
    const resetButton = document.getElementById('resetSearch');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            searchForm.reset();
            if (resultsContainer) {
                resultsContainer.innerHTML = '';
            }
        });
    }
}

/**
 * Renderiza os resultados da busca
 * @param {Array} results - Array de objetos de resultado
 * @param {HTMLElement} container - Elemento onde renderizar os resultados
 */
function renderSearchResults(results, container) {
    if (!container) return;
    
    // Se não houver resultados
    if (results.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                Nenhum laudo encontrado com os critérios informados.
            </div>
        `;
        return;
    }
    
    // Construir tabela de resultados
    let html = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead class="table-primary">
                    <tr>
                        <th>Título</th>
                        <th>Categoria</th>
                        <th>Fornecedor</th>
                        <th>Data do Laudo</th>
                        <th>Arquivo</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    // Adicionar cada resultado
    results.forEach(report => {
        html += `
            <tr>
                <td>${report.title}</td>
                <td>${report.category || '-'}</td>
                <td>${report.supplier || '-'}</td>
                <td>${report.report_date || '-'}</td>
                <td>
                    <span class="badge bg-secondary">${report.file_type.toUpperCase()}</span>
                    ${report.original_filename}
                </td>
                <td>
                    <a href="/reports/view/${report.id}" class="btn btn-sm btn-info" title="Visualizar">
                        <i class="fas fa-eye"></i>
                    </a>
                    <a href="/reports/download/${report.id}" class="btn btn-sm btn-success" title="Baixar">
                        <i class="fas fa-download"></i>
                    </a>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
        <p class="text-muted">Encontrados ${results.length} laudos.</p>
    `;
    
    container.innerHTML = html;
}

/**
 * Configura a busca rápida no cabeçalho
 */
function setupQuickSearch() {
    const quickSearchInput = document.getElementById('quickSearch');
    const quickSearchResults = document.getElementById('quickSearchResults');
    
    if (!quickSearchInput || !quickSearchResults) return;
    
    // Variável para rastrear timeout (debounce)
    let searchTimeout;
    
    // Adicionar evento de input
    quickSearchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Limpar timeout anterior
        clearTimeout(searchTimeout);
        
        // Se o campo estiver vazio, limpar resultados
        if (query === '') {
            quickSearchResults.innerHTML = '';
            quickSearchResults.classList.add('d-none');
            return;
        }
        
        // Configurar debounce (500ms)
        searchTimeout = setTimeout(function() {
            // Fazer requisição AJAX para busca rápida
            fetch(`/reports/api/search?query=${encodeURIComponent(query)}&limit=5`)
                .then(response => response.json())
                .then(data => {
                    // Renderizar resultados rápidos
                    renderQuickSearchResults(data, quickSearchResults);
                })
                .catch(error => {
                    console.error('Erro na busca rápida:', error);
                    quickSearchResults.innerHTML = `
                        <div class="quick-search-error">
                            Erro ao processar busca
                        </div>
                    `;
                    quickSearchResults.classList.remove('d-none');
                });
        }, 500);
    });
    
    // Fechar resultados quando clicar fora
    document.addEventListener('click', function(e) {
        if (!quickSearchInput.contains(e.target) && !quickSearchResults.contains(e.target)) {
            quickSearchResults.classList.add('d-none');
        }
    });
}

/**
 * Renderiza os resultados da busca rápida
 * @param {Array} results - Array de objetos de resultado
 * @param {HTMLElement} container - Elemento onde renderizar os resultados
 */
function renderQuickSearchResults(results, container) {
    if (!container) return;
    
    // Se não houver resultados
    if (results.length === 0) {
        container.innerHTML = `
            <div class="quick-search-item">
                Nenhum laudo encontrado
            </div>
        `;
        container.classList.remove('d-none');
        return;
    }
    
    // Construir lista de resultados
    let html = '';
    
    // Adicionar cada resultado
    results.forEach(report => {
        html += `
            <a href="/reports/view/${report.id}" class="quick-search-item">
                <div class="quick-search-title">${report.title}</div>
                <div class="quick-search-meta">
                    ${report.category ? `<span class="badge bg-primary">${report.category}</span>` : ''}
                    ${report.supplier ? `<span class="badge bg-secondary">${report.supplier}</span>` : ''}
                    <small>${report.report_date || 'Sem data'}</small>
                </div>
            </a>
        `;
    });
    
    // Adicionar link para busca avançada
    html += `
        <a href="/reports/search" class="quick-search-footer">
            Busca avançada <i class="fas fa-arrow-right"></i>
        </a>
    `;
    
    container.innerHTML = html;
    container.classList.remove('d-none');
}
