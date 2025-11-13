# 📥 Como Exportar Workflows do n8n

## ⚠️ Situação

Os arquivos JSON dos workflows foram perdidos durante a organização. É necessário exportá-los novamente do n8n.

---

## 📋 Workflows Necessários

### 1. **Relatório de Visita - Fase 1 - COM ATENDIMENTO.json**
- **Webhook**: `/webhook/bot-relatorio-chef-fase1`
- **URL**: `https://chefpessoal.app.n8n.cloud/webhook/bot-relatorio-chef-fase1`
- **Função**: Recebe dados da FASE 1, cria página no Notion, atualiza relação no calendário

### 2. **Relatório de Visita - Fase 2A - Processar (COM TESTE).json**
- **Webhook**: `/webhook/fase2-processar`
- **URL**: `https://chefpessoal.app.n8n.cloud/webhook/fase2-processar`
- **Função**: Processa inventário (parse simples + validação de temperos sensíveis)

### 3. **Relatório de Visita - Fase 2B - Salvar.json**
- **Webhook**: `/webhook/fase2-salvar`
- **URL**: `https://chefpessoal.app.n8n.cloud/webhook/fase2-salvar`
- **Função**: Salva inventário processado no Notion

---

## 📥 Passos para Exportar

### 1. Acessar o n8n
1. Acesse: `https://chefpessoal.app.n8n.cloud`
2. Faça login
3. Vá para "Workflows"

### 2. Exportar cada workflow

#### **Fase 1 - COM ATENDIMENTO**
1. Procure por: "Relatório de Visita - Fase 1 - COM ATENDIMENTO"
2. Clique no workflow
3. Clique nos **3 pontos** (menu) no canto superior direito
4. Selecione **"Download"** ou **"Export"**
5. Salve como: `Relatório de Visita - Fase 1 - COM ATENDIMENTO.json`
6. Mova para: `/Users/erickcardealdossantos/Desktop/Bot/n8n/`

#### **Fase 2A - Processar (COM TESTE)**
1. Procure por: "Relatório de Visita - Fase 2A - Processar (COM TESTE)"
2. Clique no workflow
3. Clique nos **3 pontos** (menu) no canto superior direito
4. Selecione **"Download"** ou **"Export"**
5. Salve como: `Relatório de Visita - Fase 2A - Processar (COM TESTE).json`
6. Mova para: `/Users/erickcardealdossantos/Desktop/Bot/n8n/`

#### **Fase 2B - Salvar**
1. Procure por: "Relatório de Visita - Fase 2B - Salvar"
2. Clique no workflow
3. Clique nos **3 pontos** (menu) no canto superior direito
4. Selecione **"Download"** ou **"Export"**
5. Salve como: `Relatório de Visita - Fase 2B - Salvar.json`
6. Mova para: `/Users/erickcardealdossantos/Desktop/Bot/n8n/`

---

## ✅ Verificação

Após exportar, verifique:

```bash
cd /Users/erickcardealdossantos/Desktop/Bot/n8n/
ls -la *.json
```

Você deve ver:
- `Relatório de Visita - Fase 1 - COM ATENDIMENTO.json`
- `Relatório de Visita - Fase 2A - Processar (COM TESTE).json`
- `Relatório de Visita - Fase 2B - Salvar.json`

---

## 🔄 Alternativa: Usar o n8n Cloud

Se os workflows não estiverem no n8n local, você pode:

1. **Acessar o n8n Cloud**: `https://chefpessoal.app.n8n.cloud`
2. **Exportar diretamente** do n8n Cloud
3. **Salvar os arquivos** na pasta `n8n/`

---

## 📝 Notas

- Os workflows **devem estar ativos** no n8n
- Os webhooks **devem estar configurados** corretamente
- Após exportar, **verifique se os arquivos estão corretos**
- Se necessário, **teste os workflows** no n8n antes de usar

---

## 🆘 Se os Workflows Não Estiverem no n8n

Se os workflows não estiverem no n8n, você pode:

1. **Recriar os workflows** baseado na documentação:
   - `docs/implementacao/GUIA_IMPLEMENTACAO_FASE1.md`
   - `docs/implementacao/GUIA_IMPLEMENTACAO_FASE2A.md`
   - `docs/implementacao/GUIA_IMPLEMENTACAO_FASE2B.md`

2. **Usar a documentação** para recriar os workflows manualmente

3. **Contatar o suporte** se necessário

---

**Última atualização**: 2025-11-13

