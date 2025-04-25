# Sistema de Testes e Monitoramento Automático do Zelopack

Este diretório contém o sistema de testes automatizados, monitoramento contínuo e assistência baseada em IA para o projeto Zelopack.

## Componentes Principais

### 1. Auto Check (`auto_check.py`)

Sistema automatizado de testes e verificações de qualidade de código que:
- Verifica arquivos estáticos, Python, templates e modelos de banco de dados
- Identifica problemas de código, segurança e acessibilidade
- Aplica correções automáticas para problemas simples
- Gera relatórios detalhados

**Uso:**
```bash
python auto_check.py              # Executa verificações básicas
python auto_check.py --test       # Executa apenas testes
python auto_check.py --fix        # Executa testes e aplica correções
python auto_check.py --watch      # Monitora alterações em tempo real
python auto_check.py --schedule   # Agenda verificações periódicas
```

### 2. Monitor Zelopack (`zelopack_monitor.py`)

Sistema de monitoramento e melhoria contínua que:
- Executa testes de componentes
- Analisa código em busca de melhorias
- Verifica problemas de performance
- Gera relatórios detalhados com sugestões

**Uso:**
```bash
python -m tests.zelopack_monitor             # Executar monitoramento padrão
python -m tests.zelopack_monitor --fix       # Aplicar correções automáticas
python -m tests.zelopack_monitor --watch     # Monitorar alterações continuamente
```

### 3. Assistente IA (`zelopack_ai_assistant.py`)

Assistente baseado em IA que:
- Analisa código e sugere melhorias avançadas
- Aprende com problemas recorrentes
- Aplica correções baseadas em padrões
- Gera sugestões inteligentes

**Uso:**
```bash
python -m tests.zelopack_ai_assistant --suggest   # Gerar sugestões de melhoria
python -m tests.zelopack_ai_assistant --fix       # Aplicar melhorias automáticas
python -m tests.zelopack_ai_assistant --dry-run   # Simular melhorias sem aplicá-las
```

## Estrutura de Diretórios

```
tests/
├── reports/           # Relatórios gerados pelos sistemas de teste e monitoramento
├── suggestions/       # Sugestões geradas pelo assistente de IA
├── fixes/             # Backups de arquivos modificados automaticamente
├── auto_test_runner.py  # Executor de testes automático
├── test_components.py   # Testes de componentes do sistema
├── zelopack_monitor.py  # Sistema de monitoramento e melhoria contínua
└── zelopack_ai_assistant.py  # Assistente de IA para melhorias avançadas
```

## Arquivos de Configuração

- `improvement_rules.json` - Regras para detecção e correção de problemas de código
- `code_patterns.json` - Padrões de código para análise pelo assistente de IA
- `ai_knowledge_base.json` - Base de conhecimento do assistente de IA
- `project_info.json` - Informações sobre o projeto para contextualização da IA

## Execução Agendada

Os sistemas podem ser configurados para execução periódica:

1. **Auto Check**: A cada 2 horas
2. **Zelopack Monitor**: A cada 4 horas
3. **Assistente IA**: Diariamente às 2h da manhã

Para configurar a execução agendada:
```bash
python auto_check.py --setup-cron
python -m tests.zelopack_monitor --schedule
python -m tests.zelopack_ai_assistant --schedule
```

## Integração com OpenAI

Para habilitar os recursos avançados de IA, defina a variável de ambiente `OPENAI_API_KEY`:

```bash
export OPENAI_API_KEY="sua-chave-api"
```

Ou passe a chave diretamente:

```bash
python -m tests.zelopack_ai_assistant --key "sua-chave-api" --suggest
```

## Relatórios

Os relatórios são gerados em formato JSON e texto simples, e são armazenados no diretório `reports/`. Consulte o README naquele diretório para mais detalhes sobre a estrutura dos relatórios.