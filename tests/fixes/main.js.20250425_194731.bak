/**
 * Script principal para funcionalidades gerais do sistema Zelopack
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers do Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Formatação de datas para o formato brasileiro
    formatDates();
    
    // Inicializar elementos de arquivo customizados
    setupFileInputs();
    
    // Animação para mensagens flash
    animateFlashMessages();
    
    // Confirmação para exclusão
    setupDeleteConfirmations();
    
    // Efeito de scroll na barra de navegação
    setupScrollNavbar();
    
    // Adicionar classe active ao link atual
    highlightCurrentNavLink();
    
    // Configurar efeito de ripple em botões
    setupRippleEffect();
    
    // Inicializar contadores animados
    setupAnimatedCounters();
});

/**
 * Formata elementos de data para formato brasileiro
 */
function formatDates() {
    document.querySelectorAll('.date-br').forEach(function(element) {
        const date = new Date(element.getAttribute('data-date'));
        if (!isNaN(date)) {
            const options = { 
                year: 'numeric', 
                month: '2-digit', 
                day: '2-digit'
            };
            element.textContent = date.toLocaleDateString('pt-BR', options);
        }
    });
    
    document.querySelectorAll('.datetime-br').forEach(function(element) {
        const date = new Date(element.getAttribute('data-date'));
        if (!isNaN(date)) {
            const options = { 
                year: 'numeric', 
                month: '2-digit', 
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            };
            element.textContent = date.toLocaleDateString('pt-BR', options) + 
                ' ' + date.toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'});
        }
    });
}

/**
 * Configura inputs de arquivo para mostrar nome do arquivo selecionado
 * e adiciona barra de progresso para uploads
 */
function setupFileInputs() {
    // Para inputs com classe custom-file-input (Bootstrap 4)
    document.querySelectorAll('.custom-file-input').forEach(function(input) {
        input.addEventListener('change', function(e) {
            const fileName = this.files[0]?.name;
            const label = this.nextElementSibling;
            
            if (label && fileName) {
                label.textContent = fileName;
            }
        });
    });
    
    // Para inputs de arquivo padrão (Bootstrap 5)
    document.querySelectorAll('input[type="file"]').forEach(function(input) {
        input.addEventListener('change', function(e) {
            if (this.files.length > 0) {
                const fileName = this.files[0].name;
                const fileSize = formatFileSize(this.files[0].size);
                
                // Mostrar nome do arquivo próximo ao input
                const fileInfo = this.parentElement.querySelector('.file-info') || 
                                document.createElement('div');
                
                if (!this.parentElement.querySelector('.file-info')) {
                    fileInfo.className = 'file-info mt-2 small text-muted';
                    this.parentElement.appendChild(fileInfo);
                }
                
                fileInfo.innerHTML = `<strong>Arquivo selecionado:</strong> ${fileName} (${fileSize})`;
            }
        });
    });
    
    // Configurar formulário de upload para mostrar progresso
    const uploadForm = document.querySelector('form[enctype="multipart/form-data"]');
    if (uploadForm) {
        const progressContainer = document.createElement('div');
        progressContainer.className = 'progress mt-3 d-none';
        progressContainer.style.height = '25px';
        progressContainer.innerHTML = `
            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                 role="progressbar" aria-valuenow="0" aria-valuemin="0" 
                 aria-valuemax="100" style="width: 0%">0%</div>
        `;
        
        // Inserir depois do input de arquivo
        const fileInput = uploadForm.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.parentElement.appendChild(progressContainer);
            
            uploadForm.addEventListener('submit', function(e) {
                const fileInput = this.querySelector('input[type="file"]');
                if (fileInput && fileInput.files.length > 0) {
                    progressContainer.classList.remove('d-none');
                    // Simulação de progresso para feedback visual
                    // (numa implementação real, isso seria feito com XMLHttpRequest ou fetch)
                    simulateProgress(progressContainer.querySelector('.progress-bar'));
                }
            });
        }
    }
}

/**
 * Simula progresso de upload para melhor feedback ao usuário
 * @param {HTMLElement} progressBar - Elemento da barra de progresso
 */
function simulateProgress(progressBar) {
    let progress = 0;
    const interval = setInterval(function() {
        progress += Math.floor(Math.random() * 10) + 1;
        
        if (progress >= 100) {
            clearInterval(interval);
            progress = 100;
            progressBar.classList.remove('progress-bar-animated');
        }
        
        progressBar.style.width = progress + '%';
        progressBar.setAttribute('aria-valuenow', progress);
        progressBar.textContent = progress + '%';
    }, 200);
}

/**
 * Anima mensagens flash para desaparecer após alguns segundos
 */
function animateFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    flashMessages.forEach(function(flash) {
        setTimeout(function() {
            // Adicionar fade-out
            flash.style.transition = 'opacity 1s';
            flash.style.opacity = '0';
            
            // Remover elemento após a animação
            setTimeout(function() {
                flash.remove();
            }, 1000);
        }, 5000); // 5 segundos antes de iniciar o fade
    });
}

/**
 * Configura confirmações para ações de exclusão
 */
function setupDeleteConfirmations() {
    document.querySelectorAll('.delete-confirm').forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.')) {
                e.preventDefault();
                return false;
            }
        });
    });
}

/**
 * Formata tamanho de arquivo em bytes para formato legível (KB, MB, etc)
 * @param {number} bytes - Tamanho em bytes
 * @return {string} Tamanho formatado
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Configura efeito de scroll para a barra de navegação
 */
function setupScrollNavbar() {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        const handleScroll = () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        };
        
        // Verificar posição inicial no carregamento
        handleScroll();
        
        // Adicionar listener de scroll
        window.addEventListener('scroll', handleScroll);
    }
}

/**
 * Destaca o link de navegação atual
 */
function highlightCurrentNavLink() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && (href === currentPath || (currentPath.includes(href) && href !== '/'))) {
            link.classList.add('active');
            
            // Se estiver dentro de dropdown, ativar o dropdown também
            const dropdownParent = link.closest('.dropdown-menu');
            if (dropdownParent) {
                const dropdownToggle = dropdownParent.previousElementSibling;
                if (dropdownToggle && dropdownToggle.classList.contains('dropdown-toggle')) {
                    dropdownToggle.classList.add('active');
                }
            }
        }
    });
}

/**
 * Configura efeito de ripple em elementos interativos
 */
function setupRippleEffect() {
    // Adicionar estilo de ripple ao head se ainda não existir
    if (!document.getElementById('ripple-style')) {
        const style = document.createElement('style');
        style.id = 'ripple-style';
        style.textContent = `
            .ripple {
                position: absolute;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple-animation 0.6s linear;
                pointer-events: none;
            }
            
            @keyframes ripple-animation {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Adicionar efeito a botões e cards interativos
    const interactiveElements = document.querySelectorAll('.btn, .card-interactive, .nav-link');
    interactiveElements.forEach(element => {
        // Verificar se já tem o listener configurado
        if (!element.hasAttribute('data-ripple-configured')) {
            element.setAttribute('data-ripple-configured', 'true');
            element.style.position = element.style.position || 'relative';
            element.style.overflow = element.style.overflow || 'hidden';
            
            element.addEventListener('click', function(e) {
                const rect = element.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const circle = document.createElement('span');
                circle.classList.add('ripple');
                
                const diameter = Math.max(rect.width, rect.height);
                circle.style.width = circle.style.height = `${diameter}px`;
                circle.style.left = `${x - diameter/2}px`;
                circle.style.top = `${y - diameter/2}px`;
                
                element.appendChild(circle);
                
                // Remover após animação
                setTimeout(() => {
                    if (circle.parentElement === element) {
                        element.removeChild(circle);
                    }
                }, 600);
            });
        }
    });
}

/**
 * Configura contadores com animação
 */
function setupAnimatedCounters() {
    const counters = document.querySelectorAll('.counter-value');
    
    // Se não encontrar contadores, não fazer nada
    if (!counters.length) return;
    
    // Verificar se IntersectionObserver é suportado
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const target = parseInt(counter.getAttribute('data-target'), 10);
                    const duration = parseInt(counter.getAttribute('data-duration') || '2000', 10);
                    const formatter = counter.getAttribute('data-formatter');
                    
                    let start = 0;
                    const startTime = performance.now();
                    
                    function updateCounter(timestamp) {
                        const elapsed = timestamp - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        
                        // Usar easeOutQuad para animação mais natural
                        const easeProgress = 1 - Math.pow(1 - progress, 2);
                        const currentValue = Math.floor(easeProgress * target);
                        
                        if (formatter === 'currency') {
                            counter.textContent = currentValue.toLocaleString('pt-BR', {
                                style: 'currency',
                                currency: 'BRL'
                            });
                        } else {
                            counter.textContent = currentValue.toLocaleString('pt-BR');
                        }
                        
                        if (progress < 1) {
                            requestAnimationFrame(updateCounter);
                        }
                    }
                    
                    requestAnimationFrame(updateCounter);
                    observer.unobserve(counter);
                }
            });
        }, { threshold: 0.1 });
        
        counters.forEach(counter => {
            observer.observe(counter);
        });
    } else {
        // Fallback para navegadores sem suporte a IntersectionObserver
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'), 10);
            const formatter = counter.getAttribute('data-formatter');
            
            if (formatter === 'currency') {
                counter.textContent = target.toLocaleString('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                });
            } else {
                counter.textContent = target.toLocaleString('pt-BR');
            }
        });
    }
}
