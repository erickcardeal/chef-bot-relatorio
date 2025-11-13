# 🧪 Guia de Teste - FASE 2A (n8n)

## 📋 Visão Geral

Este workflow permite testar o processamento de inventário **sem precisar rodar o bot**. Você pode testar diferentes cenários diretamente no n8n usando payloads de teste.

## 🚀 Como Usar

### 1. Importar o Workflow

1. Abra o n8n
2. Vá em **Workflows** → **Import from File**
3. Selecione o arquivo: `Relatório de Visita - Fase 2A - Processar (COM TESTE).json`
4. O workflow será importado

### 2. Configurar o Modo de Teste

1. Abra o nó **"Code - Payload de Teste"**
2. Edite as variáveis no início do código:

```javascript
const MODO_TESTE = true; // true = usa dados de teste, false = usa dados do webhook
const CENARIO_TESTE = 'completo'; // Escolha o cenário de teste
```

### 3. Cenários de Teste Disponíveis

#### 📦 `simples`
**Inventário simples (tudo encontrado na base)**
```
arroz: 500g, feijão: 300g, macarrão: 250g, leite: 500ml, azeite: 200ml
```
**O que testa:** Busca exata na base de ingredientes

---

#### ❌ `com_erros`
**Inventário com erros de digitação**
```
aroz: 500g, feijao: 300g, macarrao: 250g, leite integral: 500ml, azeite de oliva: 200ml, acucar: 1kg
```
**O que testa:** Busca fuzzy (correção automática de erros)

---

#### ⚠️ `temperos_sensiveis`
**Inventário com temperos sensíveis**
```
arroz: 500g, pimenta do reino: 50g, açafrão da terra: 30g, canela: 25g, páprica: 40g, cominho: 20g
```
**O que testa:** Identificação de temperos sensíveis

---

#### 📋 `completo`
**Inventário completo (múltiplas categorias, erros, temperos)**
```
arroz: 500g, feijão preto: 300g, macarrão espaguete: 250g, leite integral: 500ml, azeite de oliva: 200ml, açúcar: 1kg, sal: 500g, pimenta do reino: 50g, açafrão da terra: 30g, canela em pó: 25g, páprica doce: 40g, cominho: 20g, curry: 35g, tomate: 5 unidades, cebola: 3 unidades, alho: 1 cabeça, limão: 4 unidades
```
**O que testa:** Processamento completo com todos os recursos

---

#### 🔍 `ingredientes_desconhecidos`
**Inventário com ingredientes não encontrados**
```
arroz: 500g, tempero especial da casa: 100g, mistura de especiarias: 50g, molho secreto: 200ml
```
**O que testa:** Processamento com Claude (ingredientes não encontrados na base)

---

#### 📝 `formatacao_inconsistente`
**Inventário com formatação inconsistente**
```
arroz 500g; feijão, 300g. macarrão:250g leite 500ml azeite:200ml
```
**O que testa:** Parse de diferentes formatos de entrada

---

#### 🚫 `vazio`
**Inventário vazio**
```
(empty)
```
**O que testa:** Tratamento de erro (inventário vazio)

---

## 🧪 Executar Teste

### Método 1: Executar Workflow Manualmente

1. Certifique-se de que `MODO_TESTE = true`
2. Escolha o cenário de teste (`CENARIO_TESTE = 'completo'`)
3. Clique em **"Execute Workflow"** (botão de play)
4. O workflow será executado com os dados de teste
5. Verifique o resultado no nó **"Respond - Retorna pro Bot"**

### Método 2: Executar Apenas um Nó

1. Clique com o botão direito no nó **"Code - Payload de Teste"**
2. Selecione **"Execute Node"**
3. O nó será executado e você verá o payload de teste gerado
4. Continue executando os próximos nós manualmente

---

## 📊 Verificar Resultados

### 1. Verificar Payload de Teste

**Nó:** `Code - Payload de Teste`
- Verifique se o payload foi gerado corretamente
- Confirme que `modo_teste = true`
- Confirme que `cenario_teste` está correto

### 2. Verificar Busca Fuzzy

**Nó:** `Code - Busca Fuzzy`
- Verifique `ingredientes_processados` (encontrados via fuzzy)
- Verifique `ingredientes_para_claude` (não encontrados)
- Verifique `metodos_usados` (exato, fuzzy_alta, fuzzy_media, nao_encontrado)

### 3. Verificar Processamento Claude (se necessário)

**Nó:** `Code - Parse Claude Response`
- Verifique se o Claude processou os ingredientes não encontrados
- Verifique se os ingredientes foram normalizados corretamente

### 4. Verificar Resultado Final

**Nó:** `Code - Combinar Resultados`
- Verifique `inventario_estruturado` (array com todos os ingredientes)
- Verifique `inventario_visualizacao` (texto formatado para o chef)
- Verifique `temperos_sensiveis` (array com temperos sensíveis)
- Verifique `metodos_usados` (resumo dos métodos utilizados)

### 5. Verificar Resposta

**Nó:** `Respond - Retorna pro Bot`
- Verifique se a resposta JSON está correta
- Verifique se `success = true`
- Verifique se todos os campos estão presentes

---

## 🔄 Modo Produção

Para usar em produção (com dados do bot):

1. Abra o nó **"Code - Payload de Teste"**
2. Altere `MODO_TESTE = false`
3. O workflow agora usará os dados do webhook (`Webhook - Recebe do Bot`)

---

## 🎯 Dicas de Teste

### 1. Testar Diferentes Cenários

Teste todos os cenários disponíveis para garantir que o workflow funciona em diferentes situações:

```javascript
// Teste 1: Inventário simples
CENARIO_TESTE = 'simples'

// Teste 2: Inventário com erros
CENARIO_TESTE = 'com_erros'

// Teste 3: Inventário com temperos sensíveis
CENARIO_TESTE = 'temperos_sensiveis'

// Teste 4: Inventário completo
CENARIO_TESTE = 'completo'
```

### 2. Criar Novos Cenários

Você pode criar novos cenários adicionando ao objeto `cenarios`:

```javascript
const cenarios = {
  // ... cenários existentes ...
  
  // Novo cenário
  meu_teste: {
    notion_page_id: 'test-notion-page-id-12345',
    inventario_texto: 'arroz: 500g, feijão: 300g',
    foto_inventario_base64: ''
  }
};
```

### 3. Testar Erros

Teste cenários de erro para garantir que o workflow trata erros corretamente:

- Inventário vazio
- Formatação inválida
- Ingredientes não encontrados
- Base de ingredientes vazia

### 4. Verificar Logs

Verifique os logs do n8n para ver mensagens de console:

```javascript
console.log(`🧪 MODO TESTE ATIVO - Cenário: ${CENARIO_TESTE}`);
console.log(`📦 Payload de teste:`, payload);
```

---

## 📝 Checklist de Teste

- [ ] Workflow importado com sucesso
- [ ] Modo de teste configurado (`MODO_TESTE = true`)
- [ ] Cenário de teste selecionado (`CENARIO_TESTE = 'completo'`)
- [ ] Workflow executado manualmente
- [ ] Payload de teste gerado corretamente
- [ ] Base de ingredientes carregada do Google Sheets
- [ ] Busca fuzzy funcionando (encontra ingredientes com erros)
- [ ] Claude processando ingredientes não encontrados (se necessário)
- [ ] Resultado final formatado corretamente
- [ ] Resposta JSON correta
- [ ] Temperos sensíveis identificados corretamente
- [ ] Métodos utilizados registrados corretamente

---

## 🐛 Troubleshooting

### Problema: Workflow não executa

**Solução:** Verifique se o workflow está ativo e se todos os nós estão conectados corretamente.

### Problema: Payload de teste não é gerado

**Solução:** Verifique se `MODO_TESTE = true` no nó `Code - Payload de Teste`.

### Problema: Base de ingredientes não carrega

**Solução:** Verifique as credenciais do Google Sheets e se a planilha está acessível.

### Problema: Claude não processa ingredientes

**Solução:** Verifique as credenciais do Claude API e se o prompt está correto.

### Problema: Resultado final incorreto

**Solução:** Verifique os logs de cada nó para identificar onde o problema ocorre.

---

## 📚 Próximos Passos

1. Teste todos os cenários disponíveis
2. Crie novos cenários de teste conforme necessário
3. Teste em modo de produção (com dados do bot)
4. Ajuste o workflow conforme necessário
5. Implemente melhorias baseadas nos testes

---

## ✅ Resultado Esperado

Ao executar o workflow com `CENARIO_TESTE = 'completo'`, você deve ver:

```json
{
  "success": true,
  "inventario_estruturado": [
    {
      "nome_oficial": "Arroz",
      "quantidade": "500",
      "unidade": "g",
      "categoria": "Grãos e Cereais",
      "tempero_sensivel": false,
      "confianca": 1.0,
      "metodo": "exato"
    },
    // ... mais ingredientes ...
  ],
  "inventario_visualizacao": "📦 INVENTÁRIO PROCESSADO\n\n...",
  "temperos_sensiveis": [
    {
      "nome_oficial": "Pimenta do reino",
      "quantidade": "50",
      "unidade": "g"
    }
  ],
  "total_ingredientes": 17,
  "total_temperos_sensiveis": 6,
  "metodos_usados": {
    "exato": 10,
    "fuzzy_alta": 5,
    "fuzzy_media": 2,
    "nao_encontrado": 0,
    "claude": 0
  }
}
```

---

**Boa sorte com os testes! 🚀**

