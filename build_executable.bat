@echo off
REM Script para compilar o aplicativo ZELOPACK em um executável

echo ===================================================
echo ZELOPACK - Compilador de Aplicativo Executável
echo ===================================================
echo.

REM Verificar se o Python está instalado
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Erro: Python não encontrado! Por favor, instale o Python 3.8 ou superior.
    pause
    exit /b 1
)

echo 1. Instalando dependências necessárias...
pip install -r dependencies.txt
echo.

echo 2. Gerando ícone do aplicativo...
python generate_icon.py
echo.

echo 3. Criando diretórios necessários...
if not exist "dist" mkdir dist
if not exist "build" mkdir build
if not exist "uploads" mkdir uploads
echo.

echo 4. Compilando o aplicativo...
pyinstaller zelopack.spec
echo.

echo 5. Copiando arquivos adicionais...
if exist "LICENSE" copy "LICENSE" "dist\ZELOPACK\"
echo Compilação > "dist\ZELOPACK\version.txt"
echo Data: %date% %time% >> "dist\ZELOPACK\version.txt"
echo.

echo Compilação concluída com sucesso!
echo O aplicativo executável está disponível na pasta 'dist\ZELOPACK'
echo.

echo Para executar o aplicativo, clique duas vezes em 'dist\ZELOPACK\ZELOPACK.exe'
echo.

pause