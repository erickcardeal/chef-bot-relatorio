# 📁 Guia de Organização do Projeto

## 🎯 Objetivo

Organizar o projeto para facilitar o deploy no Railway e manter o código limpo e documentado.

---

## 📂 Estrutura de Diretórios Recomendada

```
Bot/
├── main.py                      # Arquivo principal do bot
├── config.py                   # Configurações e variáveis de ambiente
├── notion_api.py               # API do Notion
├── requirements.txt            # Dependências Python
├── .gitignore                  # Arquivos ignorados pelo Git
├── .env.example                # Exemplo de variáveis de ambiente
├── Procfile                    # Comando de inicialização (Railway)
├── railway.json                # Configuração do Railway (opcional)
├── README.md                   # Documentação principal
├── docs/                       # Documentação adicional
│   ├── deploy/
│   │   └── CHECKLIST_DEPLOY_RAILWAY.md
│   ├── REGRAS_BUSCA_ATENDIMENTO.md
│   ├── RESUMO_FILTRO_RELATORIO.md
│   └── ...
├── n8n/                        # Workflows n8n
│   ├── Relatorio_de_Visita_v2_FASE1.json
│   └── ...
├── scripts/                    # Scripts auxiliares (opcional)
│   └── processar_csv_ingredientes.py
├── logs/                       # Logs (criado em runtime, no .gitignore)
│   └── bot.log
└── venv/                       # Ambiente virtual (não commitado)
```

---

## 📄 Arquivos Essenciais

### 1. `requirements.txt`
Lista todas as dependências Python necessárias.

**Exemplo**:
```
python-telegram-bot==22.5
requests==2.31.0
python-dotenv==1.0.0
pytz==2023.3
aiohttp==3.9.1
```

### 2. `.gitignore`
Arquivos que NÃO devem ser commitados no Git.

**Conteúdo sugerido**:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Ambiente
.env
.env.local
.env.*.local

# Logs
*.log
logs/
bot.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Railway
.railway/

# Arquivos temporários
*.tmp
*.bak
*.pid
bot.pid
```

### 3. `Procfile`
Comando que o Railway executa para iniciar o bot.

**Conteúdo**:
```
worker: python3 main.py
```

### 4. `.env.example`
Exemplo de variáveis de ambiente (sem valores reais).

**Conteúdo**:
```
# Telegram
TELEGRAM_BOT_TOKEN=seu_token_do_telegram_aqui

# Notion
NOTION_TOKEN=seu_token_do_notion_aqui
NOTION_CHEFS_DB=id_do_database_chefs_aqui
NOTION_CLIENTES_DB=id_do_database_clientes_aqui
NOTION_CALENDARIO_DB=id_do_database_calendario_aqui
NOTION_RELATORIOS_DB=id_do_database_relatorios_aqui

# n8n Webhooks (Produção)
N8N_WEBHOOK_URL_FASE1=https://chefpessoal.app.n8n.cloud/webhook/bot-relatorio-chef-fase1
N8N_WEBHOOK_URL_FASE2A=https://chefpessoal.app.n8n.cloud/webhook/fase2-processar
N8N_WEBHOOK_URL_FASE2B=https://chefpessoal.app.n8n.cloud/webhook/fase2-salvar

# Opcional
PROCESSAR_INVENTARIO_LOCAL=false
ANTHROPIC_API_KEY=opcional_se_quiser_processar_localmente
```

### 5. `railway.json` (Opcional)
Configuração do Railway.

**Conteúdo**:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "python3 main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 6. `README.md`
Documentação principal do projeto.

**Conteúdo sugerido**:
```markdown
# Bot Telegram - Relatórios de Visita

Bot para coleta de relatórios pós-visita dos chefs.

## 🚀 Deploy

Veja [CHECKLIST_DEPLOY_RAILWAY.md](docs/deploy/CHECKLIST_DEPLOY_RAILWAY.md)

## 📚 Documentação

- [Regras de Busca de Atendimento](docs/REGRAS_BUSCA_ATENDIMENTO.md)
- [Filtro de Relatórios](docs/RESUMO_FILTRO_RELATORIO.md)

## 🔧 Configuração

1. Copiar `.env.example` para `.env`
2. Preencher variáveis de ambiente
3. Instalar dependências: `pip install -r requirements.txt`
4. Executar: `python3 main.py`
```

---

## 🔄 Migração de Arquivos

### Passo 1: Criar Estrutura de Diretórios
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
mkdir -p docs/deploy
mkdir -p n8n
mkdir -p scripts
```

### Passo 2: Mover Arquivos
```bash
# Mover workflows n8n
mv "Relatório de Visita - Fase 1 - COM ATENDIMENTO.json" n8n/
mv "Relatório de Visita - Fase 2A - Processar (COM TESTE).json" n8n/
mv "Relatório de Visita - Fase 2B - Salvar.json" n8n/

# Mover documentação
mv CHECKLIST_DEPLOY_RAILWAY.md docs/deploy/
mv REGRAS_BUSCA_ATENDIMENTO.md docs/
mv RESUMO_FILTRO_RELATORIO.md docs/
# ... mover outros docs relevantes

# Mover scripts (se houver)
mv processar_csv_ingredientes.py scripts/
```

### Passo 3: Limpar Arquivos Desnecessários
```bash
# Remover arquivos temporários
rm -f *.log
rm -f *.pid
rm -rf __pycache__/

# Remover arquivos de teste (opcional)
# rm -f TESTE_*.md
# rm -f GUIA_TESTE_*.md
```

### Passo 4: Criar Arquivos Essenciais
```bash
# Criar .gitignore
# Criar .env.example
# Criar Procfile
# Criar railway.json (opcional)
# Atualizar README.md
```

---

## 📦 GitHub vs Railway CLI

### GitHub (Recomendado) ✅
**Vantagens**:
- Integração automática com Railway
- Histórico de commits
- Colaboração fácil
- Backup automático
- CI/CD fácil de configurar

**Como funciona**:
1. Criar repositório no GitHub
2. Fazer push do código
3. Conectar Railway com GitHub
4. Railway faz deploy automático a cada push

### Railway CLI (Alternativa)
**Vantagens**:
- Mais controle
- Deploy direto
- Não precisa de GitHub

**Como funciona**:
1. Instalar Railway CLI
2. Fazer login
3. Fazer deploy direto

**Instalação**:
```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

---

## 🔐 Segurança

### Variáveis de Ambiente
- ✅ **SEMPRE** usar `.env` localmente
- ✅ **SEMPRE** usar variáveis de ambiente no Railway
- ❌ **NUNCA** commitar `.env` no Git
- ❌ **NUNCA** hardcodar tokens no código

### Tokens e Secrets
- ✅ Usar `.env.example` como template
- ✅ Usar variáveis de ambiente no Railway
- ✅ Rotacionar tokens regularmente
- ❌ Não compartilhar tokens em mensagens

---

## 📝 Checklist de Organização

### Antes de Fazer Deploy
- [ ] Estrutura de diretórios criada
- [ ] Arquivos movidos para locais corretos
- [ ] `.gitignore` configurado
- [ ] `.env.example` criado
- [ ] `requirements.txt` atualizado
- [ ] `Procfile` criado
- [ ] `README.md` atualizado
- [ ] Código limpo e organizado
- [ ] Documentação atualizada

### Após Deploy
- [ ] Repositório GitHub criado
- [ ] Código commitado e pushado
- [ ] Projeto Railway configurado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado
- [ ] Bot testado
- [ ] Logs verificados

---

## 🚀 Próximos Passos

1. **Organizar arquivos** seguindo a estrutura sugerida
2. **Criar arquivos essenciais** (.gitignore, Procfile, etc.)
3. **Criar repositório GitHub**
4. **Fazer commit e push**
5. **Configurar Railway**
6. **Fazer deploy**
7. **Testar bot**

---

## 📚 Referências

- [Railway Docs](https://docs.railway.app/)
- [GitHub Docs](https://docs.github.com/)
- [Python Best Practices](https://docs.python-guide.org/writing/structure/)

---

**Última atualização**: 2025-11-13

