# 🤖 Bot Telegram - Relatório de Visita Chef

Bot para coleta automatizada de relatórios pós-visita dos chefs, com processamento inteligente de inventário usando Claude Vision.

## 📋 Requisitos

- Python 3.12+
- Conta Telegram
- Acesso ao n8n
- Token Notion API

## 🚀 Instalação Local

### 1. Copiar arquivos para ~/Desktop/Bot/

```bash
cd ~/Desktop/Bot
```

Copiar os seguintes arquivos:
- `main.py`
- `config.py` (versão corrigida)
- `notion_api.py` (versão corrigida)
- `requirements.txt` (versão corrigida)
- `.env.example`

### 2. Criar ambiente virtual

```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

**IMPORTANTE:** Copie `.env.example` para `.env` e preencha com suas credenciais reais:

```bash
cp .env.example .env
nano .env  # ou use seu editor preferido
```

**Preencha o arquivo `.env` com:**

```bash
# ===== TELEGRAM =====
TELEGRAM_BOT_TOKEN=seu_token_do_botfather

# ===== n8n =====
N8N_WEBHOOK_URL=https://seu-n8n.app/webhook/relatorio-chef

# ===== NOTION =====
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_CHEFS_DB=18eb71fbd8f980e4b104ff998e930d61
NOTION_CLIENTES_DB=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_CALENDARIO_DB=18eb71fbd8f980e4b499d30617e6914e
NOTION_RELATORIOS_DB=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Como obter as credenciais:**

1. **TELEGRAM_BOT_TOKEN**: 
   - Abra o Telegram
   - Busque por @BotFather
   - Envie `/mybots` e selecione seu bot (@PaulBotuse)
   - Clique em "API Token"

2. **N8N_WEBHOOK_URL**:
   - Entre no seu n8n
   - Abra o workflow de relatórios
   - Copie a URL do nó Webhook

3. **NOTION_TOKEN**:
   - Acesse https://www.notion.so/my-integrations
   - Encontre sua integração
   - Copie o "Internal Integration Token"

4. **Database IDs**:
   - Abra cada database no Notion
   - Copie o ID da URL (parte entre `notion.so/` e `?v=`)
   - Exemplo: `https://notion.so/workspace/18eb71fbd8f980e4b104ff998e930d61?v=...`

### 5. Rodar o bot

```bash
python main.py
```

Você deve ver:
```
Bot iniciado! 🤖
```

## 📱 Uso

### Para os Chefs:

1. Abrir Telegram
2. Buscar: `@PaulBotuse`
3. Enviar: `/start`
4. Seguir as perguntas do bot
5. Enviar inventário (texto OU foto do caderno OU ambos)
6. **IMPORTANTE:** Revisar inventário processado e confirmar
7. Enviar fotos entrada/saída
8. Revisar resumo final e confirmar envio

**Tempo estimado:** 5-7 minutos

## 🔄 Fluxo Completo

```
1. Chef envia /start
2. Bot identifica chef e lista atendimentos (últimos 7 dias)
3. Chef seleciona atendimento e confirma
4. Bot coleta:
   - Horários (chegada e saída)
   - Como foi a visita
   - Comentário do cliente
   - Porções (suficientes ou não)
   - Desperdício (se houver)
   - Itens vencidos (se houver)
5. INVENTÁRIO (escolhe método):
   - 📸 Foto do caderno com anotações
   - 📝 Digitar texto
   - 📝📸 Ambos
6. Bot envia pro n8n → Claude processa (OCR + Normalização)
7. Bot mostra inventário processado
8. Chef confirma/corrige/adiciona itens
9. Bot coleta fotos entrada e saída
10. Bot mostra resumo final
11. Chef confirma e envia
12. Salvo no Notion ✅
```

## 🎯 Novidades nesta Versão

### ✅ Inventário com Confirmação
- Chef pode enviar **foto do caderno** com anotações
- OCR com Claude Vision extrai ingredientes
- Normalização automática contra lista oficial
- **Chef SEMPRE confirma antes de salvar**
- Pode corrigir quantidades
- Pode adicionar itens esquecidos

### ✅ UX Melhorada
- Botões inline para Sim/Não
- Validação de horários (saída > chegada)
- Normalização automática de horários (1430 → 14:30)
- Mensagens mais claras e diretas
- Emoji para facilitar leitura

### ✅ Busca por Username
- Identificação por `Telegram Username` (não ID)
- Mais confiável e fácil de gerenciar
- Campo no Notion: "Telegram Username" (sem @)

## 📊 Estrutura dos Arquivos

```
~/Desktop/Bot/
├── main.py              # Lógica principal do bot
├── config.py            # Estados e configurações (CORRIGIDO)
├── notion_api.py        # Integrações com Notion (CORRIGIDO)
├── .env                 # Variáveis de ambiente (NÃO commitar)
├── .env.example         # Template do .env
├── requirements.txt     # Dependências (ATUALIZADO)
└── README.md           # Esta documentação
```

## 🐛 Troubleshooting

### Erro: "Token não configurado"

**Solução:**
1. Verifique se o arquivo `.env` existe
2. Confirme que `TELEGRAM_BOT_TOKEN` está preenchido
3. Reinicie o bot

### Chef não consegue iniciar

**Erro:** "Chef não encontrado no sistema"

**Solução:**
1. Verificar se o chef tem `Telegram Username` preenchido no Notion
2. Campo: "Telegram Username" (sem @)
3. Exemplo: `erick_cardeal`

### Bot não lista atendimentos

**Causas comuns:**
- Não há atendimentos nos últimos 7 dias
- Campo "Chef Alocado" não preenchido no Calendário

### Erro ao processar inventário

**Se foto ilegível:**
- Pedir pro chef tirar foto mais clara
- OU digitar o inventário manualmente

**Se processamento falhou:**
- Verificar se n8n está ativo
- Verificar logs do n8n
- Verificar credenciais Claude API

### Erro: ModuleNotFoundError

**Solução:**
```bash
# Ative o ambiente virtual primeiro
source venv/bin/activate

# Reinstale as dependências
pip install -r requirements.txt
```

## 🚀 Deploy no Railway (Produção)

### 📋 Checklist Completo

Veja o [CHECKLIST_DEPLOY_RAILWAY.md](CHECKLIST_DEPLOY_RAILWAY.md) para instruções detalhadas.

### 🎯 Resumo Rápido

1. **Organizar Projeto**
   - Ver [GUIA_ORGANIZACAO_PROJETO.md](GUIA_ORGANIZACAO_PROJETO.md)

2. **Criar Repositório GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Bot relatório chef"
   git remote add origin https://github.com/seu-usuario/bot-relatorio-chef.git
   git push -u origin main
   ```
   **IMPORTANTE:** Nunca faça commit do arquivo `.env` (já está no `.gitignore`)

3. **Deploy no Railway**
   - Acessar https://railway.app/
   - New Project → Deploy from GitHub
   - Selecionar repositório
   - Adicionar variáveis de ambiente (copiar do `.env.example`)
   - Deploy automático

4. **Verificar Logs**
   - Railway Dashboard → Deployments → Ver logs
   - Deve aparecer: `Bot iniciado! 🤖`

### 🔐 Variáveis de Ambiente no Railway

Configure as seguintes variáveis no Railway:

**Obrigatórias:**
- `TELEGRAM_BOT_TOKEN`
- `NOTION_TOKEN`
- `NOTION_CHEFS_DB`
- `NOTION_CLIENTES_DB`
- `NOTION_CALENDARIO_DB`
- `NOTION_RELATORIOS_DB`

**Produção (já configuradas com defaults):**
- `N8N_WEBHOOK_URL_FASE1` (já tem default)
- `N8N_WEBHOOK_URL_FASE2A` (já tem default)
- `N8N_WEBHOOK_URL_FASE2B` (já tem default)

## 📚 Documentação Completa

Ver documentação detalhada no Notion:
https://www.notion.so/Bot-Telegram-Relat-rio-de-Visita-2a8b71fbd8f98021a3ecc09eed2d28ff

## 🔧 Changelog

### v1.1.0 - 12/11/2024
- ✅ **CORREÇÃO CRÍTICA:** Alinhamento de variáveis entre `main.py` e `config.py`
- ✅ Criada classe `NotionAPI` para compatibilidade com `main.py`
- ✅ Adicionadas dependências faltantes: `aiohttp` e `pytz`
- ✅ Criado `.env.example` com todas as variáveis necessárias
- ✅ Mantida retrocompatibilidade com funções antigas

### v1.0.0 - 11/11/2024
- ✅ Primeira versão funcional
- ✅ Bot com fluxo completo de coleta de relatórios
- ✅ Integração com Notion e n8n
- ✅ Processamento de inventário via OCR

## 💡 Suporte

Problemas? Entre em contato com:
- **Operações:** Thaísa/Julio
- **Tech:** Erick

---

**Status:** ✅ Pronto para Produção  
**Última atualização:** 12/11/2024  
**Versão:** 1.1.0
