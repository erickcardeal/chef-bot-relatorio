# 📊 Estrutura Proposta - FASE 2A e FASE 2B

## 🎯 Visão Geral

Separação do processamento de inventário em **duas fases distintas**:

1. **FASE 2A - Processar Inventário**: Apenas processar e retornar (sem salvar)
2. **FASE 2B - Salvar no Notion**: Salvar inventário validado no Notion (PATCH)

---

## ✅ Análise da Estrutura Proposta

### 🎯 **Faz MUITO sentido!**

**Vantagens:**
- ✅ **Separação de responsabilidades** (processar vs salvar)
- ✅ **Validação antes de salvar** (chef confirma antes)
- ✅ **Melhor UX** (chef vê o resultado antes de salvar)
- ✅ **Redução de erros** (validação antes de salvar no Notion)
- ✅ **Facilita correções** (chef pode refazer sem salvar)
- ✅ **Melhor rastreabilidade** (sabe quando foi processado vs salvo)

**Estrutura proposta:**
```
FASE 2A (Processar):
- Recebe inventário (texto ou foto)
- Processa (busca fuzzy + Claude se necessário)
- Retorna JSON estruturado
- Bot mostra para chef validar

FASE 2B (Salvar):
- Recebe inventário validado
- Atualiza página no Notion (PATCH)
- Marca status como "Inventário Completo"
- Bot confirma finalização
```

---

## 🚀 Melhorias Sugeridas

### 1. **Incluir Busca Fuzzy na FASE 2A** ✅

**Por quê:**
- Reduz custo (66% menos chamadas ao Claude)
- Aumenta velocidade (50% mais rápido)
- Melhora precisão (corrige erros de digitação)
- Melhor rastreabilidade (sabe qual método foi usado)

**Como funciona:**
1. **Pré-processar inventário** com busca fuzzy (Jaro-Winkler)
2. **Classificar confiança**:
   - **≥ 0.9**: Alta (usa direto, não precisa Claude)
   - **≥ 0.7**: Média (marca para revisão)
   - **< 0.7**: Baixa (envia para Claude)
3. **Claude só processa** ingredientes com confiança < 0.7
4. **Combinar resultados** (fuzzy + Claude)

**Resultado esperado:**
- ✅ 66% redução de custo
- ✅ 50% mais rápido
- ✅ Maior precisão
- ✅ Melhor rastreabilidade

---

### 2. **Webhooks Separados** ✅

**FASE 2A - Processar:**
- **Webhook**: `/fase2-processar`
- **Função**: Processar inventário (busca fuzzy + Claude)
- **Retorna**: JSON estruturado
- **NÃO salva** no Notion

**FASE 2B - Salvar:**
- **Webhook**: `/fase2-salvar`
- **Função**: Salvar inventário validado no Notion
- **Método**: PATCH (atualiza página existente)
- **Retorna**: Confirmação de salvamento

---

### 3. **Fluxo de Validação** ✅

**FASE 2A - Processar:**
1. Bot recebe inventário (texto ou foto)
2. Bot envia para n8n `/fase2-processar`
3. n8n processa (busca fuzzy + Claude se necessário)
4. n8n retorna JSON estruturado
5. Bot mostra formatado para chef validar
6. Chef clica: ✅ Confirmar ou ❌ Refazer

**FASE 2B - Salvar:**
1. Se ✅ Confirmar:
   - Bot envia para n8n `/fase2-salvar`
   - n8n ATUALIZA página no Notion (PATCH)
   - n8n marca status como "Inventário Completo"
   - Bot: "✅ Relatório finalizado!"
2. Se ❌ Refazer:
   - Bot: "Ok, envie novamente o inventário"
   - Volta para FASE 2A

---

## 📊 Fluxo Completo (Com Busca Fuzzy)

```
┌─────────────────────────────────────────────────────┐
│ FASE 2A - Processar Inventário                      │
└─────────────────────────────────────────────────────┘

Bot: "Envie fotos ou texto do inventário"
  ↓
Chef: "300g arroz, 2 tomates, 500ml leite..."
  ↓
Bot envia via webhook /fase2-processar
  {
    "notion_page_id": "abc123...",
    "inventario_texto": "300g arroz, 2 tomates...",
    "foto_inventario_base64": "" // ou base64 se foto
  }
  ↓
n8n recebe via webhook /fase2-processar
  ↓
1. Ler base de ingredientes (Google Sheets)
  ↓
2. 🆕 Code - Busca Fuzzy
   - Pré-processar inventário
   - Buscar match exato (nome oficial ou sinônimos)
   - Buscar fuzzy (Jaro-Winkler) se não encontrar
   - Classificar confiança (≥ 0.9: alta, ≥ 0.7: média, < 0.7: baixa)
  ↓
3. 🆕 IF - Precisa Claude?
   - Se confiança < 0.7: SIM (chama Claude)
   - Se confiança ≥ 0.7: NÃO (usa fuzzy direto)
  ↓
4. Claude - Normaliza Inventário (SE necessário)
   - Só processa ingredientes com confiança < 0.7
   - Normaliza com base de ingredientes
   - Identifica temperos sensíveis
   - Categoriza ingredientes
  ↓
5. 🆕 Code - Combinar Resultados
   - Combina resultados do fuzzy e Claude
   - Mantém rastreabilidade (método usado)
   - Cria JSON estruturado
  ↓
6. Code - Parse JSON
   - Processa resposta
   - Cria visualização formatada
   - Identifica temperos sensíveis
  ↓
7. Respond - Retorna pro Bot
   {
     "success": true,
     "inventario_estruturado": [
       {
         "nome": "Arroz branco",
         "quantidade": 300,
         "unidade": "g",
         "categoria": "Grãos e Cereais",
         "tempero_sensivel": false,
         "confianca": 0.95,
         "metodo": "fuzzy_alta"
       },
       {
         "nome": "Tomate italiano",
         "quantidade": 2,
         "unidade": "unidades",
         "categoria": "Hortaliças e Verduras",
         "tempero_sensivel": false,
         "confianca": 1.0,
         "metodo": "exato"
       },
       {
         "nome": "Leite integral",
         "quantidade": 500,
         "unidade": "ml",
         "categoria": "Laticínios",
         "tempero_sensivel": false,
         "confianca": 0.92,
         "metodo": "fuzzy_alta"
       }
     ],
     "inventario_visualizacao": "📦 INVENTÁRIO PROCESSADO\n\n...",
     "temperos_sensiveis": [],
     "total_ingredientes": 3,
     "total_temperos_sensiveis": 0,
     "metodos_usados": {
       "exato": 1,
       "fuzzy_alta": 2,
       "fuzzy_media": 0,
       "claude": 0
     }
   }
  ↓
Bot recebe resposta
  ↓
Bot mostra formatado para o chef VALIDAR
  ↓
┌─────────────────────────────────────────────────────┐
│ Bot mostra formatado para o chef VALIDAR            │
└─────────────────────────────────────────────────────┘

Bot: "📋 Inventário processado:

     🌾 Grãos e Cereais:
     • Arroz branco: 300g

     🍅 Hortaliças e Verduras:
     • Tomate italiano: 2 unidades

     🥛 Laticínios:
     • Leite integral: 500ml

     📊 Resumo:
     • Total de ingredientes: 3
     • Temperos sensíveis: 0

     ✅ Está correto?
     ❌ Precisa corrigir?"

  ↓
Chef clica: ✅ Confirmar  ou  ❌ Refazer
  ↓
┌─────────────────────────────────────────────────────┐
│ FASE 2B - Salvar no Notion                          │
└─────────────────────────────────────────────────────┘

Se ✅ Confirmar:
  Bot envia via webhook /fase2-salvar
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
  ↓
  n8n recebe via webhook /fase2-salvar
  ↓
  1. HTTP - Buscar Página (Notion)
     - Busca página pelo notion_page_id
  ↓
  2. HTTP - Atualizar Página (Notion) - PATCH
     - Atualiza propriedade "Inventário (JSON)"
     - Atualiza propriedade "Inventário (Visualização)"
     - Atualiza propriedade "Inventário atualizado?" = "Sim"
     - Atualiza propriedade "Status" = "Inventário Completo"
  ↓
  3. Respond - Confirma pro Bot
     {
       "success": true,
       "message": "Inventário salvo com sucesso!",
       "notion_page_id": "abc123...",
       "notion_url": "https://notion.so/..."
     }
  ↓
  Bot: "✅ Relatório finalizado!"

Se ❌ Refazer:
  Bot: "Ok, envie novamente o inventário"
  ↓
  Volta pro início da FASE 2A
```

---

## 📋 Implementação no n8n

### **FASE 2A - Processar Inventário**

**Workflow:** `Relatório de Visita - Fase 2A - Processar`

**Nodes:**
1. **Webhook - Recebe do Bot** (`/fase2-processar`)
2. **Set - Extrai Variáveis**
3. **Google Sheets - Ler Ingredientes**
4. **Code - Format Base Ingredientes**
5. **IF - Tem Foto Inventário?**
   - SIM → Claude Vision - OCR Foto
   - NÃO → Set - Usa Texto Digitado
6. **Preparar Prompt**
7. **🆕 Code - Busca Fuzzy**
8. **🆕 IF - Precisa Claude?**
   - SIM (conf < 0.7) → Claude - Normaliza Inventário
   - NÃO (conf ≥ 0.7) → 🆕 Code - Combinar Resultados
9. **🆕 Code - Combinar Resultados**
10. **Code - Parse JSON**
11. **Respond - Retorna pro Bot**

**Retorna:**
```json
{
  "success": true,
  "inventario_estruturado": [...],
  "inventario_visualizacao": "...",
  "temperos_sensiveis": [...],
  "total_ingredientes": 3,
  "total_temperos_sensiveis": 0,
  "metodos_usados": {
    "exato": 1,
    "fuzzy_alta": 2,
    "fuzzy_media": 0,
    "claude": 0
  }
}
```

---

### **FASE 2B - Salvar no Notion**

**Workflow:** `Relatório de Visita - Fase 2B - Salvar`

**Nodes:**
1. **Webhook - Recebe do Bot** (`/fase2-salvar`)
2. **Set - Extrai Variáveis**
3. **HTTP - Buscar Página** (Notion)
   - Busca página pelo `notion_page_id`
4. **HTTP - Atualizar Página** (Notion) - PATCH
   - Atualiza propriedades:
     - `Inventário (JSON)`
     - `Inventário (Visualização)`
     - `Inventário atualizado?` = "Sim"
     - `Status` = "Inventário Completo"
5. **Respond - Confirma pro Bot**

**Retorna:**
```json
{
  "success": true,
  "message": "Inventário salvo com sucesso!",
  "notion_page_id": "abc123...",
  "notion_url": "https://notion.so/..."
}
```

---

## 🔧 Modificações no Bot

### **1. Função `processar_inventario()` (FASE 2A)**

**O que faz:**
- Recebe inventário (texto ou foto)
- Envia para n8n `/fase2-processar`
- Recebe JSON estruturado
- Mostra formatado para chef validar
- Chef clica: ✅ Confirmar ou ❌ Refazer

**Código:**
```python
async def processar_inventario(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processar inventário com n8n (FASE 2A)"""
    await update.message.reply_text(
        "🔄 *Processando inventário...*\n"
        "Aguarde enquanto analiso as informações.",
        parse_mode='Markdown'
    )
    
    # Preparar dados para n8n
    webhook_data = {
        'notion_page_id': context.user_data['relatorio'].get('notion_page_id'),
        'inventario_texto': context.user_data.get('inventario_texto', ''),
        'foto_inventario_base64': context.user_data.get('foto_inventario_base64', '')
    }
    
    # Enviar para n8n FASE 2A (processar)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            N8N_WEBHOOK_URL_FASE2A,  # /fase2-processar
            json=webhook_data,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            if response.status == 200:
                resultado = await response.json()
                
                # Salvar inventário processado
                context.user_data['inventario_processado'] = resultado.get('inventario_estruturado', [])
                context.user_data['inventario_visualizacao'] = resultado.get('inventario_visualizacao', '')
                
                # Mostrar formatado para chef validar
                keyboard = [
                    ['✅ Está correto'],
                    ['❌ Precisa correção']
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
                
                await update.message.reply_text(
                    resultado.get('inventario_visualizacao', '') +
                    "\n\n*Por favor, confirme se está correto:*",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
                return CONFIRMAR_INVENTARIO
```

---

### **2. Função `confirmar_inventario()` (FASE 2B)**

**O que faz:**
- Recebe confirmação do chef
- Se ✅ Confirmar: Envia para n8n `/fase2-salvar`
- Se ❌ Refazer: Volta para FASE 2A

**Código:**
```python
async def confirmar_inventario(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirmar ou corrigir inventário (FASE 2B)"""
    resposta = update.message.text
    
    if '✅' in resposta:
        # Inventário confirmado, salvar no Notion (FASE 2B)
        webhook_data = {
            'notion_page_id': context.user_data['relatorio'].get('notion_page_id'),
            'inventario_validado': {
                'inventario_json': json.dumps(context.user_data.get('inventario_processado', [])),
                'inventario_visualizacao': context.user_data.get('inventario_visualizacao', ''),
                'temperos_sensiveis': context.user_data.get('temperos_sensiveis', []),
                'total_ingredientes': len(context.user_data.get('inventario_processado', [])),
                'total_temperos_sensiveis': len(context.user_data.get('temperos_sensiveis', []))
            },
            'status': 'confirmado'
        }
        
        # Enviar para n8n FASE 2B (salvar)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                N8N_WEBHOOK_URL_FASE2B,  # /fase2-salvar
                json=webhook_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    resultado = await response.json()
                    
                    # Confirmação de salvamento
                    await update.message.reply_text(
                        "✅ *Relatório finalizado!*\n\n"
                        f"📎 [Ver relatório no Notion]({resultado.get('notion_url', '')})",
                        parse_mode='Markdown',
                        reply_markup=ReplyKeyboardRemove()
                    )
                    
                    # Limpar dados
                    context.user_data.clear()
                    return ConversationHandler.END
    else:
        # Precisa correção - voltar para FASE 2A
        await update.message.reply_text(
            "✏️ *Digite o inventário corrigido:*\n\n"
            "Exemplo: 500g arroz branco, 2 tomates italianos, meio pacote macarrão penne\n\n"
            "Ou digite a lista completa:",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardRemove()
        )
        
        return INVENTARIO_TEXTO
```

---

## 🎯 Comparação: Antes vs Depois

### **Antes (Atual)**
```
Inventário → Processar (TUDO junto) → Salvar no Notion
```
- ⚠️ Processa e salva em uma única chamada
- ⚠️ Chef não vê resultado antes de salvar
- ⚠️ Dificulta correções
- ⚠️ Não há validação antes de salvar

### **Depois (Proposto)**
```
Inventário → FASE 2A (Processar) → Validar → FASE 2B (Salvar)
```
- ✅ Processa e retorna (sem salvar)
- ✅ Chef vê resultado antes de salvar
- ✅ Facilita correções
- ✅ Validação antes de salvar
- ✅ Melhor UX
- ✅ Redução de erros

---

## ✅ Conclusão

### **Faz MUITO sentido!** ✅

**Vantagens:**
- ✅ **Separação de responsabilidades** (processar vs salvar)
- ✅ **Validação antes de salvar** (chef confirma antes)
- ✅ **Melhor UX** (chef vê o resultado antes de salvar)
- ✅ **Redução de erros** (validação antes de salvar no Notion)
- ✅ **Facilita correções** (chef pode refazer sem salvar)
- ✅ **Melhor rastreabilidade** (sabe quando foi processado vs salvo)

### **Melhorias Sugeridas:**
1. ✅ **Incluir busca fuzzy** na FASE 2A (reduz custo, aumenta velocidade)
2. ✅ **Webhooks separados** (`/fase2-processar` e `/fase2-salvar`)
3. ✅ **Fluxo de validação** (chef confirma antes de salvar)

### **Próximos Passos:**
1. **Criar workflow n8n FASE 2A** (processar)
2. **Criar workflow n8n FASE 2B** (salvar)
3. **Implementar busca fuzzy** na FASE 2A
4. **Modificar bot** para usar dois webhooks
5. **Testar fluxo completo**

---

Quer que eu implemente agora? 🚀

