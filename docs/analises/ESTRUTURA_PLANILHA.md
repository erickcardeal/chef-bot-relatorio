# 📊 Estrutura da Planilha de Ingredientes

## 🎯 Estrutura Recomendada

### Aba 1: Ingredientes

| Nome Oficial | Sinônimos | Categoria | Unidade Padrão | Tempero Sensível | Aviso |
|-------------|-----------|-----------|----------------|------------------|-------|
| Arroz branco | arroz, arroz comum, arroz branco | Grãos | g | Não | - |
| Pimenta do reino | pimenta, pimenta preta, pimenta do reino, pimenta preta moída | Temperos | g | Sim | ⚠️ ATENÇÃO: Verifique se a quantidade está correta! |
| Açafrão | açafrão, cúrcuma, curcuma, açafrão em pó | Temperos | g | Sim | ⚠️ ATENÇÃO: Verifique se a quantidade está correta! |
| Leite integral | leite, leite integral, leite de vaca | Laticínios | ml | Não | - |
| Azeite de oliva | azeite, azeite de oliva, azeite extra virgem | Óleos | ml | Não | - |

### 📋 Regras:

#### 1. Nome Oficial
- Nome padrão que será usado no inventário
- Sempre no singular
- Capitalização correta

#### 2. Sinônimos
- **Formato**: Separados por vírgula
- **Exemplo**: `arroz, arroz comum, arroz branco`
- **Regras**:
  - Sempre em minúsculas
  - Incluir variações comuns (plural, com/sem acento)
  - Incluir nomes populares
  - Incluir variações regionais
  - Incluir o próprio nome oficial (para facilitar busca)

#### 3. Categoria
- Categoria do ingrediente
- Exemplos: Grãos, Temperos, Laticínios, Óleos, Carnes, Verduras, etc.

#### 4. Unidade Padrão
- **Sólidos**: `g` (gramas)
- **Líquidos**: `ml` (mililitros)
- **Observação**: Líquidos podem ter descrições como "meia litro", "meia garrafa"

#### 5. Tempero Sensível
- **Valores**: `Sim` ou `Não`
- **Temperos sensíveis**: Pimenta, curcuma, açafrão, canela, noz-moscada, etc.
- **Uso**: Para exibir aviso especial na lista

#### 6. Aviso
- Mensagem personalizada para temperos sensíveis
- **Exemplo**: `⚠️ ATENÇÃO: Verifique se a quantidade está correta!`
- **Opcional**: Pode ser vazio (`-`) para ingredientes normais

---

## 🔧 Implementação no n8n

### Fluxo:

```
1. Webhook recebe inventário (texto ou foto)
   ↓
2. Se foto: Claude Vision (OCR)
   Se texto: Parse básico
   ↓
3. Ler Google Sheets (com cache de 30 minutos)
   ↓
4. Criar mapa de sinônimos:
   {
     "arroz": "Arroz branco",
     "arroz comum": "Arroz branco",
     "arroz branco": "Arroz branco",
     "pimenta": "Pimenta do reino",
     "pimenta preta": "Pimenta do reino",
     ...
   }
   ↓
5. Para cada ingrediente encontrado:
   a. Normalizar texto (remover acentos, minúsculas, plural)
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

### Normalização Básica (em código no n8n):

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
// "Pimentas" → "pimenta" → buscar "pimenta" no mapa
// "Pimenta do reino" → "pimenta do reino" → buscar no mapa
```

---

## 📝 Exemplos de Sinônimos

### Exemplo 1: Arroz branco
```
Nome Oficial: Arroz branco
Sinônimos: arroz, arroz comum, arroz branco, arroz branco comum
```

### Exemplo 2: Pimenta do reino
```
Nome Oficial: Pimenta do reino
Sinônimos: pimenta, pimenta preta, pimenta do reino, pimenta preta moída, pimenta preta em grão
```

### Exemplo 3: Açafrão
```
Nome Oficial: Açafrão
Sinônimos: açafrão, cúrcuma, curcuma, açafrão em pó, cúrcuma em pó
```

### Exemplo 4: Leite integral
```
Nome Oficial: Leite integral
Sinônimos: leite, leite integral, leite de vaca, leite comum
```

### Exemplo 5: Azeite de oliva
```
Nome Oficial: Azeite de oliva
Sinônimos: azeite, azeite de oliva, azeite extra virgem, azeite de oliva extra virgem
```

---

## ✅ Vantagens da Abordagem

1. **Time de operações autônomo**: Pode adicionar/editar sinônimos sem depender de dev
2. **Fácil de manter**: Alterações são imediatas (sem deploy)
3. **Colaborativo**: Várias pessoas podem editar simultaneamente
4. **Histórico**: Google Sheets mantém histórico de alterações
5. **Testável**: Pode testar novos sinônimos rapidamente
6. **Escalável**: 300 ingredientes é gerenciável
7. **Cacheável**: n8n pode cachear por 30 minutos (não precisa ler toda hora)

---

## 🎯 Resposta à Pergunta

### Sinônimos: Planilha ou Código?

**Resposta: Planilha** ✅

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

## 📋 Checklist de Implementação

### 1. Estrutura da Planilha
- [ ] Adicionar coluna "Sinônimos"
- [ ] Adicionar coluna "Tempero Sensível"
- [ ] Adicionar coluna "Aviso" (opcional)
- [ ] Popular sinônimos para todos os ingredientes
- [ ] Marcar temperos sensíveis

### 2. Configuração no n8n
- [ ] Conectar com Google Sheets
- [ ] Configurar cache (30 minutos)
- [ ] Implementar leitura da planilha
- [ ] Criar mapa de sinônimos
- [ ] Implementar normalização básica

### 3. Processamento
- [ ] Normalizar ingredientes usando sinônimos
- [ ] Identificar temperos sensíveis
- [ ] Normalizar unidades (sempre em gramas)
- [ ] Categorizar ingredientes
- [ ] Retornar inventário estruturado

### 4. Testes
- [ ] Testar normalização de sinônimos
- [ ] Testar normalização básica (plural, acentos)
- [ ] Testar identificação de temperos sensíveis
- [ ] Testar normalização de unidades
- [ ] Testar fluxo completo

---

## 💡 Dicas

### 1. Sinônimos Comuns
- Incluir variações com/sem acento
- Incluir plural/singular
- Incluir variações regionais
- Incluir nomes populares
- Incluir o próprio nome oficial

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

**Estrutura:**
- Coluna "Sinônimos" separados por vírgula
- Normalização básica em código (plural, acentos)
- Cache de 30 minutos
- Logs para identificar ingredientes não normalizados

Quer que eu detalhe alguma parte específica da implementação?

