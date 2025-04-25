; Script de instalação NSIS para ZELOPACK
; Para usar este script, você precisa instalar o NSIS: https://nsis.sourceforge.io/

; Nome do produto e versão
!define PRODUCT_NAME "ZELOPACK"
!define PRODUCT_VERSION "1.0.0"
!define PRODUCT_PUBLISHER "ZELOPACK"
!define PRODUCT_WEB_SITE "https://zelopack.com.br"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\ZELOPACK.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; Configuração do instalador moderna
SetCompressor lzma
!include "MUI2.nsh"

; Interface de configuração MUI
!define MUI_ABORTWARNING
!define MUI_ICON "static\img\favicon.ico"
!define MUI_UNICON "static\img\favicon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "static\img\installer-sidebar.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "static\img\installer-header.bmp"
!define MUI_HEADERIMAGE_RIGHT

; Páginas do assistente de instalação
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\ZELOPACK.exe"
!insertmacro MUI_PAGE_FINISH

; Páginas do assistente de desinstalação
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Idioma
!insertmacro MUI_LANGUAGE "PortugueseBR"

; Nome do arquivo de instalação
OutFile "ZELOPACK_Setup.exe"

; Diretório de instalação padrão
InstallDir "$PROGRAMFILES\ZELOPACK"

; Registrar a localização no registro
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""

; Mostrar informações do instalador
ShowInstDetails show
ShowUnInstDetails show

; Seção principal de instalação
Section "Principal" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  
  ; Extrair todos os arquivos do diretório dist
  File /r "dist\ZELOPACK\*.*"
  
  ; Criar atalho no menu iniciar
  CreateDirectory "$SMPROGRAMS\ZELOPACK"
  CreateShortCut "$SMPROGRAMS\ZELOPACK\ZELOPACK.lnk" "$INSTDIR\ZELOPACK.exe"
  CreateShortCut "$DESKTOP\ZELOPACK.lnk" "$INSTDIR\ZELOPACK.exe"
  
  ; Escrever chaves de registro para desinstalação
  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\ZELOPACK.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\ZELOPACK.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

; Seção de desinstalação
Section Uninstall
  ; Remover arquivos e atalhos
  Delete "$INSTDIR\*.*"
  RMDir /r "$INSTDIR"
  
  Delete "$SMPROGRAMS\ZELOPACK\*.*"
  RMDir "$SMPROGRAMS\ZELOPACK"
  Delete "$DESKTOP\ZELOPACK.lnk"
  
  ; Remover chaves de registro
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
SectionEnd