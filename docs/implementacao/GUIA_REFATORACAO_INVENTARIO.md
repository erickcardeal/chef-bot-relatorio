# 🔄 Guia de Refatoração - Sistema de Inventário (Fase 2A)

## 📋 Contexto

Estamos **simplificando radicalmente** o sistema de processamento de inventário para criar um MVP funcional e transparente. A versão atual com fuzzy match está muito complexa e sensível a erros (ex: "sal" → "salmão", "arroz" → "vinagre de arroz").

### Decisão estratégica:
- ❌ **Antes:** Tentar "adivinhar" o que o chef quis dizer (fuzzy match complexo)
- ✅ **Agora:** Parse simples + validação do chef antes de salvar

---

## 🎯 Objetivo Final

Criar um fluxo onde:
1. Chef digita inventário em texto livre
2. Sistema faz parse simples (nome, quantidade, unidade)
3. Sistema **valida temperos sensíveis** (crítico para operação!)
4. Bot mostra visualização formatada pro chef
5. Chef confirma: ✅ Sim / ❌ Corrigir
6. Só depois salva no Notion

---

## 🗑️ O que REMOVER do workflow atual

### Nodes para deletar:
1. ❌ `Google Sheets - Ler Ingredientes`
2. ❌ `Code - Format Base Ingredientes`
3. ❌ `Code - Busca Fuzzy`
4. ❌ `IF - Precisa Claude?`
5. ❌ `Preparar Prompt`
6. ❌ `Claude - Normaliza Inventário`
7. ❌ `Code - Parse Claude Response`
8. ❌ `Code - Combinar Resultados`

### Nodes para MANTER:
1. ✅ `Webhook - Recebe do Bot`
2. ✅ `Code - Payload de Teste`
3. ✅ `Set - Extrai Variáveis`
4. ✅ `Set - Usa Texto Digitado`
5. ✅ `Respond - Retorna pro Bot`

---

## ➕ O que ADICIONAR ao workflow

### Node novo: `Code - Processar Inventário`

**Posição:** Entre `Set - Usa Texto Digitado` e `Respond - Retorna pro Bot`

**Função:** 
- Parse simples do texto
- Validação de temperos sensíveis
- Formatação da visualização

---

## 📝 Código Completo do Node

### `Code - Processar Inventário`

```javascript
// ===== CODE - PROCESSAR INVENTÁRIO (VERSÃO SIMPLES) =====
// Objetivo: Parse simples + validação de temperos sensíveis + visualização

const inventarioTexto = $input.first().json.inventario_extraido || '';

if (!inventarioTexto || typeof inventarioTexto !== 'string') {
  return {
    json: {
      success: false,
      erro: 'Inventário não encontrado ou vazio'
    }
  };
}

console.log('📦 Inventário recebido:', inventarioTexto);

// ===== LISTA DE TEMPEROS SENSÍVEIS =====
// Temperos que SEMPRE devem ser revisados pelo chef
const temperosSensiveis = [
  'pimenta do reino',
  'pimenta',
  'açafrão',
  'açafrão da terra',
  'cúrcuma',
  'canela',
  'páprica',
  'cominho',
  'curry',
  'noz-moscada',
  'pimenta caiena',
  'pimenta de cheiro',
  'pimenta dedo de moça',
  'pimentão',
  'zatar',
  'pimenta verde'
];

// ===== FUNÇÃO: Normalizar texto para comparação =====
function normalizarTexto(texto) {
  if (!texto) return '';
  return texto
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove acentos
    .toLowerCase()
    .trim();
}

// ===== FUNÇÃO: Verificar se ingrediente é tempero sensível =====
function ehTemperoSensivel(nomeIngrediente) {
  const nomeNormalizado = normalizarTexto(nomeIngrediente);
  
  for (const tempero of temperosSensiveis) {
    const temperoNormalizado = normalizarTexto(tempero);
    if (nomeNormalizado.includes(temperoNormalizado)) {
      return true;
    }
  }
  return false;
}

// ===== PARSE SIMPLES =====
const ingredientes = inventarioTexto
  .split(/[,\n;]/) // Separa por vírgula, quebra de linha ou ponto-e-vírgula
  .map(item => item.trim())
  .filter(item => item.length > 0)
  .map(ingredienteTexto => {
    // Extrair nome, quantidade e unidade
    let nome = ingredienteTexto;
    let quantidade = '';
    let unidade = '';

    // Tentar com dois-pontos: "ingrediente: quantidade unidade"
    const matchComDoisPontos = ingredienteTexto.match(/^(.+?)\s*:\s*(\d+(?:[.,]\d+)?)\s*(g|kg|ml|l|litros?|unidade|unidades|un|pct|pacote|pacotes|unid|cabeça|cabeças|maço|maços)?$/i);
    
    if (matchComDoisPontos) {
      nome = matchComDoisPontos[1].trim();
      quantidade = matchComDoisPontos[2].replace(',', '.');
      unidade = (matchComDoisPontos[3] || 'unidade').toLowerCase();
    } else {
      // Tentar sem dois-pontos: "ingrediente quantidade unidade"
      const matchSemDoisPontos = ingredienteTexto.match(/^(.+?)\s+(\d+(?:[.,]\d+)?)\s*(g|kg|ml|l|litros?|unidade|unidades|un|pct|pacote|pacotes|unid|cabeça|cabeças|maço|maços)?$/i);
      if (matchSemDoisPontos) {
        nome = matchSemDoisPontos[1].trim();
        quantidade = matchSemDoisPontos[2].replace(',', '.');
        unidade = (matchSemDoisPontos[3] || 'unidade').toLowerCase();
      }
    }

    // Normalizar unidades comuns
    const unidadesMap = {
      'un': 'unidade',
      'unid': 'unidade',
      'unidades': 'unidade',
      'pct': 'pacote',
      'pacotes': 'pacote',
      'litros': 'l',
      'litro': 'l',
      'maços': 'maço',
      'cabeças': 'cabeça'
    };
    
    unidade = unidadesMap[unidade] || unidade;

    // Verificar se é tempero sensível
    const isTemperoSensivel = ehTemperoSensivel(nome);

    return {
      nome_original: ingredienteTexto,
      nome: nome,
      quantidade: quantidade,
      unidade: unidade,
      tempero_sensivel: isTemperoSensivel
    };
  });

console.log('📋 Total de ingredientes parseados:', ingredientes.length);

// ===== ANÁLISE DE TEMPEROS SENSÍVEIS =====
const temperosSensiveisEncontrados = ingredientes.filter(item => item.tempero_sensivel);
const totalTemperos = temperosSensiveisEncontrados.length;

console.log('⚠️ Temperos sensíveis encontrados:', totalTemperos);

// ===== VALIDAÇÃO DE TEMPEROS =====
let avisoTemperos = null;
let precisaRevisaoTemperos = false;

if (totalTemperos === 0) {
  avisoTemperos = '⚠️ ATENÇÃO: Nenhum tempero sensível foi encontrado no inventário!\n\n🔍 Revise se você incluiu:\n• Pimenta do reino\n• Páprica\n• Cominho\n• Curry\n• Canela\n• Açafrão/Cúrcuma\n• Outros temperos usados\n\n❓ Confirma que NÃO usou temperos sensíveis?';
  precisaRevisaoTemperos = true;
} else if (totalTemperos === 1) {
  avisoTemperos = `⚠️ ATENÇÃO: Apenas 1 tempero sensível encontrado!\n\nEncontrado: ${temperosSensiveisEncontrados[0].nome}\n\n🔍 Revise se você incluiu todos os temperos usados.\n\n❓ Confirma que usou APENAS esse tempero?`;
  precisaRevisaoTemperos = true;
} else if (totalTemperos === 2) {
  const nomesTemperos = temperosSensiveisEncontrados.map(t => t.nome).join(', ');
  avisoTemperos = `⚠️ ATENÇÃO: Apenas 2 temperos sensíveis encontrados!\n\nEncontrados: ${nomesTemperos}\n\n🔍 Revise se você incluiu todos os temperos usados.\n\n❓ Confirma que são APENAS esses temperos?`;
  precisaRevisaoTemperos = true;
}

// ===== FORMATAR VISUALIZAÇÃO =====
let inventarioVisualizacao = '';

inventarioVisualizacao += '📦 INVENTÁRIO PROCESSADO\n';
inventarioVisualizacao += '═════════════════════════════\n\n';

// Agrupar por tipo (temperos sensíveis primeiro)
const temperos = ingredientes.filter(item => item.tempero_sensivel);
const normais = ingredientes.filter(item => !item.tempero_sensivel);

if (temperos.length > 0) {
  inventarioVisualizacao += '⚠️ TEMPEROS SENSÍVEIS:\n';
  temperos.forEach((item, index) => {
    inventarioVisualizacao += `   ${index + 1}. ${item.nome}`;
    if (item.quantidade) {
      inventarioVisualizacao += `: ${item.quantidade}${item.unidade}`;
    }
    inventarioVisualizacao += '\n';
  });
  inventarioVisualizacao += '\n';
}

if (normais.length > 0) {
  inventarioVisualizacao += '📋 INGREDIENTES GERAIS:\n';
  normais.forEach((item, index) => {
    inventarioVisualizacao += `   ${index + 1}. ${item.nome}`;
    if (item.quantidade) {
      inventarioVisualizacao += `: ${item.quantidade}${item.unidade}`;
    }
    inventarioVisualizacao += '\n';
  });
}

inventarioVisualizacao += '\n═════════════════════════════\n';
inventarioVisualizacao += `📊 TOTAL: ${ingredientes.length} ingredientes\n`;
inventarioVisualizacao += `⚠️ TEMPEROS SENSÍVEIS: ${totalTemperos}\n\n`;

// Adicionar aviso de temperos se necessário
if (avisoTemperos) {
  inventarioVisualizacao += avisoTemperos + '\n\n';
}

inventarioVisualizacao += '✅ Confirma que está correto?\n';
inventarioVisualizacao += '✅ Sim → Tudo certo!\n';
inventarioVisualizacao += '❌ Não → Me manda corrigido';

// ===== RETORNAR RESULTADO =====
return {
  json: {
    success: true,
    inventario_estruturado: ingredientes,
    inventario_visualizacao: inventarioVisualizacao,
    total_ingredientes: ingredientes.length,
    temperos_sensiveis: temperosSensiveisEncontrados,
    total_temperos_sensiveis: totalTemperos,
    precisa_revisao_temperos: precisaRevisaoTemperos,
    aviso_temperos: avisoTemperos,
    metodo: 'parse_simples',
    precisa_validacao: true
  }
};
```

---

## 🎯 Lógica de Validação de Temperos

### Regras implementadas:

1. **0 temperos sensíveis:**
   - ⚠️ Alerta CRÍTICO
   - Lista temperos comuns que deveriam estar
   - Pergunta: "Confirma que NÃO usou temperos?"

2. **1 tempero sensível:**
   - ⚠️ Alerta MODERADO
   - Mostra qual tempero foi encontrado
   - Pergunta: "Confirma que usou APENAS esse?"

3. **2 temperos sensíveis:**
   - ⚠️ Alerta LEVE
   - Mostra quais temperos foram encontrados
   - Pergunta: "Confirma que são APENAS esses?"

4. **3+ temperos sensíveis:**
   - ✅ Nenhum alerta
   - Considerado normal para uma visita

---

## 📊 Exemplo de Output

### Input do chef:
```
arroz: 500g, feijão preto: 300g, tomate: 5 unidades, sal: 500g
```

### Output do sistema:
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
      "nome_original": "feijão preto: 300g",
      "nome": "feijão preto",
      "quantidade": "300",
      "unidade": "g",
      "tempero_sensivel": false
    },
    {
      "nome_original": "tomate: 5 unidades",
      "nome": "tomate",
      "quantidade": "5",
      "unidade": "unidade",
      "tempero_sensivel": false
    },
    {
      "nome_original": "sal: 500g",
      "nome": "sal",
      "quantidade": "500",
      "unidade": "g",
      "tempero_sensivel": false
    }
  ],
  "temperos_sensiveis": [],
  "total_temperos_sensiveis": 0,
  "precisa_revisao_temperos": true,
  "aviso_temperos": "⚠️ ATENÇÃO: Nenhum tempero sensível foi encontrado...",
  "total_ingredientes": 4
}
```

### Visualização pro chef:
```
📦 INVENTÁRIO PROCESSADO
═════════════════════════════

📋 INGREDIENTES GERAIS:
   1. arroz: 500g
   2. feijão preto: 300g
   3. tomate: 5 unidade
   4. sal: 500g

═════════════════════════════
📊 TOTAL: 4 ingredientes
⚠️ TEMPEROS SENSÍVEIS: 0

⚠️ ATENÇÃO: Nenhum tempero sensível foi encontrado no inventário!

🔍 Revise se você incluiu:
• Pimenta do reino
• Páprica
• Cominho
• Curry
• Canela
• Açafrão/Cúrcuma
• Outros temperos usados

❓ Confirma que NÃO usou temperos sensíveis?

✅ Confirma que está correto?
✅ Sim → Tudo certo!
❌ Não → Me manda corrigido
```

---

## 🔄 Fluxo Completo do Workflow

```
1. Webhook - Recebe do Bot
   ↓
2. Code - Payload de Teste
   ↓
3. Set - Extrai Variáveis
   ↓
4. Set - Usa Texto Digitado
   ↓
5. Code - Processar Inventário (NOVO!)
   ↓
6. Respond - Retorna pro Bot
```

---

## ✅ Checklist de Implementação

- [ ] Deletar nodes antigos (fuzzy match, Google Sheets, Claude API, etc)
- [ ] Adicionar node `Code - Processar Inventário`
- [ ] Colar código completo no node
- [ ] Conectar node entre `Set - Usa Texto Digitado` e `Respond`
- [ ] Testar com cenário `'completo'`
- [ ] Testar com cenário `'temperos_sensiveis'`
- [ ] Testar com cenário sem temperos (deve gerar alerta)
- [ ] Testar com cenário com apenas 1 tempero (deve gerar alerta)
- [ ] Validar formato do output
- [ ] Verificar se logs aparecem no console

---

## 🎯 Próximos Passos (Fase 2B)

Depois que essa Fase 2A estiver funcionando:

1. **Bot aguarda confirmação do chef:**
   - ✅ Chef clica "Sim" → Chama Fase 2B
   - ❌ Chef clica "Não" → Pede correção

2. **Fase 2B - Salvar no Notion:**
   - Recebe inventário validado
   - PATCH na página do Notion
   - Atualiza campos:
     - `Inventário (JSON)`
     - `Inventário (Texto)`
     - `Total Ingredientes`
     - `Temperos Sensíveis (JSON)`
     - `Total Temperos Sensíveis`
     - `Status` → "Validado pelo Chef"
     - `Data Validação`

---

## 📈 Benefícios desta Abordagem

### Imediatos:
- ✅ **Simplicidade:** 1 node ao invés de 8
- ✅ **Transparência:** Chef vê exatamente o que será salvo
- ✅ **Segurança:** Validação obrigatória de temperos
- ✅ **Confiabilidade:** Sem "adivinhações" do sistema
- ✅ **Performance:** Sem chamadas de API externas

### Futuros:
- ✅ **Aprendizado:** Dados reais de como chefs digitam
- ✅ **Melhoria contínua:** Padrões identificados com dados reais
- ✅ **Base para IA:** Depois adiciona inteligência com contexto real

---

## 🚨 Pontos de Atenção

### Temperos sensíveis são CRÍTICOS porque:
- ❌ Geram problemas recorrentes na operação
- ❌ Clientes reclamam quando usados incorretamente
- ❌ Podem causar problemas de saúde (alergias)
- ❌ Afetam diretamente a qualidade percebida

### Por isso:
- ✅ SEMPRE validar se foram incluídos
- ✅ SEMPRE alertar quando faltarem
- ✅ SEMPRE pedir confirmação explícita

---

## 📞 Suporte

Qualquer dúvida durante implementação:
1. Verifique os logs do console no n8n
2. Teste com cenários simples primeiro
3. Valide o output JSON antes de conectar ao bot

---

**Versão:** 1.0
**Data:** 2025-11-13
**Autor:** Claude + Erick
