#!/bin/bash
# Script para reiniciar o bot

echo "🛑 Parando bot atual..."
pkill -f "python.*main.py"
sleep 2

echo "✅ Bot parado"
echo ""
echo "🚀 Para reiniciar o bot, execute:"
echo "   cd /Users/erickcardealdossantos/Desktop/Bot"
echo "   source venv/bin/activate  # Se usar venv"
echo "   python3 main.py"
echo ""
echo "Ou execute:"
echo "   ./INICIAR_BOT.sh"


