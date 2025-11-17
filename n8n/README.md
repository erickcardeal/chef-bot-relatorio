# 📁 Workflows n8n

## ✅ Workflows Disponíveis

### 1. **Relatório de Visita - Fase 1.json**
- **Webhook**: `/webhook/bot-relatorio-chef-fase1`
- **URL Produção**: `https://chefpessoal.app.n8n.cloud/webhook/bot-relatorio-chef-fase1`
- **Função**: Recebe dados da FASE 1, cria página no Notion, atualiza relação no calendário
- **Status**: ✅ Disponível

### 2. **Relatório de Visita - Fase 2A (processar).json**
- **Webhook**: `/webhook/fase2-processar`
- **URL Produção**: `https://chefpessoal.app.n8n.cloud/webhook/fase2-processar`
- **Função**: Processa inventário (parse simples + validação de temperos sensíveis)
- **Status**: ✅ Disponível

### 3. **Relatório de Visita - Fase 2B (Salvar).json**
- **Webhook**: `/webhook/fase2-salvar`
- **URL Produção**: `https://chefpessoal.app.n8n.cloud/webhook/fase2-salvar`
- **Função**: Salva inventário processado no Notion
- **Status**: ✅ Disponível

---

## 📥 Como Importar no n8n

### Passo 1: Acessar o n8n
1. Acesse: `https://chefpessoal.app.n8n.cloud`
2. Faça login
3. Vá para **"Workflows"** no menu lateral

### Passo 2: Importar cada workflow

Para cada workflow:

1. **Clique em "Import from File"** (ou arraste o arquivo)
2. **Selecione o arquivo JSON** desta pasta
3. **Clique em "Import"**
4. **Configure as credenciais** necessárias:
   - **Notion API** (para Fase 1 e Fase 2B)
   - **Anthropic API** (para Fase 2A, se necessário)
5. **Ative o workflow** (toggle no canto superior direito)

### Passo 3: Verificar Webhooks

Após importar, verifique:

- **Fase 1**: Webhook path deve ser `/webhook/bot-relatorio-chef-fase1`
- **Fase 2A**: Webhook path deve ser `/webhook/fase2-processar`
- **Fase 2B**: Webhook path deve ser `/webhook/fase2-salvar`

---

## 📝 Documentação Relacionada

- **`../docs/n8n/INSTRUCOES_IMPORTAR_N8N.md`** - Instruções detalhadas de importação
- **`../docs/implementacao/GUIA_IMPLEMENTACAO_FASE1.md`** - Guia FASE 1
- **`../docs/implementacao/GUIA_IMPLEMENTACAO_FASE2A.md`** - Guia FASE 2A
- **`../docs/implementacao/GUIA_IMPLEMENTACAO_FASE2B.md`** - Guia FASE 2B

---

## ✅ Checklist de Importação

### Fase 1
- [ ] JSON importado
- [ ] Webhook configurado (`/webhook/bot-relatorio-chef-fase1`)
- [ ] Response Mode: `responseNode`
- [ ] Response Node: `Respond - Confirma ao Bot`
- [ ] Notion API configurada
- [ ] Conexões verificadas
- [ ] Workflow ativado

### Fase 2A
- [ ] JSON importado
- [ ] Webhook configurado (`/webhook/fase2-processar`)
- [ ] Response Mode: `responseNode`
- [ ] Response Node: `Respond - Retorna pro Bot`
- [ ] Credenciais configuradas (se necessário)
- [ ] Conexões verificadas
- [ ] Workflow ativado

### Fase 2B
- [ ] JSON importado
- [ ] Webhook configurado (`/webhook/fase2-salvar`)
- [ ] Response Mode: `responseNode`
- [ ] Response Node: `Respond - Confirma pro Bot`
- [ ] Notion API configurada
- [ ] Conexões verificadas
- [ ] Workflow ativado

---

## 🔄 Atualização dos Workflows

### Quando atualizar:
- Quando houver mudanças nos workflows no n8n
- Quando houver correções ou melhorias
- Quando houver mudanças nas APIs (Notion, Anthropic, etc.)

### Como atualizar:
1. **Exportar o workflow atualizado** do n8n
2. **Substituir o arquivo** nesta pasta
3. **Verificar** se as mudanças estão corretas
4. **Documentar** as mudanças se necessário

---

## 📊 Estrutura dos Arquivos

```
n8n/
├── README.md (este arquivo)
├── Relatório de Visita - Fase 1.json
├── Relatório de Visita - Fase 2A (processar).json
└── Relatório de Visita - Fase 2B (Salvar).json
```

---

## 🚀 Próximos Passos

1. **Importar workflows** no n8n (se ainda não foram importados)
2. **Configurar credenciais** necessárias
3. **Ativar workflows** no n8n
4. **Testar fluxo completo** com o bot
5. **Verificar logs** se necessário

---

**Última atualização**: 2025-11-13
