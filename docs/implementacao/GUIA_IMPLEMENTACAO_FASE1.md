# 🚀 Guia de Implementação - Fase 1

## ✅ O que foi implementado

### Modificações realizadas:

1. **Google Sheets - Ler Ingredientes** (NOVO)
   - Lê a base de ingredientes do Google Sheets
   - Planilha: `1MoClw9F5N94APD7SwTLO3kR9iiiXIj9VmR8vPfBB-as`
   - Aba: `Lista de Ingredientes`

2. **Code - Format Base Ingredientes** (NOVO)
   - Formata a base para uso no Claude
   - Cria JSON estruturado
   - Conta ingredientes e categorias

3. **Claude - Normaliza Inventário** (MODIFICADO)
   - Prompt atualizado com base dinâmica do Google Sheets
   - Usa: `{{ $('Code - Format Base Ingredientes').item.json.base_ingredientes_json }}`
   - Identifica temperos sensíveis automaticamente

4. **Code - Parse JSON** (MODIFICADO)
   - Suporte a formato novo e antigo do Claude
   - Identificação automática de temperos sensíveis
   - Visualização melhorada com emojis de alerta
   - Agrupamento por categoria

5. **Respond - Confirma pro Bot** (MODIFICADO)
   - Adiciona informações sobre base carregada
   - Mostra quantidade de ingredientes processados
   - Mostra quantidade de temperos sensíveis

---

## 📋 Passo a Passo no n8n

### 1. Fazer backup do workflow atual
- Exportar workflow atual antes de modificar
- Salvar como `Relatorio_de_Visita_BACKUP.json`

### 2. Importar novo workflow
- Abrir n8n
- Clicar em **Menu** > **Import from File**
- Selecionar o arquivo `Relatorio_de_Visita_v2_FASE1.json`
- Clicar em **Import**

### 3. Configurar credenciais do Google Sheets
- Abrir node **Google Sheets - Ler Ingredientes**
- Clicar em **Select Credential**
- Se não tiver credencial:
  1. Clicar em **+ Create New Credential**
  2. Escolher **Google Sheets OAuth2**
  3. Fazer autenticação com Google
  4. Salvar credencial

### 4. Testar o workflow

#### Teste 1: Verificar base de ingredientes
1. Executar apenas o node **Google Sheets - Ler Ingredientes**
2. Verificar se retornou os ingredientes
3. Executar o node **Code - Format Base Ingredientes**
4. Verificar se formatou corretamente

#### Teste 2: Testar com inventário de texto
1. Criar payload de teste:
```json
{
  "chef_telegram_id": "123456789",
  "chef_username": "chef_teste",
  "cliente_nome": "Cliente Teste",
  "data_atendimento": "2025-11-12",
  "horario_chegada": "10:00",
  "horario_saida": "14:00",
  "como_foi_visita": "Tudo certo",
  "comentario_cliente": "Excelente",
  "problema_especifico": "Nenhum",
  "porcoes_exatas": "Sim",
  "motivo_porcoes": "",
  "inventario_atualizado": "Sim",
  "inventario_texto": "500g arroz branco, 2 tomates, 50g pimenta do reino",
  "foto_inventario_base64": "",
  "descarte": "Não",
  "itens_descartados": "",
  "pode_vencer": "Não",
  "itens_podem_vencer": "",
  "foto_entrada_base64": "",
  "foto_saida_base64": ""
}
```

2. Executar workflow completo
3. Verificar se:
   - Base foi carregada
   - Claude normalizou os ingredientes
   - Temperos sensíveis foram identificados
   - Visualização está formatada

#### Teste 3: Testar com foto (se tiver)
1. Usar payload com `foto_inventario_base64` preenchido
2. Executar workflow
3. Verificar se OCR funcionou

---

## 🔍 O que verificar após implementação

### ✅ Checklist de validação:

1. **Google Sheets**
   - [ ] Base carrega corretamente
   - [ ] Todos os ingredientes aparecem
   - [ ] Colunas estão corretas (Ingrediente, Sinônimos, Categoria, etc.)

2. **Claude - Normaliza Inventário**
   - [ ] Prompt usa base dinâmica
   - [ ] Identifica ingredientes corretamente
   - [ ] Normaliza quantidades
   - [ ] Identifica temperos sensíveis

3. **Code - Parse JSON**
   - [ ] Parseia resposta do Claude
   - [ ] Identifica temperos sensíveis
   - [ ] Cria visualização formatada
   - [ ] Agrupa por categoria

4. **Notion**
   - [ ] Relatório é criado
   - [ ] Inventário JSON está correto
   - [ ] Visualização está formatada
   - [ ] Temperos sensíveis destacados

---

## 🎯 Resultados esperados

### Antes (sem base dinâmica):
```
❌ Ingredientes hardcoded no prompt
❌ Erros de digitação não corrigidos
❌ Temperos sensíveis não identificados
❌ Visualização simples
```

### Depois (com base dinâmica - Fase 1):
```
✅ Base de ingredientes do Google Sheets
✅ Normalização baseada na base
✅ Temperos sensíveis identificados automaticamente
✅ Visualização melhorada com:
   - Agrupamento por categoria
   - Emoji de alerta (⚠️) para temperos sensíveis
   - Resumo com estatísticas
   - Confiança do Claude
```

### Exemplo de visualização:

```
📦 INVENTÁRIO PROCESSADO

⚠️ ATENÇÃO: Verifique especialmente os temperos sensíveis: Pimenta do Reino em Grãos

═══════════════════════════════════════

📂 GRÃOS E CEREAIS
────────────────────────────────────────
  • Arroz - Branco: 500g (95%)

📂 HORTALIÇAS E VERDURAS
────────────────────────────────────────
  • Tomate Italiano: 2unidade (90%)

📂 TEMPEROS E ESPECIARIAS
────────────────────────────────────────
⚠️ • Pimenta do Reino em Grãos: 50g (95%)

═══════════════════════════════════════
📊 RESUMO:
   • Total de ingredientes: 3
   • Categorias: 3
   • Temperos sensíveis: 1
```

---

## 🐛 Troubleshooting

### Problema 1: Google Sheets não carrega
**Solução:**
1. Verificar se credencial está configurada
2. Verificar se tem permissão na planilha
3. Verificar se ID da planilha está correto
4. Verificar se nome da aba está correto (`Lista de Ingredientes`)

### Problema 2: Claude não normaliza corretamente
**Solução:**
1. Verificar se base foi carregada (node anterior)
2. Verificar se base está no formato correto
3. Verificar se prompt está completo
4. Testar com inventário simples primeiro

### Problema 3: Parse JSON falha
**Solução:**
1. Verificar resposta do Claude (pode ter markdown)
2. Código já trata remoção de markdown
3. Verificar se Claude retornou JSON válido

### Problema 4: Temperos sensíveis não identificados
**Solução:**
1. Verificar se base tem coluna "Tempero Sensível"
2. Verificar se valores são "Sim" ou "Não"
3. Verificar se Claude marcou `tempero_sensivel: true`

---

## 📊 Monitoramento

### Métricas para acompanhar:

1. **Taxa de sucesso**
   - Quantos relatórios são processados com sucesso?
   - Quantos falham?

2. **Qualidade da normalização**
   - Claude está identificando ingredientes corretamente?
   - Temperos sensíveis estão sendo marcados?

3. **Performance**
   - Tempo de processamento (antes vs depois)
   - Custo de API do Claude

---

## 🎓 Próximos passos (Fase 2 - Opcional)

Se você observar:
- ❌ Muitos erros de OCR (ex: "aroz" em vez de "arroz")
- ❌ Claude falhando em normalizar
- ❌ Tempo de processamento alto

Então considere implementar **Fase 2** com:
1. **Code - Busca Fuzzy** (corrige erros de digitação)
2. **IF - Precisa Claude?** (só usa Claude quando necessário)
3. **Code - Processar Temperos** (destaque adicional)
4. **Code - Normalizar Unidades** (g/ml padronizado)

---

## ✅ Conclusão

**Fase 1 implementada com sucesso!**

✅ Base dinâmica do Google Sheets
✅ Normalização inteligente com Claude
✅ Identificação de temperos sensíveis
✅ Visualização melhorada
✅ Arquitetura simples e escalável

**Resultado:**
- Mais preciso (usa base real)
- Mais flexível (atualiza base sem mudar código)
- Mais útil (temperos sensíveis destacados)
- Mais simples (menos nodes que Fase 2 completa)

Qualquer dúvida, consulte este guia ou entre em contato!
