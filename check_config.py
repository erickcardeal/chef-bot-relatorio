#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de Verificação de Configuração
Verifica se todas as variáveis de ambiente estão configuradas corretamente
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

print("🔍 Verificando configurações...\n")

# Lista de variáveis obrigatórias
required_vars = {
    'TELEGRAM_BOT_TOKEN': 'Token do Bot do Telegram',
    'N8N_WEBHOOK_URL': 'URL do Webhook do n8n',
    'NOTION_TOKEN': 'Token da API do Notion',
    'NOTION_CHEFS_DB': 'ID do Database de Chefs',
    'NOTION_CLIENTES_DB': 'ID do Database de Clientes',
    'NOTION_CALENDARIO_DB': 'ID do Database do Calendário',
}

all_ok = True

for var, description in required_vars.items():
    value = os.getenv(var)
    if value and value != 'seu_token_aqui' and 'xxxxxxxx' not in value:
        print(f"✅ {var}: {description}")
        # Mostra parte do valor (ofusca para segurança)
        if 'TOKEN' in var:
            preview = value[:10] + '...' + value[-5:] if len(value) > 15 else value
        elif 'DB' in var:
            preview = value[:8] + '...' + value[-8:] if len(value) > 16 else value
        else:
            preview = value[:20] + '...' if len(value) > 20 else value
        print(f"   Valor: {preview}\n")
    else:
        print(f"❌ {var}: {description}")
        print(f"   FALTANDO ou não configurado corretamente!\n")
        all_ok = False

print("\n" + "="*50)
if all_ok:
    print("✅ TODAS AS CONFIGURAÇÕES ESTÃO OK!")
    print("\nVocê pode iniciar o bot com:")
    print("   python main.py")
else:
    print("❌ EXISTEM CONFIGURAÇÕES FALTANDO!")
    print("\nPor favor:")
    print("1. Copie o arquivo .env.example para .env")
    print("2. Preencha todas as variáveis com valores reais")
    print("3. Execute este script novamente para verificar")
print("="*50)

# Verificar imports críticos
print("\n🔍 Verificando dependências Python...\n")

try:
    import telegram
    print("✅ python-telegram-bot instalado")
except ImportError:
    print("❌ python-telegram-bot NÃO instalado")
    all_ok = False

try:
    import requests
    print("✅ requests instalado")
except ImportError:
    print("❌ requests NÃO instalado")
    all_ok = False

try:
    import aiohttp
    print("✅ aiohttp instalado")
except ImportError:
    print("❌ aiohttp NÃO instalado")
    all_ok = False

try:
    import pytz
    print("✅ pytz instalado")
except ImportError:
    print("❌ pytz NÃO instalado")
    all_ok = False

if not all_ok:
    print("\n❌ Instale as dependências com:")
    print("   pip install -r requirements.txt")
else:
    print("\n✅ Todas as dependências estão instaladas!")

print("\n" + "="*50)
print("📚 Documentação completa:")
print("https://www.notion.so/Bot-Telegram-Relat-rio-de-Visita-2a8b71fbd8f98021a3ecc09eed2d28ff")
print("="*50)
