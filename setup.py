#!/usr/bin/env python3
"""
Script de configuração para instalação do ZELOPACK
"""

from setuptools import setup, find_packages
import os

# Obter a versão atual do arquivo (se existir)
version = '1.0.0'
version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
if os.path.exists(version_file):
    with open(version_file, 'r') as f:
        version = f.read().strip()

# Ler o README para a descrição longa
long_description = """
# ZELOPACK - Sistema de Gerenciamento de Laudos

Sistema completo para gerenciamento de laudos e relatórios técnicos para indústria de sucos.
Inclui funcionalidades de upload, busca, visualização e gestão de laudos com dashboard
e recursos avançados de análise.

## Características principais:

- Interface moderna e intuitiva
- Sistema de autenticação seguro
- Upload e gerenciamento de arquivos
- Dashboards interativos
- Formulários personalizados
- Controle de acesso baseado em funções
- Banco de dados PostgreSQL
"""

# Dependências do projeto
requirements = [
    'flask',
    'flask-login',
    'flask-sqlalchemy',
    'flask-wtf',
    'email-validator',
    'werkzeug',
    'jinja2',
    'sqlalchemy',
    'matplotlib',
    'numpy',
    'pandas',
    'openpyxl',
    'pillow',
    'pypdf2',
    'python-docx',
    'reportlab',
    'sendgrid',
    'twilio',
    'psycopg2-binary',
    'gunicorn',
]

setup(
    name="zelopack",
    version=version,
    author="ZELOPACK",
    author_email="admin@zelopack.com.br",
    description="Sistema de Gerenciamento de Laudos para a indústria de sucos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://zelopack.com.br",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "zelopack=zelopack_app:main",
        ],
    },
)