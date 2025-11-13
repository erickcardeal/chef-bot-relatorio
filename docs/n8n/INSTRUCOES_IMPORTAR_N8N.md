# 📥 Instruções para Importar Workflows no n8n

## 🎯 Arquivos JSON Criados

1. **`Relatório de Visita - Fase 2A - Processar.json`** - Workflow para processar inventário
2. **`Relatório de Visita - Fase 2B - Salvar.json`** - Workflow para salvar no Notion (será criado)

---

## 📋 Passo a Passo para Importar

### **1. Importar FASE 2A - Processar Inventário**

1. **Abrir n8n**
2. **Clicar em "Workflows"** no menu lateral
3. **Clicar em "Import from File"** (ou arrastar o arquivo)
4. **Selecionar** `Relatório de Visita - Fase 2A - Processar.json`
5. **Clicar em "Import"**

### **2. Configurar FASE 2A**

#### **2.1. Configurar Webhook**
- Abrir node **"Webhook - Recebe do Bot"**
- Verificar path: `/fase2-processar`
- Verificar **Response Mode**: `responseNode`
- Verificar **Response Node**: `Respond - Retorna pro Bot`

#### **2.2. Configurar Credenciais**
- **Google Sheets**: Configurar credencial do Google Sheets
- **Anthropic API**: Configurar credencial do Claude API

#### **2.3. Copiar Código de Busca Fuzzy**
- Abrir node **"Code - Busca Fuzzy"**
- Copiar TODO o código do arquivo `CODIGO_BUSCA_FUZZY_N8N.txt`
- Colar no campo de código do node
- Salvar

#### **2.4. Verificar Conexões**
- Verificar se todas as conexões estão corretas
- Verificar se o fluxo está completo

### **3. Importar FASE 2B - Salvar no Notion**

1. **Abrir n8n**
2. **Criar novo workflow** (ou importar JSON se disponível)
3. **Configurar webhook** com path `/fase2-salvar`
4. **Configurar nodes** conforme `GUIA_IMPLEMENTACAO_FASE2B.md`

### **4. Ativar Workflows**

1. **Ativar FASE 2A** (toggle no canto superior direito)
2. **Ativar FASE 2B** (toggle no canto superior direito)
3. **Copiar URLs dos webhooks**:
   - FASE 2A: `https://chefpessoal.app.n8n.cloud/webhook-test/fase2-processar`
   - FASE 2B: `https://chefpessoal.app.n8n.cloud/webhook-test/fase2-salvar`

### **5. Configurar Bot**

1. **Adicionar variáveis de ambiente** no `.env`:
   ```env
   N8N_WEBHOOK_URL_FASE2A=https://chefpessoal.app.n8n.cloud/webhook-test/fase2-processar
   N8N_WEBHOOK_URL_FASE2B=https://chefpessoal.app.n8n.cloud/webhook-test/fase2-salvar
   ```

2. **Ou usar valores padrão** (já configurados em `config.py`)

---

## ⚠️ Problemas Comuns

### **Problema 1: Código de Busca Fuzzy muito longo**
**Solução**: Copiar código do arquivo `CODIGO_BUSCA_FUZZY_N8N.txt` e colar diretamente no node

### **Problema 2: Credenciais não configuradas**
**Solução**: Configurar credenciais do Google Sheets e Anthropic API

### **Problema 3: Conexões incorretas**
**Solução**: Verificar conexões entre nodes conforme o fluxo

### **Problema 4: Webhook não responde**
**Solução**: Verificar se `responseMode` está como `responseNode` e `responseNode` está configurado

---

## ✅ Checklist de Validação

### **FASE 2A - Processar**
- [ ] Webhook configurado com path `/fase2-processar`
- [ ] Response Mode: `responseNode`
- [ ] Response Node: `Respond - Retorna pro Bot`
- [ ] Google Sheets configurado
- [ ] Código de busca fuzzy copiado
- [ ] Credenciais configuradas
- [ ] Conexões verificadas
- [ ] Workflow ativado

### **FASE 2B - Salvar**
- [ ] Webhook configurado com path `/fase2-salvar`
- [ ] Response Mode: `responseNode`
- [ ] Response Node: `Respond - Confirma pro Bot`
- [ ] Notion API configurada
- [ ] Conexões verificadas
- [ ] Workflow ativado

---

## 🚀 Próximos Passos

1. **Importar workflows** no n8n
2. **Configurar credenciais**
3. **Copiar código de busca fuzzy**
4. **Ativar workflows**
5. **Testar fluxo completo**

---

Quer que eu crie os JSONs completos agora? 🚀

