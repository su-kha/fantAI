# FantAI - AI Fanta-Agent 🤖⚽️

FantAI è un agente intelligente progettato per assistere e automatizzare le decisioni durante l'asta del Fantacalcio (Serie A). 
Sfruttando metriche di *Value Over Replacement Player* (VORP), modelli statistici sui punti attesi e algoritmi di ottimizzazione dinamica (Knapsack), l'agente calcola il valore reale di mercato dei giocatori e suggerisce le migliori allocazioni di budget in tempo reale.

## 🚀 Caratteristiche Principali

- **Data Ingestion Dinamica:** Scraping delle API (es. FantaLab) per listoni, FVA (Fanta Valore Asta) e probabilità aggiornate.
- **Entity Resolution & Storage:** Mapping univoco dei giocatori tramite ID proprietari per evitare conflitti di omonimia e tracking dello storico delle ultime stagioni.
- **Motore Statistico VORP:** Calcolo del "Willingness to Pay" basato sulle differenze marginali tra i titolari e i panchinari di lega.
- **Dynamic Budget Allocation:** Ricalcolo live del budget durante le chiamate sequenziali (Portieri -> Difensori -> Centrocampisti -> Attaccanti).



#### TODO: CONTROLLARE QUANTO E' FUTURE PROOF