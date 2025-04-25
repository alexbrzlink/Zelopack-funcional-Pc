/**
 * Gerenciador de temas para o sistema ZeloPack
 * Permite alternar entre tema claro e escuro e gerenciar preferências de acessibilidade
 */

(function() {
    'use strict';
    
    // Armazenamento de configurações
    const STORAGE_KEY = 'zelopack_theme_preferences';
    
    // Valores padrão
    const DEFAULT_PREFERENCES = {
        theme: 'auto',          // 'light', 'dark', 'auto'
        fontSize: 'medium',     // 'small', 'medium', 'large'
        animationLevel: 'standard' // 'minimal', 'standard', 'enhanced'
    };
    
    /**
     * Inicializa o tema baseado em preferências salvas ou configuração do sistema
     */
    function initializeTheme() {
        // Obter configurações salvas ou usar padrões
        const savedPrefs = localStorage.getItem(STORAGE_KEY);
        const preferences = savedPrefs ? JSON.parse(savedPrefs) : DEFAULT_PREFERENCES;
        
        // Determinar o tema a ser usado
        let themeToApply = preferences.theme;
        
        // Se configurado como automático, usar preferência do sistema
        if (themeToApply === 'auto') {
            const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
            themeToApply = prefersDarkScheme ? 'dark' : 'light';
        }
        
        // Aplicar tema inicial
        applyTheme(themeToApply);
        
        // Aplicar tamanho de fonte
        setFontSize(preferences.fontSize);
        
        // Aplicar nível de animação
        setAnimationLevel(preferences.animationLevel);
        
        // Configurar listener para tema do sistema (modo automático)
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (preferences.theme === 'auto') {
                applyTheme(e.matches ? 'dark' : 'light');
            }
        });
        
        // Configurar botões e controles
        setupThemeToggle();
        setupAccessibilityOptions();
    }
    
    /**
     * Aplica o tema selecionado ao documento
     * @param {string} theme - Tema a ser aplicado ('dark' ou 'light')
     */
    function applyTheme(theme) {
        // Atualizar as classes/atributos no documento
        document.documentElement.setAttribute('data-bs-theme', theme);
        document.body.classList.toggle('dark-mode', theme === 'dark');
        
        // Atualizar ícones de tema
        updateThemeIcons(theme === 'dark');
        
        // Disparar evento para outros scripts poderem reagir
        document.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: theme }
        }));
    }
    
    /**
     * Configura os botões de alternância de tema
     */
    function setupThemeToggle() {
        const themeToggleButtons = document.querySelectorAll('.theme-toggle');
        
        themeToggleButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Obter configurações atuais
                const currentPrefs = getPreferences();
                
                // Se estiver em modo automático, alternar para modo específico
                if (currentPrefs.theme === 'auto') {
                    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                    // Se o sistema prefere escuro, alternar para claro, e vice-versa
                    const newTheme = systemPrefersDark ? 'light' : 'dark';
                    savePreferences({ ...currentPrefs, theme: newTheme });
                    applyTheme(newTheme);
                } else {
                    // Alternar entre claro e escuro
                    const newTheme = currentPrefs.theme === 'dark' ? 'light' : 'dark';
                    savePreferences({ ...currentPrefs, theme: newTheme });
                    applyTheme(newTheme);
                }
            });
        });
    }
    
    /**
     * Atualiza os ícones de tema em toda a aplicação
     * @param {boolean} isDarkMode - Se está no modo escuro
     */
    function updateThemeIcons(isDarkMode) {
        // Atualizar ícones nos botões de alternância
        document.querySelectorAll('.theme-toggle i').forEach(icon => {
            // Remover todas as classes de ícone
            icon.classList.remove('fa-sun', 'fa-moon');
            
            // Adicionar ícone correto
            if (isDarkMode) {
                icon.classList.add('fa-sun');  // No modo escuro, mostrar sol para alternar para claro
            } else {
                icon.classList.add('fa-moon'); // No modo claro, mostrar lua para alternar para escuro
            }
        });
    }
    
    /**
     * Configura opções adicionais de acessibilidade
     */
    function setupAccessibilityOptions() {
        // Exemplo: botões de tamanho de fonte, se existirem
        document.querySelectorAll('[data-font-size]').forEach(button => {
            button.addEventListener('click', () => {
                const size = button.getAttribute('data-font-size');
                setFontSize(size);
                savePreference('fontSize', size);
            });
        });
        
        // Exemplo: botões de nível de animação, se existirem
        document.querySelectorAll('[data-animation-level]').forEach(button => {
            button.addEventListener('click', () => {
                const level = button.getAttribute('data-animation-level');
                setAnimationLevel(level);
                savePreference('animationLevel', level);
            });
        });
    }
    
    /**
     * Define o tamanho da fonte para toda a aplicação
     * @param {string} size - Tamanho (small, medium, large)
     */
    function setFontSize(size) {
        // Remover classes de tamanho anteriores
        document.documentElement.classList.remove('font-small', 'font-medium', 'font-large');
        // Adicionar nova classe de tamanho
        document.documentElement.classList.add(`font-${size}`);
        // Definir atributo para CSS específico
        document.documentElement.setAttribute('data-font-size', size);
    }
    
    /**
     * Define o nível de animações
     * @param {string} level - Nível (minimal, standard, enhanced)
     */
    function setAnimationLevel(level) {
        // Remover configurações de animação anteriores
        document.documentElement.classList.remove('animations-minimal', 'animations-standard', 'animations-enhanced');
        // Adicionar nova configuração
        document.documentElement.classList.add(`animations-${level}`);
        // Definir atributo para CSS específico
        document.documentElement.setAttribute('data-animation-level', level);
    }
    
    /**
     * Obtém as preferências salvas
     * @returns {Object} Preferências atuais
     */
    function getPreferences() {
        const savedPrefs = localStorage.getItem(STORAGE_KEY);
        return savedPrefs ? JSON.parse(savedPrefs) : DEFAULT_PREFERENCES;
    }
    
    /**
     * Salva todas as preferências
     * @param {Object} preferences - Objeto com todas as preferências
     */
    function savePreferences(preferences) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
    }
    
    /**
     * Salva uma preferência específica
     * @param {string} key - Chave da preferência
     * @param {*} value - Valor a ser salvo
     */
    function savePreference(key, value) {
        const currentPrefs = getPreferences();
        currentPrefs[key] = value;
        savePreferences(currentPrefs);
    }
    
    /**
     * API pública do Theme Manager
     */
    window.ThemeManager = {
        toggleTheme: function() {
            const currentPrefs = getPreferences();
            const newTheme = currentPrefs.theme === 'dark' ? 'light' : 'dark';
            savePreferences({ ...currentPrefs, theme: newTheme });
            applyTheme(newTheme);
        },
        
        setTheme: function(theme) {
            if (['light', 'dark', 'auto'].includes(theme)) {
                savePreference('theme', theme);
                
                if (theme === 'auto') {
                    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                    applyTheme(systemPrefersDark ? 'dark' : 'light');
                } else {
                    applyTheme(theme);
                }
            }
        },
        
        setFontSize: function(size) {
            if (['small', 'medium', 'large'].includes(size)) {
                setFontSize(size);
                savePreference('fontSize', size);
            }
        },
        
        setAnimationLevel: function(level) {
            if (['minimal', 'standard', 'enhanced'].includes(level)) {
                setAnimationLevel(level);
                savePreference('animationLevel', level);
            }
        },
        
        getPreferences: getPreferences
    };
    
    // Inicializar tema quando o DOM estiver carregado
    document.addEventListener('DOMContentLoaded', initializeTheme);
})();