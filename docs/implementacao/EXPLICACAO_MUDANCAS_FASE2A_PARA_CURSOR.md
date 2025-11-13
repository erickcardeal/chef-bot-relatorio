# 📋 MUDANÇAS NA FASE 2A - SISTEMA DE INVENTÁRIO

## 🎯 CONTEXTO

Simplificamos radicalmente o processamento de inventário no n8n (Fase 2A). Agora o sistema:
1. Faz parse simples do texto
2. Valida temperos sensíveis (crítico para operação)
3. Retorna visualização formatada + alertas operacionais
4. **AGUARDA CONFIRMAÇÃO DO CHEF** antes de salvar

---

## ⚠️ IMPACTO NO BOT TELEGRAM (PYTHON)

### ANTES (comportamento antigo):
```
Chef digita inventário → n8n processa → salva direto no Notion
```

### AGORA (novo comportamento):
```
Chef digita inventário 
  ↓
n8n Fase 2A processa
  ↓
Bot recebe JSON com visualização + alertas
  ↓
Bot mostra pro chef e AGUARDA CONFIRMAÇÃO
  ↓
  SE chef confirma (✅ Sim):
    → Bot envia para n8n Fase 2B (salvar no Notion)
  
  SE chef corrige (❌ Não):
    → Bot pede: "Me manda o inventário corrigido"
    → Chef digita correção
    → Bot REENVIA para n8n Fase 2A (loop até confirmar)
```

---

## 📥 RESPONSE DO N8N FASE 2A

Quando o bot envia o inventário para n8n, ele recebe este JSON:

```json
{
  "success": true,
  "inventario_estruturado": [
    {
      "nome_original": "arroz: 500g",
      "nome": "arroz",
      "quantidade": "500",
      "unidade": "g",
      "tempero_sensivel": false
    },
    {
      "nome_original": "pimenta do reino: 50g",
      "nome": "pimenta do reino",
      "quantidade": "50",
      "unidade": "g",
      "tempero_sensivel": true
    }
  ],
  "inventario_visualizacao": "📦 INVENTÁRIO PROCESSADO\n...\n✅ Confirma que está correto?",
  "total_ingredientes": 17,
  "temperos_sensiveis": [...],
  "total_temperos_sensiveis": 6,
  "precisa_revisao_temperos": false,
  "aviso_temperos": null,
  "metodo": "parse_simples",
  "precisa_validacao": true
}
```

---

## 🔧 MUDANÇAS NECESSÁRIAS NO BOT PYTHON

### 1️⃣ ADICIONAR ESTADO DE CONVERSA

```python
# Adicionar novos estados
class ConversationState:
    # ... estados existentes ...
    AGUARDANDO_CONFIRMACAO_INVENTARIO = "aguardando_confirmacao_inventario"
    AGUARDANDO_CORRECAO_INVENTARIO = "aguardando_correcao_inventario"
```

### 2️⃣ MODIFICAR PROCESSAMENTO DE INVENTÁRIO

Quando chef envia inventário (texto OU foto processada):

```python
# ANTES: Enviava direto para salvar
# AGORA: Envia para Fase 2A e aguarda confirmação

async def processar_inventario_chef(update, context, inventario_texto):
    # Enviar para n8n Fase 2A (processar)
    response = await enviar_para_n8n_fase2a(
        notion_page_id=context.user_data['notion_page_id'],
        inventario_texto=inventario_texto
    )
    
    if response['success']:
        # Armazenar dados para usar depois
        context.user_data['inventario_processado'] = response['inventario_estruturado']
        context.user_data['inventario_visualizacao'] = response['inventario_visualizacao']
        
        # Mostrar visualização pro chef
        await update.message.reply_text(response['inventario_visualizacao'])
        
        # Criar botões de confirmação
        keyboard = [
            [
                InlineKeyboardButton("✅ Sim, está correto", callback_data="inventario_confirmar"),
                InlineKeyboardButton("❌ Não, corrigir", callback_data="inventario_corrigir")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Confirma que o inventário está correto?",
            reply_markup=reply_markup
        )
        
        # Mudar estado
        context.user_data['state'] = ConversationState.AGUARDANDO_CONFIRMACAO_INVENTARIO
```

### 3️⃣ ADICIONAR HANDLERS DE CONFIRMAÇÃO

```python
async def handle_inventario_confirmar(update, context):
    """Chef confirmou que inventário está correto"""
    query = update.callback_query
    await query.answer()
    
    # Enviar para n8n Fase 2B (salvar no Notion)
    await enviar_para_n8n_fase2b(
        notion_page_id=context.user_data['notion_page_id'],
        inventario_estruturado=context.user_data['inventario_processado']
    )
    
    await query.edit_message_text("✅ Inventário salvo com sucesso!")
    
    # Continuar para próximo passo do relatório
    # ... código existente ...


async def handle_inventario_corrigir(update, context):
    """Chef quer corrigir o inventário"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "❌ Ok, vamos corrigir!\n\n"
        "Me envie o inventário corrigido no formato:\n"
        "ingrediente: quantidade unidade, ingrediente: quantidade unidade"
    )
    
    # Mudar estado para aguardar correção
    context.user_data['state'] = ConversationState.AGUARDANDO_CORRECAO_INVENTARIO


async def handle_correcao_inventario(update, context):
    """Chef enviou inventário corrigido"""
    inventario_texto = update.message.text
    
    # REENVIAR para Fase 2A (loop até confirmar)
    await processar_inventario_chef(update, context, inventario_texto)
```

### 4️⃣ ADICIONAR CALLBACK QUERY HANDLER

```python
# No main() ou onde configura os handlers
application.add_handler(CallbackQueryHandler(
    handle_inventario_confirmar, 
    pattern="^inventario_confirmar$"
))

application.add_handler(CallbackQueryHandler(
    handle_inventario_corrigir, 
    pattern="^inventario_corrigir$"
))
```

### 5️⃣ ADICIONAR NO MESSAGE HANDLER

```python
async def handle_message(update, context):
    state = context.user_data.get('state')
    
    # ... handlers existentes ...
    
    if state == ConversationState.AGUARDANDO_CORRECAO_INVENTARIO:
        await handle_correcao_inventario(update, context)
        return
```

---

## 🌐 ENDPOINTS N8N

### Fase 2A - Processar (já existe):
```
POST https://seu-n8n.com/webhook/fase2-processar

Body:
{
  "notion_page_id": "abc123",
  "inventario_texto": "arroz: 500g, feijão: 300g"
}

Response: JSON com visualização e dados estruturados
```

### Fase 2B - Salvar (será criado):
```
POST https://seu-n8n.com/webhook/fase2-salvar

Body:
{
  "notion_page_id": "abc123",
  "inventario_estruturado": [...],
  "inventario_visualizacao": "...",
  "total_ingredientes": 17,
  "temperos_sensiveis": [...],
  "total_temperos_sensiveis": 6
}

Response: 
{
  "success": true,
  "message": "Inventário salvo no Notion"
}
```

---

## ⚠️ MENSAGENS DE ALERTA

O n8n agora retorna **3 tipos de alertas** operacionais:

### 1. ZERO TEMPEROS (Crítico):
```
🚨 ATENÇÃO CRÍTICA: Nenhum tempero sensível registrado!

🔍 REVISE SE SOBRARAM TEMPEROS que você usou:
• Pimenta do reino
• Páprica
• Cominho
• Curry
• Canela
• Açafrão/Cúrcuma
• Outros temperos

💰 IMPACTO OPERACIONAL:
Se sobraram temperos e você NÃO registrou, o sistema vai 
RECOMPRÁ-LOS DESNECESSARIAMENTE na próxima visita, gerando:
→ Desperdício de produto
→ Aumento de custos
→ Estoque duplicado

❓ Confirma que NÃO SOBRARAM temperos sensíveis para registrar?
```

### 2. UM TEMPERO (Moderado):
```
⚠️ ATENÇÃO: Apenas 1 tempero sensível registrado!

Tempero encontrado:
• pimenta do reino: 50g

🔍 REVISE: É comum usar vários temperos em uma visita.
Verifique se SOBRARAM outros temperos que você usou.

💰 IMPACTO: Temperos não registrados serão recomprados 
desnecessariamente.

❓ Confirma que APENAS esse tempero sobrou?
```

### 3. DOIS TEMPEROS (Leve):
```
⚠️ ATENÇÃO: Apenas 2 temperos sensíveis registrados!

Temperos encontrados:
• pimenta do reino: 50g
• páprica: 40g

🔍 REVISE: É comum usar mais temperos em uma visita completa.
Verifique se SOBRARAM outros temperos que você usou.

💰 IMPACTO: Temperos não registrados serão recomprados 
desnecessariamente.

❓ Confirma que APENAS esses 2 temperos sobraram?
```

**IMPORTANTE:** Essas mensagens já vêm prontas do n8n dentro do campo `inventario_visualizacao`. O bot só precisa exibir o texto, sem precisar gerar lógica adicional.

---

## 📝 RESUMO DO QUE PRECISA

1. ✅ Adicionar estados: `AGUARDANDO_CONFIRMACAO_INVENTARIO` e `AGUARDANDO_CORRECAO_INVENTARIO`
2. ✅ Modificar função que processa inventário para chamar Fase 2A (não salvar direto)
3. ✅ Criar handler `handle_inventario_confirmar` → chama Fase 2B
4. ✅ Criar handler `handle_inventario_corrigir` → pede correção
5. ✅ Criar handler `handle_correcao_inventario` → reprocessa inventário
6. ✅ Adicionar CallbackQueryHandlers para os botões
7. ✅ Modificar message handler para capturar correções

---

## 🎯 FLUXO VISUAL COMPLETO

```
┌─────────────────────────────────────────────────────────┐
│ CHEF: "arroz: 500g, feijão: 300g"                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ BOT → N8N FASE 2A (processar)                          │
│ POST /webhook/fase2-processar                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ N8N: Parse + Validação Temperos                        │
│ Retorna: visualização + alertas + dados estruturados   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ BOT MOSTRA: Visualização formatada                     │
│ "📦 INVENTÁRIO PROCESSADO..."                          │
│ "⚠️ TEMPEROS SENSÍVEIS: 0"                             │
│ "🚨 ATENÇÃO CRÍTICA..."                                │
│                                                         │
│ [✅ Sim, está correto] [❌ Não, corrigir]              │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
   [✅ SIM]          [❌ NÃO]
        │                 │
        │                 ▼
        │    ┌────────────────────────────────┐
        │    │ BOT: "Me manda corrigido"      │
        │    └────────┬───────────────────────┘
        │             │
        │             ▼
        │    ┌────────────────────────────────┐
        │    │ CHEF: envia correção           │
        │    └────────┬───────────────────────┘
        │             │
        │             └─────► VOLTA PARA FASE 2A (loop)
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│ BOT → N8N FASE 2B (salvar no Notion)                   │
│ POST /webhook/fase2-salvar                             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ N8N: PATCH no Notion com todos os dados               │
│ Atualiza: Inventário (JSON), Inventário (Texto),      │
│ Total Ingredientes, Temperos Sensíveis, etc.          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ BOT: "✅ Inventário salvo com sucesso!"                │
│ [Continua para próxima etapa do relatório]            │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 PRIORIDADE

**ALTA** - Sem essas mudanças, o bot vai quebrar quando tentar processar inventário, pois o n8n agora não salva direto no Notion (aguarda confirmação).

---

**Criado em:** 2025-11-13  
**Autor:** Claude + Erick  
**Versão:** 1.0
