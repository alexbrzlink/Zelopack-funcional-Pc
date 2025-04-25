/**
 * ZeloPack Theme Manager
 * Sistema centralizado para gerenciar temas e preferências visuais da aplicação
 */

// Constantes de tema
const THEME_KEY = 'zelopack_theme';
const DARK_MODE = 'dark';
const LIGHT_MODE = 'light';

// Configurações padrão
const DEFAULT_THEME = LIGHT_MODE;
const DEFAULT_FONT_SIZE = 'medium'; // small, medium, large
const DEFAULT_ANIMATION_LEVEL = 'standard'; // minimal, standard, enhanced

// Inicialização do sistema de temas
document.addEventListener('DOMContentLoaded', function() {
    console.log("ZeloPack Theme Manager: Inicializando...");
    initializeTheme();
    setupThemeToggle();
    setupAccessibilityOptions();
});

/**
 * Inicializa o tema baseado em preferências salvas ou configuração do sistema
 */
function initializeTheme() {
    // Verificar preferência salva
    const savedTheme = localStorage.getItem(THEME_KEY);
    
    // Se não houver preferência salva, usar preferência do sistema
    if (!savedTheme) {
        const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const themeToApply = prefersDarkMode ? DARK_MODE : LIGHT_MODE;
        applyTheme(themeToApply);
        localStorage.setItem(THEME_KEY, themeToApply);
    } else {
        applyTheme(savedTheme);
    }

    // Escutar mudanças na preferência do sistema
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        // Só mudar automaticamente se o usuário não tiver preferência específica salva
        if (!localStorage.getItem(THEME_KEY)) {
            const themeToApply = e.matches ? DARK_MODE : LIGHT_MODE;
            applyTheme(themeToApply);
        }
    });
}

/**
 * Aplica o tema selecionado ao documento
 * @param {string} theme - Tema a ser aplicado ('dark' ou 'light')
 */
function applyTheme(theme) {
    if (theme === DARK_MODE) {
        document.body.classList.add('dark-mode');
        document.documentElement.setAttribute('data-bs-theme', 'dark');
        updateThemeIcons(true);
    } else {
        document.body.classList.remove('dark-mode');
        document.documentElement.setAttribute('data-bs-theme', 'light');
        updateThemeIcons(false);
    }
    
    // Evento para notificar outras partes da aplicação
    document.dispatchEvent(new CustomEvent('themeChanged', { 
        detail: { theme: theme } 
    }));
}

/**
 * Configura os botões de alternância de tema
 */
function setupThemeToggle() {
    // Botões de tema no header principal
    const themeButtons = document.querySelectorAll('.theme-toggle');
    
    themeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const currentTheme = localStorage.getItem(THEME_KEY) || DEFAULT_THEME;
            const newTheme = currentTheme === LIGHT_MODE ? DARK_MODE : LIGHT_MODE;
            
            localStorage.setItem(THEME_KEY, newTheme);
            applyTheme(newTheme);
        });
    });
}

/**
 * Atualiza os ícones de tema em toda a aplicação
 * @param {boolean} isDarkMode - Se está no modo escuro
 */
function updateThemeIcons(isDarkMode) {
    const themeButtons = document.querySelectorAll('.theme-toggle');
    
    themeButtons.forEach(button => {
        // Limpar conteúdo existente
        while (button.firstChild) {
            button.removeChild(button.firstChild);
        }
        
        // Adicionar ícone apropriado
        const icon = document.createElement('i');
        icon.className = isDarkMode ? 'fas fa-sun' : 'fas fa-moon';
        button.appendChild(icon);
        
        // Opcional: atualizar texto se existe
        const textSpan = button.querySelector('.toggle-text');
        if (textSpan) {
            textSpan.textContent = isDarkMode ? 'Modo Claro' : 'Modo Escuro';
        }
    });
}

/**
 * Configura opções adicionais de acessibilidade
 */
function setupAccessibilityOptions() {
    // Tamanho de fonte
    const fontSizeControls = document.querySelectorAll('[data-font-size]');
    fontSizeControls.forEach(control => {
        control.addEventListener('click', function() {
            const size = this.getAttribute('data-font-size');
            setFontSize(size);
        });
    });
    
    // Nível de animação
    const animationControls = document.querySelectorAll('[data-animation-level]');
    animationControls.forEach(control => {
        control.addEventListener('click', function() {
            const level = this.getAttribute('data-animation-level');
            setAnimationLevel(level);
        });
    });
}

/**
 * Define o tamanho da fonte para toda a aplicação
 * @param {string} size - Tamanho (small, medium, large)
 */
function setFontSize(size) {
    document.documentElement.setAttribute('data-font-size', size);
    localStorage.setItem('zelopack_font_size', size);
}

/**
 * Define o nível de animações
 * @param {string} level - Nível (minimal, standard, enhanced)
 */
function setAnimationLevel(level) {
    document.documentElement.setAttribute('data-animation-level', level);
    localStorage.setItem('zelopack_animation_level', level);
}

/**
 * API pública do Theme Manager
 */
window.ThemeManager = {
    toggleTheme: function() {
        const currentTheme = localStorage.getItem(THEME_KEY) || DEFAULT_THEME;
        const newTheme = currentTheme === LIGHT_MODE ? DARK_MODE : LIGHT_MODE;
        localStorage.setItem(THEME_KEY, newTheme);
        applyTheme(newTheme);
    },
    
    setTheme: function(theme) {
        if (theme === DARK_MODE || theme === LIGHT_MODE) {
            localStorage.setItem(THEME_KEY, theme);
            applyTheme(theme);
        }
    },
    
    getCurrentTheme: function() {
        return localStorage.getItem(THEME_KEY) || DEFAULT_THEME;
    },
    
    setFontSize: setFontSize,
    setAnimationLevel: setAnimationLevel
};