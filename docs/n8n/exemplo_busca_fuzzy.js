// Exemplo de busca fuzzy para n8n (Function Node)
// Este código pode ser usado no n8n para encontrar ingredientes mesmo com erros de digitação

/**
 * Normalizar texto (remover acentos, minúsculas, plural)
 */
function normalizarTexto(texto) {
  if (!texto) return '';
  
  // Remover acentos
  texto = texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  
  // Converter para minúsculas
  texto = texto.toLowerCase().trim();
  
  // Remover espaços extras
  texto = texto.replace(/\s+/g, ' ');
  
  // Remover plural comum (s, es, ões)
  texto = texto.replace(/(s|es|ões)$/, '');
  
  return texto;
}

/**
 * Calcular similaridade entre duas strings (Jaro-Winkler)
 */
function jaroWinkler(str1, str2) {
  if (str1 === str2) return 1.0;
  
  const len1 = str1.length;
  const len2 = str2.length;
  
  if (len1 === 0 || len2 === 0) return 0.0;
  
  const matchWindow = Math.floor(Math.max(len1, len2) / 2) - 1;
  const str1Matches = new Array(len1).fill(false);
  const str2Matches = new Array(len2).fill(false);
  
  let matches = 0;
  let transpositions = 0;
  
  // Encontrar matches
  for (let i = 0; i < len1; i++) {
    const start = Math.max(0, i - matchWindow);
    const end = Math.min(i + matchWindow + 1, len2);
    
    for (let j = start; j < end; j++) {
      if (str2Matches[j] || str1[i] !== str2[j]) continue;
      str1Matches[i] = true;
      str2Matches[j] = true;
      matches++;
      break;
    }
  }
  
  if (matches === 0) return 0.0;
  
  // Encontrar transposições
  let k = 0;
  for (let i = 0; i < len1; i++) {
    if (!str1Matches[i]) continue;
    while (!str2Matches[k]) k++;
    if (str1[i] !== str2[k]) transpositions++;
    k++;
  }
  
  // Calcular Jaro
  const jaro = (matches / len1 + matches / len2 + (matches - transpositions / 2) / matches) / 3.0;
  
  // Calcular Winkler (prefixo comum)
  let prefix = 0;
  const maxPrefix = Math.min(4, Math.min(len1, len2));
  for (let i = 0; i < maxPrefix; i++) {
    if (str1[i] === str2[i]) prefix++;
    else break;
  }
  
  // Jaro-Winkler
  const winkler = jaro + (prefix * 0.1 * (1 - jaro));
  
  return winkler;
}

/**
 * Buscar ingrediente similar na base
 */
function encontrarIngredienteSimilar(nome, baseIngredientes, threshold = 0.8) {
  let melhorMatch = null;
  let melhorSimilaridade = 0;
  let melhorSinonimo = null;
  
  const nomeNormalizado = normalizarTexto(nome);
  
  // Buscar em cada ingrediente
  for (const ingrediente of baseIngredientes) {
    // Buscar no nome oficial
    const nomeOficialNormalizado = normalizarTexto(ingrediente['Ingrediente']);
    const similaridadeNome = jaroWinkler(nomeNormalizado, nomeOficialNormalizado);
    
    if (similaridadeNome > melhorSimilaridade && similaridadeNome >= threshold) {
      melhorSimilaridade = similaridadeNome;
      melhorMatch = ingrediente;
      melhorSinonimo = ingrediente['Ingrediente'];
    }
    
    // Buscar nos sinônimos
    if (ingrediente['Sinônimos']) {
      const sinonimos = ingrediente['Sinônimos'].split(',').map(s => s.trim());
      
      for (const sinonimo of sinonimos) {
        const sinonimoNormalizado = normalizarTexto(sinonimo);
        const similaridadeSinonimo = jaroWinkler(nomeNormalizado, sinonimoNormalizado);
        
        if (similaridadeSinonimo > melhorSimilaridade && similaridadeSinonimo >= threshold) {
          melhorSimilaridade = similaridadeSinonimo;
          melhorMatch = ingrediente;
          melhorSinonimo = sinonimo;
        }
      }
    }
  }
  
  if (melhorMatch) {
    return {
      ingrediente: melhorMatch,
      similaridade: melhorSimilaridade,
      sinonimo: melhorSinonimo,
      nome_oficial: melhorMatch['Ingrediente']
    };
  }
  
  return null;
}

/**
 * Processar ingrediente do chef
 */
function processarIngrediente(nomeChef, baseIngredientes) {
  // 1. Normalizar texto do chef
  const nomeNormalizado = normalizarTexto(nomeChef);
  
  // 2. Buscar match exato (primeiro nos sinônimos)
  for (const ingrediente of baseIngredientes) {
    if (ingrediente['Sinônimos']) {
      const sinonimos = ingrediente['Sinônimos'].split(',').map(s => s.trim().toLowerCase());
      const nomeOficialNormalizado = normalizarTexto(ingrediente['Ingrediente']);
      
      // Verificar se está nos sinônimos ou no nome oficial
      if (sinonimos.includes(nomeNormalizado) || nomeOficialNormalizado === nomeNormalizado) {
        return {
          nome_oficial: ingrediente['Ingrediente'],
          confianca: 1.0,
          metodo: 'exato',
          categoria: ingrediente['Categoria'],
          unidade_padrao: ingrediente['Unidade Padrão'],
          tempero_sensivel: ingrediente['Tempero Sensível'],
          aviso: ingrediente['Aviso']
        };
      }
    }
  }
  
  // 3. Busca fuzzy (similaridade)
  const matchFuzzy = encontrarIngredienteSimilar(nomeChef, baseIngredientes, 0.7);
  
  if (matchFuzzy) {
    if (matchFuzzy.similaridade >= 0.9) {
      // Confiança alta: usa direto
      return {
        nome_oficial: matchFuzzy.nome_oficial,
        confianca: matchFuzzy.similaridade,
        metodo: 'fuzzy_alta',
        correcao: `${nomeChef} → ${matchFuzzy.nome_oficial}`,
        categoria: matchFuzzy.ingrediente['Categoria'],
        unidade_padrao: matchFuzzy.ingrediente['Unidade Padrão'],
        tempero_sensivel: matchFuzzy.ingrediente['Tempero Sensível'],
        aviso: matchFuzzy.ingrediente['Aviso']
      };
    } else if (matchFuzzy.similaridade >= 0.7) {
      // Confiança média: marca para revisão
      return {
        nome_oficial: matchFuzzy.nome_oficial,
        confianca: matchFuzzy.similaridade,
        metodo: 'fuzzy_media',
        correcao: `${nomeChef} → ${matchFuzzy.nome_oficial}`,
        precisa_revisao: true,
        categoria: matchFuzzy.ingrediente['Categoria'],
        unidade_padrao: matchFuzzy.ingrediente['Unidade Padrão'],
        tempero_sensivel: matchFuzzy.ingrediente['Tempero Sensível'],
        aviso: matchFuzzy.ingrediente['Aviso']
      };
    }
  }
  
  // 4. Não encontrou: retorna original (será processado por Claude)
  return {
    nome_oficial: nomeChef,
    confianca: 0.5,
    metodo: 'nao_encontrado',
    precisa_claude: true
  };
}

// Exemplo de uso no n8n
// const baseIngredientes = $input.all(); // Dados do Google Sheets
// const ingredienteChef = $input.item.json.ingrediente; // Ingrediente do chef
// const resultado = processarIngrediente(ingredienteChef, baseIngredientes);
// return resultado;

// Exemplos de teste
console.log('=== TESTES DE BUSCA FUZZY ===\n');

// Teste 1: Erro de digitação simples
console.log('Teste 1: "aroz branco"');
const resultado1 = processarIngrediente('aroz branco', [
  {
    'Ingrediente': 'Arroz - Branco',
    'Sinônimos': 'arroz - branco, arroz branco, branco',
    'Categoria': 'Grãos e Cereais',
    'Unidade Padrão': 'g',
    'Tempero Sensível': 'Não',
    'Aviso': '-'
  }
]);
console.log('Resultado:', resultado1);
console.log('');

// Teste 2: Erro de acento
console.log('Teste 2: "acafrao"');
const resultado2 = processarIngrediente('acafrao', [
  {
    'Ingrediente': 'Açafrão da terra/cúrcuma em pó',
    'Sinônimos': 'açafrão da terra, açafrão da terra/cúrcuma em pó, cúrcuma em pó',
    'Categoria': 'Temperos e Especiarias',
    'Unidade Padrão': 'g',
    'Tempero Sensível': 'Sim',
    'Aviso': '⚠️ ATENÇÃO: Verifique se a quantidade está correta!'
  }
]);
console.log('Resultado:', resultado2);
console.log('');

// Teste 3: Erro de espaço
console.log('Teste 3: "pimenta  do  reino"');
const resultado3 = processarIngrediente('pimenta  do  reino', [
  {
    'Ingrediente': 'Pimenta do Reino em Grãos',
    'Sinônimos': 'pimenta, pimenta do reino, pimenta do reino em grãos',
    'Categoria': 'Temperos e Especiarias',
    'Unidade Padrão': 'g',
    'Tempero Sensível': 'Sim',
    'Aviso': '⚠️ ATENÇÃO: Verifique se a quantidade está correta!'
  }
]);
console.log('Resultado:', resultado3);
console.log('');

// Teste 4: Match exato
console.log('Teste 4: "arroz branco"');
const resultado4 = processarIngrediente('arroz branco', [
  {
    'Ingrediente': 'Arroz - Branco',
    'Sinônimos': 'arroz - branco, arroz branco, branco',
    'Categoria': 'Grãos e Cereais',
    'Unidade Padrão': 'g',
    'Tempero Sensível': 'Não',
    'Aviso': '-'
  }
]);
console.log('Resultado:', resultado4);
console.log('');

// Teste 5: Não encontrado
console.log('Teste 5: "ingrediente inexistente"');
const resultado5 = processarIngrediente('ingrediente inexistente', [
  {
    'Ingrediente': 'Arroz - Branco',
    'Sinônimos': 'arroz - branco, arroz branco, branco',
    'Categoria': 'Grãos e Cereais',
    'Unidade Padrão': 'g',
    'Tempero Sensível': 'Não',
    'Aviso': '-'
  }
]);
console.log('Resultado:', resultado5);
console.log('');

