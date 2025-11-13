# ✅ Checklist Final de Deploy

## 📋 Status Atual do Projeto

### ✅ Estrutura de Arquivos
- [x] `main.py` - Código principal do bot
- [x] `config.py` - Configurações e variáveis de ambiente
- [x] `notion_api.py` - API do Notion
- [x] `requirements.txt` - Dependências Python
- [x] `Procfile` - Comando de inicialização (Railway)
- [x] `.gitignore` - Arquivos ignorados pelo Git
- [x] `.env.example` - Template de variáveis de ambiente (se existir)
- [x] `README.md` - Documentação principal

### ✅ Estrutura de Diretórios
- [x] `docs/` - Documentação organizada (58 arquivos)
- [x] `n8n/` - Workflows n8n (3 arquivos JSON)
- [x] `scripts/` - Scripts auxiliares (5 arquivos)

### ✅ Workflows n8n
- [x] `Relatório de Visita - Fase 1.json`
- [x] `Relatório de Visita - Fase 2A (processar).json`
- [x] `Relatório de Visita - Fase 2B (Salvar).json`

---

## 🚀 Passos para Deploy

### 1. Preparar Projeto Local ✅

#### 1.1 Verificar Arquivos
```bash
cd /Users/erickcardealdossantos/Desktop/Bot

# Verificar arquivos essenciais
ls -la | grep -E "requirements.txt|Procfile|.gitignore|main.py"
```

#### 1.2 Verificar Dependências
```bash
# Verificar Python
python3 --version

# Verificar se requirements.txt está correto
cat requirements.txt
```

#### 1.3 Criar .env.example (se não existir)
```bash
# Verificar se existe
ls -la .env.example

# Se não existir, criar baseado no config.py
```

---

### 2. Criar Repositório GitHub

#### 2.1 Criar Conta GitHub (se não tiver)
1. Acessar: https://github.com/signup
2. Criar conta
3. Verificar email

#### 2.2 Criar Repositório
1. Acessar: https://github.com/new
2. Nome: `chef-bot-relatorio` (ou outro nome)
3. Descrição: "Bot Telegram para relatórios de visita de chefs"
4. Público ou Privado (escolher)
5. **NÃO** inicializar com README
6. Clicar em "Create repository"

#### 2.3 Inicializar Git e Fazer Push
```bash
cd /Users/erickcardealdossantos/Desktop/Bot

# Inicializar Git (se não tiver)
git init

# Verificar status
git status

# Adicionar arquivos
git add .

# Fazer commit
git commit -m "Initial commit: Bot relatório chef - projeto organizado"

# Adicionar remote
git remote add origin https://github.com/SEU-USUARIO/chef-bot-relatorio.git

# Fazer push
git branch -M main
git push -u origin main
```

---

### 3. Configurar Railway

#### 3.1 Criar Conta Railway (se não tiver)
1. Acessar: https://railway.app/
2. Clicar em "Start a New Project"
3. Conectar com GitHub (recomendado)

#### 3.2 Criar Novo Projeto
1. Clicar em "New Project"
2. Selecionar "Deploy from GitHub repo"
3. Conectar GitHub (se necessário)
4. Selecionar repositório `chef-bot-relatorio`
5. Clicar em "Deploy"

#### 3.3 Configurar Variáveis de Ambiente
1. Clicar em "Variables" no projeto
2. Adicionar todas as variáveis necessárias:

```env
# Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui

# Notion
NOTION_TOKEN=seu_token_aqui
NOTION_CHEFS_DB=seu_id_aqui
NOTION_CLIENTES_DB=seu_id_aqui
NOTION_CALENDARIO_DB=seu_id_aqui
NOTION_RELATORIOS_DB=seu_id_aqui

# n8n (opcional - já tem valores padrão)
N8N_WEBHOOK_URL_FASE1=https://chefpessoal.app.n8n.cloud/webhook/bot-relatorio-chef-fase1
N8N_WEBHOOK_URL_FASE2A=https://chefpessoal.app.n8n.cloud/webhook/fase2-processar
N8N_WEBHOOK_URL_FASE2B=https://chefpessoal.app.n8n.cloud/webhook/fase2-salvar

# Processamento de Inventário (opcional)
PROCESSAR_INVENTARIO_LOCAL=false
ANTHROPIC_API_KEY=seu_token_aqui (se usar processamento local)
```

#### 3.4 Verificar Deploy
1. Railway detecta automaticamente Python
2. Instala dependências do `requirements.txt`
3. Executa `python3 main.py` (via Procfile)
4. Bot inicia automaticamente

---

### 4. Verificar Deploy

#### 4.1 Verificar Logs
1. Railway Dashboard → Deployments → Logs
2. Deve aparecer: `Bot iniciado! 🤖`
3. Verificar se não há erros

#### 4.2 Testar Bot
1. Abrir Telegram
2. Enviar `/relatorio` para o bot
3. Verificar se responde
4. Testar fluxo completo

#### 4.3 Monitorar
- **Logs**: Railway Dashboard → Logs
- **Métricas**: Railway Dashboard → Metrics
- **Deployments**: Railway Dashboard → Deployments

---

### 5. Configurar Workflows n8n (se necessário)

#### 5.1 Importar Workflows
1. Acessar: https://chefpessoal.app.n8n.cloud
2. Importar workflows de `n8n/`:
   - `Relatório de Visita - Fase 1.json`
   - `Relatório de Visita - Fase 2A (processar).json`
   - `Relatório de Visita - Fase 2B (Salvar).json`

#### 5.2 Configurar Credenciais
- Notion API
- Anthropic API (se necessário)
- Google Sheets (se necessário)

#### 5.3 Ativar Workflows
- Ativar todos os workflows
- Verificar webhooks estão corretos

---

## ✅ Checklist Final

### Pré-Deploy
- [ ] Todos os arquivos essenciais presentes
- [ ] `requirements.txt` atualizado
- [ ] `Procfile` configurado
- [ ] `.gitignore` configurado
- [ ] Estrutura de pastas organizada
- [ ] Workflows n8n organizados

### GitHub
- [ ] Conta GitHub criada
- [ ] Repositório GitHub criado
- [ ] Código commitado
- [ ] Código pushado para GitHub

### Railway
- [ ] Conta Railway criada
- [ ] Projeto Railway criado
- [ ] Repositório GitHub conectado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado

### Verificação
- [ ] Logs verificados
- [ ] Bot testado
- [ ] Fluxo completo testado
- [ ] Workflows n8n configurados (se necessário)

---

## 🐛 Problemas Comuns

### Bot não inicia
- Verificar logs no Railway
- Verificar variáveis de ambiente
- Verificar `requirements.txt`
- Verificar `Procfile`

### Erro de conexão
- Verificar tokens (Telegram, Notion)
- Verificar URLs de webhooks
- Verificar firewall

### Erro de dependências
- Verificar `requirements.txt`
- Verificar versão do Python
- Verificar instalação de pacotes

### Erro de variáveis de ambiente
- Verificar se todas as variáveis estão configuradas
- Verificar se os valores estão corretos
- Verificar se não há espaços extras

---

## 📚 Documentação

- **`docs/deploy/QUICK_START_RAILWAY.md`** - Guia rápido (5 minutos)
- **`docs/deploy/CHECKLIST_DEPLOY_RAILWAY.md`** - Checklist detalhado
- **`docs/deploy/RESUMO_DEPLOY.md`** - Resumo de deploy
- **`README.md`** - Documentação principal

---

## 🔗 Links Úteis

- [Railway Dashboard](https://railway.app/)
- [GitHub](https://github.com/)
- [Railway Docs](https://docs.railway.app/)
- [n8n Cloud](https://chefpessoal.app.n8n.cloud)

---

## 🎯 Próximos Passos

1. **Criar conta GitHub** (se não tiver)
2. **Criar repositório GitHub**
3. **Fazer push do código**
4. **Criar conta Railway** (se não tiver)
5. **Criar projeto Railway**
6. **Configurar variáveis de ambiente**
7. **Fazer deploy**
8. **Testar bot**
9. **Monitorar logs**

---

**Última atualização**: 2025-11-13

