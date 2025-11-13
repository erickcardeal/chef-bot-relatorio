# 📋 Resumo: Filtro de Atendimentos Sem Relatório

## ✅ Implementação

### Mudanças Realizadas

1. **`notion_api.py`**:
   - Adicionado parâmetro `sem_relatorio: bool = True` na função `buscar_atendimentos_chef()`
   - Filtro condicional: Se `sem_relatorio=True`, adiciona filtro `is_empty: True` na propriedade "Relatório"
   - Logs atualizados para indicar o tipo de filtro aplicado

2. **`main.py`**:
   - Mensagem atualizada: "Chequei aqui no sistema e você tem X atendimentos nos últimos 7 dias sem relatório."
   - Pergunta atualizada: "Qual deles você quer enviar o relatório?"

3. **`REGRAS_BUSCA_ATENDIMENTO.md`**:
   - Documentação atualizada com a nova regra de filtro de relatório

## 🔍 Como Funciona

### Filtro no Notion API

Quando `sem_relatorio=True` (padrão), a query adiciona o seguinte filtro:

```json
{
  "property": "Relatório",
  "relation": {
    "is_empty": true
  }
}
```

### Comportamento

- **`sem_relatorio=True`** (padrão): Retorna apenas atendimentos que NÃO têm relatório (propriedade "Relatório" vazia)
- **`sem_relatorio=False`**: Retorna todos os atendimentos (com ou sem relatório)

### Filtros Aplicados

1. **Data**: Últimos 7 dias (inclusivo)
2. **Chef Alocado**: Chef específico
3. **Cliente**: Obrigatório
4. **Relatório**: Vazio (se `sem_relatorio=True`)

## 📝 Mensagem do Bot

**Antes**:
```
Busquei aqui no sistema e encontrei X atendimentos nos últimos 7 dias.
Qual deles você quer reportar?
```

**Depois**:
```
Chequei aqui no sistema e você tem X atendimentos nos últimos 7 dias sem relatório.
Qual deles você quer enviar o relatório?
```

## 🧪 Teste

1. Criar um atendimento no calendário do Notion
2. Verificar se a propriedade "Relatório" está vazia
3. Testar o bot: Deve aparecer apenas atendimentos sem relatório
4. Criar um relatório para um atendimento
5. Testar o bot novamente: O atendimento com relatório não deve aparecer

## ⚠️ Observações

1. **Sintaxe do Notion API**: O filtro `is_empty: true` funciona para propriedades do tipo Relation
2. **Propriedade "Relatório"**: Deve ser do tipo Relation no calendário do Notion
3. **Múltiplos Relatórios**: Se a propriedade permitir múltiplos relatórios, o filtro `is_empty` retorna apenas atendimentos sem nenhum relatório

## 📚 Referências

- Notion API: [Filter database entries](https://developers.notion.com/reference/post-database-query-filter)
- Propriedade Relation: [Relation property](https://developers.notion.com/reference/property-object#relation)

