# 🚀 Como Forçar Deploy no Railway

## ⚡ Método Rápido

### 1. Via Railway Dashboard (Recomendado)

1. **Acessar Railway Dashboard**
   - Ir para: https://railway.app/
   - Fazer login
   - Selecionar o projeto `chef-bot-relatorio`

2. **Forçar Redeploy**
   - Clicar em **"Deployments"** (menu lateral)
   - Encontrar o último deployment
   - Clicar nos **3 pontinhos** (⋯) ao lado do deployment
   - Selecionar **"Redeploy"**

   OU

   - Ir em **"Settings"** → **"Source"**
   - Clicar em **"Redeploy"** (botão no topo)

3. **Aguardar Deploy**
   - Railway vai fazer build novamente
   - Verificar logs para confirmar que está usando o commit mais recente

---

## 🔍 Verificar se Deploy Automático Está Ativo

### 1. Verificar Configuração de Source

1. Railway Dashboard → **Settings** → **Source**
2. Verificar:
   - ✅ Repositório conectado: `erickcardeal/chef-bot-relatorio`
   - ✅ Branch: `main`
   - ✅ Auto Deploy: **Enabled** (deve estar ativado)

### 2. Verificar Último Commit no GitHub

1. Acessar: https://github.com/erickcardeal/chef-bot-relatorio
2. Verificar se o commit mais recente está lá:
   - `315fc37 - Corrige lógica de processamento de álbuns...`

### 3. Verificar Último Deploy no Railway

1. Railway Dashboard → **Deployments**
2. Verificar o commit hash do último deploy
3. Comparar com o commit no GitHub

---

## 🐛 Problemas Comuns

### Deploy não detecta novo commit

**Solução 1: Forçar Redeploy**
- Railway Dashboard → Deployments → Redeploy

**Solução 2: Verificar Conexão GitHub**
- Settings → Source → Verificar se repositório está conectado
- Se não estiver, reconectar GitHub

**Solução 3: Verificar Branch**
- Settings → Source → Verificar se está apontando para `main`
- Se não estiver, alterar para `main`

### Deploy falha

**Verificar Logs:**
1. Railway Dashboard → Deployments → Clicar no deployment
2. Verificar logs de erro
3. Verificar se há erros de sintaxe ou dependências

**Verificar Variáveis de Ambiente:**
1. Settings → Variables
2. Verificar se todas as variáveis estão configuradas

---

## ✅ Checklist

- [ ] Commit foi feito e pushado para GitHub
- [ ] Railway está conectado ao repositório correto
- [ ] Branch configurado é `main`
- [ ] Auto Deploy está ativado
- [ ] Último commit aparece no GitHub
- [ ] Redeploy foi acionado (se necessário)
- [ ] Logs mostram que o deploy foi bem-sucedido

---

## 📝 Comandos Úteis

### Verificar último commit local
```bash
git log --oneline -1
```

### Verificar se commit está no GitHub
```bash
git log origin/main --oneline -1
```

### Forçar push (se necessário)
```bash
git push origin main --force
```

⚠️ **Cuidado**: `--force` só use se tiver certeza!

---

**Última atualização**: 2025-11-17

