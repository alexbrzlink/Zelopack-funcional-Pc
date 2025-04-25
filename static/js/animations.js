/**
 * Sistema de Animações de Carregamento - Zelopack
 * Este arquivo implementa as funções para controlar as animações
 * de carregamento e melhorar a experiência do usuário.
 */

// Namespace para as funções de animação
const ZelopackAnimations = {
    /**
     * Inicializa os elementos de animação e adiciona os eventos necessários
     */
    init: function() {
        // Adicionar overlay de carregamento ao DOM se não existir
        if (!document.querySelector('.loading-overlay')) {
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            
            // Criar o spinner padrão
            const spinner = document.createElement('div');
            spinner.className = 'spinner-zelopack';
            
            // Criar o texto de carregamento
            const loadingText = document.createElement('div');
            loadingText.className = 'loading-text';
            loadingText.textContent = 'Carregando...';
            
            overlay.appendChild(spinner);
            overlay.appendChild(loadingText);
            document.body.appendChild(overlay);
        }
        
        // Adicionar animações em botões
        document.querySelectorAll('.btn-primary, .btn-success, .btn-info').forEach(btn => {
            btn.classList.add('btn-animated');
        });
        
        // Adicionar animações em campos de formulário
        document.querySelectorAll('.form-control').forEach(input => {
            input.classList.add('form-animated');
        });
        
        // Adicionar animações em cards
        document.querySelectorAll('.card').forEach(card => {
            card.classList.add('card-hover');
        });
        
        // Interceptar envios de formulários para mostrar loading
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                // Se o formulário não tiver a classe no-loading
                if (!form.classList.contains('no-loading')) {
                    ZelopackAnimations.showLoading('Processando seu formulário...');
                }
            });
        });
        
        // Interceptar cliques em links específicos
        document.querySelectorAll('a[href]:not([href^="#"]):not([target="_blank"]):not(.no-loading)').forEach(link => {
            link.addEventListener('click', function(e) {
                // Se o link não tiver a classe no-loading
                if (!link.classList.contains('no-loading') && !link.getAttribute('download')) {
                    ZelopackAnimations.showLoading('Carregando página...');
                }
            });
        });
        
        // Interceptar cliques em botões de submissão
        document.querySelectorAll('button[type="submit"]:not(.no-loading)').forEach(button => {
            button.addEventListener('click', function(e) {
                // Verificar se o botão pertence a um formulário
                const form = button.closest('form');
                if (form && !form.classList.contains('no-loading')) {
                    ZelopackAnimations.showLoading('Enviando dados...');
                }
            });
        });
        
        // Adicionar animação nas tabelas
        this.setupTableAnimations();
        
        console.log('Zelopack Animations: Inicializado com sucesso!');
    },
    
    /**
     * Mostra a animação de carregamento com texto personalizado
     * @param {string} text - Texto a ser mostrado durante o carregamento
     * @param {string} type - Tipo de spinner (default, flow, dots, liquid)
     */
    showLoading: function(text, type = 'default') {
        const overlay = document.querySelector('.loading-overlay');
        if (!overlay) return;
        
        // Atualizar texto
        const textElement = overlay.querySelector('.loading-text');
        if (textElement) {
            textElement.textContent = text || 'Carregando...';
        }
        
        // Remover spinner atual
        const currentSpinner = overlay.querySelector('.spinner-zelopack, .spinner-flow, .loading-dots, .liquid-loader');
        if (currentSpinner) {
            currentSpinner.remove();
        }
        
        // Criar novo spinner baseado no tipo
        let newSpinner;
        
        switch (type) {
            case 'flow':
                newSpinner = document.createElement('div');
                newSpinner.className = 'spinner-flow';
                for (let i = 0; i < 4; i++) {
                    newSpinner.appendChild(document.createElement('div'));
                }
                break;
                
            case 'dots':
                newSpinner = document.createElement('div');
                newSpinner.className = 'loading-dots';
                for (let i = 0; i < 3; i++) {
                    newSpinner.appendChild(document.createElement('div'));
                }
                break;
                
            case 'liquid':
                newSpinner = document.createElement('div');
                newSpinner.className = 'liquid-loader';
                break;
                
            default:
                newSpinner = document.createElement('div');
                newSpinner.className = 'spinner-zelopack';
                break;
        }
        
        // Inserir novo spinner antes do texto
        textElement.parentNode.insertBefore(newSpinner, textElement);
        
        // Mostrar overlay
        overlay.classList.add('active');
    },
    
    /**
     * Esconde a animação de carregamento
     */
    hideLoading: function() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
    },
    
    /**
     * Configura animações para tabelas carregadas dinamicamente
     */
    setupTableAnimations: function() {
        // Observar mudanças no DOM para animar novas tabelas
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                    // Para cada novo nó adicionado ao DOM
                    mutation.addedNodes.forEach((node) => {
                        // Verificar se é uma tabela ou contém tabelas
                        if (node.nodeType === 1) { // ELEMENT_NODE
                            // Se o próprio nó for uma tabela
                            if (node.tagName === 'TABLE' && !node.classList.contains('fadeIn')) {
                                node.classList.add('fadeIn');
                            }
                            
                            // Se contiver tabelas
                            const tables = node.querySelectorAll('table:not(.fadeIn)');
                            tables.forEach(table => table.classList.add('fadeIn'));
                            
                            // Se contiver linhas de tabela
                            const rows = node.querySelectorAll('tr:not(.fadeIn)');
                            rows.forEach((row, index) => {
                                row.classList.add('fadeIn');
                                row.style.animationDelay = `${index * 0.05}s`;
                            });
                        }
                    });
                }
            });
        });
        
        // Iniciar observação
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    },
    
    /**
     * Anima um elemento específico com efeito de pulse
     * @param {HTMLElement} element - Elemento a ser animado
     */
    pulseElement: function(element) {
        if (!element) return;
        
        // Adicionar classe de animação
        element.classList.add('pulse');
        
        // Remover depois de completar a animação
        setTimeout(() => {
            element.classList.remove('pulse');
        }, 1500);
    },
    
    /**
     * Adiciona indicador de carregamento a um card/container específico
     * @param {HTMLElement|string} element - Elemento ou seletor do elemento
     * @param {boolean} isLoading - Se deve mostrar ou esconder o loading
     */
    setFormLoading: function(element, isLoading = true) {
        // Permitir passar um seletor de string
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return;
        
        if (isLoading) {
            element.classList.add('loading');
        } else {
            element.classList.remove('loading');
        }
    }
};

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    ZelopackAnimations.init();
});

// Executar quando a página estiver totalmente carregada
window.addEventListener('load', () => {
    // Ocultar qualquer animação de carregamento que possa estar ativa
    setTimeout(() => {
        ZelopackAnimations.hideLoading();
    }, 500);
});

// API pública
window.ZelopackAnimations = ZelopackAnimations;