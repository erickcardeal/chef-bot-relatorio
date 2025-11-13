# ✅ Solução para Erros de Digitação

## 🎯 Problema

**Chef escreve incorretamente:**
- "aroz" em vez de "arroz"
- "acafrao" em vez de "açafrão"
- "pimenta  do  reino" (espaço extra)

## 🔧 Solução: Busca Híbrida

### 1. **Normalização Básica** (Já Funciona)
- Remove acentos: "açafrão" → "acafrao"
- Minúsculas: "ARROZ" → "arroz"
- Remove espaços: "arroz  branco" → "arroz branco"
- Remove plural: "arrozs" → "arroz"

**Limitação:** Não corrige erros de digitação (ex: "aroz" → "arroz")

---

### 2. **Busca Fuzzy** (Precisa Implementar no n8n) ✅

**Como funciona:**
- Calcula similaridade entre strings (Jaro-Winkler)
- Encontra matches aproximados mesmo com erros
- Threshold: 0.8-0.9 (80-90% de similaridade)

**Exemplo:**
```
Chef escreve: "aroz branco"
Sistema calcula similaridade:
- "aroz branco" vs "arroz branco" = 0.95 (95%)
- Threshold: 0.8
- Resultado: ✅ Encontrado! → "Arroz branco"
```

**Quando usar:**
- ✅ Confiança alta (>0.9): Usa direto
- ⚠️ Confiança média (0.7-0.9): Marca para revisão
- ❌ Confiança baixa (<0.7): Usa Claude

---

### 3. **Claude AI** (Fallback) ✅

**Quando usar:**
- Busca fuzzy não encontrou (similaridade < 0.7)
- Erro muito grande
- Contexto necessário

**Exemplo:**
```
Chef escreve: "pimenta reino" (sem "do")
Claude entende: "pimenta do reino"
Claude retorna: "Pimenta do Reino em Grãos" (confiança: 0.95)
```

---

## 📊 Fluxo Completo

```
Chef escreve: "aroz branco"
↓
1. Normalização básica
   "aroz branco" → "aroz branco" (ainda com erro)
↓
2. Busca exata (sinônimos)
   Não encontra ❌
↓
3. Busca fuzzy (similaridade)
   "aroz branco" vs "arroz branco" = 0.95
   Confiança: 95% ✅
↓
4. Resultado
   "Arroz branco" (confiança: 0.95)
   Método: fuzzy_alta
   Correção: "aroz → arroz"
```

---

## 🔍 Exemplos Práticos

### Exemplo 1: Erro Simples
**Entrada:** "aroz branco"
**Processamento:**
- Normalização: "aroz branco"
- Busca exata: ❌ Não encontra
- Busca fuzzy: ✅ Encontra "arroz branco" (95%)
- **Resultado:** "Arroz branco" (confiança: 0.95)

### Exemplo 2: Erro de Acento
**Entrada:** "acafrao"
**Processamento:**
- Normalização: "acafrao" (remove acento)
- Busca exata: ❌ Não encontra
- Busca fuzzy: ✅ Encontra "açafrão" (92%)
- **Resultado:** "Açafrão da terra/cúrcuma em pó" (confiança: 0.92)

### Exemplo 3: Espaço Extra
**Entrada:** "pimenta  do  reino"
**Processamento:**
- Normalização: "pimenta do reino" (remove espaços)
- Busca exata: ✅ Encontra "pimenta do reino"
- **Resultado:** "Pimenta do Reino em Grãos" (confiança: 1.0)

### Exemplo 4: Erro Grande
**Entrada:** "pimenta reino" (sem "do")
**Processamento:**
- Normalização: "pimenta reino"
- Busca exata: ❌ Não encontra
- Busca fuzzy: ✅ Encontra "pimenta do reino" (85%)
- **Resultado:** "Pimenta do Reino em Grãos" (confiança: 0.85, precisa revisão)

### Exemplo 5: Não Encontrado
**Entrada:** "ingrediente inexistente"
**Processamento:**
- Normalização: "ingrediente inexistente"
- Busca exata: ❌ Não encontra
- Busca fuzzy: ❌ Não encontra (similaridade < 0.7)
- **Resultado:** Usa Claude para entender

---

## 🚀 Implementação no n8n

### Passo 1: Ler Base de Ingredientes (Google Sheets)

```javascript
// Node: Google Sheets
// Lê todos os ingredientes com sinônimos
const baseIngredientes = $input.all();
```

### Passo 2: Processar Cada Ingrediente (Function Node)

```javascript
// Usar função processarIngrediente (ver exemplo_busca_fuzzy.js)
const ingredienteChef = $input.item.json.ingrediente;
const resultado = processarIngrediente(ingredienteChef, baseIngredientes);
return resultado;
```

### Passo 3: Tratar Resultado

```javascript
if (resultado.confianca >= 0.9) {
  // Confiança alta: usa direto
  return resultado;
} else if (resultado.confianca >= 0.7) {
  // Confiança média: marca para revisão
  return {
    ...resultado,
    precisa_revisao: true
  };
} else {
  // Confiança baixa: usa Claude
  // Enviar para Claude Node
}
```

### Passo 4: Claude (Fallback)

```javascript
// Node: Claude
// Prompt: "Normalize este ingrediente: {ingrediente}"
// Retorna: ingrediente normalizado
```

---

## 📋 Estrutura de Resposta

```json
{
  "nome_oficial": "Arroz branco",
  "confianca": 0.95,
  "metodo": "fuzzy_alta",
  "correcao": "aroz → arroz",
  "categoria": "Grãos e Cereais",
  "unidade_padrao": "g",
  "tempero_sensivel": "Não",
  "aviso": "-",
  "precisa_revisao": false
}
```

---

## ✅ Vantagens da Solução

1. **Rápido:** Busca fuzzy é rápida (milissegundos)
2. **Preciso:** Encontra matches mesmo com erros
3. **Inteligente:** Claude para casos difíceis
4. **Econômico:** Menos chamadas Claude (só quando necessário)
5. **Flexível:** Threshold configurável (0.7-0.9)

---

## 🎯 Recomendação

**Implementar busca híbrida:**
1. ✅ Busca exata (já funciona)
2. ✅ Busca fuzzy (implementar no n8n)
3. ✅ Claude (fallback)

**Threshold recomendado:**
- Alta confiança: > 0.9 (usa direto)
- Média confiança: 0.7-0.9 (marca para revisão)
- Baixa confiança: < 0.7 (usa Claude)

---

## 📝 Próximos Passos

1. ✅ Implementar busca fuzzy no n8n
2. ✅ Configurar threshold (0.8-0.9)
3. ✅ Testar com erros reais
4. ✅ Configurar Claude como fallback
5. ✅ Marcar ingredientes com baixa confiança

---

## ❓ Perguntas

1. **Qual threshold usar?** (recomendo 0.8-0.9)
2. **Quando usar Claude?** (recomendo < 0.7)
3. **Como marcar para revisão?** (mostrar ao chef)
4. **Como testar?** (criar casos de teste)

---

## ✅ Conclusão

**Para tratar erros de digitação:**
1. ✅ Normalização básica (já implementada)
2. ✅ Busca fuzzy (implementar no n8n) ← **PRINCIPAL**
3. ✅ Claude (fallback)
4. ✅ Marcar para revisão (mostrar ao chef)

**Resultado:**
- ✅ Encontra ingredientes mesmo com erros
- ✅ Corrige automaticamente quando possível
- ✅ Marca para revisão quando necessário
- ✅ Usa Claude para casos difíceis

---

## 💡 Exemplo de Código

Veja o arquivo `exemplo_busca_fuzzy.js` para código completo de busca fuzzy que pode ser usado no n8n.

