#!/bin/bash
# Script para criar pacote instalável macOS (.app e .dmg)

echo "==================================================="
echo "ZELOPACK - Criador de Instalador para macOS"
echo "==================================================="
echo

# Verificar se estamos em macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Erro: Este script deve ser executado em um sistema macOS."
    echo "Para sistemas Linux, veja o README para instruções de instalação."
    exit 1
fi

# Verificar se o PyInstaller criou os arquivos
if [ ! -d "dist/ZELOPACK.app" ]; then
    echo "Erro: Aplicativo macOS não encontrado! Execute build_executable.sh primeiro."
    echo "Certifique-se de que o PyInstaller criou um aplicativo .app."
    exit 1
fi

# Verificar se o create-dmg está instalado
if ! command -v create-dmg &> /dev/null; then
    echo "Instalando create-dmg via Homebrew..."
    brew install create-dmg
    if [ $? -ne 0 ]; then
        echo "Erro ao instalar create-dmg. Por favor, instale manualmente:"
        echo "brew install create-dmg"
        exit 1
    fi
fi

# Criar diretório para o instalador
mkdir -p installers

# Gerar imagens para o instalador
echo "1. Gerando imagens para o instalador..."
python3 create_installer_images.py
echo

# Adicionar ícone ao aplicativo
echo "2. Configurando ícone do aplicativo..."
cp static/img/favicon.icns dist/ZELOPACK.app/Contents/Resources/
echo

# Criar arquivo DMG
echo "3. Criando arquivo DMG para distribuição..."
create-dmg \
    --volname "ZELOPACK Installer" \
    --volicon "static/img/favicon.icns" \
    --background "static/img/installer-background.png" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --icon "ZELOPACK.app" 200 190 \
    --hide-extension "ZELOPACK.app" \
    --app-drop-link 600 185 \
    "installers/ZELOPACK_Installer.dmg" \
    "dist/ZELOPACK.app"

if [ $? -ne 0 ]; then
    echo "Aviso: Não foi possível criar o DMG. Talvez algumas opções não estejam disponíveis."
    echo "Criando DMG básico..."
    
    # Criar DMG simples
    hdiutil create -volname "ZELOPACK" -srcfolder "dist/ZELOPACK.app" -ov -format UDZO "installers/ZELOPACK_Installer.dmg"
fi

echo
echo "Instalador macOS criado com sucesso!"
echo "O arquivo está disponível em: installers/ZELOPACK_Installer.dmg"
echo

exit 0