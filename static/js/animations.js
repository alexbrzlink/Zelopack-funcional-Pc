/**
 * ZELOPACK - Animações Globais
 * Este arquivo contém as animações JavaScript utilizadas em todo o sistema
 */

// Namespace global para as animações
window.ZelopackAnimations = {
    // Animações para elementos
    pulseElement: function(element) {
        if (!element) return;
        element.classList.add('animate-pulse');
        setTimeout(() => {
            element.classList.remove('animate-pulse');
        }, 1000);
    },
    
    pulse: function(element) {
        if (!element) return;
        element.classList.add('animate-pulse');
        setTimeout(() => {
            element.classList.remove('animate-pulse');
        }, 1000);
    },
    
    shake: function(element) {
        if (!element) return;
        element.classList.add('animate-shake');
        setTimeout(() => {
            element.classList.remove('animate-shake');
        }, 800);
    },
    
    elementHoverIn: function(element) {
        if (!element) return;
        element.classList.add('element-hovered');
        element.style.transform = 'translateY(-3px)';
        element.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)';
        element.style.transition = 'all 0.3s ease';
    },
    
    elementHoverOut: function(element) {
        if (!element) return;
        element.classList.remove('element-hovered');
        element.style.transform = '';
        element.style.boxShadow = '';
    },
    
    // Outros efeitos visuais
    showMessage: function(message, type = 'info') {
        if (typeof showFlashMessage === 'function') {
            return showFlashMessage(message, type);
        } else {
            // Implementação de fallback
            const alertClass = {
                'success': 'alert-success',
                'error': 'alert-danger',
                'warning': 'alert-warning',
                'info': 'alert-info'
            }[type] || 'alert-info';
            
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert ${alertClass} alert-dismissible fade show`;
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            // Adicionar ao topo da página
            const container = document.querySelector('.container');
            if (container) {
                container.insertBefore(alertDiv, container.firstChild);
            } else {
                document.body.insertBefore(alertDiv, document.body.firstChild);
            }
            
            // Auto-remover após 5 segundos
            setTimeout(() => {
                alertDiv.classList.add('fade');
                setTimeout(() => alertDiv.remove(), 500);
            }, 5000);
            
            return alertDiv;
        }
    },
    
    showLoading: function(message = 'Carregando...', type = 'spinner') {
        if (typeof showLoading === 'function') {
            showLoading(message, type);
        } else {
            // // // console.log('Loading: ' + message);
        }
    },
    
    hideLoading: function() {
        if (typeof hideLoading === 'function') {
            hideLoading();
        }
    },
    
    showTooltip: function(element, message) {
        if (!element) return;
        
        // Criar tooltip temporário
        const tooltip = document.createElement('div');
        tooltip.className = 'custom-tooltip animate-fade-in';
        tooltip.style.position = 'absolute';
        tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        tooltip.style.color = 'white';
        tooltip.style.padding = '8px 12px';
        tooltip.style.borderRadius = '6px';
        tooltip.style.fontSize = '0.9rem';
        tooltip.style.maxWidth = '250px';
        tooltip.style.zIndex = '9999';
        tooltip.style.pointerEvents = 'none';
        tooltip.textContent = message;
        
        // Inserir no documento
        document.body.appendChild(tooltip);
        
        // Posicionar tooltip
        const rect = element.getBoundingClientRect();
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
        tooltip.style.left = (rect.left + (rect.width/2) - (tooltip.offsetWidth/2)) + 'px';
        
        // Remover após alguns segundos
        setTimeout(() => {
            tooltip.classList.remove('animate-fade-in');
            tooltip.classList.add('animate-fade-out');
            
            setTimeout(() => {
                if (tooltip.parentNode) {
                    tooltip.parentNode.removeChild(tooltip);
                }
            }, 300);
        }, 3000);
    }
};

// Garantir que as funções estejam disponíveis globalmente para compatibilidade
function elementHoverIn(element) {
    window.ZelopackAnimations.elementHoverIn(element);
}

function elementHoverOut(element) {
    window.ZelopackAnimations.elementHoverOut(element);
}

function showTooltip(element, message) {
    window.ZelopackAnimations.showTooltip(element, message);
}

// Função global para mostrar mensagens flash
function showFlashMessage(message, type = 'info') {
    return window.ZelopackAnimations.showMessage(message, type);
}

// Funções globais para loading
function showLoading(message = 'Carregando...', type = 'spinner') {
    // Criar overlay de loading
    let loadingOverlay = document.getElementById('loading-overlay');
    if (!loadingOverlay) {
        loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'loading-overlay';
        loadingOverlay.style.position = 'fixed';
        loadingOverlay.style.top = '0';
        loadingOverlay.style.left = '0';
        loadingOverlay.style.width = '100%';
        loadingOverlay.style.height = '100%';
        loadingOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        loadingOverlay.style.zIndex = '9999';
        loadingOverlay.style.display = 'flex';
        loadingOverlay.style.justifyContent = 'center';
        loadingOverlay.style.alignItems = 'center';
        loadingOverlay.style.flexDirection = 'column';
        loadingOverlay.style.color = 'white';
        
        const spinnerDiv = document.createElement('div');
        spinnerDiv.className = 'spinner-border text-light';
        spinnerDiv.setAttribute('role', 'status');
        spinnerDiv.style.width = '3rem';
        spinnerDiv.style.height = '3rem';
        spinnerDiv.innerHTML = '<span class="visually-hidden">Carregando...</span>';
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'loading-message mt-2';
        messageDiv.textContent = message;
        
        loadingOverlay.appendChild(spinnerDiv);
        loadingOverlay.appendChild(messageDiv);
        
        document.body.appendChild(loadingOverlay);
    } else {
        const messageDiv = loadingOverlay.querySelector('.loading-message');
        if (messageDiv) {
            messageDiv.textContent = message;
        }
        loadingOverlay.style.display = 'flex';
    }
}

function hideLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

// Para garantir retrocompatibilidade
if (typeof window.ZelopackAnimations === 'undefined') {
    console.error('ZelopackAnimations não foi inicializado corretamente. Recriando objeto...');
    window.ZelopackAnimations = {
        elementHoverIn: elementHoverIn,
        elementHoverOut: elementHoverOut,
        showTooltip: showTooltip,
        pulse: function(element) {
            if (!element) return;
            element.classList.add('animate-pulse');
            setTimeout(() => { element.classList.remove('animate-pulse'); }, 1000);
        },
        pulseElement: function(element) {
            if (!element) return;
            element.classList.add('animate-pulse');
            setTimeout(() => { element.classList.remove('animate-pulse'); }, 1000);
        },
        shake: function(element) {
            if (!element) return;
            element.classList.add('animate-shake');
            setTimeout(() => { element.classList.remove('animate-shake'); }, 800);
        },
        showMessage: function(message, type = 'info') {
            if (typeof showFlashMessage === 'function') {
                return showFlashMessage(message, type);
            } else {
                alert(message);
            }
        },
        showLoading: function(message = 'Carregando...', type = 'spinner') {
            if (typeof showLoading === 'function') {
                showLoading(message, type);
            } else {
                // // // console.log(message);
            }
        },
        hideLoading: function() {
            if (typeof hideLoading === 'function') {
                hideLoading();
            }
        }
    };
}

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // // // console.log('Zelopack Animations: Inicializado com sucesso!');
    
    // Inicializar todas as animações
    initializeAnimations();
    
    // Configurar observadores para conteúdo dinâmico
    setupDynamicContentObservers();
    
    // Inicializar tooltips e popovers do Bootstrap (se disponível)
    initializeBootstrapComponents();
});

/**
 * Inicializa todas as animações principais
 */
function initializeAnimations() {
    // Animações para cards
    animateElementsOnScroll('.card', 'animate-fade-in-up');
    
    // Animações para elementos do dashboard
    animateElementsOnScroll('.dashboard-card', 'animate-fade-in-up');
    animateElementsOnScroll('.stat-number', 'animate-fade-in');
    
    // Configurar animações para alertas
    setupAlertAnimations();
    
    // Configurar animações para formulários
    setupFormAnimations();
    
    // Animações para tabelas
    setupTableAnimations();
    
    // Animar elementos sequencialmente baseado na classe .delay-*
    animateSequentially('[class*="animate-"]');
}

/**
 * Configura animações para formulários
 */
function setupFormAnimations() {
    // Animar labels de formulários quando o input for focado
    const formInputs = document.querySelectorAll('.form-control, .form-select');
    
    formInputs.forEach(input => {
        // Adicionar efeito de foco
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('input-focused');
            
            // Encontrar o label associado (se existir) e animar
            const label = this.parentElement.querySelector('label');
            if (label) {
                label.classList.add('animate-fade-in-up');
            }
        });
        
        // Remover efeito ao perder foco
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('input-focused');
            
            // Remover a animação do label
            const label = this.parentElement.querySelector('label');
            if (label) {
                label.classList.remove('animate-fade-in-up');
            }
        });
        
        // Verificar se o campo está em estado de erro
        input.addEventListener('invalid', function() {
            this.classList.add('animate-shake');
            
            // Remover a classe após a animação
            setTimeout(() => {
                this.classList.remove('animate-shake');
            }, 1000);
        });
    });
    
    // Animar botões de submit em formulários
    const submitButtons = document.querySelectorAll('button[type="submit"], input[type="submit"]');
    
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Adicionar efeito de loading nos botões de submit
            if (!this.disabled && !this.classList.contains('no-animation')) {
                const originalText = this.innerHTML;
                this.disabled = true;
                
                // Criar spinner
                const spinner = document.createElement('span');
                spinner.className = 'loading-spinner';
                if (this.classList.contains('btn-light') || this.classList.contains('btn-outline-light')) {
                    spinner.classList.add('dark');
                } else {
                    spinner.classList.add('light');
                }
                
                // Substituir texto pelo spinner
                this.innerHTML = '';
                this.appendChild(spinner);
                
                // Adicionar texto "Processando..."
                const processingText = document.createTextNode(' Processando...');
                this.appendChild(processingText);
                
                // Restaurar o botão após 3 segundos (se o formulário não for submetido)
                setTimeout(() => {
                    if (this.disabled) {
                        this.disabled = false;
                        this.innerHTML = originalText;
                    }
                }, 3000);
            }
        });
    });
}

/**
 * Configura animações para alertas e mensagens
 */
function setupAlertAnimations() {
    // Animar alertas ao aparecerem
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        if (!alert.classList.contains('animated')) {
            alert.classList.add('animate-fade-in-down', 'animated');
            
            // Adicionar botão de fechamento se não existir
            if (!alert.querySelector('.btn-close')) {
                const closeButton = document.createElement('button');
                closeButton.type = 'button';
                closeButton.className = 'btn-close';
                closeButton.setAttribute('data-bs-dismiss', 'alert');
                closeButton.setAttribute('aria-label', 'Close');
                
                alert.appendChild(closeButton);
            }
            
            // Auto-fechar alertas de sucesso após 5 segundos
            if (alert.classList.contains('alert-success')) {
                setTimeout(() => {
                    // Adicionar animação de saída
                    alert.classList.add('animate-fade-out');
                    
                    // Remover alerta após a animação
                    setTimeout(() => {
                        alert.remove();
                    }, 500);
                }, 5000);
            }
        }
    });
}

/**
 * Configura animações para tabelas
 */
function setupTableAnimations() {
    // Animar linhas de tabela quando são adicionadas
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(table => {
        // Adicionar classe para efeitos de hover se ainda não tiver
        if (!table.classList.contains('table-hover')) {
            table.classList.add('table-hover');
        }
        
        // Animar linhas existentes sequencialmente
        if (!table.classList.contains('animated')) {
            table.classList.add('animated');
            
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach((row, index) => {
                // Atraso crescente baseado no índice
                const delay = 50 * index;
                
                setTimeout(() => {
                    row.classList.add('animate-fade-in');
                }, delay);
            });
        }
    });
}

/**
 * Anima elementos quando eles aparecem na viewport durante scroll
 */
function animateElementsOnScroll(selector, animationClass) {
    const elements = document.querySelectorAll(selector);
    
    if (!elements.length) return;
    
    // Função para verificar se elemento está visível na viewport
    const isElementInViewport = (el) => {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    };
    
    // Função para animar elementos visíveis
    const animateVisibleElements = () => {
        elements.forEach(element => {
            if (isElementInViewport(element) && !element.classList.contains('animated')) {
                element.classList.add(animationClass, 'animated');
            }
        });
    };
    
    // Animar elementos já visíveis no carregamento
    animateVisibleElements();
    
    // Animar elementos que se tornam visíveis durante o scroll
    window.addEventListener('scroll', animateVisibleElements);
}

/**
 * Anima elementos sequencialmente com pequeno atraso entre eles
 */
function animateSequentially(selector) {
    const elements = document.querySelectorAll(selector);
    
    elements.forEach((element, index) => {
        // Se o elemento já tem uma classe de delay, respeitamos
        if (!element.className.includes('delay-')) {
            // Adicionar atraso crescente baseado no índice
            const delay = 100 * index;
            element.style.animationDelay = `${delay}ms`;
        }
    });
}

/**
 * Configura observadores para animar conteúdo carregado dinamicamente
 */
function setupDynamicContentObservers() {
    // Observar mudanças no DOM para animar conteúdo adicionado dinamicamente
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                // Novas divs foram adicionadas, checar se precisamos animar
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // É um elemento
                        // Reinicializar animações para este novo conteúdo
                        initializeAnimations();
                    }
                });
            }
        });
    });
    
    // Observar o corpo da página para adições de conteúdo
    observer.observe(document.body, { childList: true, subtree: true });
}

/**
 * Inicializa componentes Bootstrap que necessitam de JavaScript
 */
function initializeBootstrapComponents() {
    // Verificar se o Bootstrap está disponível
    if (typeof bootstrap !== 'undefined') {
        // Inicializar tooltips
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
        
        // Inicializar popovers
        const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }
}

/**
 * Adiciona efeito de shake em um elemento
 * @param {HTMLElement} element - Elemento a ser animado
 */
function shakeElement(element) {
    element.classList.add('animate-shake');
    
    // Remover classe após a animação terminar
    setTimeout(() => {
        element.classList.remove('animate-shake');
    }, 820); // 820ms é a duração da animação shake
}

/**
 * Adiciona efeito de pulse em um elemento
 * @param {HTMLElement} element - Elemento a ser animado
 */
function pulseElement(element) {
    element.classList.add('animate-pulse');
    
    // Remover classe após a animação terminar
    setTimeout(() => {
        element.classList.remove('animate-pulse');
    }, 1500); // 1500ms é a duração da animação pulse
}

/**
 * Anime um flash message customizado
 * @param {string} message - Mensagem a ser exibida
 * @param {string} type - Tipo da mensagem (success, error, warning, info)
 */
function showFlashMessage(message, type = 'info') {
    // Mapeamento de tipos para classes Bootstrap
    const typeClasses = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    };
    
    // Container para mensagens flash
    let flashContainer = document.getElementById('flash-messages');
    
    // Criar o container se não existir
    if (!flashContainer) {
        flashContainer = document.createElement('div');
        flashContainer.id = 'flash-messages';
        flashContainer.className = 'flash-messages-container';
        flashContainer.style.position = 'fixed';
        flashContainer.style.top = '20px';
        flashContainer.style.right = '20px';
        flashContainer.style.zIndex = '9999';
        document.body.appendChild(flashContainer);
    }
    
    // Criar elemento de alerta
    const alert = document.createElement('div');
    alert.className = `alert ${typeClasses[type] || 'alert-info'} animate-fade-in-right`;
    alert.role = 'alert';
    
    // Adicionar ícone baseado no tipo
    let icon = '';
    switch(type) {
        case 'success':
            icon = '<i class="fas fa-check-circle me-2"></i>';
            break;
        case 'error':
            icon = '<i class="fas fa-exclamation-circle me-2"></i>';
            break;
        case 'warning':
            icon = '<i class="fas fa-exclamation-triangle me-2"></i>';
            break;
        case 'info':
            icon = '<i class="fas fa-info-circle me-2"></i>';
            break;
    }
    
    // Configurar conteúdo do alerta
    alert.innerHTML = `
        ${icon}
        ${message}
        <button type="button" class="btn-close" aria-label="Close"></button>
    `;
    
    // Adicionar alerta ao container
    flashContainer.appendChild(alert);
    
    // Configurar botão de fechar
    const closeButton = alert.querySelector('.btn-close');
    closeButton.addEventListener('click', function() {
        alert.classList.remove('animate-fade-in-right');
        alert.classList.add('animate-fade-out-right');
        
        // Remover após a animação
        setTimeout(() => {
            alert.remove();
        }, 300);
    });
    
    // Auto-remover após um tempo (exceto para erros)
    if (type !== 'error') {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.classList.remove('animate-fade-in-right');
                alert.classList.add('animate-fade-out-right');
                
                // Remover após a animação
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 300);
            }
        }, 5000);
    }
    
    return alert;
}

/**
 * Mostra uma animação de carregamento global
 * @param {string} message - Mensagem a ser exibida durante o carregamento
 */
function showLoading(message = 'Carregando...') {
    // Verificar se já existe um overlay de carregamento
    let loadingOverlay = document.getElementById('zelopack-loading-overlay');
    
    // Criar o overlay se não existir
    if (!loadingOverlay) {
        loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'zelopack-loading-overlay';
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.style.position = 'fixed';
        loadingOverlay.style.top = '0';
        loadingOverlay.style.left = '0';
        loadingOverlay.style.width = '100%';
        loadingOverlay.style.height = '100%';
        loadingOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        loadingOverlay.style.display = 'flex';
        loadingOverlay.style.justifyContent = 'center';
        loadingOverlay.style.alignItems = 'center';
        loadingOverlay.style.zIndex = '9999';
        
        // Adicionar conteúdo do loading
        loadingOverlay.innerHTML = `
            <div class="loading-content text-center text-white">
                <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                <h5 class="loading-message">${message}</h5>
            </div>
        `;
        
        document.body.appendChild(loadingOverlay);
        
        // Adicionar animação de entrada
        setTimeout(() => {
            loadingOverlay.style.opacity = '1';
        }, 10);
    } else {
        // Atualizar a mensagem se já existir
        const messageElement = loadingOverlay.querySelector('.loading-message');
        if (messageElement) {
            messageElement.textContent = message;
        }
    }
}

/**
 * Esconde a animação de carregamento global
 */
function hideLoading() {
    const loadingOverlay = document.getElementById('zelopack-loading-overlay');
    
    if (loadingOverlay) {
        // Adicionar animação de saída
        loadingOverlay.style.opacity = '0';
        
        // Remover após a animação
        setTimeout(() => {
            if (loadingOverlay.parentNode) {
                loadingOverlay.parentNode.removeChild(loadingOverlay);
            }
        }, 300);
    }
}

/**
 * Aplica efeito de carregamento em um formulário ou card
 * @param {HTMLElement} element - Elemento a receber o efeito
 * @param {boolean} isLoading - Se deve mostrar ou esconder o carregamento
 */
function setFormLoading(element, isLoading) {
    if (!element) return;
    
    if (isLoading) {
        // Adicionar overlay de carregamento
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'form-loading-overlay';
        loadingOverlay.style.position = 'absolute';
        loadingOverlay.style.top = '0';
        loadingOverlay.style.left = '0';
        loadingOverlay.style.width = '100%';
        loadingOverlay.style.height = '100%';
        loadingOverlay.style.backgroundColor = 'rgba(255, 255, 255, 0.7)';
        loadingOverlay.style.display = 'flex';
        loadingOverlay.style.justifyContent = 'center';
        loadingOverlay.style.alignItems = 'center';
        loadingOverlay.style.zIndex = '10';
        loadingOverlay.style.borderRadius = 'inherit';
        
        // Adicionar spinner
        loadingOverlay.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                <p class="mt-2 text-primary">Carregando dados...</p>
            </div>
        `;
        
        // Garantir que o elemento tenha position relative para o absolute funcionar
        const originalPosition = window.getComputedStyle(element).position;
        if (originalPosition !== 'absolute' && originalPosition !== 'relative' && originalPosition !== 'fixed') {
            element.style.position = 'relative';
            element.dataset.originalPosition = originalPosition;
        }
        
        element.appendChild(loadingOverlay);
        
        // Adicionar animação de entrada
        setTimeout(() => {
            loadingOverlay.style.opacity = '1';
        }, 10);
    } else {
        // Remover overlay de carregamento
        const loadingOverlay = element.querySelector('.form-loading-overlay');
        
        if (loadingOverlay) {
            // Adicionar animação de saída
            loadingOverlay.style.opacity = '0';
            
            // Remover após a animação
            setTimeout(() => {
                if (loadingOverlay.parentNode) {
                    loadingOverlay.parentNode.removeChild(loadingOverlay);
                    
                    // Restaurar position original
                    if (element.dataset.originalPosition) {
                        element.style.position = element.dataset.originalPosition;
                        delete element.dataset.originalPosition;
                    }
                }
            }, 300);
        }
    }
}

// Exportar funções para uso global (se necessário)
window.ZelopackAnimations = {
    shake: shakeElement,
    pulse: pulseElement,
    showMessage: showFlashMessage,
    showLoading: showLoading,
    hideLoading: hideLoading,
    setFormLoading: setFormLoading,
    pulseElement: pulseElement,
    reinitialize: initializeAnimations
};