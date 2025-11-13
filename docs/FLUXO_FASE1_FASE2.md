# 🔄 Fluxo FASE 1 + FASE 2 - Implementação

## ✅ Mudanças Implementadas

### **1. Fluxo de Coleta de Dados**

#### **FASE 1 - Dados Básicos + Fotos:**
1. ✅ Selecionar Atendimento
2. ✅ Horário de Chegada
3. ✅ Horário de Saída
4. ✅ Como foi a visita
5. ✅ Comentário do cliente (opcional)
6. ✅ Problema específico (opcional)
7. ✅ Porções exatas? (opcional)
8. ✅ Motivo porções (se não exatas)
9. ✅ Descarte? (opcional)
10. ✅ Itens descartados (se houve descarte)
11. ✅ Pode vencer? (opcional)
12. ✅ Itens podem vencer (se pode vencer)
13. ✅ **Foto Entrada**
14. ✅ **Foto Saída**
15. ✅ **Mostrar Resumo** (destacando envio em 2 partes)
16. ✅ **Enviar FASE 1** (dados básicos + fotos) → Resposta rápida (3-5s)

#### **FASE 2 - Inventário:**
17. ✅ Inventário (texto ou foto)
18. ✅ **Enviar FASE 2** (inventário) → Processamento com IA

---

## 📋 Estados do Bot

### **Novos Estados:**
- `RESUMO_FASE1` - Mostrar resumo e destacar envio em 2 partes
- `CONFIRMACAO_FASE1` - Confirmar envio da FASE 1

### **Estados Modificados:**
- `FOTO_SAIDA` - Agora chama `mostrar_resumo_fase1()` após receber foto
- `INVENTARIO_OPCAO` - Agora pede confirmação para enviar FASE 2
- `CONFIRMACAO_FINAL` - Agora envia FASE 2 (inventário)

---

## 🔧 Funções Implementadas

### **1. `mostrar_resumo_fase1()`**
- Mostra resumo completo dos dados coletados
- **Destaca** que o relatório será enviado em 2 partes
- Explica o que será enviado em cada fase
- Pede confirmação para enviar FASE 1

### **2. `confirmacao_fase1()`**
- Recebe confirmação do chef
- Chama `enviar_fase1()`

### **3. `enviar_fase1()`**
- Envia dados básicos + fotos para n8n
- Recebe `notion_page_id` da resposta
- Salva `notion_page_id` para usar na FASE 2
- Mostra mensagem de sucesso
- **Continua** para inventário (FASE 2)

### **4. `confirmacao_final()`**
- Agora envia FASE 2 (inventário)
- Chama `enviar_fase2()`

### **5. `enviar_fase2()`**
- Envia apenas inventário para n8n
- Usa `notion_page_id` para atualizar relatório existente
- Mostra mensagem de sucesso
- Finaliza conversa

---

## 📊 Payload FASE 1

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

## 📊 Payload FASE 2

```json
{
  "notion_page_id": "page_id_da_fase1",
  "fase": 2,
  "inventario_atualizado": "Sim",
  "inventario_texto": "500g arroz branco, 2 tomates...",
  "foto_inventario_base64": "base64..." // ou vazio se texto
}
```

---

## 🎯 Mensagens ao Chef

### **Após FOTO_SAIDA:**
- Mostra resumo completo
- **Destaca** que será enviado em 2 partes
- Explica FASE 1 e FASE 2
- Pede confirmação

### **Após FASE 1:**
- ✅ "FASE 1 ENVIADA COM SUCESSO!"
- Link para relatório no Notion
- Explica que agora vem FASE 2 (inventário)
- Pede inventário

### **Após FASE 2:**
- ✅ "FASE 2 ENVIADA COM SUCESSO!"
- Confirma que inventário foi processado
- Relatório completo!

---

## ✅ Próximos Passos

1. ✅ **Bot modificado** - Fluxo implementado
2. ⏳ **Criar workflow n8n FASE 1** - Receber dados básicos + fotos e criar relatório
3. ⏳ **Criar workflow n8n FASE 2** - Receber inventário e atualizar relatório
4. ⏳ **Testar fluxo completo** - FASE 1 + FASE 2

---

## 📝 Notas Importantes

- **FASE 1** deve responder rapidamente (3-5 segundos)
- **FASE 2** pode demorar mais (30-60 segundos) para processar inventário com IA
- O `notion_page_id` é salvo após FASE 1 e usado na FASE 2
- Se FASE 1 falhar, o bot continua para FASE 2 (inventário) mesmo assim
- Se FASE 2 falhar, a FASE 1 já foi enviada com sucesso


