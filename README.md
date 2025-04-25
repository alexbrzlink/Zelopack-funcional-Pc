# ZELOPACK - Sistema de Gerenciamento de Laudos

Sistema completo para gerenciamento de laudos e relatórios técnicos para indústria de sucos.
Inclui funcionalidades de upload, busca, visualização e gestão de laudos com dashboard
e recursos avançados de análise.

## Características principais

- Interface moderna e intuitiva
- Sistema de autenticação seguro
- Upload e gerenciamento de arquivos
- Dashboards interativos
- Formulários personalizados
- Controle de acesso baseado em funções
- Banco de dados PostgreSQL

## Requisitos de Sistema

- Python 3.8 ou superior
- Navegador Web moderno (Chrome, Firefox, Edge, Safari)
- 4GB de RAM ou superior
- 1GB de espaço em disco
- Conexão com a Internet (para atualizações e algumas funcionalidades)

## Instalação

### Windows

1. Baixe o instalador `ZELOPACK_Setup.exe` da pasta de releases.
2. Execute o instalador e siga as instruções na tela.
3. O aplicativo será instalado e estará disponível no menu Iniciar.

### macOS

1. Baixe o arquivo `ZELOPACK_Installer.dmg` da pasta de releases.
2. Monte o arquivo DMG clicando duas vezes sobre ele.
3. Arraste o aplicativo ZELOPACK para a pasta Aplicativos.
4. Execute o aplicativo a partir da pasta Aplicativos ou Launchpad.

### Linux

#### Debian/Ubuntu e derivados

1. Baixe o arquivo `zelopack_1.0.0_amd64.deb` da pasta de releases.
2. Instale com o comando: `sudo dpkg -i zelopack_1.0.0_amd64.deb`
3. Se houver dependências não satisfeitas, execute: `sudo apt -f install`
4. Execute o aplicativo a partir do menu de aplicativos ou com o comando `zelopack`

#### Fedora/RHEL e derivados

1. Baixe o arquivo `zelopack-1.0.0-1.fc35.x86_64.rpm` da pasta de releases.
2. Instale com o comando: `sudo dnf install zelopack-1.0.0-1.fc35.x86_64.rpm`
3. Execute o aplicativo a partir do menu de aplicativos ou com o comando `zelopack`

#### Outras distribuições

1. Baixe o arquivo `zelopack-1.0.0-linux.tar.gz` da pasta de releases.
2. Extraia o conteúdo: `tar -xzf zelopack-1.0.0-linux.tar.gz`
3. Entre no diretório extraído: `cd zelopack-1.0.0-linux`
4. Execute o script de instalação: `sudo ./install.sh`
5. Execute o aplicativo a partir do menu de aplicativos ou com o comando `zelopack`

## Execução a partir do código-fonte

Se preferir executar a partir do código-fonte, siga estas instruções:

1. Clone o repositório ou baixe o código-fonte.
2. Instale as dependências:
   ```
   pip install -r dependencies.txt
   ```
3. Execute o aplicativo:
   ```
   python zelopack_app.py
   ```

## Compilando o executável a partir do código-fonte

### Windows

1. Certifique-se de ter instalado o Python e o PyInstaller:
   ```
   pip install pyinstaller
   ```
2. Execute o script de compilação:
   ```
   build_executable.bat
   ```
3. O executável será gerado na pasta `dist\ZELOPACK\`

4. Para criar um instalador, você precisará do NSIS (Nullsoft Scriptable Install System):
   - Baixe e instale o NSIS de https://nsis.sourceforge.io/
   - Execute o script:
     ```
     create_windows_installer.bat
     ```
   - O instalador será criado na pasta `installers\`

### macOS

1. Certifique-se de ter instalado o Python e o PyInstaller:
   ```
   pip3 install pyinstaller
   ```
2. Execute o script de compilação:
   ```
   ./build_executable.sh
   ```
3. O aplicativo será gerado na pasta `dist/ZELOPACK.app/`

4. Para criar um DMG, execute:
   ```
   ./create_macos_installer.sh
   ```
   - O instalador será criado na pasta `installers/`

### Linux

1. Certifique-se de ter instalado o Python e o PyInstaller:
   ```
   pip3 install pyinstaller
   ```
2. Execute o script de compilação:
   ```
   ./build_executable.sh
   ```
3. O executável será gerado na pasta `dist/ZELOPACK/`

4. Para criar um pacote para distribuição, execute:
   ```
   ./create_linux_package.sh
   ```
   - O pacote será criado na pasta `installers/`

## Configuração do Banco de Dados

O aplicativo suporta tanto SQLite (para uso local) quanto PostgreSQL (para instalações em rede).

### Configuração PostgreSQL

Por padrão, o aplicativo procura uma variável de ambiente `DATABASE_URL` para a conexão com o banco de dados PostgreSQL. Você pode configurá-la da seguinte forma:

```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/zelopack
```

Ou definir as variáveis individuais:

```
PGHOST=localhost
PGPORT=5432
PGUSER=usuario
PGPASSWORD=senha
PGDATABASE=zelopack
```

### Configuração SQLite (Local)

Para usar SQLite localmente, não é necessária nenhuma configuração especial. O aplicativo criará automaticamente um banco de dados SQLite na pasta `instance/` do aplicativo.

## Credenciais Padrão

Ao iniciar o aplicativo pela primeira vez, será criado um usuário administrador com as seguintes credenciais:

- Usuário: `admin`
- Senha: `Alex`

Recomenda-se alterar a senha após o primeiro login.

## Contribuição

Contribuições são bem-vindas! Por favor, siga os seguintes passos:

1. Fork o repositório
2. Crie um branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para o branch (`git push origin feature/nova-funcionalidade`)
5. Crie um novo Pull Request

## Licença

Este software é proprietário © 2025 ZELOPACK. Todos os direitos reservados.

## Suporte

Para suporte técnico, entre em contato através do email admin@zelopack.com.br ou visite [zelopack.com.br](https://zelopack.com.br).