#!/usr/bin/env python3
"""
Gera um ícone para o aplicativo ZELOPACK
"""

from PIL import Image, ImageDraw, ImageFont
import os

def generate_icon():
    """
    Gera um ícone simples com a letra Z em fundo azul para o aplicativo ZELOPACK
    """
    # Tamanhos comuns para ícones
    sizes = [16, 32, 48, 64, 128, 256]
    
    # Cor de fundo e texto
    background_color = (13, 110, 253)  # Azul primário (#0d6efd)
    text_color = (255, 255, 255)  # Branco
    
    # Criar imagens para cada tamanho
    images = []
    
    for size in sizes:
        # Criar uma imagem quadrada com fundo azul
        img = Image.new('RGB', (size, size), background_color)
        draw = ImageDraw.Draw(img)
        
        # Tentar usar uma fonte instalada, ou usar a fonte padrão
        try:
            # A fonte deve ser escalada com o tamanho da imagem
            font_size = int(size * 0.7)
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            # Se não encontrar a fonte, usar a fonte padrão
            font = ImageFont.load_default()
        
        # Desenhar a letra "Z" centralizada
        letter = "Z"
        try:
            # Obter o tamanho do texto - método mais recente
            try:
                text_width, text_height = font.getsize(letter)
            except AttributeError:
                # Fallback para métodos mais novos do PIL
                text_width, text_height = draw.textbbox((0, 0), letter, font=font)[2:4]
                
            # Posicionar o texto no centro
            position = ((size - text_width) // 2, (size - text_height) // 2)
            # Desenhar o texto
            draw.text(position, letter, fill=text_color, font=font)
        except Exception:
            # Método alternativo se o anterior falhar
            draw.text((size // 4, size // 4), letter, fill=text_color)
        
        images.append(img)
    
    # Salvar como ICO (Windows)
    icon_path = os.path.join("static", "img", "favicon.ico")
    images[0].save(icon_path, format='ICO', sizes=[(size, size) for size in sizes])
    print(f"Ícone gerado: {icon_path}")
    
    # Salvar também como PNG para web e outros sistemas
    png_path = os.path.join("static", "img", "favicon.png")
    images[-1].save(png_path)  # Salva o maior tamanho como PNG
    print(f"Ícone PNG gerado: {png_path}")
    
    return icon_path

if __name__ == "__main__":
    icon_path = generate_icon()
    print(f"Ícone salvo em: {icon_path}")