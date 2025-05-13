#!/bin/bash
# Script para compilar o aplicativo ZELOPACK em um executável

echo "==================================================="
echo "ZELOPACK - Compilador de Aplicativo Executável"
echo "==================================================="
echo

# Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python 3 não encontrado! Por favor, instale o Python 3.8 ou superior."
    exit 1
fi

echo "1. Instalando dependências necessárias..."
pip3 install -r dependencies.txt
echo

echo "2. Gerando ícone do aplicativo..."
python3 generate_icon.py
echo

echo "3. Criando diretórios necessários..."
mkdir -p dist
mkdir -p build
mkdir -p uploads
echo

echo "4. Compilando o aplicativo..."
pyinstaller zelopack.spec
echo

echo "5. Copiando arquivos adicionais..."
if [ -f "LICENSE" ]; then
    cp "LICENSE" "dist/ZELOPACK/"
fi

echo "Compilação" > "dist/ZELOPACK/version.txt"
echo "Data: $(date)" >> "dist/ZELOPACK/version.txt"
echo

echo "Compilação concluída com sucesso!"
echo "O aplicativo executável está disponível na pasta 'dist/ZELOPACK'"
echo

# Detectar o sistema operacional
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Para executar o aplicativo, clique duas vezes em 'dist/ZELOPACK.app'"
else
    echo "Para executar o aplicativo, execute o comando: 'dist/ZELOPACK/ZELOPACK'"
fi
echo

# Tornar o script executável
chmod +x dist/ZELOPACK/ZELOPACK 2>/dev/null