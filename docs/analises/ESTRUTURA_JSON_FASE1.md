# 📋 Estrutura do JSON - Webhook FASE 1

## 🔗 URL do Webhook

```
https://chefpessoal.app.n8n.cloud/webhook-test/bot-relatorio-chef-fase1
```

---

## 📦 Estrutura do Payload

### **JSON Enviado (POST):**

```json
{
  "body": {
    "chef_id": "18eb71fbd8f9803eb104ff998e930d61",
    "chef_telegram_id": "123456789",
    "chef_username": "@chef_user",
    "chef_nome": "Nome do Chef",
    "cliente_id": "18eb71fbd8f980708b42f616b816cca2",
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
    "foto_entrada_base64": "base64_string_here...",
    "foto_saida_base64": "base64_string_here...",
    "inventario_atualizado": "Não",
    "inventario_texto": "",
    "foto_inventario_base64": ""
  }
}
```

---

## 📝 Descrição dos Campos

### **1. Chef (Identificação)**
- `chef_id` (string): ID da página do chef no Notion (ex: "18eb71fbd8f9803eb104ff998e930d61")
- `chef_telegram_id` (string): ID do Telegram do chef (ex: "123456789")
- `chef_username` (string): Username do Telegram do chef (ex: "@chef_user")
- `chef_nome` (string): Nome completo do chef (ex: "Erick Cardeal")

### **2. Cliente**
- `cliente_id` (string): ID da página do cliente no Notion (ex: "18eb71fbd8f980708b42f616b816cca2")
- `cliente_nome` (string): Nome do cliente do atendimento

### **3. Atendimento (Tempo)**
- `data_atendimento` (string): Data do atendimento no formato "YYYY-MM-DD" (ex: "2025-01-15")
- `horario_chegada` (string): Horário de chegada (sem formatação específica, será normalizado no n8n)
- `horario_saida` (string): Horário de saída (sem formatação específica, será normalizado no n8n)

### **4. Visita (Descrição)**
- `como_foi_visita` (string): Descrição de como foi a visita
- `comentario_cliente` (string): Comentários do cliente
- `problema_especifico` (string): Problemas específicos relatados (pode estar vazio)

### **5. Porções**
- `porcoes_exatas` (string): "Sim" ou "Não" (ou vazio)
- `motivo_porcoes` (string): Motivo das porções exatas (pode estar vazio)

### **6. Descarte**
- `descarte` (string): "Sim" ou "Não" (ou vazio)
- `itens_descartados` (string): Lista de itens descartados (pode estar vazio)

### **7. Pode Vencer**
- `pode_vencer` (string): "Sim" ou "Não" (ou vazio)
- `itens_podem_vencer` (string): Lista de itens que podem vencer (pode estar vazio)

### **8. Fotos (Base64)**
- `foto_entrada_base64` (string): Foto de entrada codificada em Base64 (ou string vazia se não houver)
- `foto_saida_base64` (string): Foto de saída codificada em Base64 (ou string vazia se não houver)

### **9. Inventário (FASE 1 - Vazio)**
- `inventario_atualizado` (string): Sempre "Não" na FASE 1
- `inventario_texto` (string): Sempre vazio na FASE 1
- `foto_inventario_base64` (string): Sempre vazio na FASE 1

---

## 📤 Resposta Esperada do Webhook

### **Sucesso (Status 200):**

```json
{
  "success": true,
  "message": "Relatório criado com sucesso!",
  "notion_page_id": "page_id_123",
  "notion_url": "https://notion.so/..."
}
```

### **Campos da Resposta:**
- `success` (boolean): Indica se o processamento foi bem-sucedido
- `message` (string): Mensagem de confirmação
- `notion_page_id` (string): ID da página criada no Notion (importante para FASE 2)
- `notion_url` (string): URL da página criada no Notion (opcional)

---

## ⚠️ Observações Importantes

1. **Fotos Base64:**
   - As fotos são enviadas como strings Base64
   - Podem ser muito grandes (vários MB)
   - O n8n precisa processar e salvar essas imagens

2. **Campos Vazios:**
   - Muitos campos podem estar vazios (string vazia "")
   - O n8n deve tratar campos vazios adequadamente

3. **Formato de Data:**
   - `data_atendimento` sempre no formato "YYYY-MM-DD"
   - Se não fornecida, usa a data atual

4. **Horários:**
   - `horario_chegada` e `horario_saida` não têm validação rigorosa no bot
   - O n8n deve normalizar esses horários

5. **notion_page_id:**
   - É **ESSENCIAL** que o webhook retorne o `notion_page_id`
   - Esse ID será usado na FASE 2 para atualizar o relatório

---

## 🔍 Exemplo Completo

### **Request (POST):**

```json
{
  "body": {
    "chef_id": "18eb71fbd8f9803eb104ff998e930d61",
    "chef_telegram_id": "8321596608",
    "chef_username": "@chef_exemplo",
    "chef_nome": "Erick Cardeal",
    "cliente_id": "18eb71fbd8f980708b42f616b816cca2",
    "cliente_nome": "Maria Silva",
    "data_atendimento": "2025-01-15",
    "horario_chegada": "09:30",
    "horario_saida": "14:30",
    "como_foi_visita": "Visita foi excelente, cliente muito satisfeito",
    "comentario_cliente": "Pediu para aumentar o tempero",
    "problema_especifico": "",
    "porcoes_exatas": "Sim",
    "motivo_porcoes": "Cliente pediu porções maiores",
    "descarte": "Não",
    "itens_descartados": "",
    "pode_vencer": "Sim",
    "itens_podem_vencer": "Iogurte vence em 2 dias, leite vence em 3 dias",
    "foto_entrada_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "foto_saida_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "inventario_atualizado": "Não",
    "inventario_texto": "",
    "foto_inventario_base64": ""
  }
}
```

### **Response (200 OK):**

```json
{
  "success": true,
  "message": "Relatório criado com sucesso!",
  "notion_page_id": "a801dd6a-1775-4946-9fa8-a6293be1d609",
  "notion_url": "https://notion.so/chefpessoal/a801dd6a177549469fa8a6293be1d609"
}
```

---

## 📋 Checklist para n8n

- [ ] Receber todos os campos do payload
- [ ] Validar campos obrigatórios (chef_telegram_id, cliente_nome, etc.)
- [ ] Processar fotos Base64 (salvar no Notion)
- [ ] Criar página no Notion com todos os dados
- [ ] Retornar `notion_page_id` na resposta
- [ ] Tratar campos vazios adequadamente
- [ ] Normalizar horários (horario_chegada, horario_saida)
- [ ] Retornar resposta em até 30 segundos (timeout do bot)

---

## 🔗 Referência

- **Função no código:** `enviar_fase1()` (linha ~832 do `main.py`)
- **Webhook URL:** `N8N_WEBHOOK_URL_FASE1` ou `N8N_WEBHOOK_URL`
- **Timeout:** 30 segundos
- **Método:** POST
- **Content-Type:** application/json

