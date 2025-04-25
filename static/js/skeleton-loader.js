/**
 * Sistema de Skeleton Loading do ZeloPack
 * 
 * Este script gerencia os elementos de skeleton (placeholders) durante o carregamento
 * dos dados, melhorando a experiência do usuário e reduzindo a sensação de espera.
 */

class SkeletonLoader {
    /**
     * Inicializa o gerenciador de skeleton loading
     */
    constructor() {
        this.loadingContainers = document.querySelectorAll('[data-skeleton]');
        this.init();
    }
    
    /**
     * Inicializa o sistema, configurando os skeletons e event listeners
     */
    init() {
        // Processa todos os containers marcados para skeleton loading
        this.loadingContainers.forEach(container => {
            const skeletonType = container.dataset.skeleton;
            const count = parseInt(container.dataset.skeletonCount || '1');
            
            // Esconde o container original durante o carregamento
            container.style.display = 'none';
            
            // Cria o container do skeleton
            const skeletonContainer = document.createElement('div');
            skeletonContainer.className = 'skeleton-container';
            skeletonContainer.dataset.for = container.id || Date.now();
            
            // Adiciona o número especificado de skeletons
            for (let i = 0; i < count; i++) {
                const skeleton = this._createSkeleton(skeletonType);
                skeletonContainer.appendChild(skeleton);
            }
            
            // Insere o skeleton antes do container original
            container.parentNode.insertBefore(skeletonContainer, container);
        });
        
        // Adiciona listener para eventos de carregamento de conteúdo
        document.addEventListener('content-loaded', this.hideSkeletons.bind(this));
        
        // Esconde skeletons automaticamente após timeout (para casos de falha)
        setTimeout(() => {
            this.hideAllSkeletons();
        }, 10000); // 10 segundos de timeout
    }
    
    /**
     * Cria um elemento skeleton baseado no tipo especificado
     * @param {string} type - Tipo de skeleton (table, card, list, etc)
     * @returns {HTMLElement} Elemento do skeleton
     */
    _createSkeleton(type) {
        const skeletonElem = document.createElement('div');
        skeletonElem.className = 'skeleton-item';
        
        // Configuração baseada no tipo
        switch(type) {
            case 'table-row':
                skeletonElem.innerHTML = `
                    <div class="skeleton-table-row">
                        <div class="skeleton-table-cell skeleton-loading"></div>
                        <div class="skeleton-table-cell skeleton-loading"></div>
                        <div class="skeleton-table-cell skeleton-loading"></div>
                        <div class="skeleton-table-cell skeleton-loading"></div>
                    </div>
                `;
                break;
                
            case 'list-item':
                skeletonElem.innerHTML = `
                    <div class="skeleton-list-item">
                        <div class="skeleton-avatar skeleton-loading"></div>
                        <div style="flex: 1">
                            <div class="skeleton-text skeleton-loading skeleton-text-lg"></div>
                            <div class="skeleton-text skeleton-loading skeleton-text-sm"></div>
                        </div>
                    </div>
                `;
                break;
                
            case 'card':
                skeletonElem.innerHTML = `
                    <div class="card mb-3">
                        <div class="skeleton-thumbnail skeleton-loading"></div>
                        <div class="card-body">
                            <div class="skeleton-text skeleton-loading skeleton-text-lg"></div>
                            <div class="skeleton-text skeleton-loading"></div>
                            <div class="skeleton-text skeleton-loading"></div>
                            <div class="skeleton-text skeleton-loading skeleton-text-sm"></div>
                        </div>
                    </div>
                `;
                break;
                
            case 'form':
                skeletonElem.innerHTML = `
                    <div class="mb-3">
                        <div class="skeleton-text skeleton-loading skeleton-text-sm"></div>
                        <div class="skeleton-loading" style="height: 38px"></div>
                    </div>
                    <div class="mb-3">
                        <div class="skeleton-text skeleton-loading skeleton-text-sm"></div>
                        <div class="skeleton-loading" style="height: 38px"></div>
                    </div>
                    <div class="skeleton-button skeleton-loading mt-3"></div>
                `;
                break;
                
            default:
                skeletonElem.innerHTML = `
                    <div class="skeleton-card skeleton-loading"></div>
                `;
        }
        
        return skeletonElem;
    }
    
    /**
     * Esconde os skeletons para um container específico e mostra o conteúdo real
     * @param {string} containerId - ID do container cujo conteúdo foi carregado
     */
    hideSkeletons(event) {
        const containerId = event.detail?.containerId || event.target?.id;
        if (!containerId) return;
        
        const skeletonContainer = document.querySelector(`.skeleton-container[data-for="${containerId}"]`);
        const contentContainer = document.getElementById(containerId);
        
        if (skeletonContainer && contentContainer) {
            // Esconde o skeleton
            skeletonContainer.style.display = 'none';
            
            // Mostra o conteúdo real
            contentContainer.style.display = '';
            
            // Evento personalizado para componentes que precisam se ajustar após mostrar conteúdo
            const revealEvent = new CustomEvent('content-revealed', {
                bubbles: true,
                detail: { containerId }
            });
            contentContainer.dispatchEvent(revealEvent);
        }
    }
    
    /**
     * Esconde todos os skeletons e mostra o conteúdo real
     * Usado como fallback ou quando todos os conteúdos foram carregados
     */
    hideAllSkeletons() {
        document.querySelectorAll('.skeleton-container').forEach(skeleton => {
            skeleton.style.display = 'none';
        });
        
        this.loadingContainers.forEach(container => {
            container.style.display = '';
        });
    }
    
    /**
     * Aciona evento de carregamento manual para um container específico
     * @param {string} containerId - ID do container que terminou de carregar
     */
    notifyContentLoaded(containerId) {
        if (!containerId) return;
        
        const event = new CustomEvent('content-loaded', {
            bubbles: true,
            detail: { containerId }
        });
        document.dispatchEvent(event);
    }
}

// Inicializa o sistema quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.skeletonLoader = new SkeletonLoader();
    
    // Adiciona a API ao objeto global window para uso em outros scripts
    window.showSkeleton = (containerId) => {
        const container = document.getElementById(containerId);
        if (container) {
            container.style.display = 'none';
            const skeletonContainer = document.querySelector(`.skeleton-container[data-for="${containerId}"]`);
            if (skeletonContainer) {
                skeletonContainer.style.display = '';
            }
        }
    };
    
    window.hideSkeleton = (containerId) => {
        window.skeletonLoader.notifyContentLoaded(containerId);
    };
});