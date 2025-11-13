# 🧪 Guia de Teste Rápido - FASE 2A

## ✅ Checklist Antes de Testar

### **1. Workflow FASE 2A no n8n**
- [ ] Workflow importado
- [ ] Código de busca fuzzy copiado no node "Code - Busca Fuzzy"
- [ ] Credenciais configuradas:
  - [ ] Google Sheets (ler ingredientes)
  - [ ] Anthropic API (Claude)
- [ ] Workflow **ATIVO** (toggle no canto superior direito)
- [ ] Webhook URL: `https://chefpessoal.app.n8n.cloud/webhook-test/fase2-processar`

### **2. Workflow FASE 2B no n8n**
- [ ] Workflow importado
- [ ] Credenciais configuradas:
  - [ ] Notion API
- [ ] Workflow **ATIVO**
- [ ] Webhook URL: `https://chefpessoal.app.n8n.cloud/webhook-test/fase2-salvar`

### **3. Bot**
- [ ] Bot rodando
- [ ] Variáveis de ambiente configuradas (se necessário)

---

## 🧪 Teste 1: Inventário com Texto Simples

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
2. Aguardar processamento (pode demorar 10-30 segundos)
3. Bot deve mostrar inventário formatado com categorias

### **Passo 3: Verificar Resultado Esperado**
- ✅ Inventário processado e formatado
- ✅ Categorias identificadas
- ✅ Temperos sensíveis destacados (se houver)
- ✅ Botões: "✅ Está correto" e "❌ Precisa correção"

### **Passo 4: Confirmar Inventário**
1. Clicar em "✅ Está correto"
2. Bot deve mostrar: "💾 Salvando inventário no Notion..."
3. Aguardar salvamento (5-10 segundos)
4. Bot deve mostrar: "✅ Relatório finalizado!"

---

## 🧪 Teste 2: Inventário com Erros de Digitação

### **Passo 1: Enviar Inventário com Erros**
```
500g arroz branco, 2 tomates italianos, meio pacote macarrao penne, 100g pimenta do reino, 1 pacote sal grosso
```

**Observações:**
- "macarrao" (sem acento) deve ser corrigido para "macarrão"
- Busca fuzzy deve encontrar correções

### **Passo 2: Verificar Correções**
- ✅ Erros corrigidos automaticamente
- ✅ Ingredientes normalizados
- ✅ Confiança mostrada (se houver)

---

## 🧪 Teste 3: Inventário com Temperos Sensíveis

### **Passo 1: Enviar Inventário com Temperos Sensíveis**
```
500g arroz branco, 100g pimenta do reino, 50g açafrão da terra, 30g canela em pó
```

### **Passo 2: Verificar Avisos**
- ✅ Temperos sensíveis destacados com ⚠️
- ✅ Aviso no topo: "⚠️ ATENÇÃO: Verifique especialmente os temperos sensíveis: ..."

---

## 🧪 Teste 4: Inventário com Foto

### **Passo 1: Enviar Foto do Inventário**
1. Quando pedir inventário, enviar **foto** (não texto)
2. Bot deve processar foto com Claude Vision (OCR)

### **Passo 2: Verificar Processamento**
- ✅ Foto processada com OCR
- ✅ Texto extraído da foto
- ✅ Ingredientes identificados
- ✅ Resto do fluxo igual ao teste 1

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

### **Problema 3: Inventário Não Formatado**
**Sintoma:** Bot não mostra inventário formatado

**Solução:**
- Verificar se n8n retorna `inventario_visualizacao`
- Verificar se resposta tem formato correto
- Verificar logs do bot

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
2. ✅ Enviar inventário pelo bot
3. ✅ Verificar processamento
4. ✅ Confirmar inventário
5. ✅ Verificar salvamento no Notion

**Boa sorte! 🎉**

