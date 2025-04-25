/**
 * Gerenciador de tema para o ZeloPack
 * 
 * Este script implementa a funcionalidade de alternância entre temas claro e escuro,
 * com persistência da preferência do usuário usando localStorage.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos do DOM
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    const htmlElement = document.documentElement;
    
    // Função para alternar o tema
    function toggleTheme() {
        if (htmlElement.getAttribute('data-bs-theme') === 'dark') {
            // Mudar para tema claro
            setTheme('light');
        } else {
            // Mudar para tema escuro
            setTheme('dark');
        }
    }
    
    // Função para definir o tema específico
    function setTheme(theme) {
        // Atualizar atributo HTML
        htmlElement.setAttribute('data-bs-theme', theme);
        
        // Atualizar ícone e texto do botão
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