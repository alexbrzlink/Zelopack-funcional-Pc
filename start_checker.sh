#!/bin/bash
# Script para iniciar o verificador automático em segundo plano
# com todos os mecanismos possíveis de persistência

echo "Iniciando verificador automático do ZeloPack..."

# Defina o nome do arquivo de log
LOG_FILE="zelopack_checker.log"

# Crie diretório de logs se não existir
mkdir -p logs

# Defina o comando a ser executado (vai rodar mesmo se o terminal for fechado)
nohup python auto_check.py --schedule --minutes 5 > $LOG_FILE 2>&1 &

# Salve o PID para referência futura
CHECKER_PID=$!
echo $CHECKER_PID > .checker_pid

echo "Verificador automático iniciado com PID: $CHECKER_PID"
echo "Log disponível em: $LOG_FILE"

# Verifique se o processo ainda está rodando após 2 segundos
sleep 2
if ps -p $CHECKER_PID > /dev/null; then
    echo "Processo verificado e funcionando."
else
    echo "AVISO: O processo parece ter encerrado prematuramente!"
    echo "Tentando método alternativo..."
    
    # Tente o método alternativo mais simples
    python simple_background_checker.py &
    SIMPLE_PID=$!
    echo $SIMPLE_PID > .simple_checker_pid
    echo "Verificador simplificado iniciado com PID: $SIMPLE_PID"
fi

echo "Configuração concluída!"