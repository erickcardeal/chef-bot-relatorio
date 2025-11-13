# 🚀 Quick Start - Deploy no Railway

## ⚡ Guia Rápido (5 minutos)

### 1. Preparar Projeto

```bash
cd /Users/erickcardealdossantos/Desktop/Bot

# Verificar arquivos essenciais
ls -la | grep -E "requirements.txt|Procfile|.gitignore|.env.example"
```

### 2. Criar Conta GitHub (se não tiver)

1. Acessar https://github.com/signup
2. Criar conta
3. Verificar email

### 3. Criar Repositório no GitHub

1. Acessar https://github.com/new
2. Nome: `chef-bot-relatorio` (ou outro nome)
3. NÃO inicializar com README
4. Clicar em "Create repository"

### 4. Fazer Push do Código

```bash
# Inicializar Git (se não tiver)
git init

# Adicionar arquivos
git add .

# Fazer commit
git commit -m "Initial commit: Bot relatório chef"

# Adicionar remote
git remote add origin https://github.com/SEU-USUARIO/chef-bot-relatorio.git

# Fazer push
git branch -M main
git push -u origin main
```

### 5. Criar Conta Railway (se não tiver)

1. Acessar https://railway.app/
2. Clicar em "Start a New Project"
3. Conectar com GitHub (recomendado)

### 6. Deploy no Railway

1. **Criar Novo Projeto**
   - Clicar em "New Project"
   - Selecionar "Deploy from GitHub repo"
   - Conectar GitHub (se necessário)
   - Selecionar repositório `chef-bot-relatorio`

2. **Configurar Variáveis de Ambiente**
   - Clicar em "Variables"
   - Adicionar todas as variáveis do `.env.example`:
     ```
     TELEGRAM_BOT_TOKEN=seu_token
     NOTION_TOKEN=seu_token
     NOTION_CHEFS_DB=seu_id
     NOTION_CLIENTES_DB=seu_id
     NOTION_CALENDARIO_DB=seu_id
     NOTION_RELATORIOS_DB=seu_id
     ```

3. **Deploy Automático**
   - Railway detecta automaticamente Python
   - Instala dependências do `requirements.txt`
   - Executa `python3 main.py` (via Procfile)
   - Bot inicia automaticamente

### 7. Verificar Deploy

1. **Ver Logs**
   - Railway Dashboard → Deployments → Logs
   - Deve aparecer: `Bot iniciado! 🤖`

2. **Testar Bot**
   - Abrir Telegram
   - Enviar `/relatorio` para o bot
   - Verificar se responde

### 8. Monitorar

- **Logs**: Railway Dashboard → Logs
- **Métricas**: Railway Dashboard → Metrics
- **Deployments**: Railway Dashboard → Deployments

---

## ✅ Checklist Rápido

- [ ] Conta GitHub criada
- [ ] Repositório GitHub criado
- [ ] Código commitado e pushado
- [ ] Conta Railway criada
- [ ] Projeto Railway criado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado
- [ ] Bot testado
- [ ] Logs verificados

---

## 🐛 Problemas Comuns

### Bot não inicia
- Verificar logs no Railway
- Verificar variáveis de ambiente
- Verificar `requirements.txt`

### Erro de conexão
- Verificar tokens
- Verificar URLs de webhooks
- Verificar firewall

### Erro de dependências
- Verificar `requirements.txt`
- Verificar versão do Python
- Verificar instalação de pacotes

---

## 📚 Documentação Completa

- [CHECKLIST_DEPLOY_RAILWAY.md](CHECKLIST_DEPLOY_RAILWAY.md) - Checklist detalhado
- [GUIA_ORGANIZACAO_PROJETO.md](GUIA_ORGANIZACAO_PROJETO.md) - Organização do projeto
- [README.md](README.md) - Documentação completa

---

## 🔗 Links Úteis

- [Railway Dashboard](https://railway.app/)
- [GitHub](https://github.com/)
- [Railway Docs](https://docs.railway.app/)

---

**Última atualização**: 2025-11-13

