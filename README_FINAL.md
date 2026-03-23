# Moteur de Rédaction Magique v4.0 - Arena Edition (FINAL)
**Rev. Alphonse Owoudou, PhD**

Questa è la versione finale e pulita del sistema, con tutti i dati simulati rimossi e la ricerca reale attivata.

## 🚀 Avvio Rapido

### 1. Backend (Cervello Centrale)
Il backend gestisce la ricerca multi-fonte, l'analisi semantica e l'integrazione con Ollama.

```bash
cd backend
pip install -r requirements.txt
python src/main.py
```
Il server si avvierà su `http://localhost:5000`.

### 2. Frontend (Knowledge Arena)
L'interfaccia utente gamificata per la ricerca e l'analisi.

```bash
cd frontend
npm install
npm run dev
```
L'applicazione sarà accessibile su `http://localhost:3000`.

## ✨ Funzionalità Attive (NO MOCK DATA)

1. **Ricerca Reale**: Connessione diretta a 12 motori accademici + Salesian.online
2. **Corpus Salesiano**: Indicizzazione reale delle Costituzioni e Regolamenti
3. **Analisi Semantica**: Comprensione del contesto multilingue (IT, FR, EN, ES, PT)
4. **Google Drive**: Integrazione predisposta (richiede configurazione OAuth reale)
5. **Upload Documenti**: Elaborazione PDF avanzata con estrazione robusta

## 🔧 Note Tecniche

- **Motore di Ricerca**: Utilizza DuckDuckGo limitato al dominio `salesian.online` per risultati affidabili senza API proprietarie costose.
- **LLM Offline**: Richiede Ollama installato localmente per le funzionalità offline.
- **Database**: I documenti caricati vengono salvati in memoria e su disco locale.

---
*Sviluppato da Manus AI per Rev. Alphonse Owoudou*
