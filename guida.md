# FantAI - Guida Rapida Operativa (Fase 1)

### 1. Configurazione Iniziale
Crea un file denominato .env nella root del progetto inserendo i seguenti parametri della tua lega:
BUDGET_LEGA=500
PARTECIPANTI_LEGA=10

### 2. Esecuzione della Pipeline in Ordine Stretto
Esegui i seguenti comandi uno alla volta tramite il package manager uv:

- Scaricare il listone FantaLab:
  uv run src/data/fetch_listone.py

- Scaricare lo storico dei voti:
  uv run src/data/fetch_storico.py

- Scaricare le statistiche avanzate (FBRef):
  uv run src/data/fetch_fbref.py

- Eseguire il Merge e l'Entity Resolution:
  uv run src/data/merge_datasets.py

### 3. Gestione del QA Report e del Manual Mapping
Dopo aver eseguito lo Step 4, osserva attentamente il terminale per verificare il QA Report:

- Se un Top Player (FVA > 15) risulta tra i "Top Player non matchati" o se l'audit automatico mostra un accoppiamento errato, apri il file data/manual_mapping.json.
- Aggiungi la corrispondenza esatta tra la chiave di FantaLab e il nome completo registrato su FBRef (es. "Dovbyk": "Artem Dovbyk").
- Rilancia lo Step 4 (uv run src/data/merge_datasets.py) finché il report non risulta completamente pulito e privo di anomalie sui giocatori chiave.

Una volta completati questi passaggi con successo, la Fase 1 è conclusa e il sistema è pronto per il calcolo VORP (Fase 2).