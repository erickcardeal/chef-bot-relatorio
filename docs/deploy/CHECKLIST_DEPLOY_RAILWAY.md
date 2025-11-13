# 🚀 Checklist de Deploy para Railway

## 📋 Pré-requisitos

### 1. Conta GitHub
- [ ] Criar conta no GitHub (se não tiver): https://github.com/signup
- [ ] Verificar email da conta
- [ ] Configurar autenticação de dois fatores (recomendado)

### 2. Conta Railway
- [ ] Criar conta no Railway: https://railway.app/
- [ ] Conectar com GitHub (opcional, mas recomendado)
- [ ] Verificar plano (free tier disponível)

### 3. Ambiente Local
- [ ] Python 3.10+ instalado
- [ ] Git instalado
- [ ] Arquivos do projeto organizados

---

## 📁 Organização do Projeto

### Estrutura de Diretórios Sugerida

```
Bot/
├── main.py                 # Arquivo principal do bot
├── config.py              # Configurações
├── notion_api.py          # API do Notion
├── requirements.txt       # Dependências Python
├── .gitignore            # Arquivos ignorados pelo Git
├── .env.example          # Exemplo de variáveis de ambiente
├── railway.json          # Configuração do Railway (opcional)
├── Procfile              # Comando de inicialização (Railway)
├── README.md             # Documentação do projeto
├── docs/                 # Documentação adicional
│   ├── REGRAS_BUSCA_ATENDIMENTO.md
│   ├── RESUMO_FILTRO_RELATORIO.md
│   └── ...
├── n8n/                  # Workflows n8n
│   ├── Relatorio_de_Visita_v2_FASE1.json
│   └── ...
└── logs/                 # Logs (criado em runtime)
    └── bot.log
```

### Arquivos Essenciais

#### 1. `requirements.txt`
Lista todas as dependências Python necessárias.

#### 2. `.gitignore`
Arquivos que NÃO devem ser commitados no Git:
- `.env` (variáveis de ambiente)
- `__pycache__/`
- `*.log`
- `venv/`
- `*.pyc`

#### 3. `Procfile`
Comando que o Railway executa para iniciar o bot:
```
worker: python3 main.py
```

#### 4. `.env.example`
Exemplo de variáveis de ambiente (sem valores reais):
```
TELEGRAM_BOT_TOKEN=seu_token_aqui
NOTION_TOKEN=seu_token_aqui
NOTION_CHEFS_DB=seu_db_id_aqui
...
```

---

## 🔧 Preparação do Código

### 1. Verificar Dependências
- [ ] `requirements.txt` está atualizado
- [ ] Todas as dependências estão listadas
- [ ] Versões específicas (se necessário)

### 2. Configurações
- [ ] URLs de produção configuradas no `config.py`
- [ ] Variáveis de ambiente usando `os.getenv()`
- [ ] Sem valores hardcoded (tokens, IDs, etc.)

### 3. Logs
- [ ] Logs configurados corretamente
- [ ] Logs não bloqueiam o processo
- [ ] Logs podem ser acessados no Railway

### 4. Tratamento de Erros
- [ ] Try/except em operações críticas
- [ ] Logs de erros adequados
- [ ] Bot não crasha facilmente

---

## 📦 GitHub Setup

### 1. Inicializar Repositório Git
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
git init
git add .
git commit -m "Initial commit: Bot Telegram para relatórios"
```

### 2. Criar Repositório no GitHub
- [ ] Ir para https://github.com/new
- [ ] Criar novo repositório (ex: `chef-bot-relatorio`)
- [ ] NÃO inicializar com README, .gitignore, ou license
- [ ] Copiar URL do repositório

### 3. Conectar Repositório Local
```bash
git remote add origin https://github.com/seu-usuario/chef-bot-relatorio.git
git branch -M main
git push -u origin main
```

### 4. Verificar Arquivos no GitHub
- [ ] Todos os arquivos estão no repositório
- [ ] `.env` NÃO está no repositório (deve estar no `.gitignore`)
- [ ] `requirements.txt` está presente
- [ ] `Procfile` está presente (se necessário)

---

## 🚂 Railway Setup

### 1. Criar Novo Projeto
- [ ] Acessar https://railway.app/
- [ ] Clicar em "New Project"
- [ ] Selecionar "Deploy from GitHub repo"
- [ ] Conectar conta do GitHub (se necessário)
- [ ] Selecionar o repositório `chef-bot-relatorio`

### 2. Configurar Variáveis de Ambiente
- [ ] Acessar "Variables" no projeto
- [ ] Adicionar todas as variáveis necessárias:

#### Variáveis Obrigatórias:
```
TELEGRAM_BOT_TOKEN=seu_token_do_telegram
NOTION_TOKEN=seu_token_do_notion
NOTION_CHEFS_DB=id_do_database_chefs
NOTION_CLIENTES_DB=id_do_database_clientes
NOTION_CALENDARIO_DB=id_do_database_calendario
NOTION_RELATORIOS_DB=id_do_database_relatorios
```

#### Variáveis Opcionais (com defaults):
```
N8N_WEBHOOK_URL_FASE1=https://chefpessoal.app.n8n.cloud/webhook/bot-relatorio-chef-fase1
N8N_WEBHOOK_URL_FASE2A=https://chefpessoal.app.n8n.cloud/webhook/fase2-processar
N8N_WEBHOOK_URL_FASE2B=https://chefpessoal.app.n8n.cloud/webhook/fase2-salvar
PROCESSAR_INVENTARIO_LOCAL=false
```

### 3. Configurar Build e Deploy
- [ ] Railway detecta automaticamente Python
- [ ] Verificar se o comando de start está correto
- [ ] Configurar `Procfile` ou comando customizado
- [ ] Verificar variáveis de ambiente

### 4. Deploy
- [ ] Clicar em "Deploy"
- [ ] Aguardar build completar
- [ ] Verificar logs de deploy
- [ ] Verificar se o bot iniciou corretamente

---

## ✅ Testes Pós-Deploy

### 1. Verificar Logs
- [ ] Acessar logs no Railway
- [ ] Verificar se o bot iniciou
- [ ] Verificar se há erros
- [ ] Verificar conexão com Telegram
- [ ] Verificar conexão com Notion

### 2. Testar Bot
- [ ] Enviar `/relatorio` no Telegram
- [ ] Verificar se o bot responde
- [ ] Testar fluxo completo:
  - [ ] Selecionar atendimento
  - [ ] Preencher dados básicos
  - [ ] Enviar fotos
  - [ ] Preencher inventário
  - [ ] Verificar se salvou no Notion

### 3. Verificar Integrações
- [ ] Webhook FASE 1 funcionando
- [ ] Webhook FASE 2A funcionando
- [ ] Webhook FASE 2B funcionando
- [ ] Relação com atendimento criada
- [ ] Dados salvos corretamente no Notion

---

## 🔍 Monitoramento

### 1. Logs
- [ ] Verificar logs regularmente
- [ ] Configurar alertas (se disponível)
- [ ] Monitorar erros

### 2. Métricas
- [ ] Verificar uso de recursos
- [ ] Verificar custos (se houver)
- [ ] Monitorar performance

### 3. Backups
- [ ] Configurar backup de dados (se necessário)
- [ ] Documentar processo de recuperação

---

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Bot não inicia
- [ ] Verificar logs de erro
- [ ] Verificar variáveis de ambiente
- [ ] Verificar `requirements.txt`
- [ ] Verificar comando de start

#### 2. Erro de conexão
- [ ] Verificar tokens
- [ ] Verificar URLs de webhooks
- [ ] Verificar firewall/proxy

#### 3. Erro de dependências
- [ ] Verificar `requirements.txt`
- [ ] Verificar versão do Python
- [ ] Verificar instalação de pacotes

---

## 📚 Próximos Passos

### Após Deploy Bem-Sucedido
- [ ] Documentar processo completo
- [ ] Criar guia de uso
- [ ] Configurar monitoramento
- [ ] Planejar melhorias

### Melhorias Futuras
- [ ] CI/CD automático
- [ ] Testes automatizados
- [ ] Monitoramento avançado
- [ ] Alertas automáticos

---

## 📝 Notas

### GitHub vs Railway CLI
- **GitHub (Recomendado)**: Mais fácil, integração automática, histórico de commits
- **Railway CLI**: Mais controle, deploy direto, sem necessidade de GitHub

### Variáveis de Ambiente
- **Railway**: Gerenciadas na dashboard
- **Local**: Gerenciadas no arquivo `.env`
- **Produção**: NUNCA commitar no Git

### Logs
- **Railway**: Logs disponíveis na dashboard
- **Local**: Logs em `bot.log`
- **Produção**: Logs devem ser monitorados regularmente

---

## 🔗 Links Úteis

- [Railway Docs](https://docs.railway.app/)
- [GitHub Docs](https://docs.github.com/)
- [Python Telegram Bot Docs](https://python-telegram-bot.org/)
- [Notion API Docs](https://developers.notion.com/)

---

## ✅ Checklist Final

- [ ] Repositório GitHub criado
- [ ] Código commitado e pushado
- [ ] Projeto Railway criado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado
- [ ] Bot testado
- [ ] Integrações verificadas
- [ ] Logs monitorados
- [ ] Documentação atualizada

---

**Última atualização**: 2025-11-13

