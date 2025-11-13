# 📋 Guia: Adicionar Relação de Relatório no Atendimento (n8n FASE 1)

## Objetivo
Após criar o relatório no Notion, atualizar o card do atendimento no calendário adicionando a relação "Relatório" com o `notion_page_id` do relatório criado.

## Alterações Necessárias no n8n

### 1. Modificar Node "Formatar Dados"

**Localização**: Após o `return { json: { ... } }` no final do código JavaScript

**Adicionar**:
```javascript
atendimento_id: body.atendimento_id || '',
```

**Onde adicionar**: Junto com os outros campos no retorno (exemplo: após `cliente_nome`)

```javascript
return {
  json: {
    payload: payload,
    titulo: titulo,
    chef_id: body.chef_id,
    chef_nome: body.chef_nome || body.chef_username,
    chef_telegram_id: body.chef_telegram_id,
    cliente_id: body.cliente_id,
    cliente_nome: body.cliente_nome,
    atendimento_id: body.atendimento_id || '',  // ← ADICIONAR ESTA LINHA
    data_atendimento: body.data_atendimento,
    horario_inicio: horarioInicio,
    horario_fim: horarioFim,
    payload_original: body
  }
};
```

---

### 2. Modificar Node "Code - Prepara Fotos"

**Localização**: Nos objetos `json` dentro do `items.push({ json: { ... } })`

**Adicionar** em TODOS os lugares onde há `cliente_id`:
```javascript
atendimento_id: dados.atendimento_id || '',
```

**Onde adicionar**: 
- No loop de fotos de entrada (após `cliente_nome`)
- No loop de fotos de saída (após `cliente_nome`)
- No caso sem fotos (após `cliente_nome`)

---

### 3. Modificar Node "Code - Agrupa URLs"

**Localização**: No `return { json: { ... } }` no final do código

**Adicionar**:
```javascript
atendimento_id: dadosBase.atendimento_id || '',
```

**Onde adicionar**: Após `cliente_nome`

```javascript
return {
  json: {
    payload: dadosBase.payload,
    chef_id: dadosBase.chef_id,
    chef_nome: dadosBase.chef_nome,
    chef_telegram_id: dadosBase.chef_telegram_id,
    cliente_id: dadosBase.cliente_id,
    cliente_nome: dadosBase.cliente_nome,
    atendimento_id: dadosBase.atendimento_id || '',  // ← ADICIONAR ESTA LINHA
    data_atendimento: dadosBase.data_atendimento,
    // ... resto dos campos
  }
};
```

---

### 4. Modificar Node "Code - Adiciona Fotos ao Payload"

**Localização**: No `return { json: { ... } }` no final do código

**Adicionar**:
```javascript
atendimento_id: dados.atendimento_id || '',
```

**Onde adicionar**: Após `cliente_nome`

```javascript
return {
  json: {
    payload: payload,
    titulo: dados.titulo,
    chef_id: dados.chef_id,
    chef_nome: dados.chef_nome,
    chef_telegram_id: dados.chef_telegram_id,
    cliente_id: dados.cliente_id,
    cliente_nome: dados.cliente_nome,
    atendimento_id: dados.atendimento_id || '',  // ← ADICIONAR ESTA LINHA
    data_atendimento: dados.data_atendimento,
    // ... resto dos campos
  }
};
```

---

### 5. Adicionar Novo Node "HTTP - Atualizar Atendimento"

**Localização**: Entre "HTTP - Criar Relatório Notion" e "Respond - Confirma ao Bot"

**Tipo**: HTTP Request

**Configuração**:
- **Method**: `PATCH`
- **URL**: `https://api.notion.com/v1/pages/{{ $('Code - Adiciona Fotos ao Payload').first().json.atendimento_id }}`
- **Authentication**: `Notion API` (mesma credencial usada no "HTTP - Criar Relatório Notion")
- **Headers**:
  - `Notion-Version`: `2022-06-28`
- **Body**:
  ```json
  {
    "properties": {
      "Relatório": {
        "relation": [
          {
            "id": "{{ $('HTTP - Criar Relatório Notion').first().json.id }}"
          }
        ]
      }
    }
  }
  ```

**IMPORTANTE**: 
- Se o `atendimento_id` estiver vazio, este node deve ser ignorado (usar IF node ou tratar erro)
- A relação permite múltiplos relatórios, então está apenas ADICIONANDO um novo, não substituindo

---

### 6. Modificar Conexões

**Antes**:
```
HTTP - Criar Relatório Notion → Respond - Confirma ao Bot
```

**Depois**:
```
HTTP - Criar Relatório Notion → HTTP - Atualizar Atendimento → Respond - Confirma ao Bot
```

---

### 7. Tratamento de Erros (Opcional mas Recomendado)

**Cenário**: Se o `atendimento_id` estiver vazio ou se houver erro ao atualizar o atendimento

**Solução**: 
- Adicionar um node IF antes de "HTTP - Atualizar Atendimento"
- Condição: `{{ $('Code - Adiciona Fotos ao Payload').first().json.atendimento_id !== '' && $('Code - Adiciona Fotos ao Payload').first().json.atendimento_id !== null }}`
- Se TRUE: Executa "HTTP - Atualizar Atendimento"
- Se FALSE: Pula direto para "Respond - Confirma ao Bot"

**OU**:
- Adicionar tratamento de erro no próprio node "HTTP - Atualizar Atendimento"
- Se houver erro (404, etc), apenas logar o erro mas continuar o fluxo

---

## Ordem de Execução Final

1. Webhook - Recebe do Bot
2. Formatar Dados (agora inclui `atendimento_id`)
3. Code - Prepara Fotos (agora inclui `atendimento_id`)
4. IF - Tem Fotos?
5. Google Drive - Upload Foto (se tiver fotos)
6. Code - Agrupa URLs (agora inclui `atendimento_id`)
7. Code - Adiciona Fotos ao Payload (agora inclui `atendimento_id`)
8. HTTP - Criar Relatório Notion
9. **HTTP - Atualizar Atendimento** (NOVO)
10. Respond - Confirma ao Bot

---

## Validações

- ✅ `atendimento_id` está sendo enviado no payload do bot
- ✅ `atendimento_id` está sendo passado através de todos os nodes do n8n
- ✅ `atendimento_id` está sendo usado para atualizar o card do atendimento
- ✅ A relação "Relatório" está sendo adicionada corretamente
- ✅ Se `atendimento_id` estiver vazio, o fluxo continua normalmente (não quebra)

---

## Teste

1. Executar workflow com `atendimento_id` válido
2. Verificar se o card do atendimento no calendário foi atualizado com a relação
3. Verificar se o relatório foi criado corretamente
4. Executar workflow sem `atendimento_id` (deve continuar funcionando)

---

## Nota Importante

- A propriedade "Relatório" no calendário permite múltiplos relatórios
- Cada vez que um relatório é criado, ele é ADICIONADO à relação (não substitui)
- Isso permite rastrear múltiplos relatórios por atendimento (útil para MVP e debugging)

