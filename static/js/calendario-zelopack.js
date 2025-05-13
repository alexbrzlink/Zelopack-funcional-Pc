document.addEventListener('DOMContentLoaded', function() {
    // Configurar o calendário
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;
    
    // Dados fixos para maio de 2025
    const ano = 2025;
    const mes = 5;
    const diasNoMes = 31;
    
    // Array para armazenar os eventos
    let events = [];
    
    // Gerar atividades para os dias do mês
    for (let dia = 1; dia <= diasNoMes; dia++) {
        // Determinar dia da semana (0 = Segunda, 6 = Domingo)
        const data = new Date(ano, mes-1, dia);
        const diaSemana = data.getDay(); // 0 = Domingo, 1 = Segunda, etc.
        const diaSemanaAjustado = diaSemana === 0 ? 6 : diaSemana - 1; // Converter para 0 = Segunda, 6 = Domingo
        
        // Criar atividades baseadas no dia da semana
        
        // 1. E.T.E (Estação de Tratamento de Efluentes)
        if (diaSemanaAjustado === 0) { // Segunda-feira
            events.push({
                title: 'E.T.E (1º Turno)',
                start: `${ano}-${mes.toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`,
                backgroundColor: '#0069A0',
                borderColor: '#004A70',
                textColor: 'white'
            });
        } else {
            events.push({
                title: 'E.T.E (3º Turno)',
                start: `${ano}-${mes.toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`,
                backgroundColor: '#00B3A0',
                borderColor: '#008577',
                textColor: 'white'
            });
        }
        
        // 2. Análise de Água - distribuição por dia da semana
        if (diaSemanaAjustado === 0) { // Segunda-feira
            events.push({
                title: 'ANÁLISE DE ÁGUA (1º Turno)',
                start: `${ano}-${mes.toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`,
                backgroundColor: '#0069A0',
                borderColor: '#004A70',
                textColor: 'white'
            });
        } else if (diaSemanaAjustado === 1) { // Terça-feira
            events.push({
                title: 'ANÁLISE DE ÁGUA (2º Turno)',
                start: `${ano}-${mes.toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`,
                backgroundColor: '#00A1CB',
                borderColor: '#0078A3',
                textColor: 'white'
            });
        } else if (diaSemanaAjustado === 2) { // Quarta-feira
            events.push({
                title: 'ANÁLISE DE ÁGUA (3º Turno)',
                start: `${ano}-${mes.toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`,
                backgroundColor: '#00B3A0',
                borderColor: '#008577',
                textColor: 'white'
            });
        } else if (diaSemanaAjustado === 3) { // Quinta-feira
            events.push({
                title: 'ANÁLISE DE ÁGUA (1º Turno)',
                start: `${ano}-${mes.toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`,
                backgroundColor: '#0069A0',
                borderColor: '#004A70',
                textColor: 'white'
            });
        } else if (diaSemanaAjustado === 4) { // Sexta-feira
            events.push({
                title: 'ANÁLISE DE ÁGUA (2º Turno)',
                start: `${ano}-${mes.toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`,
                backgroundColor: '#00A1CB',
                borderColor: '#0078A3',
                textColor: 'white'
            });
        } else if (diaSemanaAjustado === 5) { // Sábado
            events.push({
                title: 'ANÁLISE DE ÁGUA (3º Turno)',
                start: `${ano}-${mes.toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`,
                backgroundColor: '#00B3A0',
                borderColor: '#008577',
                textColor: 'white'
            });
        } else if (diaSemanaAjustado === 6) { // Domingo
            // No domingo, todos os turnos realizam análise de água (se houver expediente)
            events.push({
                title: 'ANÁLISE DE ÁGUA* (Todos os Turnos)',
                start: `${ano}-${mes.toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`,
                backgroundColor: '#F26522',
                borderColor: '#D54A00',
                textColor: 'white'
            });
        }
        
        // 3. Shelf Life 10D (alterna ciclicamente entre os turnos)
        const turnoShelfLife = dia % 3 === 1 ? 1 : (dia % 3 === 2 ? 2 : 3);
        const corTurno = turnoShelfLife === 1 ? '#0069A0' : (turnoShelfLife === 2 ? '#00A1CB' : '#00B3A0');
        const corBorda = turnoShelfLife === 1 ? '#004A70' : (turnoShelfLife === 2 ? '#0078A3' : '#008577');
        
        events.push({
            title: `SHELF LIFE 10D (${turnoShelfLife}º Turno)`,
            start: `${ano}-${mes.toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`,
            backgroundColor: corTurno,
            borderColor: corBorda,
            textColor: 'white'
        });
        
        // 4. Turbidez (Apenas às segundas-feiras, 3º turno)
        if (diaSemanaAjustado === 0) { // Segunda-feira
            events.push({
                title: 'TURBIDEZ (3º Turno)',
                start: `${ano}-${mes.toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`,
                backgroundColor: '#00B3A0',
                borderColor: '#008577',
                textColor: 'white'
            });
        }
    // Inicializa o calendário
                1: {
                    backgroundColor: '#0069A0',
                    borderColor: '#004A70',
                    textColor: 'white'
                },
                2: {
                    backgroundColor: '#00A1CB',
                    borderColor: '#0078A3',
                    textColor: 'white'
                },
                3: {
                    backgroundColor: '#00B3A0',
                    borderColor: '#008577',
                    textColor: 'white'
                }
            };
            
            // Cria os eventos para o FullCalendar
            for (const [dia, turnosAtividades] of Object.entries(atividades)) {
                for (const [turno, listaAtividades] of Object.entries(turnosAtividades)) {
                    if (listaAtividades.length > 0) {
                        listaAtividades.forEach(atividade => {
                            const corConfig = corPorTurno[turno] || {
                                backgroundColor: '#888',
                                borderColor: '#666',
                                textColor: 'white'
                            };
                            
                            // Se é análise com asterisco (domingo), usar cor de destaque
                            if (atividade.includes('*')) {
                                corConfig.backgroundColor = '#F26522';
                                corConfig.borderColor = '#D54A00';
                            }
                            
                            // Adicionar sufixo do turno
                            const title = atividade + ` (${turno}º Turno)`;
                            
                            events.push({
                                title: title,
                                start: `${ano}-${mes.toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`,
                                backgroundColor: corConfig.backgroundColor,
                                borderColor: corConfig.borderColor,
                                textColor: corConfig.textColor,
                                extendedProps: {
                                    turno: turno,
                                    atividade: atividade
                                }
                            });
                        });
                    }
                }
            }
        } catch (e) {
            console.error('Erro ao processar atividades:', e);
        }
    }
    
    // Inicializa o calendário
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        initialDate: `${ano}-${mes.toString().padStart(2, '0')}-01`,
        headerToolbar: false,
        locale: 'pt-br',
        height: 'auto',
        events: events,
        eventClick: function(info) {
            // Informações do evento clicado
            const evento = info.event;
            const data = new Date(evento.start);
            const dia = data.getDate();
            const titulo = evento.title;
            const props = evento.extendedProps;
            
            // Mostrar modal com detalhes
            mostrarDetalhesAtividade(dia, titulo, props.turno, props.atividade);
        },
        dayHeaderContent: function(arg) {
            // Personalizar cabeçalho dos dias da semana
            const diasSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
            return diasSemana[arg.dow];
        },
        dayCellDidMount: function(info) {
            // Adicionar classe especial para o dia atual
            const hoje = new Date();
            const cellDate = info.date;
            
            if (hoje.getDate() === cellDate.getDate() && 
                hoje.getMonth() === cellDate.getMonth() && 
                hoje.getFullYear() === cellDate.getFullYear()) {
                info.el.classList.add('fc-day-today');
            }
        },
        dayMaxEvents: true,
        moreLinkText: 'mais',
        moreLinkClick: 'popover'
    });
    
    calendar.render();
    
    // Configurar botões de navegação
    document.getElementById('prev-month').addEventListener('click', function() {
        window.location.href = `/laboratorio/calendario/moderno?ano=${anoAnterior}&mes=${mesAnterior}`;
    });
    
    document.getElementById('next-month').addEventListener('click', function() {
        window.location.href = `/laboratorio/calendario/moderno?ano=${anoProximo}&mes=${mesProximo}`;
    });
    
    // Função para mostrar modal com detalhes da atividade
    function mostrarDetalhesAtividade(dia, titulo, turno, atividade) {
        const modal = document.getElementById('dayDetailsModal');
        const modalTitle = document.getElementById('dayDetailsModalLabel');
        const modalBody = document.getElementById('dayActivitiesDetails');
        
        // Configurar título do modal
        modalTitle.innerHTML = `<i class="fas fa-calendar-day mr-2 text-primary"></i> ${dia} de ${mesNome} ${ano}`;
        
        // Preparar conteúdo do modal
        let conteudo = '';
        conteudo += `<div class="activity-detail turno-${turno}">`;
        conteudo += `<h5 class="activity-title">${atividade}</h5>`;
        conteudo += `<div class="activity-info">`;
        conteudo += `<span class="badge bg-info">Turno ${turno}</span>`;
        
        // Horário do turno
        let horario = '';
        if (turno == 1) horario = '07:00h às 15:00h';
        else if (turno == 2) horario = '15:00h às 23:00h';
        else if (turno == 3) horario = '23:00h às 07:00h';
        
        conteudo += `<span class="activity-time"><i class="far fa-clock mr-1"></i> ${horario}</span>`;
        conteudo += `</div>`;
        
        // Adicionar descrição baseada no tipo de atividade
        let descricao = '';
        if (atividade.includes('ANÁLISE DE ÁGUA')) {
            descricao = 'Análise de água para controle de qualidade. Verificar padrões de potabilidade, pH, cloro residual e outros parâmetros conforme SOP #A-1023.';
        } else if (atividade.includes('SHELF LIFE')) {
            descricao = 'Análise de Shelf Life para avaliação da vida útil dos produtos. Seguir protocolo de testes #SL-456 para garantir conformidade com padrões de qualidade.';
        } else if (atividade.includes('E.T.E')) {
            descricao = 'Monitoramento da Estação de Tratamento de Efluentes. Verificar parâmetros conforme procedimento #ETE-789 e registro ambiental.';
        } else if (atividade.includes('TURBIDEZ')) {
            descricao = 'Análise específica de turbidez da água. Utilizar turbidímetro conforme calibração e seguir procedimento #T-234.';
        }
        
        conteudo += `<p class="activity-description">${descricao}</p>`;
        conteudo += `<div class="activity-actions mt-3">`;
        conteudo += `<button class="btn btn-sm btn-outline-primary" onclick="alert('Funcionalidade em desenvolvimento')">`;
        conteudo += `<i class="fas fa-clipboard-check mr-1"></i> Marcar como concluída</button>`;
        conteudo += `<button class="btn btn-sm btn-outline-info ml-2" onclick="alert('Funcionalidade em desenvolvimento')">`;
        conteudo += `<i class="fas fa-file-alt mr-1"></i> Ver detalhes</button>`;
        conteudo += `</div>`;
        conteudo += `</div>`;
        
        modalBody.innerHTML = conteudo;
        
        // Mostrar o modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
    
    // Adicionar efeitos visuais específicos para ZeloPack
    adicionarEfeitosVisuais();
});

// Função para adicionar efeitos visuais ao calendário
function adicionarEfeitosVisuais() {
    // Adicionar efeito de sombra ao passar o mouse sobre o calendário
    document.querySelector('.calendar-container').addEventListener('mousemove', function(e) {
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Calcular posição relativa (0 a 1)
        const xRel = x / rect.width;
        const yRel = y / rect.height;
        
        // Aplicar efeito sutil de sombra direcionada
        const shadowX = 20 * (0.5 - xRel);
        const shadowY = 20 * (0.5 - yRel);
        
        this.style.boxShadow = `${shadowX}px ${shadowY}px 30px rgba(0, 69, 112, 0.1), 0 10px 30px rgba(0, 105, 160, 0.1)`;
    });
    
    // Resetar sombra quando o mouse sair do calendário
    document.querySelector('.calendar-container').addEventListener('mouseleave', function() {
        this.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1), 0 1px 8px rgba(0, 0, 0, 0.07)';
    });
    
    // Adicionar efeito de animação ao entrar na página
    const items = document.querySelectorAll('.calendar-legend .legend-item, .calendar-notes .notes-content p');
    
    items.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            item.style.transition = 'all 0.5s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, 500 + (index * 100));
    });
    
    // Personalizar o estilo do FullCalendar para combinar com a paleta da ZeloPack
    personalizarEstiloFullCalendar();
}

// Função para personalizar o estilo do FullCalendar
function personalizarEstiloFullCalendar() {
    // Adicionar estilos customizados através de uma folha de estilo dinâmica
    const style = document.createElement('style');
    style.textContent = `
        .fc-theme-standard td, .fc-theme-standard th {
            border-color: #e6f4f9;
        }
        
        .fc .fc-daygrid-day.fc-day-today {
            background-color: rgba(0, 105, 160, 0.1);
        }
        
        .fc-daygrid-day-frame {
            transition: all 0.3s ease;
        }
        
        .fc-daygrid-day-frame:hover {
            background-color: rgba(0, 161, 203, 0.05);
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 105, 160, 0.1);
            z-index: 1;
        }
        
        .fc .fc-daygrid-day-number {
            font-weight: 600;
            color: #004A70;
        }
        
        .fc-event {
            border-radius: 6px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
        }
        
        .fc-event:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 10;
        }
        
        .fc-header-toolbar {
            margin-bottom: 2em !important;
        }
        
        .fc-col-header-cell {
            background-color: #0069A0;
            color: white;
        }
        
        .fc-col-header-cell-cushion {
            padding: 10px 4px;
            font-weight: 600;
        }
        
        .fc-day-other .fc-daygrid-day-number {
            color: #aab7c5;
        }
    `;
    
    document.head.appendChild(style);
}
