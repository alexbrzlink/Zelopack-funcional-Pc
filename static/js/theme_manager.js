/**
 * Gerenciador de tema para o ZELOPACK 2025
 * 
 * Este script implementa a funcionalidade de alternância entre temas claro e escuro,
 * com persistência da preferência do usuário usando localStorage e animações.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos do DOM
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    const htmlElement = document.documentElement;
    
    // Variáveis CSS personalizadas para temas
    const darkModeVars = {
        '--dark-bg': '#333333', // Cinza escuro em vez de preto
        '--dark-card-bg': '#3D3D3D',
        '--dark-input-bg': '#404040',
        '--dark-border-color': '#555555',
        '--dark-text': '#F0F0F0'
    };
    
    // Aplicar estilo dark mode personalizado
    function applyCustomDarkMode() {
        const style = document.createElement('style');
        style.id = 'custom-dark-mode';
        style.textContent = `
            [data-bs-theme="dark"] body {
                background-color: ${darkModeVars['--dark-bg']} !important;
                color: ${darkModeVars['--dark-text']} !important;
            }
            [data-bs-theme="dark"] .card,
            [data-bs-theme="dark"] .dropdown-menu,
            [data-bs-theme="dark"] .modal-content {
                background-color: ${darkModeVars['--dark-card-bg']} !important;
            }
            [data-bs-theme="dark"] .form-control,
            [data-bs-theme="dark"] .form-select {
                background-color: ${darkModeVars['--dark-input-bg']} !important;
                border-color: ${darkModeVars['--dark-border-color']} !important;
                color: ${darkModeVars['--dark-text']} !important;
            }
            [data-bs-theme="dark"] .table {
                color: ${darkModeVars['--dark-text']} !important;
            }
            [data-bs-theme="dark"] .table thead th {
                background-color: rgba(0, 149, 141, 0.15);
            }
        `;
        document.head.appendChild(style);
    }
    
    // Verificar e aplicar o estilo dark mode personalizado
    if (!document.getElementById('custom-dark-mode')) {
        applyCustomDarkMode();
    }
    
    // Função para alternar o tema com animação
    function toggleTheme() {
        // Adicionar classe para animar o ícone saindo
        themeIcon.style.transform = 'scale(0)';
        themeIcon.style.opacity = '0';
        
        // Usar setTimeout para permitir a animação ocorrer antes de trocar o tema
        setTimeout(() => {
            if (htmlElement.getAttribute('data-bs-theme') === 'dark') {
                // Mudar para tema claro
                setTheme('light');
            } else {
                // Mudar para tema escuro
                setTheme('dark');
            }
            
            // Resetar a animação para o novo ícone entrar
            setTimeout(() => {
                themeIcon.style.transform = '';
                themeIcon.style.opacity = '';
            }, 50);
        }, 150);
    }
    
    // Função para definir o tema específico
    function setTheme(theme) {
        // Atualizar atributo HTML
        htmlElement.setAttribute('data-bs-theme', theme);
        
        // Atualizar ícone do botão com animação
        if (theme === 'dark') {
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
            themeText.textContent = 'Tema Escuro';
        } else {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
            themeText.textContent = 'Tema Claro';
        }
        
        // Salvar preferência no localStorage
        localStorage.setItem('zelopack-theme', theme);
    }
    
    // Verificar se há uma preferência salva
    const savedTheme = localStorage.getItem('zelopack-theme');
    if (savedTheme) {
        setTheme(savedTheme);
    } else {
        // Verificar preferência do sistema
        const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDarkScheme) {
            setTheme('dark');
        }
    }
    
    // Adicionar event listener ao botão de alternância
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
});