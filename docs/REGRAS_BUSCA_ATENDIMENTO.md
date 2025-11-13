# 📋 Regras de Busca de Atendimento no Calendário do Notion

## Visão Geral

A função `buscar_atendimentos_chef()` busca atendimentos do calendário do Notion para um chef específico dentro de um período de tempo.

## Parâmetros

### Entrada
- **`chef_id`** (string, obrigatório): ID do chef no Notion
- **`dias`** (int, opcional, padrão: 7): Número de dias para buscar no passado
- **`sem_relatorio`** (bool, opcional, padrão: True): Se True, retorna apenas atendimentos sem relatório

### Saída
- Lista de dicionários com informações dos atendimentos encontrados:
  ```python
  {
    'id': 'notion_page_id',
    'cliente_nome': 'Nome do Cliente',
    'cliente_id': 'notion_client_id',
    'horario': '12:00',
    'data': '2025-11-13T12:00:00-03:00',
    'data_formatada': '2025-11-13'
  }
  ```

## Regras de Filtro

### 1. Período de Data
- **Data de início**: `dias` dias atrás (inclusivo)
  - Exemplo: Se `dias=7` e hoje é `2025-11-13`, busca de `2025-11-06` até `2025-11-14`
- **Data de fim**: Amanhã (exclusivo)
  - Inclui todos os atendimentos até o final de hoje
  - Não inclui atendimentos de amanhã

### 2. Chef Alocado
- **Filtro**: O atendimento deve ter o `chef_id` na propriedade "Chef Alocado" (Relation)
- **Validação dupla**:
  1. API do Notion filtra na query (usando `contains`)
  2. Código Python valida novamente para garantir que o chef está na lista

### 3. Cliente Obrigatório
- **Filtro**: O atendimento deve ter um cliente na propriedade "Quem é" (Relation)
- **Validação**:
  - Verifica se existe relação com cliente
  - Busca o nome do cliente no banco de dados
  - Se o cliente não for encontrado, o atendimento é ignorado

### 4. Data Válida
- **Filtro**: A data do atendimento deve estar dentro do período especificado
- **Validação**: Compara `data_formatada` com `data_inicio` e `data_fim`
  - `data_formatada >= data_inicio` (inclusivo)
  - `data_formatada < data_fim` (exclusivo)

### 5. Relatório (Novo!)
- **Filtro**: Se `sem_relatorio=True` (padrão), retorna apenas atendimentos sem relatório
- **Validação**: Verifica se a propriedade "Relatório" está vazia (sem nenhuma relação)
- **Comportamento**: 
  - Se `sem_relatorio=True`: Apenas atendimentos que NÃO têm relatório
  - Se `sem_relatorio=False`: Todos os atendimentos (com ou sem relatório)

## Ordenação

- **Ordenação**: Por data (crescente)
  - Atendimentos mais antigos primeiro
  - Atendimentos mais recentes por último

## Paginação

- **Suporte**: Sim, o código busca todas as páginas de resultados
- **Processo**:
  1. Faz a primeira requisição
  2. Verifica se há mais páginas (`has_more`)
  3. Se houver, usa `next_cursor` para buscar a próxima página
  4. Repete até não haver mais páginas

## Validações e Logs

### Logs de Debug
- **Total de resultados por página**: Quantos atendimentos foram retornados pela API
- **Atendimentos válidos**: Quantos atendimentos passaram em todas as validações
- **Atendimentos ignorados**: 
  - Sem chef (`chef_nao_encontrado`)
  - Sem cliente (`cliente_nao_encontrado`)
  - Fora do período (`data_fora_periodo`)

### Validações
1. **Chef na relação**: Verifica se o `chef_id` está na lista de chefs alocados
2. **Cliente existe**: Verifica se existe relação com cliente e se o cliente existe no banco
3. **Data no período**: Verifica se a data está dentro do período especificado

## Exemplo de Uso

```python
from notion_api import NotionAPI

notion = NotionAPI()
atendimentos = await notion.buscar_atendimentos_chef(
    chef_id='abc123...',
    dias=7  # Busca últimos 7 dias
)

# Resultado:
# [
#   {
#     'id': 'page_id_1',
#     'cliente_nome': 'João Silva',
#     'cliente_id': 'client_id_1',
#     'horario': '14:00',
#     'data': '2025-11-13T14:00:00-03:00',
#     'data_formatada': '2025-11-13'
#   },
#   ...
# ]
```

## Código Fonte

**Arquivo**: `notion_api.py`
**Função**: `buscar_atendimentos_chef()`
**Linhas**: 79-222

## Notas Importantes

1. **Timezone**: O código usa o timezone local (São Paulo, UTC-3)
2. **Validação dupla**: O código valida novamente os filtros mesmo que a API do Notion já tenha filtrado
3. **Tratamento de erros**: 
   - Timeout: Retorna lista vazia após 10 segundos
   - Erros: Retorna lista vazia e registra o erro
4. **Performance**: Busca todas as páginas automaticamente, então pode ser lento se houver muitos atendimentos

## Possíveis Melhorias

1. **Cache**: Implementar cache para evitar buscas repetidas
2. **Limite de resultados**: Adicionar limite máximo de resultados
3. **Filtros adicionais**: Permitir filtrar por status, tipo de atendimento, etc.
4. **Otimização**: Usar apenas a validação da API do Notion se possível

