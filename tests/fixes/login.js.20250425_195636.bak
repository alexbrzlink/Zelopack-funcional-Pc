/**
 * Script para interatividade e animações da página de login
 * Sistema de gerenciamento de laudos ZELOPACK 
 * Implementa animações avançadas e feedback visual para o usuário
 */

document.addEventListener('DOMContentLoaded', function() {
    // Animar o card de login na entrada
    const loginCard = document.querySelector('.login-card');
    if (loginCard) {
        loginCard.style.opacity = '0';
        loginCard.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            loginCard.style.transition = 'all 0.5s ease-out';
            loginCard.style.opacity = '1';
            loginCard.style.transform = 'translateY(0)';
        }, 300);
    }
    // Elementos da página
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginBtn = document.getElementById('submit');
    const rememberMe = document.getElementById('remember_me');
    
    // Verificar e animar mensagens de erro existentes
    const invalidControls = document.querySelectorAll('.is-invalid');
    const errorMessages = document.querySelectorAll('.invalid-feedback');
    
    // Converter as mensagens de erro padrão para o formato animado
    errorMessages.forEach(message => {
        const parent = message.parentElement;
        const input = parent.querySelector('.form-control');
        
        // Remover a mensagem antiga
        message.remove();
        
        // Criar a nova mensagem de erro com animação
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle error-icon"></i> ${message.textContent}`;
        
        // Inserir a nova mensagem
        parent.appendChild(errorDiv);
        
        // Adicionar animação ao campo
        input.parentElement.classList.add('error-shake');
    });
    
    // Animar alertas flash
    const alerts = document.querySelectorAll('.alert');
    const loginMessages = document.getElementById('login-messages');
    
    if (alerts.length > 0 && loginMessages) {
        alerts.forEach(alert => {
            // Adicionar classe para animação
            alert.classList.add('animate-fade-in');
            
            // Adicionar ícone se não existir
            if (!alert.querySelector('i')) {
                let alertType = 'info-circle';
                
                if (alert.classList.contains('alert-danger')) {
                    alertType = 'exclamation-circle';
                } else if (alert.classList.contains('alert-success')) {
                    alertType = 'check-circle';
                } else if (alert.classList.contains('alert-warning')) {
                    alertType = 'exclamation-triangle';
                }
                
                const icon = document.createElement('i');
                icon.className = `fas fa-${alertType} me-2`;
                alert.insertBefore(icon, alert.firstChild);
            }
            
            // Fazer as mensagens de sucesso e info desaparecerem após alguns segundos
            if (!alert.classList.contains('alert-danger') && !alert.classList.contains('alert-warning')) {
                setTimeout(() => {
                    alert.style.animation = 'fadeOut 0.5s ease forwards';
                    setTimeout(() => {
                        if (alert.parentNode) {
                            alert.parentNode.removeChild(alert);
                        }
                    }, 500);
                }, 5000);
            }
            
            // Adicionar botão para fechar o alerta
            const closeButton = document.createElement('button');
            closeButton.type = 'button';
            closeButton.className = 'btn-close';
            closeButton.setAttribute('aria-label', 'Close');
            
            closeButton.addEventListener('click', function() {
                alert.style.animation = 'fadeOut 0.3s ease forwards';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 300);
            });
            
            alert.appendChild(closeButton);
        });
    }
    
    // Adicionar animação quando o formulário for enviado
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            // NÃO INTERROMPER O ENVIO NORMAL DO FORMULÁRIO
            // Apenas adicionar efeitos visuais
            
            const username = usernameInput.value.trim();
            const password = passwordInput.value.trim();
            
            // Verificar campos vazios - mas não impedir o envio do formulário
            // para preservar o token CSRF e o processamento do servidor
            if (!username || !password) {
                if (!username) {
                    showError(usernameInput, 'Por favor, digite seu nome de usuário');
                }
                
                if (!password) {
                    showError(passwordInput, 'Por favor, digite sua senha');
                }
                // O próprio navegador bloqueará o envio se campos required estiverem vazios
            } else {
                // Adicionar efeito ao botão
                loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Entrando...';
                loginBtn.disabled = true;
                
                // Mostrar animação de carregamento no fundo (se existir)
                if (window.ZelopackAnimations) {
                    window.ZelopackAnimations.showLoading('Autenticando...', 'dots');
                }
            }
        });
    }
    
    // Adicionar efeito aos campos quando focados
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('input-focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('input-focused');
            
            // Validar campo ao sair
            if (this.value.trim() === '' && this.hasAttribute('required')) {
                showError(this, `Por favor, preencha este campo`);
            } else {
                // Remover erro se estiver preenchido
                removeError(this);
            }
        });
    });
    
    // Funções auxiliares
    function showError(input, message) {
        // Remover erro anterior se existir
        removeError(input);
        
        const parentElement = input.parentElement;
        input.classList.add('is-invalid');
        parentElement.classList.add('error-shake');
        
        // Criar elemento de erro
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle error-icon"></i> ${message}`;
        
        // Adicionar após o input
        parentElement.appendChild(errorDiv);
        
        // Remover a animação de shake após um tempo
        setTimeout(() => {
            parentElement.classList.remove('error-shake');
        }, 1000);
    }
    
    function removeError(input) {
        input.classList.remove('is-invalid');
        const errorMessage = input.parentElement.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }
    
    // Adicionar animação ao checkbox de lembrar-me
    if (rememberMe) {
        const checkboxLabel = rememberMe.nextElementSibling;
        
        rememberMe.addEventListener('change', function() {
            if (this.checked) {
                checkboxLabel.innerHTML = '<i class="fas fa-check-circle me-1"></i> ' + checkboxLabel.textContent;
            } else {
                checkboxLabel.innerHTML = checkboxLabel.textContent.replace('<i class="fas fa-check-circle me-1"></i> ', '');
            }
        });
    }
    
    // Efeito de partículas no background (opcional, remover se afetar performance)
    try {
        // Configuração básica para partículas
        if (typeof particlesJS !== 'undefined') {
            particlesJS('login-particles', {
                particles: {
                    number: { value: 50, density: { enable: true, value_area: 800 } },
                    color: { value: '#0d6efd' },
                    shape: { type: 'circle' },
                    opacity: { value: 0.5, random: true },
                    size: { value: 3, random: true },
                    line_linked: {
                        enable: true,
                        distance: 150,
                        color: '#0d6efd',
                        opacity: 0.4,
                        width: 1
                    },
                    move: {
                        enable: true,
                        speed: 2,
                        direction: 'none',
                        random: false,
                        straight: false,
                        out_mode: 'out',
                        bounce: false
                    }
                },
                interactivity: {
                    detect_on: 'canvas',
                    events: {
                        onhover: { enable: true, mode: 'grab' },
                        onclick: { enable: true, mode: 'push' },
                        resize: true
                    }
                },
                retina_detect: true
            });
        }
    } catch (e) {
        // // console.log('Particles.js não carregado. Ignorando efeito de partículas.');
    }
});