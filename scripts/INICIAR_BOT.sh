#!/bin/bash
# Script para iniciar o bot

cd /Users/erickcardealdossantos/Desktop/Bot

# Verificar se venv existe
if [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Verificar se há processo rodando
if pgrep -f "python.*main.py" > /dev/null; then
    echo "⚠️ Bot já está rodando!"
    echo "Para reiniciar, execute: ./REINICIAR_BOT.sh"
    exit 1
fi

echo "🚀 Iniciando bot..."
python3 main.py


