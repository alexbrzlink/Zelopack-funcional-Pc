#!/bin/bash
# Script para criar pacote instalável Linux (DEB ou RPM)

echo "==================================================="
echo "ZELOPACK - Criador de Pacotes para Linux"
echo "==================================================="
echo

# Verificar se o PyInstaller criou os arquivos
if [ ! -d "dist/ZELOPACK" ]; then
    echo "Erro: Executável não encontrado! Execute build_executable.sh primeiro."
    exit 1
fi

# Verificar se temos ferramentas de pacotes instaladas
PACKAGE_TYPE=""
if command -v dpkg-deb &> /dev/null; then
    PACKAGE_TYPE="deb"
elif command -v rpmbuild &> /dev/null; then
    PACKAGE_TYPE="rpm"
else
    echo "Aviso: Não foram encontradas ferramentas para criação de pacotes (dpkg-deb ou rpmbuild)."
    echo "Vamos criar um pacote portátil .tar.gz ao invés disso."
    PACKAGE_TYPE="tar"
fi

# Criar pasta para instaladores
mkdir -p installers

# Gerar imagens para o instalador se necessário
if [ ! -f "static/img/favicon.png" ]; then
    echo "1. Gerando imagens para o instalador..."
    python3 create_installer_images.py
    echo
fi

# Versão do pacote
VERSION="1.0.0"
ARCHITECTURE="amd64"  # ou x86_64 para RPM

if [ "$PACKAGE_TYPE" = "deb" ]; then
    echo "2. Criando pacote DEB..."
    
    # Criar estrutura de diretórios para pacote DEB
    PKG_DIR="installers/zelopack_${VERSION}_$ARCHITECTURE"
    mkdir -p $PKG_DIR/DEBIAN
    mkdir -p $PKG_DIR/usr/local/bin
    mkdir -p $PKG_DIR/usr/local/share/zelopack
    mkdir -p $PKG_DIR/usr/share/applications
    mkdir -p $PKG_DIR/usr/share/icons/hicolor/256x256/apps
    
    # Criar arquivo de controle
    cat > $PKG_DIR/DEBIAN/control << EOF
Package: zelopack
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCHITECTURE
Maintainer: ZELOPACK <admin@zelopack.com.br>
Description: Sistema de Gerenciamento de Laudos
 ZELOPACK é um sistema completo para gerenciamento de laudos
 e relatórios técnicos para indústria de sucos.
EOF
    
    # Copiar arquivos do executável
    cp -r dist/ZELOPACK/* $PKG_DIR/usr/local/share/zelopack/
    
    # Criar script wrapper para executável
    cat > $PKG_DIR/usr/local/bin/zelopack << EOF
#!/bin/bash
cd /usr/local/share/zelopack
./ZELOPACK "\$@"
EOF
    chmod +x $PKG_DIR/usr/local/bin/zelopack
    
    # Criar arquivo .desktop
    cat > $PKG_DIR/usr/share/applications/zelopack.desktop << EOF
[Desktop Entry]
Type=Application
Name=ZELOPACK
GenericName=Sistema de Gerenciamento de Laudos
Comment=Sistema para gerenciamento de laudos e relatórios técnicos
Icon=zelopack
Exec=zelopack
Terminal=false
Categories=Office;Utility;
EOF
    
    # Copiar ícone
    cp static/img/favicon.png $PKG_DIR/usr/share/icons/hicolor/256x256/apps/zelopack.png
    
    # Criar pacote DEB
    dpkg-deb --build $PKG_DIR installers/
    
    echo "Pacote DEB criado com sucesso: installers/zelopack_${VERSION}_${ARCHITECTURE}.deb"

elif [ "$PACKAGE_TYPE" = "rpm" ]; then
    echo "2. Criando pacote RPM..."
    
    # Criar estrutura para RPM
    RPM_BUILD_DIR="$HOME/rpmbuild"
    mkdir -p $RPM_BUILD_DIR/{SPECS,SOURCES,BUILD,RPMS,SRPMS}
    
    # Criar arquivo tar.gz para source
    mkdir -p zelopack-$VERSION
    cp -r dist/ZELOPACK/* zelopack-$VERSION/
    cp static/img/favicon.png zelopack-$VERSION/
    cp LICENSE.txt zelopack-$VERSION/
    
    tar -czf $RPM_BUILD_DIR/SOURCES/zelopack-$VERSION.tar.gz zelopack-$VERSION
    rm -rf zelopack-$VERSION
    
    # Criar arquivo spec
    cat > $RPM_BUILD_DIR/SPECS/zelopack.spec << EOF
Name:           zelopack
Version:        $VERSION
Release:        1%{?dist}
Summary:        Sistema de Gerenciamento de Laudos

License:        Proprietary
URL:            https://zelopack.com.br
Source0:        %{name}-%{version}.tar.gz

BuildArch:      x86_64
Requires:       bash

%description
ZELOPACK é um sistema completo para gerenciamento de laudos
e relatórios técnicos para indústria de sucos.

%prep
%setup -q

%install
mkdir -p %{buildroot}/usr/local/share/zelopack
mkdir -p %{buildroot}/usr/local/bin
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons/hicolor/256x256/apps

cp -r * %{buildroot}/usr/local/share/zelopack/

cat > %{buildroot}/usr/local/bin/zelopack << 'EOF'
#!/bin/bash
cd /usr/local/share/zelopack
./ZELOPACK "\$@"
EOF
chmod +x %{buildroot}/usr/local/bin/zelopack

cat > %{buildroot}/usr/share/applications/zelopack.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=ZELOPACK
GenericName=Sistema de Gerenciamento de Laudos
Comment=Sistema para gerenciamento de laudos e relatórios técnicos
Icon=zelopack
Exec=zelopack
Terminal=false
Categories=Office;Utility;
EOF

cp favicon.png %{buildroot}/usr/share/icons/hicolor/256x256/apps/zelopack.png

%files
/usr/local/share/zelopack
/usr/local/bin/zelopack
/usr/share/applications/zelopack.desktop
/usr/share/icons/hicolor/256x256/apps/zelopack.png

%changelog
* $(date '+%a %b %d %Y') ZELOPACK <admin@zelopack.com.br> - $VERSION-1
- Versão inicial do pacote
EOF
    
    # Compilar RPM
    rpmbuild -ba $RPM_BUILD_DIR/SPECS/zelopack.spec
    
    # Copiar para pasta de instaladores
    cp $RPM_BUILD_DIR/RPMS/x86_64/zelopack-$VERSION-*.rpm installers/
    
    echo "Pacote RPM criado com sucesso em installers/"

else
    echo "2. Criando pacote portátil (tar.gz)..."
    
    # Criar diretório de aplicativo
    APP_DIR="installers/zelopack-$VERSION-linux"
    mkdir -p $APP_DIR
    
    # Copiar arquivos
    cp -r dist/ZELOPACK/* $APP_DIR/
    cp LICENSE.txt $APP_DIR/
    cp static/img/favicon.png $APP_DIR/
    
    # Criar script de instalação
    cat > $APP_DIR/install.sh << 'EOF'
#!/bin/bash
# Script de instalação simples para ZELOPACK

echo "Instalando ZELOPACK..."

# Diretório de instalação
INSTALL_DIR="/opt/zelopack"
BIN_LINK="/usr/local/bin/zelopack"
DESKTOP_FILE="/usr/share/applications/zelopack.desktop"
ICON_FILE="/usr/share/icons/hicolor/256x256/apps/zelopack.png"

# Criar diretório de instalação
sudo mkdir -p $INSTALL_DIR
sudo cp -r * $INSTALL_DIR/

# Remover o próprio instalador do diretório de destino
sudo rm -f "$INSTALL_DIR/install.sh"

# Criar link simbólico para o executável
sudo ln -sf "$INSTALL_DIR/ZELOPACK" $BIN_LINK

# Criar arquivo .desktop
cat > /tmp/zelopack.desktop << EOFDESKTOP
[Desktop Entry]
Type=Application
Name=ZELOPACK
GenericName=Sistema de Gerenciamento de Laudos
Comment=Sistema para gerenciamento de laudos e relatórios técnicos
Icon=zelopack
Exec=zelopack
Terminal=false
Categories=Office;Utility;
EOFDESKTOP

sudo mkdir -p $(dirname $DESKTOP_FILE)
sudo cp /tmp/zelopack.desktop $DESKTOP_FILE
rm -f /tmp/zelopack.desktop

# Copiar ícone
sudo mkdir -p $(dirname $ICON_FILE)
sudo cp "$INSTALL_DIR/favicon.png" $ICON_FILE

echo "ZELOPACK instalado com sucesso!"
echo "Você pode iniciar o programa digitando 'zelopack' no terminal"
echo "ou através do menu de aplicativos do seu sistema."
EOF
    
    chmod +x $APP_DIR/install.sh
    
    # Criar arquivo tar.gz
    cd installers
    tar -czf "zelopack-$VERSION-linux.tar.gz" "zelopack-$VERSION-linux"
    rm -rf "zelopack-$VERSION-linux"
    cd ..
    
    echo "Pacote portátil criado com sucesso: installers/zelopack-$VERSION-linux.tar.gz"
fi

echo
echo "Criação de pacote Linux concluída!"
echo "Os arquivos estão disponíveis na pasta 'installers/'."
echo

exit 0