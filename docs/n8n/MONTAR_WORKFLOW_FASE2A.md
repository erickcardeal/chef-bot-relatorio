# 🔧 Como Montar Workflow FASE 2A no n8n

## 📋 Visão Geral

Este guia mostra como montar o workflow **FASE 2A - Processar Inventário** no n8n **passo a passo**.

---

## 🎯 Estrutura do Workflow

```
Webhook - Recebe do Bot (/fase2-processar)
  ↓
Set - Extrai Variáveis
  ↓
Google Sheets - Ler Ingredientes
  ↓
Code - Format Base Ingredientes
  ↓
IF - Tem Foto Inventário?
  ├─ SIM → Claude Vision - OCR Foto → Code - Extrair Texto OCR
  └─ NÃO → Set - Usa Texto Digitado
  ↓
Code - Busca Fuzzy
  ↓
IF - Precisa Claude?
  ├─ SIM → Preparar Prompt → Claude - Normaliza Inventário → Code - Parse Claude Response → Code - Combinar Resultados
  └─ NÃO → Code - Combinar Resultados
  ↓
Respond - Retorna pro Bot
```

---

## 📝 Passo a Passo

### **1. Criar Novo Workflow**

1. Abrir n8n
2. Clicar em **"Workflows"** no menu lateral
3. Clicar em **"+ New Workflow"**
4. Nomear: **"Relatório de Visita - Fase 2A - Processar"**

---

### **2. Adicionar Node: Webhook - Recebe do Bot**

1. Arrastar node **"Webhook"** para o canvas
2. Configurar:
   - **HTTP Method**: `POST`
   - **Path**: `fase2-processar`
   - **Response Mode**: `responseNode`
   - **Response Node**: (deixar vazio por enquanto, configurar depois)
3. Salvar e copiar **Webhook URL**

---

### **3. Adicionar Node: Set - Extrai Variáveis**

1. Arrastar node **"Set"** para o canvas
2. Conectar: **Webhook → Set**
3. Configurar variáveis:
   - `notion_page_id`: `={{ $json.body.notion_page_id }}`
   - `inventario_texto`: `={{ $json.body.inventario_texto }}`
   - `foto_inventario_base64`: `={{ $json.body.foto_inventario_base64 }}`

---

### **4. Adicionar Node: Google Sheets - Ler Ingredientes**

1. Arrastar node **"Google Sheets"** para o canvas
2. Conectar: **Set → Google Sheets**
3. Configurar:
   - **Operation**: `Read`
   - **Document ID**: `1MoClw9F5N94APD7SwTLO3kR9iiiXIj9VmR8vPfBB-as`
   - **Sheet Name**: `Lista de Ingredientes`
4. Configurar credencial do Google Sheets

---

### **5. Adicionar Node: Code - Format Base Ingredientes**

1. Arrastar node **"Code"** para o canvas
2. Conectar: **Google Sheets → Code**
3. Configurar:
   - **Name**: `Code - Format Base Ingredientes`
   - **Code**:
   ```javascript
   // Formatar base de ingredientes para uso no Claude
   const baseIngredientes = $input.all().map(item => item.json);
   
   // Criar JSON formatado da base
   const baseJson = JSON.stringify(baseIngredientes, null, 2);
   
   // Contar ingredientes
   const totalIngredientes = baseIngredientes.length;
   
   // Criar resumo das categorias
   const categorias = [...new Set(baseIngredientes.map(i => i.Categoria || i.categoria || 'Sem categoria'))];
   
   return {
     json: {
       base_ingredientes_json: baseJson,
       base_ingredientes: baseIngredientes,
       total_ingredientes: totalIngredientes,
       categorias: categorias,
       resumo: `Base carregada com ${totalIngredientes} ingredientes em ${categorias.length} categorias`
     }
   };
   ```

---

### **6. Adicionar Node: IF - Tem Foto Inventário?**

1. Arrastar node **"IF"** para o canvas
2. Conectar: **Code - Format Base Ingredientes → IF**
3. Configurar condição:
   - **Condition**: `foto_inventario_base64` não está vazio
   - **Value**: `={{ $('Set - Extrai Variáveis').first().json.foto_inventario_base64 }}`
   - **Operation**: `notEmpty`

---

### **7. Adicionar Node: Claude Vision - OCR Foto** (Caminho SIM)

1. Arrastar node **"HTTP Request"** para o canvas
2. Conectar: **IF (SIM) → HTTP Request**
3. Configurar:
   - **Name**: `Claude Vision - OCR Foto`
   - **Method**: `POST`
   - **URL**: `https://api.anthropic.com/v1/messages`
   - **Authentication**: `Header Auth` (Anthropic API)
   - **Headers**:
     - `anthropic-version`: `2023-06-01`
     - `x-api-key`: `{{ $credentials.anthropicApi.key }}`
   - **Body (JSON)**:
   ```json
   {
     "model": "claude-sonnet-4-20250514",
     "max_tokens": 2000,
     "messages": [
       {
         "role": "user",
         "content": [
           {
             "type": "image",
             "source": {
               "type": "base64",
               "media_type": "image/jpeg",
               "data": "{{ $('Set - Extrai Variáveis').item.json.foto_inventario_base64 }}"
             }
           },
           {
             "type": "text",
             "text": "Extraia TODOS os ingredientes e quantidades visíveis nesta foto de inventário de cozinha. Liste no formato: 'ingrediente: quantidade'. Seja preciso nas quantidades e nomes dos ingredientes."
           }
         ]
       }
     ]
   }
   ```

---

### **8. Adicionar Node: Code - Extrair Texto OCR** (após Claude Vision)

1. Arrastar node **"Code"** para o canvas
2. Conectar: **Claude Vision → Code**
3. Configurar:
   - **Name**: `Code - Extrair Texto OCR`
   - **Code**:
   ```javascript
   // Extrair texto da resposta do Claude Vision
   const claudeResponse = $input.item.json;
   
   let inventarioTexto = '';
   
   if (claudeResponse.content && claudeResponse.content[0]) {
     inventarioTexto = claudeResponse.content[0].text;
   } else if (typeof claudeResponse === 'string') {
     inventarioTexto = claudeResponse;
   }
   
   return {
     json: {
       ...$input.item.json,
       inventario_extraido: inventarioTexto
     }
   };
   ```

---

### **9. Adicionar Node: Set - Usa Texto Digitado** (Caminho NÃO)

1. Arrastar node **"Set"** para o canvas
2. Conectar: **IF (NÃO) → Set**
3. Configurar:
   - **Name**: `Set - Usa Texto Digitado`
   - **Variável**: `inventario_extraido`
   - **Value**: `={{ $('Set - Extrai Variáveis').first().json.inventario_texto }}`

---

### **10. Adicionar Node: Code - Busca Fuzzy**

1. Arrastar node **"Code"** para o canvas
2. Conectar: 
   - **Code - Extrair Texto OCR → Code** (caminho com foto)
   - **Set - Usa Texto Digitado → Code** (caminho sem foto)
3. Configurar:
   - **Name**: `Code - Busca Fuzzy`
   - **Code**: **COPIAR TODO O CÓDIGO DO ARQUIVO `CODIGO_BUSCA_FUZZY_N8N.txt`**
   - ⚠️ **IMPORTANTE**: Copiar TODO o código do arquivo `CODIGO_BUSCA_FUZZY_N8N.txt` e colar aqui

---

### **11. Adicionar Node: IF - Precisa Claude?**

1. Arrastar node **"IF"** para o canvas
2. Conectar: **Code - Busca Fuzzy → IF**
3. Configurar condição:
   - **Condition**: `precisa_claude` é `true`
   - **Value**: `={{ $json.precisa_claude }}`
   - **Operation**: `equals`
   - **Value to compare with**: `true`

---

### **12. Adicionar Node: Preparar Prompt** (Caminho SIM)

1. Arrastar node **"Code"** para o canvas
2. Conectar: **IF (SIM) → Code**
3. Configurar:
   - **Name**: `Preparar Prompt`
   - **Code**: (ver código completo no guia)

---

### **13. Adicionar Node: Claude - Normaliza Inventário** (Caminho SIM)

1. Arrastar node **"HTTP Request"** para o canvas
2. Conectar: **Preparar Prompt → HTTP Request**
3. Configurar:
   - **Name**: `Claude - Normaliza Inventário`
   - **Method**: `POST`
   - **URL**: `https://api.anthropic.com/v1/messages`
   - **Authentication**: `Header Auth` (Anthropic API)
   - **Headers**:
     - `anthropic-version`: `2023-06-01`
     - `x-api-key`: `{{ $credentials.anthropicApi.key }}`
   - **Body**: `={{ $json }}`

---

### **14. Adicionar Node: Code - Parse Claude Response** (Caminho SIM)

1. Arrastar node **"Code"** para o canvas
2. Conectar: **Claude → Code**
3. Configurar:
   - **Name**: `Code - Parse Claude Response`
   - **Code**: (ver código completo no guia)

---

### **15. Adicionar Node: Code - Combinar Resultados**

1. Arrastar node **"Code"** para o canvas
2. Conectar:
   - **Code - Parse Claude Response → Code** (caminho com Claude)
   - **IF (NÃO) → Code** (caminho sem Claude)
3. Configurar:
   - **Name**: `Code - Combinar Resultados`
   - **Code**: (ver código completo no guia)

---

### **16. Adicionar Node: Respond - Retorna pro Bot**

1. Arrastar node **"Respond to Webhook"** para o canvas
2. Conectar: **Code - Combinar Resultados → Respond**
3. Configurar:
   - **Name**: `Respond - Retorna pro Bot`
   - **Respond With**: `json`
   - **Response Body**:
   ```json
   {
     "success": true,
     "inventario_estruturado": {{ $json.inventario_estruturado }},
     "inventario_json": {{ JSON.stringify($json.inventario_json) }},
     "inventario_visualizacao": {{ JSON.stringify($json.inventario_visualizacao) }},
     "temperos_sensiveis": {{ $json.temperos_sensiveis }},
     "total_ingredientes": {{ $json.total_ingredientes }},
     "total_temperos_sensiveis": {{ $json.total_temperos_sensiveis }},
     "metodos_usados": {{ $json.metodos_usados }}
   }
   ```

---

### **17. Configurar Response Node no Webhook**

1. Abrir node **"Webhook - Recebe do Bot"**
2. Configurar:
   - **Response Node**: `Respond - Retorna pro Bot`
   - Salvar

---

## ✅ Checklist de Validação

- [ ] Webhook configurado com path `/fase2-processar`
- [ ] Response Mode: `responseNode`
- [ ] Response Node: `Respond - Retorna pro Bot`
- [ ] Google Sheets configurado
- [ ] Código de busca fuzzy copiado
- [ ] Credenciais configuradas
- [ ] Conexões verificadas
- [ ] Workflow ativado

---

## 🚀 Próximos Passos

1. **Importar workflow** no n8n
2. **Configurar credenciais**
3. **Copiar código de busca fuzzy**
4. **Ativar workflow**
5. **Testar fluxo completo**

---

Quer que eu crie os JSONs completos agora? 🚀

