# 🧪 Teste do Bot - Checklist

## ✅ Configuração Verificada

### **1. Webhooks Configurados:**
- ✅ **FASE 1:** `https://chefpessoal.app.n8n.cloud/webhook-test/bot-relatorio-chef-fase1`
- ✅ **FASE 2:** `https://chefpessoal.app.n8n.cloud/webhook-test/bot-relatorio-chef` (webhook padrão)

### **2. Código:**
- ✅ Sem erros de lint
- ✅ Imports OK
- ✅ Config carregado corretamente

### **3. Bot:**
- ✅ Bot está rodando (processo ativo)
- ✅ Código atualizado com novas funcionalidades

---

## 🚀 Pronto para Testar!

### **O que foi implementado:**

1. ✅ **Fluxo FASE 1 + FASE 2:**
   - Coleta dados básicos até fotos
   - Mostra resumo destacando envio em 2 partes
   - Envia FASE 1 (dados básicos + fotos) → Resposta rápida
   - Continua com inventário (FASE 2)
   - Envia FASE 2 (inventário) → Processamento com IA

2. ✅ **Webhook FASE 1 configurado:**
   - Webhook específico para FASE 1
   - Payload com dados básicos + fotos
   - Espera resposta com `notion_page_id`

3. ✅ **Mensagens destacando 2 partes:**
   - Após fotos: mostra resumo e explica envio em 2 partes
   - Após FASE 1: confirma envio e explica FASE 2
   - Após FASE 2: confirma processamento completo

---

## 📋 Como Testar

### **1. Teste Completo (FASE 1 + FASE 2):**

1. Enviar `/start` no Telegram
2. Selecionar atendimento
3. Responder perguntas:
   - Horário chegada
   - Horário saída
   - Como foi visita
   - Comentário cliente (opcional)
   - Problema específico (opcional)
   - Porções exatas? (opcional)
   - Motivo porções (se não exatas)
   - Descarte? (opcional)
   - Itens descartados (se sim)
   - Pode vencer? (opcional)
   - Itens podem vencer (se sim)
4. **Enviar foto de entrada**
5. **Enviar foto de saída**
6. **Ver resumo** (destacando envio em 2 partes)
7. **Confirmar FASE 1** → Deve enviar para webhook FASE 1
8. **Registrar inventário** (texto ou foto)
9. **Confirmar FASE 2** → Deve enviar para webhook FASE 2

### **2. Teste Rápido (Apenas FASE 1):**

1. Seguir passos 1-6 acima
2. **Confirmar FASE 1** → Verificar se webhook FASE 1 foi chamado
3. Verificar resposta do webhook (deve ter `notion_page_id`)

---

## ⚠️ Pontos de Atenção

### **1. Webhook FASE 1:**
- ✅ Webhook configurado: `https://chefpessoal.app.n8n.cloud/webhook-test/bot-relatorio-chef-fase1`
- ⚠️ **Verificar se o workflow n8n FASE 1 está ATIVO**
- ⚠️ **Verificar se o workflow retorna `notion_page_id` na resposta**

### **2. Webhook FASE 2:**
- ⚠️ **Verificar se o workflow n8n FASE 2 está configurado** (ou usar o mesmo webhook)
- ⚠️ **Verificar se o workflow atualiza o relatório existente** usando `notion_page_id`

### **3. Payloads:**
- ✅ Payload FASE 1: dados básicos + fotos (base64)
- ✅ Payload FASE 2: inventário + `notion_page_id` + flag `fase: 2`

---

## 🔍 Logs para Verificar

### **No terminal do bot:**
```
Enviando FASE 1 para webhook: https://chefpessoal.app.n8n.cloud/webhook-test/bot-relatorio-chef-fase1
Enviando FASE 2 para webhook: https://chefpessoal.app.n8n.cloud/webhook-test/bot-relatorio-chef
```

### **No n8n:**
- Verificar se o workflow FASE 1 foi executado
- Verificar se criou relatório no Notion
- Verificar se retornou `notion_page_id`

---

## ✅ Status Atual

- ✅ **Código:** Implementado e sem erros
- ✅ **Webhooks:** Configurados
- ✅ **Bot:** Rodando
- ⏳ **Workflow n8n FASE 1:** Precisa estar ATIVO
- ⏳ **Workflow n8n FASE 2:** Precisa estar configurado

---

## 🎯 Próximos Passos

1. ✅ **Bot pronto para testar**
2. ⏳ **Ativar workflow n8n FASE 1** (se ainda não estiver ativo)
3. ⏳ **Configurar workflow n8n FASE 2** (se ainda não estiver configurado)
4. ⏳ **Testar fluxo completo** no Telegram
5. ⏳ **Verificar logs** e respostas dos webhooks


