# 🔗 Informações do Webhook FASE 1

## 📋 URL do Webhook

### **Webhook FASE 1:**
```
https://chefpessoal.app.n8n.cloud/webhook-test/bot-relatorio-chef-fase1
```

### **Webhook FASE 2:**
```
https://chefpessoal.app.n8n.cloud/webhook-test/bot-relatorio-chef
```
(ou o mesmo webhook FASE 1 se configurado)

---

## ⏰ Momento da Chamada

### **1. Fluxo Completo:**
1. ✅ Chef envia `/start`
2. ✅ Seleciona atendimento
3. ✅ Responde perguntas (horários, visita, comentários, etc.)
4. ✅ Envia foto de entrada
5. ✅ Envia foto de saída
6. ✅ **Mostra resumo** (destacando envio em 2 partes)
7. ✅ Chef confirma: **"✅ Sim, enviar FASE 1"**
8. 🔄 **CHAMADA DO WEBHOOK FASE 1** ← **AQUI**
9. ✅ Recebe resposta (sucesso ou erro)
10. ✅ Continua com inventário (FASE 2)

### **2. Quando o Webhook é Chamado:**
- **Momento:** Após o chef confirmar "✅ Sim, enviar FASE 1"
- **Função:** `enviar_fase1()`
- **Linha:** ~909 do `main.py`

---

## 📦 Payload Enviado

```json
{
  "chef_telegram_id": "123456789",
  "chef_username": "@chef_user",
  "cliente_nome": "Nome do Cliente",
  "data_atendimento": "2025-01-15",
  "horario_chegada": "09:30",
  "horario_saida": "14:30",
  "como_foi_visita": "Visita foi excelente...",
  "comentario_cliente": "Cliente pediu mais tempero",
  "problema_especifico": "",
  "porcoes_exatas": "Sim",
  "motivo_porcoes": "",
  "descarte": "Não",
  "itens_descartados": "",
  "pode_vencer": "Sim",
  "itens_podem_vencer": "Iogurte vence em 2 dias",
  "foto_entrada_base64": "base64...",
  "foto_saida_base64": "base64...",
  "inventario_atualizado": "Não",
  "inventario_texto": "",
  "foto_inventario_base64": ""
}
```

---

## 📥 Resposta Esperada

### **Sucesso (Status 200):**
```json
{
  "success": true,
  "message": "Relatório criado com sucesso!",
  "notion_page_id": "page_id_123",
  "notion_url": "https://notion.so/..."
}
```

### **Erro (Status 404):**
- Webhook não encontrado
- Workflow não está ativo

### **Erro (Status 500):**
- Erro no workflow n8n
- Verificar logs do n8n

---

## 🔍 Logs do Bot

### **Ver logs em tempo real:**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
tail -f bot.log
```

### **Ver últimos logs:**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
tail -50 bot.log | grep -i "webhook\|fase\|error"
```

### **Logs esperados:**
```
🔄 Enviando FASE 1 para webhook: https://chefpessoal.app.n8n.cloud/webhook-test/bot-relatorio-chef-fase1
📦 Payload: {...}
📥 Resposta do webhook FASE 1: Status 200
📄 Resposta do webhook: {...}
✅ FASE 1 enviada com sucesso! Notion Page ID: ...
```

---

## ⚠️ Problemas Comuns

### **1. Webhook não é chamado:**
- ✅ Verificar se o bot está rodando
- ✅ Verificar se chegou até a confirmação "Sim, enviar FASE 1"
- ✅ Verificar logs do bot

### **2. Webhook retorna 404:**
- ⚠️ Workflow n8n não está ativo
- ⚠️ URL do webhook está incorreta
- ⚠️ Webhook não existe no n8n

### **3. Webhook retorna 500:**
- ⚠️ Erro no workflow n8n
- ⚠️ Verificar logs do n8n
- ⚠️ Verificar configuração do workflow

### **4. Timeout (30 segundos):**
- ⚠️ Workflow n8n está demorando muito
- ⚠️ Verificar se há processamento pesado no workflow
- ⚠️ Aumentar timeout se necessário

---

## ✅ Próximos Passos

1. ✅ **Verificar se o workflow n8n FASE 1 está ATIVO**
2. ✅ **Verificar se a URL do webhook está correta**
3. ✅ **Testar novamente e verificar logs**
4. ✅ **Verificar resposta do webhook nos logs**

---

## 📝 Notas

- ✅ **Webhook está sendo chamado** (vejo nos logs)
- ⚠️ **Precisa verificar resposta do webhook** (adicionado logs detalhados)
- ⚠️ **Verificar se workflow n8n está ativo**
- ⚠️ **Verificar se workflow retorna resposta correta**


