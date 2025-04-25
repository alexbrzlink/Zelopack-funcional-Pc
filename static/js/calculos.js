/**
 * ZeloCalc - Módulo de cálculos técnicos para o Zelopack
 * Versão 2.0 - Redesenhado para uma experiência mais intuitiva
 * 
 * Este arquivo contém as funções para os cálculos técnicos do sistema Zelopack,
 * focando em cálculos laboratoriais e de produção.
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('ZeloCalc: Inicializando módulo de cálculos técnicos 2.0...');
    
    // Catálogo de todos os cálculos disponíveis para busca
    const calculosDisponiveis = [
        { 
            id: 'producao-200g', 
            nome: 'Produção 200g', 
            categoria: 'Produção', 
            descricao: 'Determinação de peso líquido de embalagens', 
            icon: 'fas fa-balance-scale', 
            favorito: true,
            frequencia: 60
        },
        { 
            id: 'finalizacao-tanque', 
            nome: 'Finalização de Tanque', 
            categoria: 'Finalização', 
            descricao: 'Diluição para Brix específico', 
            icon: 'fas fa-database', 
            favorito: true,
            frequencia: 58
        },
        { 
            id: 'brix-padrao', 
            nome: 'Brix Padrão', 
            categoria: 'Laboratório', 
            descricao: 'Padronização de valores Brix', 
            icon: 'fas fa-thermometer-half', 
            favorito: true,
            frequencia: 42
        },
        { 
            id: 'volume-producao', 
            nome: 'Volume de Produção', 
            categoria: 'Produção', 
            descricao: 'Cálculo de volume produzido', 
            icon: 'fas fa-tint', 
            favorito: false,
            frequencia: 38
        },
        { 
            id: 'rendimento', 
            nome: 'Rendimento', 
            categoria: 'Produção', 
            descricao: 'Cálculo de rendimento percentual', 
            icon: 'fas fa-percentage', 
            favorito: false,
            frequencia: 35
        },
        { 
            id: 'diluicao', 
            nome: 'Diluição', 
            categoria: 'Laboratório', 
            descricao: 'Cálculos de diluição de amostras', 
            icon: 'fas fa-vial', 
            favorito: false,
            frequencia: 30
        },
        { 
            id: 'mistura-tanques', 
            nome: 'Mistura de Tanques', 
            categoria: 'Finalização', 
            descricao: 'Combinação de produtos em tanques', 
            icon: 'fas fa-exchange-alt', 
            favorito: false,
            frequencia: 28
        },
        { 
            id: 'acidez', 
            nome: 'Conversão de Acidez', 
            categoria: 'Laboratório', 
            descricao: 'Medição de acidez em sucos', 
            icon: 'fas fa-eye-dropper', 
            favorito: false,
            frequencia: 25
        },
        { 
            id: 'ph-corrigido', 
            nome: 'pH Corrigido', 
            categoria: 'Qualidade', 
            descricao: 'Cálculos de correção de pH', 
            icon: 'fas fa-filter', 
            favorito: false,
            frequencia: 22
        },
        { 
            id: 'teor-solidos', 
            nome: 'Teor de Sólidos', 
            categoria: 'Qualidade', 
            descricao: 'Análise de conteúdo sólido', 
            icon: 'fas fa-cubes', 
            favorito: false,
            frequencia: 20
        }
    ];
    
    // Configurações dos cálculos e fatores de conversão
    const configuracoes = {
        // Produção 200g
        producao_200g: {
            toleranciaPadrao: 2.5,
            valorEspecificado: 200.0,
            taraMedia: 19.0
        },
        
        // Brix
        brix: {
            temperaturaRef: 20.0,
            fatores: {
                standard: 1.0,
                citrus: 0.98,
                nectars: 1.02,
                concentrate: 0.95
            }
        },
        
        // Finalização Tanque
        finalizacaoTanque: {
            brixPadrao: {
                suco: 11.2,
                nectar: 13.5,
                refresco: 8.5
            },
            fatores: {
                densidade: 1.045
            }
        }
    };
    
    /**
     * Funções para cálculo de produção 200g
     */
    window.calculoProducao200g = {
        /**
         * Calcula o peso líquido da embalagem
         * @param {number} pesoBruto - Peso bruto medido em gramas
         * @param {number} tara - Peso da embalagem vazia em gramas
         * @returns {number} Peso líquido em gramas
         */
        calcularPesoLiquido: function(pesoBruto, tara) {
            return pesoBruto - tara;
        },
        
        /**
         * Verifica se o peso está dentro da tolerância
         * @param {number} pesoLiquido - Peso líquido calculado
         * @param {number} pesoEspecificado - Peso que deveria ter
         * @param {number} tolerancia - Percentual de tolerância permitido
         * @returns {object} Status e desvio do peso
         */
        verificarTolerancia: function(pesoLiquido, pesoEspecificado, tolerancia) {
            const limiteInferior = pesoEspecificado * (1 - (tolerancia / 100));
            const limiteSuperior = pesoEspecificado * (1 + (tolerancia / 100));
            const desvio = ((pesoLiquido - pesoEspecificado) / pesoEspecificado) * 100;
            
            let status, statusClass;
            
            if (pesoLiquido < limiteInferior) {
                status = 'Abaixo da tolerância';
                statusClass = 'alert-danger';
            } else if (pesoLiquido > limiteSuperior) {
                status = 'Acima da tolerância';
                statusClass = 'alert-warning';
            } else {
                status = 'Dentro da tolerância';
                statusClass = 'alert-success';
            }
            
            return {
                status,
                statusClass,
                desvio,
                limiteInferior,
                limiteSuperior,
                diferencaAbsoluta: pesoLiquido - pesoEspecificado
            };
        }
    };
    
    /**
     * Funções para cálculo de Brix Padrão
     */
    window.calculoBrix = {
        /**
         * Corrige o Brix de acordo com a temperatura
         * @param {number} brixMedido - Brix medido no refratômetro
         * @param {number} temperatura - Temperatura da amostra em °C
         * @param {string|number} fatorCorrecao - Fator de correção a aplicar
         * @returns {number} Brix corrigido
         */
        calcularBrixCorrigido: function(brixMedido, temperatura, fatorCorrecao) {
            // Determinar o fator de correção de temperatura
            const deltaTempRef = temperatura - configuracoes.brix.temperaturaRef;
            
            // Fator aproximado: a cada 1°C acima de 20°C, adicionar 0.06 ao Brix
            const correcaoTemp = deltaTempRef * 0.06;
            
            // Aplicar correção de temperatura
            let brixCorrigidoTemp = brixMedido;
            
            if (temperatura !== configuracoes.brix.temperaturaRef) {
                brixCorrigidoTemp = temperatura > configuracoes.brix.temperaturaRef 
                    ? brixMedido - correcaoTemp 
                    : brixMedido + Math.abs(correcaoTemp);
            }
            
            // Aplicar fator de correção do tipo de produto
            let fator = 1.0;
            
            if (typeof fatorCorrecao === 'string') {
                fator = configuracoes.brix.fatores[fatorCorrecao] || 1.0;
            } else if (typeof fatorCorrecao === 'number') {
                fator = fatorCorrecao;
            }
            
            const brixFinal = brixCorrigidoTemp * fator;
            
            return {
                brixOriginal: brixMedido,
                brixCorrigidoTemp: brixCorrigidoTemp,
                brixFinal: brixFinal,
                correcaoAplicada: correcaoTemp,
                fatorAplicado: fator
            };
        }
    };
    
    /**
     * Funções para cálculo de Finalização de Tanque
     */
    window.calculoFinalizacaoTanque = {
        /**
         * Calcula a quantidade de água para diluição
         * @param {number} brixAtual - Brix atual do tanque
         * @param {number} brixDesejado - Brix final desejado
         * @param {number} volumeAtual - Volume atual no tanque em litros
         * @returns {number} Volume de água a adicionar
         */
        calcularDiluicao: function(brixAtual, brixDesejado, volumeAtual) {
            // Se brixAtual ≤ brixDesejado, não é possível diluir
            if (brixAtual <= brixDesejado) {
                return {
                    possivel: false,
                    mensagem: "O Brix atual já é menor ou igual ao desejado. Não é possível diluir.",
                    formula: "Não aplicável"
                };
            }
            
            // Fórmula: V2 = V1 * (B1 / B2 - 1)
            // Onde: V2 = volume de água a adicionar, V1 = volume atual, 
            // B1 = brix atual, B2 = brix desejado
            const volumeAgua = volumeAtual * (brixAtual / brixDesejado - 1);
            const volumeFinal = volumeAtual + volumeAgua;
            
            return {
                possivel: true,
                volumeAgua: volumeAgua,
                volumeFinal: volumeFinal,
                reducaoBrix: brixAtual - brixDesejado,
                formula: `V2 = ${volumeAtual} × (${brixAtual} / ${brixDesejado} - 1) = ${volumeAgua.toFixed(2)} L`
            };
        },
        
        /**
         * Calcula a quantidade de concentrado para aumentar o Brix
         * @param {number} brixAtual - Brix atual do tanque
         * @param {number} brixDesejado - Brix final desejado
         * @param {number} volumeAtual - Volume atual no tanque em litros
         * @param {number} brixConcentrado - Brix do concentrado a adicionar
         * @returns {object} Resultados do cálculo
         */
        calcularConcentracao: function(brixAtual, brixDesejado, volumeAtual, brixConcentrado) {
            // Se brixAtual ≥ brixDesejado, não é necessário concentrar
            if (brixAtual >= brixDesejado) {
                return {
                    possivel: false,
                    mensagem: "O Brix atual já é maior ou igual ao desejado. Não é necessário adicionar concentrado.",
                    formula: "Não aplicável"
                };
            }
            
            // Se brixConcentrado ≤ brixDesejado, não é possível atingir o Brix desejado
            if (brixConcentrado <= brixDesejado) {
                return {
                    possivel: false,
                    mensagem: "O Brix do concentrado deve ser maior que o Brix desejado.",
                    formula: "Não aplicável"
                };
            }
            
            // Fórmula: V2 = V1 * (B2 - B1) / (B3 - B2)
            // Onde: V2 = volume de concentrado, V1 = volume atual, 
            // B1 = brix atual, B2 = brix desejado, B3 = brix concentrado
            const volumeConcentrado = volumeAtual * (brixDesejado - brixAtual) / (brixConcentrado - brixDesejado);
            const volumeFinal = volumeAtual + volumeConcentrado;
            
            return {
                possivel: true,
                volumeConcentrado: volumeConcentrado,
                volumeFinal: volumeFinal,
                aumentoBrix: brixDesejado - brixAtual,
                formula: `V2 = ${volumeAtual} × (${brixDesejado} - ${brixAtual}) / (${brixConcentrado} - ${brixDesejado}) = ${volumeConcentrado.toFixed(2)} L`
            };
        }
    };
    
    console.log('ZeloCalc: Módulo de cálculos técnicos carregado com sucesso!');
});