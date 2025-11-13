# 🧪 Resumo do Teste - FASE 2A

## ✅ Checklist Antes de Testar

### **1. Workflow FASE 2A no n8n**
- [x] Workflow importado
- [ ] **Código de busca fuzzy copiado** no node "Code - Busca Fuzzy"
- [ ] **Response Body corrigido** no node "Respond - Retorna pro Bot"
- [ ] Credenciais configuradas:
  - [ ] Google Sheets (ler ingredientes)
  - [ ] Anthropic API (Claude)
- [ ] Workflow **ATIVO** (toggle no canto superior direito)
- [ ] Webhook URL: `https://chefpessoal.app.n8n.cloud/webhook-test/fase2-processar`

### **2. Workflow FASE 2B no n8n**
- [x] Workflow importado
- [ ] Credenciais configuradas:
  - [ ] Notion API
- [ ] Workflow **ATIVO**
- [ ] Webhook URL: `https://chefpessoal.app.n8n.cloud/webhook-test/fase2-salvar`

### **3. Bot**
- [ ] Bot rodando
- [ ] Variáveis de ambiente configuradas (se necessário)

---

## 🔧 Correções Necessárias

### **1. Copiar Código de Busca Fuzzy**
1. Abrir workflow FASE 2A no n8n
2. Abrir node **"Code - Busca Fuzzy"**
3. Copiar TODO o código do arquivo `CODIGO_BUSCA_FUZZY_N8N.txt`
4. Colar no campo de código do node
5. Salvar

### **2. Corrigir Response Body**
1. Abrir node **"Respond - Retorna pro Bot"**
2. No campo **"Response Body"**, usar:

```javascript
=={{
  {
    "success": true,
    "inventario_estruturado": $json.inventario_estruturado,
    "inventario_json": $json.inventario_json,
    "inventario_visualizacao": $json.inventario_visualizacao,
    "temperos_sensiveis": $json.temperos_sensiveis,
    "total_ingredientes": $json.total_ingredientes,
    "total_temperos_sensiveis": $json.total_temperos_sensiveis,
    "metodos_usados": $json.metodos_usados
  }
}}
```

3. Salvar

---

## 🧪 Teste Rápido

### **Passo 1: Enviar Inventário**
1. Abrir bot no Telegram
2. Enviar `/start`
3. Completar FASE 1 (dados básicos + fotos)
4. Quando pedir inventário, enviar:
   ```
   500g arroz branco, 2 tomates italianos, meio pacote macarrão penne, 100g pimenta do reino, 1 pacote sal grosso
   ```

### **Passo 2: Verificar Processamento**
1. Bot deve mostrar: "🔄 Processando inventário..."
2. Aguardar processamento (10-30 segundos)
3. Bot deve mostrar inventário formatado com categorias

### **Passo 3: Confirmar Inventário**
1. Clicar em "✅ Está correto"
2. Bot deve mostrar: "💾 Salvando inventário no Notion..."
3. Aguardar salvamento (5-10 segundos)
4. Bot deve mostrar: "✅ Relatório finalizado!"

---

## 🔍 Verificar Logs

### **1. Logs do Bot**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
tail -f bot.log
```

**Procurar por:**
- `🔄 Enviando FASE 2A (processar) para webhook: ...`
- `✅ Inventário processado: X ingredientes`
- `🔄 Enviando FASE 2B (salvar) para webhook: ...`
- `✅ Inventário salvo com sucesso!`

### **2. Logs do n8n**
- Abrir workflow FASE 2A no n8n
- Verificar execuções recentes
- Verificar se houve erros
- Verificar tempo de execução

---

## ❌ Problemas Comuns

### **Problema 1: Timeout ao Processar**
**Sintoma:** Bot mostra "⏱️ O processamento demorou muito."

**Solução:**
- Verificar se Google Sheets está acessível
- Verificar se Claude API está funcionando
- Verificar se há muitos ingredientes para processar
- Aumentar timeout no n8n (se necessário)

### **Problema 2: Erro ao Processar**
**Sintoma:** Bot mostra "❌ Erro no processamento do inventário"

**Solução:**
- Verificar logs do n8n
- Verificar se código de busca fuzzy está correto
- Verificar se Google Sheets tem dados
- Verificar se Claude API está configurada corretamente
- Verificar se Response Body está correto

### **Problema 3: Inventário Não Formatado**
**Sintoma:** Bot não mostra inventário formatado

**Solução:**
- Verificar se n8n retorna `inventario_visualizacao`
- Verificar se resposta tem formato correto
- Verificar logs do bot
- Verificar se Response Body está correto

### **Problema 4: Erro ao Salvar**
**Sintoma:** Bot mostra "❌ Erro ao salvar inventário"

**Solução:**
- Verificar se FASE 2B está ativa
- Verificar se `notion_page_id` está correto
- Verificar se Notion API está configurada
- Verificar logs do n8n FASE 2B

---

## 📊 Payload Enviado pelo Bot

```json
{
  "notion_page_id": "page_id_123",
  "inventario_texto": "500g arroz branco, 2 tomates italianos...",
  "foto_inventario_base64": "" // ou base64 se foto
}
```

---

## 📥 Resposta Esperada do n8n FASE 2A

```json
{
  "success": true,
  "inventario_estruturado": [...],
  "inventario_json": "...",
  "inventario_visualizacao": "📦 INVENTÁRIO PROCESSADO\n\n...",
  "temperos_sensiveis": [...],
  "total_ingredientes": 5,
  "total_temperos_sensiveis": 1,
  "metodos_usados": {
    "exato": 3,
    "fuzzy_alta": 1,
    "fuzzy_media": 1,
    "nao_encontrado": 0
  }
}
```

---

## 🚀 Pronto para Testar!

1. ✅ Verificar checklist acima
2. ✅ Copiar código de busca fuzzy
3. ✅ Corrigir Response Body
4. ✅ Ativar workflows
5. ✅ Enviar inventário pelo bot
6. ✅ Verificar processamento
7. ✅ Confirmar inventário
8. ✅ Verificar salvamento no Notion

**Boa sorte! 🎉**

