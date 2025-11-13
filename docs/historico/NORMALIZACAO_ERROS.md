# 🔍 Normalização com Tratamento de Erros

## 🎯 Problema

**O que acontece quando o chef escreve incorretamente?**
- Exemplo: "aroz" em vez de "arroz"
- Exemplo: "pimenta do reino" em vez de "pimenta do reino" (espaço extra)
- Exemplo: "açafrão" em vez de "açafrão" (acento diferente)

## ✅ Soluções Implementadas

### 1. Normalização Básica (Já Implementada)

**O que faz:**
- Remove acentos: "aroz" → "aroz" (ainda não resolve)
- Converte para minúsculas: "ARROZ" → "arroz"
- Remove espaços extras: "arroz  branco" → "arroz branco"
- Remove plural: "arrozs" → "arroz"

**Limitações:**
- ❌ Não corrige erros de digitação (ex: "aroz" → "arroz")
- ❌ Não encontra sinônimos com variações
- ❌ Requer match exato após normalização

---

## 🚀 Soluções Avançadas

### Opção 1: Busca por Similaridade (Fuzzy Matching) ✅ **RECOMENDADO**

**Como funciona:**
- Usa algoritmos de similaridade de strings (Levenshtein, Jaro-Winkler)
- Encontra matches aproximados mesmo com erros
- Sugere correção automática

**Exemplo:**
```
Chef escreve: "aroz branco"
Sistema encontra: "arroz branco" (similaridade: 95%)
Resultado: Normaliza para "Arroz branco"
```

**Implementação:**
```python
from difflib import SequenceMatcher

def encontrar_similar(nome, base_ingredientes, threshold=0.8):
    """Encontrar ingrediente similar na base"""
    melhor_match = None
    melhor_similaridade = 0
    
    nome_normalizado = normalizar_texto(nome)
    
    for ingrediente in base_ingredientes:
        ingrediente_normalizado = normalizar_texto(ingrediente['nome'])
        
        # Calcular similaridade
        similaridade = SequenceMatcher(None, nome_normalizado, ingrediente_normalizado).ratio()
        
        if similaridade > melhor_similaridade and similaridade >= threshold:
            melhor_similaridade = similaridade
            melhor_match = ingrediente
    
    return melhor_match, melhor_similaridade
```

**Vantagens:**
- ✅ Funciona com erros de digitação
- ✅ Encontra variações automaticamente
- ✅ Pode ser implementado no n8n
- ✅ Rápido e eficiente

**Desvantagens:**
- ⚠️ Pode ter falsos positivos se threshold muito baixo
- ⚠️ Pode não encontrar se erro muito grande

---

### Opção 2: Claude AI no n8n ✅ **RECOMENDADO**

**Como funciona:**
- Usa Claude para entender contexto
- Claude pode corrigir erros de digitação
- Claude pode sugerir ingredientes similares

**Exemplo:**
```
Chef escreve: "aroz branco"
Claude entende: "arroz branco"
Claude normaliza: "Arroz branco"
Claude retorna: {
  "nome": "Arroz branco",
  "confianca": 0.95,
  "correcao": "aroz → arroz"
}
```

**Prompt para Claude:**
```
Você recebe uma lista de ingredientes escritos por chefs (podem ter erros de digitação).

Sua tarefa:
1. Identificar o ingrediente correto na base de dados
2. Corrigir erros de digitação
3. Normalizar para o nome oficial
4. Retornar confiança (0-1)

Base de ingredientes:
{lista_ingredientes}

Ingrediente do chef: "{ingrediente_chef}"

Retorne JSON:
{
  "nome_oficial": "nome correto",
  "confianca": 0.95,
  "correcao": "correção feita",
  "sinonimos_encontrados": ["sinonimo1", "sinonimo2"]
}
```

**Vantagens:**
- ✅ Entende contexto
- ✅ Corrige erros inteligentemente
- ✅ Pode sugerir múltiplas opções
- ✅ Alta precisão

**Desvantagens:**
- ⚠️ Mais lento (requer chamada API)
- ⚠️ Mais caro (usa tokens Claude)
- ⚠️ Depende de Claude estar disponível

---

### Opção 3: Híbrida (Busca Fuzzy + Claude) ✅ **MELHOR OPÇÃO**

**Como funciona:**
1. Primeiro: Busca fuzzy (rápida, local)
2. Se confiança alta (>0.9): Usa resultado direto
3. Se confiança média (0.7-0.9): Pede confirmação ao chef
4. Se confiança baixa (<0.7): Usa Claude para entender

**Fluxo:**
```
Chef escreve: "aroz branco"
↓
1. Busca fuzzy: Encontra "arroz branco" (similaridade: 0.95)
   → Confiança alta → Usa direto
↓
Resultado: "Arroz branco"
```

**Se não encontrar:**
```
Chef escreve: "aroz branco"
↓
1. Busca fuzzy: Não encontra (similaridade: 0.6)
   → Confiança baixa → Usa Claude
↓
2. Claude: Entende "arroz branco"
   → Retorna com confiança 0.95
↓
Resultado: "Arroz branco"
```

**Vantagens:**
- ✅ Rápido para casos comuns (busca fuzzy)
- ✅ Preciso para casos difíceis (Claude)
- ✅ Balanceia velocidade e precisão
- ✅ Reduz custos (menos chamadas Claude)

---

## 🔧 Implementação no n8n

### Fluxo Completo:

```
1. Chef envia inventário (texto ou foto)
   ↓
2. n8n processa (OCR se foto, parse se texto)
   ↓
3. Para cada ingrediente:
   a. Normalizar texto (acentos, minúsculas, plural)
   b. Buscar na base de sinônimos (match exato)
   c. Se não encontrar:
      - Busca fuzzy (similaridade)
      - Se confiança alta (>0.9): Usa direto
      - Se confiança média (0.7-0.9): Marca para revisão
      - Se confiança baixa (<0.7): Usa Claude
   ↓
4. Retornar inventário normalizado
   ↓
5. Chef confirma/corrige
```

### Código no n8n (Function Node):

```javascript
// Função de similaridade (Jaro-Winkler)
function jaroWinkler(str1, str2) {
    // Implementação do algoritmo Jaro-Winkler
    // Retorna similaridade entre 0 e 1
}

// Buscar ingrediente similar
function encontrarIngredienteSimilar(nome, baseIngredientes, threshold = 0.8) {
    let melhorMatch = null;
    let melhorSimilaridade = 0;
    
    const nomeNormalizado = normalizarTexto(nome);
    
    for (const ingrediente of baseIngredientes) {
        const sinonimos = ingrediente.sinonimos.split(',').map(s => s.trim());
        
        for (const sinonimo of sinonimos) {
            const sinonimoNormalizado = normalizarTexto(sinonimo);
            const similaridade = jaroWinkler(nomeNormalizado, sinonimoNormalizado);
            
            if (similaridade > melhorSimilaridade && similaridade >= threshold) {
                melhorSimilaridade = similaridade;
                melhorMatch = {
                    nome: ingrediente.nome,
                    similaridade: similaridade,
                    sinonimo: sinonimo
                };
            }
        }
    }
    
    return melhorMatch;
}

// Processar ingrediente
function processarIngrediente(nome, baseIngredientes) {
    // 1. Normalizar
    const nomeNormalizado = normalizarTexto(nome);
    
    // 2. Buscar match exato
    const matchExato = baseIngredientes.find(ing => {
        const sinonimos = ing.sinonimos.split(',').map(s => s.trim().toLowerCase());
        return sinonimos.includes(nomeNormalizado);
    });
    
    if (matchExato) {
        return {
            nome: matchExato.nome,
            confianca: 1.0,
            metodo: 'exato'
        };
    }
    
    // 3. Busca fuzzy
    const matchFuzzy = encontrarIngredienteSimilar(nome, baseIngredientes, 0.8);
    
    if (matchFuzzy && matchFuzzy.similaridade >= 0.9) {
        // Confiança alta: usa direto
        return {
            nome: matchFuzzy.nome,
            confianca: matchFuzzy.similaridade,
            metodo: 'fuzzy',
            correcao: nome + ' → ' + matchFuzzy.nome
        };
    } else if (matchFuzzy && matchFuzzy.similaridade >= 0.7) {
        // Confiança média: marca para revisão
        return {
            nome: matchFuzzy.nome,
            confianca: matchFuzzy.similaridade,
            metodo: 'fuzzy_revisao',
            correcao: nome + ' → ' + matchFuzzy.nome,
            precisa_revisao: true
        };
    } else {
        // Confiança baixa: usa Claude
        return {
            nome: nome,
            confianca: 0.5,
            metodo: 'claude',
            precisa_claude: true
        };
    }
}
```

---

## 📊 Exemplos Práticos

### Exemplo 1: Erro de Digitação Simples

**Entrada do chef:** "aroz branco"
**Processamento:**
1. Normalização: "aroz branco" → "aroz branco" (ainda com erro)
2. Busca exata: Não encontra
3. Busca fuzzy: Encontra "arroz branco" (similaridade: 0.95)
4. **Resultado:** "Arroz branco" (confiança: 0.95)

### Exemplo 2: Erro de Acento

**Entrada do chef:** "acafrão" (sem ç)
**Processamento:**
1. Normalização: Remove acentos → "acafrao"
2. Busca exata: Não encontra
3. Busca fuzzy: Encontra "açafrão" (similaridade: 0.92)
4. **Resultado:** "Açafrão da terra/cúrcuma em pó" (confiança: 0.92)

### Exemplo 3: Erro Múltiplo

**Entrada do chef:** "pimenta do reino" (espaço extra)
**Processamento:**
1. Normalização: Remove espaços extras → "pimenta do reino"
2. Busca exata: Encontra "pimenta do reino"
3. **Resultado:** "Pimenta do Reino em Grãos" (confiança: 1.0)

### Exemplo 4: Erro Grande (Precisa Claude)

**Entrada do chef:** "pimenta reino" (sem "do")
**Processamento:**
1. Normalização: "pimenta reino"
2. Busca exata: Não encontra
3. Busca fuzzy: Encontra "pimenta do reino" (similaridade: 0.85)
4. **Resultado:** "Pimenta do Reino em Grãos" (confiança: 0.85, precisa revisão)

---

## 🎯 Recomendação Final

### Implementar: **Busca Híbrida (Fuzzy + Claude)**

**Estratégia:**
1. **Busca Exata** (rápida): Match exato após normalização
2. **Busca Fuzzy** (média): Similaridade > 0.9 → usa direto
3. **Busca Fuzzy** (baixa): Similaridade 0.7-0.9 → marca para revisão
4. **Claude** (último recurso): Similaridade < 0.7 → usa Claude

**Vantagens:**
- ✅ Rápido para casos comuns (busca fuzzy)
- ✅ Preciso para casos difíceis (Claude)
- ✅ Balanceia velocidade e precisão
- ✅ Reduz custos (menos chamadas Claude)

**Implementação:**
- ✅ Busca fuzzy no n8n (Function Node)
- ✅ Claude como fallback
- ✅ Marcar ingredientes com baixa confiança para revisão

---

## 📝 Próximos Passos

1. ✅ Implementar busca fuzzy no n8n
2. ✅ Configurar threshold de confiança
3. ✅ Implementar fallback para Claude
4. ✅ Marcar ingredientes com baixa confiança
5. ✅ Testar com erros reais

---

## ❓ Perguntas

1. **Qual threshold usar?** (recomendo 0.8-0.9)
2. **Quando usar Claude?** (recomendo < 0.7)
3. **Como marcar para revisão?** (recomendo mostrar ao chef)
4. **Como testar?** (recomendo criar casos de teste)

---

## ✅ Conclusão

**Para tratar erros de digitação:**
1. ✅ Normalização básica (já implementada)
2. ✅ Busca fuzzy (implementar no n8n)
3. ✅ Claude como fallback (implementar no n8n)
4. ✅ Marcar para revisão (mostrar ao chef)

**Resultado:**
- ✅ Encontra ingredientes mesmo com erros
- ✅ Corrige automaticamente quando possível
- ✅ Marca para revisão quando necessário
- ✅ Usa Claude para casos difíceis

Quer que eu implemente a busca fuzzy no script ou prefere fazer no n8n?

