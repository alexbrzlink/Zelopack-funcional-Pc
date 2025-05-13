document.addEventListener('DOMContentLoaded', function() {
    // Selecionar o elemento do calendário
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    // Configuração para Maio de 2025
    const ano = 2025;
    const mes = 5;
    const diasNoMes = 31;
    
    // Array para armazenar os eventos
    const events = [];
    
    // Configurar os eventos para cada dia
    for (let dia = 1; dia <= diasNoMes; dia++) {
        // Determinar o dia da semana (0=Domingo, 1=Segunda...)
        const data = new Date(ano, mes-1, dia);
        const diaSemana = data.getDay();
        
        // Converter para formato padrão do calendário
        const dataFormatada = `${ano}-${mes.toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`;
        
        // 1. E.T.E (Estação de Tratamento de Efluentes)
        // Segundas no 1º turno, demais dias no 3º
        if (diaSemana === 1) { // Segunda-feira
            events.push({
                title: 'E.T.E',
                start: dataFormatada,
                classNames: ['turno-1'],
                extendedProps: {
                    turno: 1,
                    descricao: 'Estação de Tratamento de Efluentes no 1º Turno'
                }
            });
        } else {
            events.push({
                title: 'E.T.E',
                start: dataFormatada,
                classNames: ['turno-3'],
                extendedProps: {
                    turno: 3,
                    descricao: 'Estação de Tratamento de Efluentes no 3º Turno'
                }
            });
        }
        
        // 2. Análise de Água - distribuição por dia da semana
        switch (diaSemana) {
            case 1: // Segunda
                events.push({
                    title: 'ANÁLISE DE ÁGUA',
                    start: dataFormatada,
                    classNames: ['turno-1'],
                    extendedProps: {
                        turno: 1,
                        descricao: 'Análise de água no 1º Turno'
                    }
                });
                break;
            case 2: // Terça
                events.push({
                    title: 'ANÁLISE DE ÁGUA',
                    start: dataFormatada,
                    classNames: ['turno-2'],
                    extendedProps: {
                        turno: 2,
                        descricao: 'Análise de água no 2º Turno'
                    }
                });
                break;
            case 3: // Quarta
                events.push({
                    title: 'ANÁLISE DE ÁGUA',
                    start: dataFormatada,
                    classNames: ['turno-3'],
                    extendedProps: {
                        turno: 3,
                        descricao: 'Análise de água no 3º Turno'
                    }
                });
                break;
            case 4: // Quinta
                events.push({
                    title: 'ANÁLISE DE ÁGUA',
                    start: dataFormatada,
                    classNames: ['turno-1'],
                    extendedProps: {
                        turno: 1,
                        descricao: 'Análise de água no 1º Turno'
                    }
                });
                break;
            case 5: // Sexta
                events.push({
                    title: 'ANÁLISE DE ÁGUA',
                    start: dataFormatada,
                    classNames: ['turno-2'],
                    extendedProps: {
                        turno: 2,
                        descricao: 'Análise de água no 2º Turno'
                    }
                });
                break;
            case 6: // Sábado
                events.push({
                    title: 'ANÁLISE DE ÁGUA',
                    start: dataFormatada,
                    classNames: ['turno-3'],
                    extendedProps: {
                        turno: 3,
                        descricao: 'Análise de água no 3º Turno'
                    }
                });
                break;
            case 0: // Domingo
                // No domingo, todos os turnos realizam análise de água
                events.push({
                    title: 'ANÁLISE DE ÁGUA*',
                    start: dataFormatada,
                    classNames: ['todos-turnos'],
                    extendedProps: {
                        turno: 'TODOS',
                        descricao: 'Análise de água em todos os turnos'
                    }
                });
                break;
        }
        
        // 3. Shelf Life 10D (alternando entre turnos)
        const turnoShelfLife = dia % 3 === 1 ? 1 : (dia % 3 === 2 ? 2 : 3);
        events.push({
            title: 'SHELF LIFE 10D',
            start: dataFormatada,
            classNames: [`turno-${turnoShelfLife}`],
            extendedProps: {
                turno: turnoShelfLife,
                descricao: `Shelf Life 10D no ${turnoShelfLife}º Turno`
            }
        });
        
        // 4. Turbidez (Apenas às segundas-feiras, 3º turno)
        if (diaSemana === 1) { // Segunda-feira
            events.push({
                title: 'TURBIDEZ',
                start: dataFormatada,
                classNames: ['turno-3'],
                extendedProps: {
                    turno: 3,
                    descricao: 'Análise de Turbidez no 3º Turno'
                }
            });
        }
    }
    
    // Inicializar o calendário
    const calendar = new FullCalendar.Calendar(calendarEl, {
        headerToolbar: false, // Cabeçalho personalizado fora do FullCalendar
        initialView: 'dayGridMonth',
        initialDate: `${ano}-${mes.toString().padStart(2, '0')}-01`,
        locale: 'pt-br',
        height: 'auto',
        events: events,
        eventDidMount: function(info) {
            // Adicionar tooltips nos eventos
            tippy(info.el, {
                content: `${info.event.title} - ${info.event.extendedProps.turno === 'TODOS' ? 'Todos os turnos' : info.event.extendedProps.turno + 'º Turno'}`,
                placement: 'top',
                arrow: true,
                theme: 'zelopack'
            });
        },
        eventClick: function(info) {
            mostrarDetalhesAtividade(info.event);
        },
        dayCellDidMount: function(info) {
            const hoje = new Date();
            const cellDate = info.date;
            
            if (hoje.getDate() === cellDate.getDate() && 
                hoje.getMonth() === cellDate.getMonth() && 
                hoje.getFullYear() === cellDate.getFullYear()) {
                info.el.classList.add('fc-day-today');
            }
        }
    });
    
    // Renderizar o calendário
    calendar.render();
    
    // Adicionar navegação pelos botões personalizados
    document.getElementById('prev-month').addEventListener('click', function() {
        const prevDate = new Date(ano, mes-2, 1); // Mês anterior
        window.location.href = `/laboratorio/calendario/moderno?ano=${prevDate.getFullYear()}&mes=${prevDate.getMonth()+1}`;
    });
    
    document.getElementById('next-month').addEventListener('click', function() {
        const nextDate = new Date(ano, mes, 1); // Próximo mês
        window.location.href = `/laboratorio/calendario/moderno?ano=${nextDate.getFullYear()}&mes=${nextDate.getMonth()+1}`;
    });
    
    // Função para mostrar o modal com detalhes da atividade
    function mostrarDetalhesAtividade(evento) {
        const modal = document.getElementById('dayDetailsModal');
        const modalTitle = document.getElementById('dayDetailsModalLabel');
        const modalBody = document.getElementById('dayActivitiesDetails');
        
        // Data formatada para o título
        const data = new Date(evento.start);
        const dia = data.getDate();
        const mesNome = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'][data.getMonth()];
        
        // Configurar título do modal
        modalTitle.innerHTML = `<i class="fas fa-calendar-day mr-2"></i> ${dia} de ${mesNome} de ${data.getFullYear()}`;
        
        // Conteúdo do modal
        let conteudo = `
            <div class="activity-detail ${evento.classNames[0]}">
                <h5 class="activity-title">${evento.title}</h5>
                <div class="activity-info">
                    <span class="badge bg-primary">${evento.extendedProps.turno === 'TODOS' ? 'Todos os turnos' : evento.extendedProps.turno + 'º Turno'}</span>
                    <span class="activity-time"><i class="far fa-clock mr-1"></i> ${getHorarioTurno(evento.extendedProps.turno)}</span>
                </div>
                <p class="activity-description">${evento.extendedProps.descricao}</p>
                <div class="activity-actions mt-3">
                    <button class="btn btn-sm btn-outline-primary" onclick="marcarConcluida()">
                        <i class="fas fa-clipboard-check mr-1"></i> Marcar como concluída
                    </button>
                    <button class="btn btn-sm btn-outline-info ml-2" onclick="verDetalhes()">
                        <i class="fas fa-file-alt mr-1"></i> Ver detalhes
                    </button>
                </div>
            </div>
        `;
        
        modalBody.innerHTML = conteudo;
        
        // Abrir o modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
    
    // Função auxiliar para obter o horário do turno
    function getHorarioTurno(turno) {
        if (turno === 1) return '07:00h às 15:00h';
        if (turno === 2) return '15:00h às 23:00h';
        if (turno === 3) return '23:00h às 07:00h';
        return 'Horário completo';
    }
    
    // Funções auxiliares para os botões do modal
    window.marcarConcluida = function() {
        alert('Funcionalidade em desenvolvimento: Marcar como concluída');
    };
    
    window.verDetalhes = function() {
        alert('Funcionalidade em desenvolvimento: Ver detalhes da atividade');
    };
});

// Aplicar efeitos visuais ao calendário
document.addEventListener('DOMContentLoaded', function() {
    // Adicionar tema ZeloPack ao body
    document.body.classList.add('zelopack-theme');
    
    // Adicionar efeito 3D suave ao passar o mouse sobre o calendário
    const container = document.querySelector('.calendar-container');
    if (container) {
        container.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Calcular posição relativa (0 a 1)
            const xRel = x / rect.width;
            const yRel = y / rect.height;
            
            // Limitar a quantidade de movimento para um efeito sutil
            const tiltX = 1.5 * (0.5 - xRel);
            const tiltY = 1.5 * (0.5 - yRel);
            
            // Aplicar transformação
            this.style.transform = `perspective(1000px) rotateX(${tiltY}deg) rotateY(${-tiltX}deg) scale3d(1, 1, 1)`;
        });
        
        container.addEventListener('mouseleave', function() {
            // Resetar transformação
            this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1,.98, 1)';
        });
    }
    
    // Animar entrada de elementos na página
    const animateElements = document.querySelectorAll('.legend-item, .notes-content p');
    animateElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            el.style.transition = 'all 0.5s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 100 + (index * 100));
    });
});
