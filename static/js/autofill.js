/**
 * ZeloFill - Módulo de preenchimento automático para o Zelopack
 * Sistema intuitivo para preenchimento de formulários com templates
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicialização do módulo
    initializeAutofill();
    
    /**
     * Inicialização dos componentes de autofill
     */
    function initializeAutofill() {
        setupSuggestions();
        setupTemplates();
        setupFormActions();
    }
    
    /**
     * Configuração do sistema de sugestões
     */
    function setupSuggestions() {
        const suggestionButtons = document.querySelectorAll('.field-suggestion');
        const suggestionToast = document.getElementById('suggestion-toast');
        let currentSuggestionField = null;
        let currentSuggestionValue = null;
        
        // Obter sugestões da API
        fetch('/api/autofill/suggest')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const suggestions = data.suggestions;
                    
                    // Aplicar sugestões aos botões
                    suggestionButtons.forEach(button => {
                        const fieldName = button.previousElementSibling.name;
                        if (suggestions[fieldName]) {
                            button.setAttribute('data-suggestion', suggestions[fieldName]);
                            button.setAttribute('title', `Usar sugestão: ${suggestions[fieldName]}`);
                        }
                    });
                }
            })
            .catch(error => console.error('Erro ao carregar sugestões:', error));
        
        // Configurar eventos de clique
        suggestionButtons.forEach(button => {
            button.addEventListener('click', function() {
                const suggestion = this.getAttribute('data-suggestion');
                const field = this.previousElementSibling;
                
                // Mostrar toast de sugestão
                currentSuggestionField = field;
                currentSuggestionValue = suggestion;
                
                const toastText = document.querySelector('.suggestion-toast-text');
                toastText.textContent = `Deseja usar "${suggestion}" para o campo ${field.name}?`;
                
                suggestionToast.classList.add('show');
                
                // Auto-ocultar depois de 5 segundos
                setTimeout(() => {
                    suggestionToast.classList.remove('show');
                }, 5000);
            });
        });
        
        // Lidar com aceitação de sugestão
        document.querySelector('.suggestion-toast-btn-accept')?.addEventListener('click', function() {
            if (currentSuggestionField && currentSuggestionValue) {
                currentSuggestionField.value = currentSuggestionValue;
                // Animar campo preenchido
                currentSuggestionField.classList.add('field-highlighted');
                setTimeout(() => {
                    currentSuggestionField.classList.remove('field-highlighted');
                }, 800);
                suggestionToast.classList.remove('show');
            }
        });
        
        // Lidar com rejeição de sugestão
        document.querySelector('.suggestion-toast-btn-dismiss')?.addEventListener('click', function() {
            suggestionToast.classList.remove('show');
        });
    }
    
    /**
     * Configuração dos templates salvos
     */
    function setupTemplates() {
        // Seleção de templates existentes
        const templateCards = document.querySelectorAll('.template-card:not(#add-template)');
        templateCards.forEach(card => {
            card.addEventListener('click', function(e) {
                if (!e.target.classList.contains('template-action-btn') && !e.target.closest('.template-action-btn')) {
                    const templateId = this.getAttribute('data-template-id');
                    applyTemplate(templateId);
                    
                    // Feedback visual
                    this.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        this.style.transform = '';
                    }, 300);
                }
            });
        });
        
        // Ações de template (editar, tornar padrão, excluir)
        document.querySelectorAll('.template-action-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const action = this.getAttribute('data-template-action');
                const templateCard = this.closest('.template-card');
                const templateId = templateCard.getAttribute('data-template-id');
                
                if (action === 'edit') {
                    editTemplate(templateId);
                } else if (action === 'default') {
                    setDefaultTemplate(templateId);
                } else if (action === 'delete') {
                    deleteTemplate(templateId);
                }
            });
        });
        
        // Adicionar novo template
        document.getElementById('add-template')?.addEventListener('click', function() {
            showCreateTemplateModal();
        });
    }
    
    /**
     * Aplicar template aos campos do formulário
     */
    function applyTemplate(templateId) {
        fetch(`/api/autofill/templates/${templateId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.template) {
                    const fields = data.template.fields;
                    
                    // Preencher campos do formulário
                    Object.keys(fields).forEach(fieldName => {
                        const input = document.getElementById(fieldName);
                        if (input) {
                            input.value = fields[fieldName];
                            // Animar campo preenchido
                            input.classList.add('field-highlighted');
                            setTimeout(() => {
                                input.classList.remove('field-highlighted');
                            }, 800);
                        }
                    });
                    
                    showMessage('Template aplicado com sucesso!');
                } else {
                    showMessage('Erro ao aplicar template', 'danger');
                }
            })
            .catch(error => {
                console.error('Erro ao carregar template:', error);
                showMessage('Erro ao aplicar template', 'danger');
            });
    }
    
    /**
     * Editar template existente
     */
    function editTemplate(templateId) {
        // Implementar modal de edição
        console.log('Editar template:', templateId);
    }
    
    /**
     * Definir template como padrão
     */
    function setDefaultTemplate(templateId) {
        fetch(`/api/autofill/templates/${templateId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                is_default: true
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Atualizar visualmente os templates
                document.querySelectorAll('.template-card').forEach(card => {
                    card.classList.remove('template-default');
                });
                
                const targetCard = document.querySelector(`.template-card[data-template-id="${templateId}"]`);
                if (targetCard) {
                    targetCard.classList.add('template-default');
                }
                
                showMessage('Template definido como padrão!');
            } else {
                showMessage('Erro ao definir template como padrão', 'danger');
            }
        })
        .catch(error => {
            console.error('Erro ao atualizar template:', error);
            showMessage('Erro ao definir template como padrão', 'danger');
        });
    }
    
    /**
     * Excluir template
     */
    function deleteTemplate(templateId) {
        if (confirm('Tem certeza que deseja excluir este template?')) {
            fetch(`/api/autofill/templates/${templateId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remover card do template
                    const targetCard = document.querySelector(`.template-card[data-template-id="${templateId}"]`);
                    if (targetCard) {
                        targetCard.remove();
                    }
                    
                    showMessage('Template excluído com sucesso!');
                } else {
                    showMessage('Erro ao excluir template', 'danger');
                }
            })
            .catch(error => {
                console.error('Erro ao excluir template:', error);
                showMessage('Erro ao excluir template', 'danger');
            });
        }
    }
    
    /**
     * Mostrar modal para criar novo template
     */
    function showCreateTemplateModal() {
        // Implementar modal de criação
        console.log('Criar novo template');
        
        // Coletar valores dos campos
        const fields = {};
        document.querySelectorAll('.custom-field-input').forEach(input => {
            if (input.value.trim() !== '') {
                fields[input.id] = input.value;
            }
        });
        
        // Verificar se há campos preenchidos
        if (Object.keys(fields).length === 0) {
            showMessage('Preencha pelo menos um campo para criar um template', 'warning');
            return;
        }
        
        // Simular abertura de modal
        const templateName = prompt('Digite um nome para o template:');
        if (templateName) {
            const templateDesc = prompt('Digite uma descrição (opcional):');
            
            // Criar template via API
            fetch('/api/autofill/templates', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    name: templateName,
                    description: templateDesc || '',
                    fields: fields
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage('Template criado com sucesso!');
                    // Atualizar a lista de templates (ideal seria fazer isso via DOM)
                    window.location.reload();
                } else {
                    showMessage('Erro ao criar template', 'danger');
                }
            })
            .catch(error => {
                console.error('Erro ao criar template:', error);
                showMessage('Erro ao criar template', 'danger');
            });
        }
    }
    
    /**
     * Configuração das ações de formulário
     */
    function setupFormActions() {
        // Limpar todos os campos
        document.getElementById('clear-all')?.addEventListener('click', function() {
            document.querySelectorAll('.custom-field-input').forEach(input => {
                input.value = '';
            });
            
            showMessage('Todos os campos foram limpos!');
        });
        
        // Aplicar ao formulário atual
        document.getElementById('apply-fields')?.addEventListener('click', function() {
            // Obter id do formulário atual
            const formId = getUrlParameter('form_id') || getUrlParameter('id');
            
            if (!formId) {
                showMessage('Nenhum formulário selecionado para aplicar os campos', 'warning');
                return;
            }
            
            // Coletar valores dos campos
            const fields = {};
            document.querySelectorAll('.custom-field-input').forEach(input => {
                if (input.value.trim() !== '') {
                    fields[input.id] = input.value;
                }
            });
            
            // Verificar se há campos preenchidos
            if (Object.keys(fields).length === 0) {
                showMessage('Preencha pelo menos um campo para aplicar ao formulário', 'warning');
                return;
            }
            
            // Enviar dados para API
            fetch('/api/autofill/apply', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    form_id: formId,
                    fields: fields
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage('Campos aplicados ao formulário com sucesso!');
                    
                    // Redirecionar se houver URL
                    if (data.redirect_url) {
                        setTimeout(() => {
                            window.location.href = data.redirect_url;
                        }, 1500);
                    }
                } else {
                    showMessage('Erro ao aplicar campos ao formulário', 'danger');
                }
            })
            .catch(error => {
                console.error('Erro ao aplicar campos:', error);
                showMessage('Erro ao aplicar campos ao formulário', 'danger');
            });
        });
        
        // Salvar como template
        document.getElementById('save-as-template')?.addEventListener('click', function() {
            showCreateTemplateModal();
        });
    }
    
    /**
     * Função para exibir mensagem temporária
     */
    function showMessage(message, type = 'success') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Adicionar alerta ao DOM
        const container = document.querySelector('.autofill-container');
        if (container) {
            const firstChild = container.firstChild;
            const alertDiv = document.createElement('div');
            alertDiv.innerHTML = alertHtml;
            container.insertBefore(alertDiv.firstChild, firstChild);
            
            // Auto-remover depois de 3 segundos
            setTimeout(() => {
                const alerts = document.querySelectorAll('.alert');
                alerts.forEach(alert => {
                    if (typeof bootstrap !== 'undefined') {
                        const bsAlert = new bootstrap.Alert(alert);
                        bsAlert.close();
                    } else {
                        alert.remove();
                    }
                });
            }, 3000);
        }
    }
    
    /**
     * Obter token CSRF
     */
    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
    
    /**
     * Obter parâmetro da URL
     */
    function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        var results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }
});