# Relatórios do Sistema de Monitoramento Zelopack

Este diretório contém relatórios gerados pelo sistema de monitoramento e análise automática do Zelopack. Os relatórios são gerados periodicamente para ajudar a identificar problemas, sugerir melhorias e monitorar a qualidade do código.

## Tipos de Relatórios

Os relatórios são gerados em dois formatos:

1. **JSON** - Formato completo e estruturado para processamento automatizado
2. **TXT** - Formato de texto legível para análise humana

## Nomenclatura dos Arquivos

Os arquivos de relatório seguem o padrão de nomenclatura:

- `zelopack_report_YYYY-MM-DD_HH-MM-SS.json` - Relatório do sistema de monitoramento em JSON
- `zelopack_report_YYYY-MM-DD_HH-MM-SS.txt` - Relatório do sistema de monitoramento em texto
- `ai_report_YYYY-MM-DD_HH-MM-SS.json` - Relatório do assistente de IA em JSON
- `ai_report_YYYY-MM-DD_HH-MM-SS.txt` - Relatório do assistente de IA em texto

## Estrutura do Relatório JSON

Relatório do sistema de monitoramento:

```json
{
  "timestamp": "2025-04-25_19-13-15",
  "test_results": {
    "passed": ["test_01", "test_02"],
    "failed": ["test_03"],
    "errors": [],
    "details": { ... }
  },
  "improvements": {
    "total": 100,
    "by_severity": {
      "critical": 5,
      "warning": 30,
      "info": 65
    },
    "critical_issues": 5,
    "details": [ ... ]
  },
  "performance_issues": {
    "total": 8,
    "details": [ ... ]
  },
  "auto_fixes": {
    "total": 25,
    "applied": 20,
    "details": [ ... ]
  }
}
```

Relatório do assistente de IA:

```json
{
  "timestamp": "2025-04-25_19-30-10",
  "suggestions": [
    {
      "title": "Título da sugestão",
      "description": "Descrição detalhada da sugestão",
      "items": ["Item 1", "Item 2", "Item 3"],
      "priority": "high|medium|low"
    },
    ...
  ],
  "improvements": [
    {
      "file": "path/to/file.py",
      "line": 42,
      "pattern": "nome_padrão",
      "original": "linha original",
      "fixed": "linha corrigida",
      "applied": true|false
    },
    ...
  ]
}
```

## Uso dos Relatórios

Os relatórios podem ser usados para:

1. **Identificar problemas recorrentes** - Analisar padrões de problemas que aparecem frequentemente
2. **Priorizar melhorias** - Usar a classificação de severidade para priorizar correções
3. **Verificar progresso** - Comparar relatórios ao longo do tempo para verificar o progresso
4. **Implementar sugestões da IA** - Avaliar e implementar as sugestões fornecidas pelo assistente de IA

## Rotação e Limpeza

Os relatórios mais antigos do que 30 dias são automaticamente compactados e movidos para a pasta `archived`. Relatórios com mais de 90 dias são excluídos automaticamente.