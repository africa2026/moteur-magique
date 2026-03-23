#!/bin/bash
echo "======================================================="
echo "🚀 Démarrage du Moteur de Rédaction Magique v5.0 (Mac)"
echo "======================================================="

# Vérification de Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer depuis python.org"
    exit 1
fi

# Création de l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activation de l'environnement virtuel
source venv/bin/activate

# Installation des dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Vérification d'Ollama
if command -v ollama &> /dev/null; then
    echo "✅ Ollama détecté. Les fonctionnalités IA locales seront actives."
else
    echo "⚠️ Ollama non détecté. Certaines fonctionnalités avancées nécessitent Ollama."
    echo "   Vous pouvez l'installer depuis ollama.com"
fi

# Lancement du serveur
echo "🌟 Démarrage du serveur local..."
echo "👉 Ouvrez votre navigateur à l'adresse : http://localhost:5000"
python backend/src/main.py
