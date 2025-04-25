#!/usr/bin/env python3
"""
Cria imagens para o instalador NSIS
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_installer_sidebar():
    """Cria uma imagem para a barra lateral do instalador"""
    width, height = 164, 314
    color = (13, 110, 253)  # Azul primário (#0d6efd)
    
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)
    
    # Adicionar texto "ZELOPACK"
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except Exception:
        font = ImageFont.load_default()
    
    text = "ZELOPACK"
    text_color = (255, 255, 255)
    
    # Posicionar o texto
    try:
        # Tentar obter largura e altura do texto
        text_width, text_height = font.getbbox(text)[2:4]
        position = ((width - text_width) // 2, 40)
    except Exception:
        position = (30, 40)
    
    draw.text(position, text, fill=text_color, font=font)
    
    # Adicionar subtítulo
    try:
        small_font = ImageFont.truetype("arial.ttf", 12)
    except Exception:
        small_font = ImageFont.load_default()
    
    subtitle = "Sistema de Gerenciamento de Laudos"
    
    try:
        # Tentar obter largura e altura do texto
        sub_width, sub_height = small_font.getbbox(subtitle)[2:4]
        sub_position = ((width - sub_width) // 2, 80)
    except Exception:
        sub_position = (10, 80)
    
    draw.text(sub_position, subtitle, fill=text_color, font=small_font)
    
    # Adicionar versão
    version = "Versão 1.0.0"
    
    try:
        # Tentar obter largura e altura do texto
        ver_width, ver_height = small_font.getbbox(version)[2:4]
        ver_position = ((width - ver_width) // 2, height - 40)
    except Exception:
        ver_position = (40, height - 40)
    
    draw.text(ver_position, version, fill=text_color, font=small_font)
    
    # Salvar a imagem
    os.makedirs("static/img", exist_ok=True)
    sidebar_path = os.path.join("static", "img", "installer-sidebar.bmp")
    img.save(sidebar_path, format="BMP")
    print(f"Imagem da barra lateral do instalador gerada: {sidebar_path}")
    
    return sidebar_path

def create_installer_header():
    """Cria uma imagem para o cabeçalho do instalador"""
    width, height = 150, 57
    color = (13, 110, 253)  # Azul primário (#0d6efd)
    
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)
    
    # Adicionar texto "ZELOPACK"
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
    
    text = "ZELOPACK"
    text_color = (255, 255, 255)
    
    # Posicionar o texto
    try:
        # Tentar obter largura e altura do texto
        text_width, text_height = font.getbbox(text)[2:4]
        position = ((width - text_width) // 2, (height - text_height) // 2)
    except Exception:
        position = (20, 15)
    
    draw.text(position, text, fill=text_color, font=font)
    
    # Salvar a imagem
    header_path = os.path.join("static", "img", "installer-header.bmp")
    img.save(header_path, format="BMP")
    print(f"Imagem do cabeçalho do instalador gerada: {header_path}")
    
    return header_path

def create_license_file():
    """Cria um arquivo de licença básico para o instalador"""
    license_text = """ZELOPACK - SISTEMA DE GERENCIAMENTO DE LAUDOS
CONTRATO DE LICENÇA DE USO DE SOFTWARE
======================================

Ao instalar este software, você concorda com os seguintes termos:

1. CONCESSÃO DE LICENÇA:
   Este software é licenciado, não vendido. Esta licença concede a você o direito não exclusivo de usar o software.

2. DIREITOS AUTORAIS:
   Todos os direitos, título e interesse no software permanecem com a ZELOPACK.

3. LIMITAÇÕES:
   Você não pode:
   - Reverter a engenharia, descompilar ou desmontar o software.
   - Alugar, arrendar ou emprestar o software.
   - Transferir o software ou este acordo para terceiros.

4. ISENÇÃO DE GARANTIAS:
   Este software é fornecido "como está" sem garantias de qualquer tipo.

5. LIMITAÇÃO DE RESPONSABILIDADE:
   Em nenhum caso a ZELOPACK será responsável por quaisquer danos consequenciais, 
   especiais, indiretos ou incidentais relacionados ao uso do software.

© 2025 ZELOPACK. Todos os direitos reservados.
"""
    
    license_path = os.path.join("LICENSE.txt")
    with open(license_path, "w") as f:
        f.write(license_text)
    
    print(f"Arquivo de licença gerado: {license_path}")
    
    return license_path

if __name__ == "__main__":
    create_installer_sidebar()
    create_installer_header()
    create_license_file()
    print("Todas as imagens e arquivos do instalador foram gerados.")