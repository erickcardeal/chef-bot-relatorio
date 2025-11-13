# 🔗 Webhooks Configurados

## ✅ Webhook FASE 1 Adicionado

### **Webhook da FASE 1:**
```
https://chefpessoal.app.n8n.cloud/webhook-test/bot-relatorio-chef-fase1
```

### **Configuração:**
- ✅ Adicionado em `config.py` como `N8N_WEBHOOK_URL_FASE1`
- ✅ Valor padrão: `https://chefpessoal.app.n8n.cloud/webhook-test/bot-relatorio-chef-fase1`
- ✅ Pode ser sobrescrito via variável de ambiente `N8N_WEBHOOK_URL_FASE1`

---

## 📋 Variáveis de Ambiente

### **No arquivo `.env`:**
```bash
# Webhook padrão (usado para FASE 2 se N8N_WEBHOOK_URL_FASE2 não estiver definido)
N8N_WEBHOOK_URL=https://seu-n8n.app/webhook/relatorio-chef

# Webhook específico para FASE 1 (dados básicos + fotos)
N8N_WEBHOOK_URL_FASE1=https://chefpessoal.app.n8n.cloud/webhook-test/bot-relatorio-chef-fase1

# Webhook específico para FASE 2 (inventário) - opcional
# Se não definido, usa N8N_WEBHOOK_URL
N8N_WEBHOOK_URL_FASE2=https://seu-n8n.app/webhook/relatorio-chef-fase2
```

---

## 🔄 Fluxo de Webhooks

### **FASE 1:**
- **Webhook:** `N8N_WEBHOOK_URL_FASE1` (ou `N8N_WEBHOOK_URL` se não definido)
- **Payload:** Dados básicos + fotos (entrada e saída)
- **Resposta esperada:**
  ```json
  {
    "success": true,
    "message": "Relatório criado com sucesso!",
    "notion_page_id": "page_id_123",
    "notion_url": "https://notion.so/..."
  }
  ```

### **FASE 2:**
- **Webhook:** `N8N_WEBHOOK_URL_FASE2` (ou `N8N_WEBHOOK_URL` se não definido)
- **Payload:** Inventário + `notion_page_id` + flag `fase: 2`
- **Resposta esperada:**
  ```json
  {
    "success": true,
    "message": "Inventário processado com sucesso!"
  }
  ```

---

## 📊 Código Modificado

### **1. `config.py`:**
```python
# Webhook específico para FASE 1 (dados básicos + fotos)
N8N_WEBHOOK_URL_FASE1 = os.getenv('N8N_WEBHOOK_URL_FASE1', 'https://chefpessoal.app.n8n.cloud/webhook-test/bot-relatorio-chef-fase1')

# Webhook específico para FASE 2 (inventário) - usa FASE2 se definido, senão usa o webhook padrão
N8N_WEBHOOK_URL_FASE2 = os.getenv('N8N_WEBHOOK_URL_FASE2') or N8N_WEBHOOK_URL
```

### **2. `main.py` - Função `enviar_fase1()`:**
```python
# Enviar para n8n FASE 1 (webhook específico da FASE 1)
webhook_url_fase1 = N8N_WEBHOOK_URL_FASE1 or N8N_WEBHOOK_URL
logger.info(f"Enviando FASE 1 para webhook: {webhook_url_fase1}")

async with aiohttp.ClientSession() as session:
    async with session.post(
        webhook_url_fase1,
        json=payload,
        timeout=aiohttp.ClientTimeout(total=30)
    ) as response:
        # ...
```

### **3. `main.py` - Função `enviar_fase2()`:**
```python
# Enviar para n8n FASE 2 (webhook específico da FASE 2)
webhook_url_fase2 = N8N_WEBHOOK_URL_FASE2 or N8N_WEBHOOK_URL
payload['fase'] = 2
logger.info(f"Enviando FASE 2 para webhook: {webhook_url_fase2}")

async with aiohttp.ClientSession() as session:
    async with session.post(
        webhook_url_fase2,
        json=payload,
        timeout=aiohttp.ClientTimeout(total=60)
    ) as response:
        # ...
```

---

## ✅ Próximos Passos

1. ✅ **Webhook FASE 1 configurado** - `https://chefpessoal.app.n8n.cloud/webhook-test/bot-relatorio-chef-fase1`
2. ⏳ **Criar workflow n8n FASE 1** - Receber dados básicos + fotos e criar relatório no Notion
3. ⏳ **Configurar workflow n8n FASE 2** - Receber inventário e atualizar relatório existente
4. ⏳ **Testar fluxo completo** - FASE 1 + FASE 2

---

## 📝 Notas

- O webhook da FASE 1 está **hardcoded** no código como valor padrão
- Pode ser sobrescrito via variável de ambiente `N8N_WEBHOOK_URL_FASE1`
- O webhook da FASE 2 usa o webhook padrão (`N8N_WEBHOOK_URL`) se não for definido um específico
- Logs são gerados mostrando qual webhook está sendo usado


