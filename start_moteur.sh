#!/bin/bash

echo "🚀 Avvio Moteur de Rédaction Magique v4.0..."

# 1. Setup Backend
echo "📦 Configurazione Backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate || echo "Warning: Could not activate venv, using system python"

echo "Installing dependencies..."
pip install -r requirements.txt

# 2. Avvio
echo "🌟 Avvio del sistema..."
echo "Il backend sarà disponibile su http://localhost:5000"
echo "Apri il browser a questo indirizzo una volta avviato."

python3 src/main.py
