@echo off
REM Script para criar o instalador Windows do ZELOPACK

echo ===================================================
echo ZELOPACK - Criador de Instalador Windows
echo ===================================================
echo.

REM Verificar se o PyInstaller criou os arquivos
if not exist "dist\ZELOPACK\ZELOPACK.exe" (
    echo Erro: Executável não encontrado! Execute build_executable.bat primeiro.
    pause
    exit /b 1
)

REM Verificar se o NSIS está instalado
where makensis.exe > nul 2>&1
if %errorlevel% neq 0 (
    echo Aviso: NSIS não encontrado no PATH. O script de instalação será gerado, mas não será compilado.
    echo Para criar o instalador, instale o NSIS de https://nsis.sourceforge.io/
    echo e execute "makensis.exe installer_config.nsi" manualmente.
    pause
    exit /b 1
)

REM Verificar se as imagens foram geradas
if not exist "static\img\installer-sidebar.bmp" (
    echo Gerando imagens para o instalador...
    python create_installer_images.py
    echo.
)

echo 1. Compilando o instalador NSIS...
makensis.exe installer_config.nsi
if %errorlevel% neq 0 (
    echo Erro ao compilar o instalador. Verifique o NSIS e as configurações.
    pause
    exit /b 1
)

echo 2. Movendo o instalador para a pasta 'installers'...
if not exist "installers" mkdir installers
move /Y "ZELOPACK_Setup.exe" "installers\ZELOPACK_Setup.exe"
echo.

echo Instalador criado com sucesso!
echo O arquivo está disponível em: installers\ZELOPACK_Setup.exe
echo.

pause