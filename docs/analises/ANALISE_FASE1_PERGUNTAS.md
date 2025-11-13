# 📋 Análise: Perguntas Necessárias para FASE 1

## 🎯 Objetivo da FASE 1
Criar relatório básico no Notion rapidamente (3-5 segundos) com dados essenciais e responder ao bot imediatamente.

---

## ✅ Dados Necessários para FASE 1

### **1. Dados que JÁ temos (sem perguntar):**
- ✅ **Chef** (relation) - vem do contexto ao fazer `/start`
- ✅ **Cliente** (relation) - vem da seleção do atendimento
- ✅ **Data Atendimento** - vem da seleção do atendimento

### **2. Perguntas NECESSÁRIAS para FASE 1:**

#### **🔴 OBRIGATÓRIAS (dados básicos do relatório):**
1. ✅ **Horário de Chegada** - `HORARIO_CHEGADA`
   - Já existe no fluxo atual
   - Formato: HH:MM
   - **Necessário para FASE 1**

2. ✅ **Horário de Saída** - `HORARIO_SAIDA`
   - Já existe no fluxo atual
   - Formato: HH:MM
   - **Necessário para FASE 1**

3. ✅ **Como foi a visita** - `COMO_FOI_VISITA`
   - Já existe no fluxo atual
   - Texto livre
   - **Necessário para FASE 1**

#### **🟡 OPCIONAIS (podem ser vazios, mas devem ser coletados):**
4. ✅ **Comentário do Cliente** - `COMENTARIO_CLIENTE`
   - Já existe no fluxo atual
   - Pergunta: "O cliente fez algum comentário?"
   - Se "Sim": pede detalhe (`DETALHE_COMENTARIO`)
   - Se "Não": valor vazio
   - **Necessário para FASE 1** (pode ser vazio)

5. ✅ **Problema Específico** - `PROBLEMA_ESPECIFICO`
   - Já existe no fluxo atual
   - Pergunta: "Houve algum problema específico?"
   - Se "Sim": pede detalhe (`DETALHE_PROBLEMA`)
   - Se "Não": valor vazio
   - **Necessário para FASE 1** (pode ser vazio)

6. ✅ **Porções Exatas?** - `PORCOES_EXATAS`
   - Já existe no fluxo atual
   - Pergunta: "As porções foram produzidas na mesma quantidade da planilha?"
   - Se "Sim": valor "Sim", motivo vazio
   - Se "Não": pede motivo (`MOTIVO_PORCOES`)
   - **Necessário para FASE 1**

7. ✅ **Motivo Porções** - `MOTIVO_PORCOES`
   - Já existe no fluxo atual
   - Só pergunta se porções não foram exatas
   - **Necessário para FASE 1** (pode ser vazio)

8. ✅ **Descarte?** - `DESCARTE`
   - Já existe no fluxo atual
   - Pergunta: "Algum ingrediente precisou ser DESCARTADO?"
   - Se "Sim": pede detalhe (`ITENS_DESCARTADOS`)
   - Se "Não": valor vazio
   - **Necessário para FASE 1** (pode ser vazio)

9. ✅ **Itens Descartados** - `ITENS_DESCARTADOS`
   - Já existe no fluxo atual
   - Só pergunta se houve descarte
   - **Necessário para FASE 1** (pode ser vazio)

10. ✅ **Pode Vencer?** - `PODE_VENCER`
    - Já existe no fluxo atual
    - Pergunta: "Algum ingrediente possivelmente NÃO vai durar até o próximo atendimento?"
    - Se "Sim": pede detalhe (`ITENS_PODEM_VENCER`)
    - Se "Não": valor vazio
    - **Necessário para FASE 1** (pode ser vazio)

11. ✅ **Itens Podem Vencer** - `ITENS_PODEM_VENCER`
    - Já existe no fluxo atual
    - Só pergunta se pode vencer
    - **Necessário para FASE 1** (pode ser vazio)

---

### **3. Dados NÃO necessários para FASE 1 (ficam para FASE 2):**

#### **❌ REMOVER do fluxo antes de enviar para FASE 1:**
- ❌ **Foto Entrada** - `FOTO_ENTRADA`
  - Será enviada depois na FASE 2
  - Não é necessária para criar relatório básico

- ❌ **Foto Saída** - `FOTO_SAIDA`
  - Será enviada depois na FASE 2
  - Não é necessária para criar relatório básico

- ❌ **Inventário (texto ou foto)** - `INVENTARIO_OPCAO`, `INVENTARIO_TEXTO`, `INVENTARIO_FOTO`
  - Será processado na FASE 2
  - Não é necessário para criar relatório básico

- ❌ **Confirmação de Inventário** - `CONFIRMAR_INVENTARIO`, `CORRIGIR_INVENTARIO`
  - Será processado na FASE 2
  - Não é necessário para criar relatório básico

---

## 📊 Fluxo Proposto para FASE 1

### **Sequência de Perguntas (após selecionar atendimento):**

```
1. Horário de Chegada ✅
2. Horário de Saída ✅
3. Como foi a visita? ✅
4. Comentário do cliente? (Sim/Não) ✅
   → Se Sim: Qual foi o comentário?
5. Problema específico? (Sim/Não) ✅
   → Se Sim: Qual foi o problema?
6. Porções exatas? (Sim/Não) ✅
   → Se Não: Motivo?
7. Descarte? (Sim/Não) ✅
   → Se Sim: Quais itens?
8. Pode vencer? (Sim/Não) ✅
   → Se Sim: Quais itens?
9. ✅ ENVIAR PARA FASE 1 (criar relatório básico no Notion)
10. ✅ RESPOSTA RÁPIDA AO BOT (3-5 segundos)
11. ⏳ CONTINUAR: Fotos e Inventário (FASE 2 - assíncrono)
```

---

## 🔄 Mudanças Necessárias no Bot

### **1. Modificar fluxo de estados:**
- **Manter:** Todos os estados até `ITENS_PODEM_VENCER`
- **Remover temporariamente:** `FOTO_ENTRADA`, `FOTO_SAIDA`, `INVENTARIO_OPCAO`, `CONFIRMAR_INVENTARIO`, `CORRIGIR_INVENTARIO`
- **Adicionar:** Novo estado `ENVIAR_FASE1` após `ITENS_PODEM_VENCER`

### **2. Criar função `enviar_fase1()`:**
- Coletar apenas dados básicos
- Enviar para n8n FASE 1
- Receber resposta rápida (3-5s)
- Mostrar confirmação ao chef
- **Depois disso**, continuar coletando fotos e inventário (FASE 2)

### **3. Modificar `finalizar_relatorio()`:**
- Dividir em duas partes:
  - `enviar_fase1()`: Dados básicos → n8n FASE 1 → resposta rápida
  - `enviar_fase2()`: Fotos + Inventário → n8n FASE 2 → atualizar relatório

---

## 📋 Payload para FASE 1 (n8n)

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
  "itens_podem_vencer": "Iogurte vence em 2 dias"
}
```

**NOTA:** Campos opcionais podem ser vazios (`""`) ou `null`.

---

## ✅ Resumo

### **Perguntas Necessárias para FASE 1:**
1. ✅ Horário de Chegada
2. ✅ Horário de Saída
3. ✅ Como foi a visita
4. ✅ Comentário do cliente (opcional)
5. ✅ Problema específico (opcional)
6. ✅ Porções exatas? (opcional)
7. ✅ Motivo porções (opcional)
8. ✅ Descarte? (opcional)
9. ✅ Itens descartados (opcional)
10. ✅ Pode vencer? (opcional)
11. ✅ Itens podem vencer (opcional)

### **Perguntas que FICAM para FASE 2:**
- ❌ Foto Entrada
- ❌ Foto Saída
- ❌ Inventário (texto ou foto)

### **Ação após FASE 1:**
- ✅ Enviar dados básicos para n8n
- ✅ Receber resposta rápida (3-5s)
- ✅ Confirmar ao chef que relatório foi criado
- ✅ **Depois disso**, continuar coletando fotos e inventário (FASE 2)

---

## 🎯 Próximos Passos

1. ✅ **Modificar bot** para enviar dados básicos após coletar todas as perguntas obrigatórias
2. ✅ **Criar workflow n8n FASE 1** que recebe dados básicos e cria relatório no Notion
3. ✅ **Testar fluxo FASE 1** (criar relatório básico)
4. ✅ **Implementar FASE 2** (fotos + inventário)


