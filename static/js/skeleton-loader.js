/**
 * Zelopack - Skeleton Loading
 * Implementa estados de carregamento esqueleto para melhorar a experiência do usuário
 * durante o carregamento de dados.
 */

(function() {
    'use strict';

    // Classes CSS para controlar a visibilidade
    const SKELETON_CLASS = 'skeleton-loading';
    const SKELETON_HIDDEN_CLASS = 'skeleton-hidden';
    const CONTENT_HIDDEN_CLASS = 'content-hidden';

    // Configurações padrão do skeleton loader
    const DEFAULT_CONFIG = {
        fadeDelay: 300,     // Tempo de delay antes de iniciar o fade
        fadeDuration: 400,  // Duração da animação de fade
        minDisplayTime: 700 // Tempo mínimo para exibir o skeleton (evita flashes)
    };
    
    /**
     * Inicializa um skeleton loader para um container específico
     * @param {string|HTMLElement} container - Seletor ou elemento container 
     * @param {Object} options - Opções de configuração
     */
    function initSkeletonLoader(container, options = {}) {
        // Mesclar configurações padrão com as opções fornecidas
        const config = { ...DEFAULT_CONFIG, ...options };
        
        // Obter o container como elemento DOM
        const containerEl = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
            
        if (!containerEl) {
            console.warn('Skeleton Loader: Container não encontrado', container);
            return;
        }
        
        // Verificar se o container tem esqueletos e conteúdo
        const skeletons = containerEl.querySelectorAll(`.${SKELETON_CLASS}`);
        const contents = containerEl.querySelectorAll('[data-skeleton-content]');
        
        if (!skeletons.length || !contents.length) {
            console.warn('Skeleton Loader: Esqueletos ou conteúdos não encontrados no container', container);
            return;
        }
        
        // Ocultar o conteúdo inicialmente
        contents.forEach(content => {
            content.classList.add(CONTENT_HIDDEN_CLASS);
        });
        
        // Exibir esqueletos
        skeletons.forEach(skeleton => {
            skeleton.classList.remove(SKELETON_HIDDEN_CLASS);
        });
        
        // Registrar o tempo de início
        const startTime = Date.now();
        
        // Função para ocultar esqueletos e mostrar conteúdo
        const showContent = () => {
            // Garantir tempo mínimo de exibição
            const elapsed = Date.now() - startTime;
            const remainingTime = Math.max(0, config.minDisplayTime - elapsed);
            
            setTimeout(() => {
                // Ocultar esqueletos com fade-out
                skeletons.forEach(skeleton => {
                    skeleton.style.transition = `opacity ${config.fadeDuration}ms ease-in-out`;
                    skeleton.style.opacity = '0';
                    
                    setTimeout(() => {
                        skeleton.classList.add(SKELETON_HIDDEN_CLASS);
                    }, config.fadeDuration);
                });
                
                // Mostrar conteúdo com fade-in
                contents.forEach(content => {
                    content.style.transition = `opacity ${config.fadeDuration}ms ease-in-out`;
                    content.style.opacity = '0';
                    content.classList.remove(CONTENT_HIDDEN_CLASS);
                    
                    // Usar setTimeout para garantir que a transição aplique
                    setTimeout(() => {
                        content.style.opacity = '1';
                    }, 50);
                });
                
                // Disparar evento de conteúdo carregado
                containerEl.dispatchEvent(new CustomEvent('content-loaded'));
                
            }, config.fadeDelay + remainingTime);
        };
        
        return {
            show: showContent,
            container: containerEl
        };
    }
    
    /**
     * Carrega dados via AJAX e inicializa o skeleton loader
     * @param {string|HTMLElement} container - Seletor ou elemento container
     * @param {string} url - URL para carregar os dados
     * @param {Function} renderCallback - Função de callback para renderizar os dados
     * @param {Object} options - Opções de configuração
     */
    function loadWithSkeleton(container, url, renderCallback, options = {}) {
        // Inicializar o loader
        const loader = initSkeletonLoader(container, options);
        
        if (!loader) return;
        
        // Carregar dados
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Renderizar os dados
                renderCallback(data, loader.container);
                
                // Mostrar o conteúdo
                loader.show();
            })
            .catch(error => {
                console.error('Erro ao carregar dados:', error);
                
                // Exibir mensagem de erro no conteúdo
                const errorTemplate = `
                    <div class="skeleton-error">
                        <div class="skeleton-error-icon">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <div class="skeleton-error-message">
                            <h5>Erro ao carregar dados</h5>
                            <p>${error.message || 'Ocorreu um erro inesperado.'}</p>
                        </div>
                        <button class="btn btn-outline-primary btn-sm skeleton-retry-btn">
                            <i class="fas fa-redo-alt"></i> Tentar novamente
                        </button>
                    </div>
                `;
                
                // Adicionar opção de retry
                loader.container.innerHTML += errorTemplate;
                const retryBtn = loader.container.querySelector('.skeleton-retry-btn');
                
                if (retryBtn) {
                    retryBtn.addEventListener('click', () => {
                        // Remover mensagem de erro
                        loader.container.querySelector('.skeleton-error').remove();
                        
                        // Tentar novamente
                        loadWithSkeleton(container, url, renderCallback, options);
                    });
                }
                
                // Ocultar esqueletos mesmo em caso de erro
                loader.show();
            });
    }
    
    // Expor API pública
    window.ZelopackSkeletonLoader = {
        init: initSkeletonLoader,
        load: loadWithSkeleton
    };
    
    // Inicializar automaticamente esqueletos com data-skeleton-auto="true"
    document.addEventListener('DOMContentLoaded', () => {
        const autoSkeletons = document.querySelectorAll('[data-skeleton-auto="true"]');
        
        autoSkeletons.forEach(container => {
            const url = container.getAttribute('data-skeleton-url');
            const templateId = container.getAttribute('data-skeleton-template');
            
            if (url && templateId) {
                const template = document.getElementById(templateId);
                
                if (template) {
                    loadWithSkeleton(
                        container, 
                        url, 
                        (data, container) => {
                            // Renderizar usando a template
                            const templateFn = new Function('data', 'return `' + template.innerHTML + '`');
                            container.querySelector('[data-skeleton-content]').innerHTML = templateFn(data);
                        }
                    );
                }
            } else {
                // Apenas inicializar o skeleton
                const loader = initSkeletonLoader(container);
                
                // Mostrar conteúdo após um tempo simulado de carregamento (apenas para demonstração)
                setTimeout(() => {
                    if (loader) loader.show();
                }, 1500);
            }
        });
    });
})();