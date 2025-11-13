# 🚀 Guia de Implementação - FASE 2A (Processar Inventário)

## 📋 Visão Geral

**FASE 2A - Processar Inventário:**
- Recebe inventário (texto ou foto)
- Processa com busca fuzzy + Claude (se necessário)
- Retorna JSON estruturado
- **NÃO salva no Notion**

---

## 🔧 Workflow n8n - Estrutura

### **1. Webhook - Recebe do Bot**
- **Nome**: `Webhook - Recebe do Bot`
- **Path**: `/fase2-processar`
- **Método**: POST
- **Response Mode**: `responseNode`
- **Response Node**: `Respond - Retorna pro Bot`

**Payload esperado:**
```json
{
  "notion_page_id": "abc123...",
  "inventario_texto": "300g arroz, 2 tomates, 500ml leite...",
  "foto_inventario_base64": "" // ou base64 se foto
}
```

---

### **2. Set - Extrai Variáveis**
- **Nome**: `Set - Extrai Variáveis`
- **Tipo**: Set

**Variáveis a extrair:**
- `notion_page_id`: `={{ $json.body.notion_page_id }}`
- `inventario_texto`: `={{ $json.body.inventario_texto }}`
- `foto_inventario_base64`: `={{ $json.body.foto_inventario_base64 }}`

---

### **3. Google Sheets - Ler Ingredientes**
- **Nome**: `Google Sheets - Ler Ingredientes`
- **Tipo**: Google Sheets
- **Ação**: Read
- **Document ID**: `1MoClw9F5N94APD7SwTLO3kR9iiiXIj9VmR8vPfBB-as`
- **Sheet Name**: `Lista de Ingredientes`

---

### **4. Code - Format Base Ingredientes**
- **Nome**: `Code - Format Base Ingredientes`
- **Tipo**: Code

**Código:**
```javascript
// Formatar base de ingredientes para uso no Claude
const baseIngredientes = $input.all().map(item => item.json);

// Criar JSON formatado da base
const baseJson = JSON.stringify(baseIngredientes, null, 2);

// Contar ingredientes
const totalIngredientes = baseIngredientes.length;

// Criar resumo das categorias
const categorias = [...new Set(baseIngredientes.map(i => i.Categoria || i.categoria || 'Sem categoria'))];

return {
  json: {
    base_ingredientes_json: baseJson,
    base_ingredientes: baseIngredientes,
    total_ingredientes: totalIngredientes,
    categorias: categorias,
    resumo: `Base carregada com ${totalIngredientes} ingredientes em ${categorias.length} categorias`
  }
};
```

---

### **5. IF - Tem Foto Inventário?**
- **Nome**: `IF - Tem Foto Inventário?`
- **Tipo**: IF

**Condição:**
- `foto_inventario_base64` não está vazio

**Caminhos:**
- **SIM (True)**: Vai para `Claude Vision - OCR Foto`
- **NÃO (False)**: Vai para `Set - Usa Texto Digitado`

---

### **6A. Claude Vision - OCR Foto** (se tiver foto)
- **Nome**: `Claude Vision - OCR Foto`
- **Tipo**: HTTP Request
- **Método**: POST
- **URL**: `https://api.anthropic.com/v1/messages`
- **Authentication**: Anthropic API

**Body:**
```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 2000,
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": "{{ $('Set - Extrai Variáveis').item.json.foto_inventario_base64 }}"
          }
        },
        {
          "type": "text",
          "text": "Extraia TODOS os ingredientes e quantidades visíveis nesta foto de inventário de cozinha. Liste no formato: 'ingrediente: quantidade'. Seja preciso nas quantidades e nomes dos ingredientes."
        }
      ]
    }
  ]
}
```

**Headers:**
- `anthropic-version`: `2023-06-01`
- `x-api-key`: `{{ $credentials.anthropicApi.key }}`

**Após OCR:**
- Conectar para `Code - Extrair Texto OCR`

---

### **6B. Set - Usa Texto Digitado** (se não tiver foto)
- **Nome**: `Set - Usa Texto Digitado`
- **Tipo**: Set

**Variáveis:**
- `inventario_extraido`: `={{ $('Set - Extrai Variáveis').first().json.inventario_texto }}`

**Após Set:**
- Conectar para `Code - Busca Fuzzy`

---

### **6C. Code - Extrair Texto OCR** (novo)
- **Nome**: `Code - Extrair Texto OCR`
- **Tipo**: Code

**Código:**
```javascript
// Extrair texto da resposta do Claude Vision
const claudeResponse = $input.item.json;

let inventarioTexto = '';

if (claudeResponse.content && claudeResponse.content[0]) {
  inventarioTexto = claudeResponse.content[0].text;
} else if (typeof claudeResponse === 'string') {
  inventarioTexto = claudeResponse;
}

return {
  json: {
    ...$input.item.json,
    inventario_extraido: inventarioTexto
  }
};
```

**Após Code:**
- Conectar para `Code - Busca Fuzzy`

---

### **7. Code - Busca Fuzzy** (NOVO)
- **Nome**: `Code - Busca Fuzzy`
- **Tipo**: Code

**Código:**
- Copiar código do arquivo `n8n_busca_fuzzy.js`
- Este código processa o inventário com busca fuzzy
- Retorna ingredientes processados e ingredientes que precisam de Claude

**Entrada:**
- `base_ingredientes`: `={{ $('Code - Format Base Ingredientes').first().json.base_ingredientes }}`
- `inventario_extraido`: `={{ $input.first().json.inventario_extraido }}`

**Saída:**
```json
{
  "ingredientes_processados": [...],
  "ingredientes_para_claude": [...],
  "metodos_usados": {
    "exato": 1,
    "fuzzy_alta": 2,
    "fuzzy_media": 0,
    "nao_encontrado": 1
  },
  "total_ingredientes": 4,
  "precisa_claude": true,
  "total_processados_fuzzy": 3,
  "total_para_claude": 1
}
```

---

### **8. IF - Precisa Claude?** (NOVO)
- **Nome**: `IF - Precisa Claude?`
- **Tipo**: IF

**Condição:**
- `precisa_claude` é `true`

**Caminhos:**
- **SIM (True)**: Vai para `Preparar Prompt`
- **NÃO (False)**: Vai para `Code - Combinar Resultados`

---

### **9. Preparar Prompt** (se precisar Claude)
- **Nome**: `Preparar Prompt`
- **Tipo**: Code

**Código:**
```javascript
const baseIngredientes = $('Code - Format Base Ingredientes').first().json.base_ingredientes_json;
const ingredientesParaClaude = $input.first().json.ingredientes_para_claude;

// Criar texto com ingredientes que precisam de Claude
const inventarioTexto = ingredientesParaClaude
  .map(item => `${item.nome_original}${item.quantidade ? `: ${item.quantidade}${item.unidade || ''}` : ''}`)
  .join(', ');

if (!baseIngredientes) {
  throw new Error('Base de ingredientes não encontrada');
}

if (!inventarioTexto) {
  throw new Error('Inventário não encontrado');
}

const promptText = `Você é um assistente especializado em normalizar inventários de cozinha.

BASE DE INGREDIENTES (com sinônimos, categorias e temperos sensíveis):
${baseIngredientes}

INVENTÁRIO DO CHEF (apenas ingredientes que não foram encontrados na base):
${inventarioTexto}

SUA TAREFA:
1. Identificar cada ingrediente na base de ingredientes (usar sinônimos)
2. Normalizar para o nome oficial da base
3. Extrair quantidade e unidade corretamente
4. Identificar se é tempero sensível
5. Categorizar ingrediente
6. Normalizar unidades (sempre g para sólidos, ml para líquidos)

REGRAS:
- Use APENAS nomes da base de ingredientes
- Se um ingrediente não estiver na base, use o nome mais próximo possível
- Se encontrar erros de digitação, corrija automaticamente
- Se encontrar variações (plural, acentos), normalize para o nome oficial
- Sempre use a categoria e unidade padrão da base
- Se for tempero sensível, marque como true

FORMATO DE RESPOSTA:
Retorne APENAS um JSON válido (sem markdown, sem explicações) no formato:

[
  {
    "nome": "Nome Oficial da Base",
    "quantidade": "500",
    "unidade": "g",
    "unidade_padrao": "g",
    "categoria": "Categoria da Base",
    "tempero_sensivel": false,
    "confianca": 0.95
  }
]

IMPORTANTE:
- Retorne APENAS o JSON, sem markdown, sem explicações
- Use nomes exatos da base de ingredientes
- Se não encontrar na base, use o nome mais próximo possível
- Marque temperos sensíveis corretamente
- Normalize unidades corretamente (g para sólidos, ml para líquidos)
- Use categorias da base (Grãos e Cereais, Temperos e Especiarias, Laticínios, etc.)`;

// Retornar o payload completo já formatado
return {
  json: {
    model: "claude-sonnet-4-20250514",
    max_tokens: 3000,
    messages: [
      {
        role: "user",
        content: promptText
      }
    ]
  }
};
```

**Após Code:**
- Conectar para `Claude - Normaliza Inventário`

---

### **10. Claude - Normaliza Inventário** (se precisar Claude)
- **Nome**: `Claude - Normaliza Inventário`
- **Tipo**: HTTP Request
- **Método**: POST
- **URL**: `https://api.anthropic.com/v1/messages`
- **Authentication**: Anthropic API

**Body:**
```json
={{ $json }}
```

**Headers:**
- `anthropic-version`: `2023-06-01`
- `x-api-key`: `{{ $credentials.anthropicApi.key }}`

**Após Claude:**
- Conectar para `Code - Parse Claude Response`

---

### **11. Code - Parse Claude Response** (NOVO)
- **Nome**: `Code - Parse Claude Response`
- **Tipo**: Code

**Código:**
```javascript
// Parse da resposta do Claude
const claudeResponse = $input.item.json;

// Extrair o JSON da resposta
let inventarioArray = [];

try {
  // Tentar parsear diretamente (novo formato)
  if (claudeResponse.content && claudeResponse.content[0]) {
    const texto = claudeResponse.content[0].text;
    
    // Remover markdown se existir
    const textoLimpo = texto.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
    
    inventarioArray = JSON.parse(textoLimpo);
  }
  // Fallback: formato antigo
  else if (typeof claudeResponse === 'string') {
    const textoLimpo = claudeResponse.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
    inventarioArray = JSON.parse(textoLimpo);
  }
} catch (error) {
  console.error('Erro ao parsear JSON:', error);
  inventarioArray = [];
}

// Adicionar método usado
inventarioArray = inventarioArray.map(item => ({
  ...item,
  metodo: 'claude',
  nome_original: item.nome_original || item.nome
}));

return {
  json: {
    ...$input.item.json,
    ingredientes_claude: inventarioArray
  }
};
```

**Após Code:**
- Conectar para `Code - Combinar Resultados`

---

### **12. Code - Combinar Resultados** (NOVO)
- **Nome**: `Code - Combinar Resultados`
- **Tipo**: Code

**Código:**
```javascript
// Combinar resultados do fuzzy e Claude
const ingredientesFuzzy = $('Code - Busca Fuzzy').first().json.ingredientes_processados || [];
const ingredientesClaude = $input.first().json.ingredientes_claude || [];

// Combinar arrays
const todosIngredientes = [...ingredientesFuzzy, ...ingredientesClaude];

// Identificar temperos sensíveis
const temperosSensiveis = todosIngredientes.filter(item => item.tempero_sensivel === true);
const temTemperoSensivel = temperosSensiveis.length > 0;

// Criar aviso para temperos sensíveis
let avisoTemperos = null;
if (temTemperoSensivel) {
  const nomesTemperos = temperosSensiveis.map(t => t.nome_oficial || t.nome).join(', ');
  avisoTemperos = `⚠️ ATENÇÃO: Verifique especialmente os temperos sensíveis: ${nomesTemperos}`;
}

// Criar visualização formatada
let inventarioVisualizacao = '';

if (todosIngredientes.length > 0) {
  // Agrupar por categoria
  const categorias = {};
  
  todosIngredientes.forEach(item => {
    const categoria = item.categoria || 'Sem categoria';
    if (!categorias[categoria]) {
      categorias[categoria] = [];
    }
    categorias[categoria].push(item);
  });
  
  // Criar visualização
  inventarioVisualizacao += `📦 INVENTÁRIO PROCESSADO\n\n`;
  
  // Adicionar aviso de temperos sensíveis no topo
  if (avisoTemperos) {
    inventarioVisualizacao += `${avisoTemperos}\n\n`;
    inventarioVisualizacao += `═══════════════════════════════════════\n\n`;
  }
  
  // Listar por categoria
  for (const [categoria, itens] of Object.entries(categorias)) {
    inventarioVisualizacao += `📂 ${categoria.toUpperCase()}\n`;
    inventarioVisualizacao += `${'─'.repeat(40)}\n`;
    
    itens.forEach(item => {
      const emoji = item.tempero_sensivel ? '⚠️ ' : '  ';
      const confianca = item.confianca ? ` (${Math.round(item.confianca * 100)}%)` : '';
      const nome = item.nome_oficial || item.nome || item.nome_original || '';
      const quantidade = item.quantidade || '';
      const unidade = item.unidade || item.unidade_padrao || '';
      inventarioVisualizacao += `${emoji}• ${nome}: ${quantidade}${unidade}${confianca}\n`;
    });
    
    inventarioVisualizacao += `\n`;
  }
  
  // Adicionar resumo
  inventarioVisualizacao += `\n═══════════════════════════════════════\n`;
  inventarioVisualizacao += `📊 RESUMO:\n`;
  inventarioVisualizacao += `   • Total de ingredientes: ${todosIngredientes.length}\n`;
  inventarioVisualizacao += `   • Categorias: ${Object.keys(categorias).length}\n`;
  inventarioVisualizacao += `   • Temperos sensíveis: ${temperosSensiveis.length}\n`;
  
} else {
  inventarioVisualizacao = '❌ Nenhum ingrediente processado';
}

// Obter métodos usados
const metodosUsados = $('Code - Busca Fuzzy').first().json.metodos_usados || {};
if (ingredientesClaude.length > 0) {
  metodosUsados.claude = ingredientesClaude.length;
}

// Retornar resultado
return {
  json: {
    ...$input.item.json,
    inventario_estruturado: todosIngredientes,
    inventario_json: JSON.stringify(todosIngredientes, null, 2),
    inventario_visualizacao: inventarioVisualizacao,
    temperos_sensiveis: temperosSensiveis,
    tem_tempero_sensivel: temTemperoSensivel,
    aviso_temperos: avisoTemperos,
    total_ingredientes: todosIngredientes.length,
    total_temperos_sensiveis: temperosSensiveis.length,
    metodos_usados: metodosUsados
  }
};
```

**Após Code:**
- Conectar para `Respond - Retorna pro Bot`

---

### **13. Respond - Retorna pro Bot**
- **Nome**: `Respond - Retorna pro Bot`
- **Tipo**: Respond to Webhook
- **Response Mode**: `json`

**Response Body:**
```json
{
  "success": true,
  "inventario_estruturado": "{{ $('Code - Combinar Resultados').item.json.inventario_estruturado }}",
  "inventario_json": "{{ $('Code - Combinar Resultados').item.json.inventario_json }}",
  "inventario_visualizacao": "{{ $('Code - Combinar Resultados').item.json.inventario_visualizacao }}",
  "temperos_sensiveis": "{{ $('Code - Combinar Resultados').item.json.temperos_sensiveis }}",
  "total_ingredientes": "{{ $('Code - Combinar Resultados').item.json.total_ingredientes }}",
  "total_temperos_sensiveis": "{{ $('Code - Combinar Resultados').item.json.total_temperos_sensiveis }}",
  "metodos_usados": "{{ $('Code - Combinar Resultados').item.json.metodos_usados }}"
}
```

---

## 🔗 Conexões do Workflow

```
Webhook - Recebe do Bot
  ↓
Set - Extrai Variáveis
  ↓
Google Sheets - Ler Ingredientes
  ↓
Code - Format Base Ingredientes
  ↓
IF - Tem Foto Inventário?
  ├─ SIM → Claude Vision - OCR Foto → Code - Extrair Texto OCR → Code - Busca Fuzzy
  └─ NÃO → Set - Usa Texto Digitado → Code - Busca Fuzzy
  ↓
IF - Precisa Claude?
  ├─ SIM → Preparar Prompt → Claude - Normaliza Inventário → Code - Parse Claude Response → Code - Combinar Resultados
  └─ NÃO → Code - Combinar Resultados
  ↓
Respond - Retorna pro Bot
```

---

## ✅ Próximos Passos

1. **Criar workflow no n8n** seguindo esta estrutura
2. **Configurar webhook** com path `/fase2-processar`
3. **Testar workflow** com inventário de teste
4. **Validar resposta** retornada ao bot

---

## 📝 Notas Importantes

- **Webhook deve ter `responseMode: "responseNode"`** e apontar para `Respond - Retorna pro Bot`
- **Código de busca fuzzy** deve ser copiado do arquivo `n8n_busca_fuzzy.js`
- **Claude só é chamado** se houver ingredientes com confiança < 0.7
- **Resposta deve incluir** `inventario_estruturado`, `inventario_visualizacao`, e `metodos_usados`

---

Quer que eu crie o workflow JSON completo? 🚀

