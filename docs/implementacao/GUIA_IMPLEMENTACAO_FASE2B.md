# 🚀 Guia de Implementação - FASE 2B (Salvar no Notion)

## 📋 Visão Geral

**FASE 2B - Salvar no Notion:**
- Recebe inventário validado (do bot)
- Atualiza página no Notion (PATCH)
- Marca status como "Inventário Completo"
- Retorna confirmação de salvamento

---

## 🔧 Workflow n8n - Estrutura

### **1. Webhook - Recebe do Bot**
- **Nome**: `Webhook - Recebe do Bot`
- **Path**: `/fase2-salvar`
- **Método**: POST
- **Response Mode**: `responseNode`
- **Response Node**: `Respond - Confirma pro Bot`

**Payload esperado:**
```json
{
  "notion_page_id": "abc123...",
  "inventario_validado": {
    "inventario_json": "{ JSON estruturado }",
    "inventario_visualizacao": "📦 INVENTÁRIO PROCESSADO\n\n...",
    "temperos_sensiveis": [],
    "total_ingredientes": 3,
    "total_temperos_sensiveis": 0
  },
  "status": "confirmado"
}
```

---

### **2. Set - Extrai Variáveis**
- **Nome**: `Set - Extrai Variáveis`
- **Tipo**: Set

**Variáveis a extrair:**
- `notion_page_id`: `={{ $json.body.notion_page_id }}`
- `inventario_json`: `={{ $json.body.inventario_validado.inventario_json }}`
- `inventario_visualizacao`: `={{ $json.body.inventario_validado.inventario_visualizacao }}`
- `temperos_sensiveis`: `={{ $json.body.inventario_validado.temperos_sensiveis }}`
- `total_ingredientes`: `={{ $json.body.inventario_validado.total_ingredientes }}`
- `total_temperos_sensiveis`: `={{ $json.body.inventario_validado.total_temperos_sensiveis }}`
- `status`: `={{ $json.body.status }}`

---

### **3. HTTP - Buscar Página** (Notion)
- **Nome**: `HTTP - Buscar Página`
- **Tipo**: HTTP Request
- **Método**: GET
- **URL**: `https://api.notion.com/v1/pages/{{ $('Set - Extrai Variáveis').item.json.notion_page_id }}`
- **Authentication**: Notion API

**Headers:**
- `Notion-Version`: `2022-06-28`
- `Authorization`: `Bearer {{ $credentials.notionApi.accessToken }}`

**Após Buscar:**
- Conectar para `HTTP - Atualizar Página`

---

### **4. HTTP - Atualizar Página** (Notion) - PATCH
- **Nome**: `HTTP - Atualizar Página`
- **Tipo**: HTTP Request
- **Método**: PATCH
- **URL**: `https://api.notion.com/v1/pages/{{ $('Set - Extrai Variáveis').item.json.notion_page_id }}`
- **Authentication**: Notion API

**Headers:**
- `Notion-Version`: `2022-06-28`
- `Authorization`: `Bearer {{ $credentials.notionApi.accessToken }}`
- `Content-Type`: `application/json`

**Body:**
```json
{
  "properties": {
    "Inventário (JSON)": {
      "rich_text": [
        {
          "text": {
            "content": "{{ $('Set - Extrai Variáveis').item.json.inventario_json }}"
          }
        }
      ]
    },
    "Inventário (Visualização)": {
      "rich_text": [
        {
          "text": {
            "content": "{{ $('Set - Extrai Variáveis').item.json.inventario_visualizacao }}"
          }
        }
      ]
    },
    "Inventário atualizado?": {
      "select": {
        "name": "Sim"
      }
    },
    "Status": {
      "select": {
        "name": "Inventário Completo"
      }
    }
  }
}
```

**Após Atualizar:**
- Conectar para `Respond - Confirma pro Bot`

---

### **5. Respond - Confirma pro Bot**
- **Nome**: `Respond - Confirma pro Bot`
- **Tipo**: Respond to Webhook
- **Response Mode**: `json`

**Response Body:**
```json
{
  "success": true,
  "message": "Inventário salvo com sucesso!",
  "notion_page_id": "{{ $('Set - Extrai Variáveis').item.json.notion_page_id }}",
  "notion_url": "{{ $('HTTP - Atualizar Página').item.json.url }}"
}
```

---

## 🔗 Conexões do Workflow

```
Webhook - Recebe do Bot
  ↓
Set - Extrai Variáveis
  ↓
HTTP - Buscar Página (Notion)
  ↓
HTTP - Atualizar Página (Notion) - PATCH
  ↓
Respond - Confirma pro Bot
```

---

## ✅ Próximos Passos

1. **Criar workflow no n8n** seguindo esta estrutura
2. **Configurar webhook** com path `/fase2-salvar`
3. **Testar workflow** com inventário validado
4. **Validar atualização** no Notion

---

## 📝 Notas Importantes

- **Webhook deve ter `responseMode: "responseNode"`** e apontar para `Respond - Confirma pro Bot`
- **PATCH atualiza apenas** as propriedades especificadas
- **Status deve ser atualizado** para "Inventário Completo"
- **Resposta deve incluir** `notion_page_id` e `notion_url`

---

## 🎯 Propriedades do Notion

### **Propriedades a atualizar:**
1. **Inventário (JSON)**: JSON estruturado do inventário
2. **Inventário (Visualização)**: Visualização formatada do inventário
3. **Inventário atualizado?**: "Sim"
4. **Status**: "Inventário Completo"

### **Estrutura das propriedades:**
- **Inventário (JSON)**: `rich_text` (texto)
- **Inventário (Visualização)**: `rich_text` (texto)
- **Inventário atualizado?**: `select` (Sim/Não)
- **Status**: `select` (Inventário Completo/Completo/Pendente)

---

## 🔍 Validações

### **Antes de atualizar:**
1. Verificar se `notion_page_id` existe
2. Verificar se página existe no Notion
3. Validar formato do `inventario_json`
4. Validar formato do `inventario_visualizacao`

### **Após atualizar:**
1. Verificar se atualização foi bem-sucedida
2. Verificar se status foi atualizado
3. Retornar `notion_url` para o bot

---

## ❌ Tratamento de Erros

### **Erro 1: Página não encontrada**
- **Código**: 404
- **Ação**: Retornar erro ao bot
- **Mensagem**: "Página não encontrada no Notion"

### **Erro 2: Erro de autenticação**
- **Código**: 401
- **Ação**: Retornar erro ao bot
- **Mensagem**: "Erro de autenticação no Notion"

### **Erro 3: Erro de validação**
- **Código**: 400
- **Ação**: Retornar erro ao bot
- **Mensagem**: "Erro ao validar dados"

---

## ✅ Conclusão

### **Workflow FASE 2B:**
1. ✅ Recebe inventário validado
2. ✅ Atualiza página no Notion (PATCH)
3. ✅ Marca status como "Inventário Completo"
4. ✅ Retorna confirmação de salvamento

### **Próximos passos:**
1. **Criar workflow no n8n**
2. **Configurar webhook**
3. **Testar workflow**
4. **Validar atualização no Notion**

---

Quer que eu crie o workflow JSON completo? 🚀

