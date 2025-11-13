import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# ===== TELEGRAM =====
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# Alias para compatibilidade com main.py
TELEGRAM_TOKEN = TELEGRAM_BOT_TOKEN

# ===== n8n =====
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')
# Webhook específico para FASE 1 (dados básicos + fotos)
N8N_WEBHOOK_URL_FASE1 = os.getenv('N8N_WEBHOOK_URL_FASE1', 'https://chefpessoal.app.n8n.cloud/webhook/bot-relatorio-chef-fase1')
# Webhook específico para FASE 2A (processar inventário) - apenas processa, não salva
N8N_WEBHOOK_URL_FASE2A = os.getenv('N8N_WEBHOOK_URL_FASE2A', 'https://chefpessoal.app.n8n.cloud/webhook/fase2-processar')
# Webhook específico para FASE 2B (salvar inventário no Notion) - atualiza página existente
N8N_WEBHOOK_URL_FASE2B = os.getenv('N8N_WEBHOOK_URL_FASE2B', 'https://chefpessoal.app.n8n.cloud/webhook/fase2-salvar')
# Webhook específico para FASE 2 (inventário) - mantido para compatibilidade (deprecated)
N8N_WEBHOOK_URL_FASE2 = os.getenv('N8N_WEBHOOK_URL_FASE2') or N8N_WEBHOOK_URL

# ===== Processamento de Inventário =====
# Se True: processa localmente usando Claude API
# Se False: usa n8n webhook (produção)
PROCESSAR_INVENTARIO_LOCAL = os.getenv('PROCESSAR_INVENTARIO_LOCAL', 'false').lower() == 'true'
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# ===== NOTION =====
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
# Alias para compatibilidade com main.py
NOTION_API_KEY = NOTION_TOKEN

# Database IDs
NOTION_CHEFS_DB = os.getenv('NOTION_CHEFS_DB')
NOTION_CLIENTES_DB = os.getenv('NOTION_CLIENTES_DB')
NOTION_CALENDARIO_DB = os.getenv('NOTION_CALENDARIO_DB')
NOTION_RELATORIOS_DB = os.getenv('NOTION_RELATORIOS_DB')

# Aliases para compatibilidade com main.py
NOTION_DATABASE_ID = NOTION_CLIENTES_DB
NOTION_CALENDAR_DB_ID = NOTION_CALENDARIO_DB
NOTION_CHEFS_DB_ID = NOTION_CHEFS_DB

# Headers Notion
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}
