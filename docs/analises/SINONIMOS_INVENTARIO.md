# 🔍 Sinônimos de Ingredientes: Planilha vs Código

## 📊 Análise das Opções

### Opção 1: Sinônimos na Planilha ✅ **RECOMENDADO**

**Estrutura:**
```
| Nome Oficial | Sinônimos | Categoria | Unidade | Tempero Sensível |
|-------------|-----------|-----------|---------|------------------|
| Arroz branco | arroz, arroz comum, arroz branco | Grãos | g | Não |
| Pimenta do reino | pimenta, pimenta preta, pimenta do reino, pimenta preta moída | Temperos | g | Sim |
```

**Vantagens:**
- ✅ **Fácil de manter**: Time de operações pode editar diretamente
- ✅ **Centralizado**: Tudo em um lugar
- ✅ **Escalável**: Pode ter muitos sinônimos por ingrediente
- ✅ **Histórico**: Google Sheets mantém histórico
- ✅ **Colaborativo**: Várias pessoas podem editar
- ✅ **Sem necessidade de dev**: Time de operações é autônomo
- ✅ **Fácil de testar**: Pode testar novos sinônimos rapidamente

**Desvantagens:**
- ⚠️ Planilha pode ficar grande (mas 300 ingredientes é gerenciável)
- ⚠️ Precisa ler do Sheets (mas n8n pode cachear)

**Como implementar:**
1. Coluna "Sinônimos" na planilha (separados por vírgula)
2. n8n lê planilha e cria mapa de sinônimos
3. Normaliza ingrediente usando mapa
4. Se não encontrar, tenta normalização básica (plural, acentos)

---

### Opção 2: Sinônimos em Código

**Estrutura:**
```python
SINONIMOS = {
    "arroz branco": ["arroz", "arroz comum", "arroz branco"],
    "pimenta do reino": ["pimenta", "pimenta preta", "pimenta do reino"],
    ...
}
```

**Vantagens:**
- ✅ Mais rápido (não precisa ler do Sheets)
- ✅ Pode ter lógica complexa

**Desvantagens:**
- ❌ Precisa de dev para alterar
- ❌ Time de operações não consegue editar
- ❌ Não é centralizado
- ❌ Difícil de manter
- ❌ Precisa fazer deploy para alterar

---

### Opção 3: Híbrida (Sinônimos na Planilha + Normalização em Código)

**Estrutura:**
- Sinônimos específicos na planilha (ex: "pimenta" → "pimenta do reino")
- Normalização básica em código (plural, acentos, etc.)

**Vantagens:**
- ✅ Melhor dos dois mundos
- ✅ Sinônimos editáveis pelo time
- ✅ Normalização básica automática

**Desvantagens:**
- ⚠️ Mais complexo de implementar
- ⚠️ Pode ter conflitos entre sinônimos e normalização

---

## 🎯 **Recomendação: Opção 1 (Sinônimos na Planilha)**

### Por quê?

1. **Time de operações precisa editar**: Se um chef escrever "arroz integral" e não estiver na base, time pode adicionar sem depender de dev
2. **300 ingredientes é gerenciável**: Não é muito grande para planilha
3. **Colaborativo**: Várias pessoas podem editar simultaneamente
4. **Histórico**: Google Sheets mantém histórico de alterações
5. **Fácil de testar**: Pode testar novos sinônimos rapidamente
6. **Sem necessidade de deploy**: Alterações são imediatas

### Como implementar:

#### 1. Estrutura da Planilha

**Aba 1: Ingredientes**

| Nome Oficial | Sinônimos | Categoria | Unidade Padrão | Tempero Sensível | Aviso |
|-------------|-----------|-----------|----------------|------------------|-------|
| Arroz branco | arroz, arroz comum, arroz branco | Grãos | g | Não | - |
| Pimenta do reino | pimenta, pimenta preta, pimenta do reino, pimenta preta moída | Temperos | g | Sim | ⚠️ ATENÇÃO: Verifique se a quantidade está correta! |
| Açafrão | açafrão, cúrcuma, curcuma, açafrão em pó | Temperos | g | Sim | ⚠️ ATENÇÃO: Verifique se a quantidade está correta! |
| Leite integral | leite, leite integral, leite de vaca | Laticínios | ml | Não | - |

**Formato dos sinônimos:**
- Separados por vírgula
- Minúsculas (normalização automática)
- Incluir variações comuns (plural, com/sem acento, etc.)

#### 2. Fluxo no n8n

```
1. Ler Google Sheets (cachear por X minutos)
2. Criar mapa de sinônimos:
   {
     "arroz": "Arroz branco",
     "arroz comum": "Arroz branco",
     "arroz branco": "Arroz branco",
     "pimenta": "Pimenta do reino",
     "pimenta preta": "Pimenta do reino",
     ...
   }
3. Normalizar ingrediente:
   a. Buscar no mapa de sinônimos (exato)
   b. Se não encontrar, tentar normalização básica:
      - Remover acentos
      - Converter para minúsculas
      - Remover plural
      - Buscar novamente
   c. Se ainda não encontrar, usar como está (marcar como não normalizado)
4. Retornar ingrediente normalizado
```

#### 3. Normalização Básica (em código no n8n)

```javascript
// Função de normalização básica
function normalizarTexto(texto) {
  // Remover acentos
  texto = texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  
  // Converter para minúsculas
  texto = texto.toLowerCase();
  
  // Remover espaços extras
  texto = texto.trim();
  
  // Remover plural comum (s, es, ões)
  texto = texto.replace(/(s|es|ões)$/, "");
  
  return texto;
}

// Exemplo:
// "Arroz branco" → "arroz branco"
// "Pimenta do reino" → "pimenta do reino"
// "Pimentas" → "pimenta" → buscar "pimenta" no mapa
```

---

## 📋 Estrutura Completa da Planilha

### Aba 1: Ingredientes

| Nome Oficial | Sinônimos | Categoria | Unidade Padrão | Tempero Sensível | Aviso |
|-------------|-----------|-----------|----------------|------------------|-------|
| Arroz branco | arroz, arroz comum, arroz branco | Grãos | g | Não | - |
| Pimenta do reino | pimenta, pimenta preta, pimenta do reino, pimenta preta moída | Temperos | g | Sim | ⚠️ ATENÇÃO: Verifique se a quantidade está correta! |
| Açafrão | açafrão, cúrcuma, curcuma, açafrão em pó | Temperos | g | Sim | ⚠️ ATENÇÃO: Verifique se a quantidade está correta! |
| Leite integral | leite, leite integral, leite de vaca | Laticínios | ml | Não | - |
| Azeite de oliva | azeite, azeite de oliva, azeite extra virgem | Óleos | ml | Não | - |

**Regras:**
- **Nome Oficial**: Nome padrão que será usado no inventário
- **Sinônimos**: Lista separada por vírgula (incluir variações comuns)
- **Categoria**: Categoria do ingrediente (Grãos, Temperos, Laticínios, etc.)
- **Unidade Padrão**: Unidade padrão (g para sólidos, ml para líquidos)
- **Tempero Sensível**: Sim/Não
- **Aviso**: Mensagem personalizada (opcional)

### Aba 2: Configurações (Opcional)

| Chave | Valor |
|-------|-------|
| Cache tempo (minutos) | 30 |
| Timeout processamento (segundos) | 60 |
| Unidade padrão sólidos | g |
| Unidade padrão líquidos | ml |

---

## 🔧 Implementação no n8n

### Fluxo Completo:

```
1. Webhook recebe inventário (texto ou foto)
   ↓
2. Se foto: Claude Vision (OCR)
   Se texto: Parse básico
   ↓
3. Ler Google Sheets (com cache)
   ↓
4. Criar mapa de sinônimos
   ↓
5. Para cada ingrediente:
   a. Normalizar texto (acentos, minúsculas, plural)
   b. Buscar no mapa de sinônimos
   c. Se encontrar: usar nome oficial
   d. Se não encontrar: usar como está (marcar como não normalizado)
   ↓
6. Identificar temperos sensíveis
   ↓
7. Normalizar unidades (sempre em gramas, líquidos com descrição)
   ↓
8. Categorizar ingredientes
   ↓
9. Retornar inventário estruturado
```

### Código de Normalização (n8n Function Node):

```javascript
// Ler planilha do Google Sheets
const ingredientes = $input.all();

// Criar mapa de sinônimos
const mapaSinonimos = {};
ingredientes.forEach(item => {
  const nomeOficial = item.json['Nome Oficial'];
  const sinonimos = item.json['Sinônimos'].split(',').map(s => s.trim().toLowerCase());
  
  // Adicionar nome oficial ao mapa
  mapaSinonimos[nomeOficial.toLowerCase()] = nomeOficial;
  
  // Adicionar sinônimos ao mapa
  sinonimos.forEach(sinonimo => {
    mapaSinonimos[sinonimo] = nomeOficial;
  });
});

// Função de normalização
function normalizarIngrediente(texto) {
  // Normalizar texto
  let normalizado = texto
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
  
  // Remover plural
  normalizado = normalizado.replace(/(s|es|ões)$/, "");
  
  // Buscar no mapa
  if (mapaSinonimos[normalizado]) {
    return mapaSinonimos[normalizado];
  }
  
  // Se não encontrar, tentar busca parcial
  for (const [sinonimo, nomeOficial] of Object.entries(mapaSinonimos)) {
    if (normalizado.includes(sinonimo) || sinonimo.includes(normalizado)) {
      return nomeOficial;
    }
  }
  
  // Se ainda não encontrar, retornar original
  return texto;
}

// Aplicar normalização
const ingredienteNormalizado = normalizarIngrediente($input.item.json.ingrediente);

return {
  original: $input.item.json.ingrediente,
  normalizado: ingredienteNormalizado
};
```

---

## ✅ Vantagens da Abordagem (Sinônimos na Planilha)

1. **Time de operações autônomo**: Pode adicionar/editar sinônimos sem depender de dev
2. **Fácil de manter**: Alterações são imediatas (sem deploy)
3. **Colaborativo**: Várias pessoas podem editar simultaneamente
4. **Histórico**: Google Sheets mantém histórico de alterações
5. **Testável**: Pode testar novos sinônimos rapidamente
6. **Escalável**: 300 ingredientes é gerenciável
7. **Cacheável**: n8n pode cachear por X minutos (não precisa ler toda hora)

---

## 🎯 Recomendação Final

**Sinônimos na Planilha** ✅

**Por quê?**
- Time de operações precisa editar
- 300 ingredientes é gerenciável
- Fácil de manter
- Sem necessidade de deploy
- Colaborativo

**Implementação:**
1. Coluna "Sinônimos" na planilha (separados por vírgula)
2. n8n lê planilha e cria mapa de sinônimos
3. Normaliza ingrediente usando mapa
4. Se não encontrar, tenta normalização básica (plural, acentos)
5. Cachear mapa por 30 minutos (não precisa ler toda hora)

---

## 📝 Próximos Passos

1. ✅ Adicionar coluna "Sinônimos" na planilha
2. ✅ Adicionar coluna "Tempero Sensível" na planilha
3. ✅ Adicionar coluna "Aviso" na planilha (opcional)
4. ✅ Configurar n8n para ler Google Sheets
5. ✅ Implementar normalização no n8n
6. ✅ Testar fluxo completo

---

## ❓ Perguntas

1. **Quantos sinônimos por ingrediente em média?** (para dimensionar)
2. **Tem ingredientes com muitos sinônimos?** (ex: "pimenta" tem várias variações)
3. **Prefere cache de quanto tempo?** (30 minutos é bom?)
4. **Tem ingredientes que precisam de normalização especial?** (ex: "meia garrafa de azeite")

---

## 💡 Dicas

### 1. Sinônimos Comuns
- Incluir variações com/sem acento
- Incluir plural/singular
- Incluir variações regionais
- Incluir nomes populares

### 2. Normalização Básica
- Remover acentos
- Converter para minúsculas
- Remover plural
- Remover espaços extras

### 3. Cache
- Cachear mapa por 30 minutos
- Invalidar cache se planilha for atualizada
- Log de quando cache é atualizado

### 4. Logs
- Registrar quando ingrediente não é normalizado
- Registrar quando sinônimo é usado
- Identificar ingredientes que precisam de sinônimos

---

## ✅ Conclusão

**Sinônimos na Planilha** é a melhor opção porque:
- ✅ Time de operações pode editar
- ✅ Fácil de manter
- ✅ Colaborativo
- ✅ Sem necessidade de deploy
- ✅ Histórico de alterações

Quer que eu detalhe alguma parte específica da implementação?

