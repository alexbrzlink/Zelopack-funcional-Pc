/**
 * Scripts principais para o ZeloPack
 * Contém funções de uso comum em todo o sistema
 */

document.addEventListener('DOMContentLoaded', function() {
    // Ativa tooltips do Bootstrap em toda a aplicação
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Ativa popovers do Bootstrap em toda a aplicação
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Função para mostrar/esconder senha em campos de formulário
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const passwordField = document.querySelector(this.dataset.target);
            if (passwordField) {
                // Alterar o tipo do campo
                const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordField.setAttribute('type', type);
                
                // Atualizar o ícone
                const icon = this.querySelector('i');
                if (icon) {
                    if (type === 'password') {
                        icon.classList.remove('fa-eye-slash');
                        icon.classList.add('fa-eye');
                    } else {
                        icon.classList.remove('fa-eye');
                        icon.classList.add('fa-eye-slash');
                    }
                }
            }
        });
    });
    
    // Inicializar DataTables nas tabelas com a classe .datatable
    if (typeof $.fn.DataTable !== 'undefined') {
        $('.datatable').DataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/Portuguese-Brasil.json'
            },
            responsive: true,
            processing: true
        });
    }
    
    // Configurar confirmações de deleção
    const deleteButtons = document.querySelectorAll('.btn-delete-confirm');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.')) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Configurar máscaras de entrada para campos específicos
    setupInputMasks();
    
    // Inicializar calendários e seletores de data
    setupDatepickers();
    
    // Configurar redimensionamento automático para textareas
    setupAutoResizeTextareas();
});

/**
 * Configura máscaras de entrada para campos específicos
 */
function setupInputMasks() {
    // Se o plugin inputmask estiver disponível
    if (typeof Inputmask !== 'undefined') {
        // Máscara para CPF
        Inputmask('999.999.999-99').mask(document.querySelectorAll('.mask-cpf'));
        
        // Máscara para CNPJ
        Inputmask('99.999.999/9999-99').mask(document.querySelectorAll('.mask-cnpj'));
        
        // Máscara para telefone
        Inputmask('(99) 99999-9999').mask(document.querySelectorAll('.mask-phone'));
        
        // Máscara para CEP
        Inputmask('99999-999').mask(document.querySelectorAll('.mask-cep'));
        
        // Máscara para data
        Inputmask('99/99/9999').mask(document.querySelectorAll('.mask-date'));
        
        // Máscara para valores monetários
        Inputmask('currency', {
            radixPoint: ',',
            groupSeparator: '.',
            digits: 2,
            autoGroup: true,
            prefix: 'R$ ',
            rightAlign: false
        }).mask(document.querySelectorAll('.mask-currency'));
    }
}

/**
 * Configura calendários e seletores de data
 */
function setupDatepickers() {
    // Se o plugin flatpickr estiver disponível
    if (typeof flatpickr !== 'undefined') {
        flatpickr('.datepicker', {
            locale: 'pt',
            dateFormat: 'd/m/Y',
            altInput: true,
            altFormat: 'd/m/Y',
            allowInput: true
        });
        
        flatpickr('.datetimepicker', {
            locale: 'pt',
            dateFormat: 'd/m/Y H:i',
            enableTime: true,
            time_24hr: true,
            altInput: true,
            altFormat: 'd/m/Y H:i',
            allowInput: true
        });
    }
}

/**
 * Configura redimensionamento automático para textareas
 */
function setupAutoResizeTextareas() {
    const autoResizeTextareas = document.querySelectorAll('textarea.auto-resize');
    
    function resizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';
    }
    
    autoResizeTextareas.forEach(textarea => {
        resizeTextarea(textarea);
        textarea.addEventListener('input', function() {
            resizeTextarea(this);
        });
    });
}

/**
 * Formata uma data JS para string no formato brasileiro
 * @param {Date} date - A data a ser formatada
 * @returns {string} Data formatada DD/MM/YYYY
 */
function formatDateBr(date) {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    
    return `${day}/${month}/${year}`;
}

/**
 * Formata um valor para o formato de moeda brasileira
 * @param {number} value - O valor a ser formatado
 * @param {boolean} withSymbol - Se deve incluir o símbolo R$
 * @returns {string} Valor formatado
 */
function formatCurrencyBr(value, withSymbol = true) {
    const formatted = new Intl.NumberFormat('pt-BR', {
        style: withSymbol ? 'currency' : 'decimal',
        currency: 'BRL',
        minimumFractionDigits: 2
    }).format(value);
    
    return formatted;
}

/**
 * Envia uma notificação para o usuário
 * @param {string} message - Mensagem a ser exibida
 * @param {string} type - Tipo de notificação (success, error, warning, info)
 * @param {number} duration - Duração em ms
 */
function notify(message, type = 'info', duration = 5000) {
    // Se o Toastify ou similar estiver disponível
    if (typeof Toastify !== 'undefined') {
        Toastify({
            text: message,
            duration: duration,
            close: true,
            gravity: 'top',
            position: 'right',
            backgroundColor: type === 'success' ? '#198754' : 
                             type === 'error' ? '#dc3545' : 
                             type === 'warning' ? '#ffc107' : '#0dcaf0'
        }).showToast();
    } else {
        // Fallback para alert
        alert(message);
    }
}