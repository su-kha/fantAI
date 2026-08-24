# FantAI - Guida Rapida Operativa (Fase 1 e 2)

## FASE 1: Data Ingestion & Entity Resolution

### 1. Ottenere il Token FantaLab
Per scaricare i dati è necessario un token di autorizzazione valido. Essendo un'API privata, va recuperato manualmente dal browser:

1. Apri FantaLab su Chrome o Edge ed effettua il login.
2. Premi F12 per aprire gli Strumenti per Sviluppatori (Developer Tools).
3. Vai nella scheda "Rete" (Network).
4. Ricarica la pagina del Listone.
5. Cerca una richiesta (nella colonna Name) verso l'API, ad esempio qualcosa che contiene "listone" o "players".
6. Cliccaci sopra, vai nella scheda "Headers" (Intestazioni) e scendi fino a "Request Headers".
7. Trova la voce "Authorization". Vedrai una stringa del tipo: `Bearer eyJhbG...`
8. Copia SOLO la parte lunga del codice (tutto ciò che c'è dopo "Bearer "). Quello è il tuo token.

### 2. Configurazione Iniziale
Crea un file denominato `.env` nella directory principale del progetto e inserisci i seguenti parametri:

    FANTALAB_TOKEN=il_tuo_token_copiato_al_passaggio_precedente
    BUDGET_LEGA=500
    PARTECIPANTI_LEGA=10
    USO_MODIFICATORE=True

### 3. Esecuzione della Pipeline (Data Ingestion)
Esegui i seguenti comandi nel terminale, in ordine rigoroso, utilizzando il package manager `uv`:

**Step 1: Scaricare il listone FantaLab**

    uv run src/data/fetch_listone.py

**Step 2: Scaricare lo storico dei voti**

    uv run src/data/fetch_storico.py

**Step 3: Scaricare le statistiche avanzate (FBRef)**

    uv run src/data/fetch_fbref.py

**Step 4: Eseguire Merge ed Entity Resolution**

    uv run src/data/merge_datasets.py

### 4. Gestione del QA Report e Manual Mapping
Al termine dello Step 4, il terminale mostrerà un **QA Report**. Segui questi passaggi per assicurarti che i dati siano perfettamente allineati:

* **Verifica anomalie:** Controlla la lista dei *"Top Player non matchati"* e l'audit dei match eseguiti in automatico.
* **Aggiorna il mapping:** Se un giocatore chiave manca o è stato associato in modo errato, apri il file `data/manual_mapping.json` e aggiungi la corrispondenza esatta ("Chiave FantaLab": "Nome Completo FBRef").

*Esempio di aggiornamento nel JSON:*

    {
        "Dovbyk": "Artem Dovbyk",
        "Castro S.": "Santiago Castro",
        "Di Lorenzo": "Giovanni Di Lorenzo"
    }

* **Riavvia il Merge:** Salva il file JSON e lancia nuovamente `uv run src/data/merge_datasets.py`. Ripeti l'operazione finché il QA Report non risulta pulito. A questo punto viene generato il `master_dataset.csv`.

---

## FASE 2: Motore Statistico e Calcolo Prezzi AI (VORP)

Questa fase trasforma i dati grezzi in valutazioni economiche reali. L'algoritmo non utilizza pesi fissi, ma esegue una **Grid Search automatica** (Testing Suite) per testare decine di scenari (peso storico vs expected, soglie di titolarità, moltiplicatore modificatore) e selezionare la configurazione matematica ottimale.

### 1. Esecuzione della Diagnostics Suite
Esegui il calcolo del VORP (Value Over Replacement Player) e la generazione dei prezzi lanciando il super-script di validazione:

    uv run src/models/diagnostics_suite.py

### 2. Analisi del Report di Validazione
Il terminale non si limiterà a calcolare i prezzi, ma sceglierà in autonomia i parametri migliori e stamperà una **Pagella Diagnostica**. Controlla questi due indicatori per assicurarti che il mercato generato sia sano:
* **Correlazione di Rank (Spearman):** Un valore ottimale oscilla tra `0.70` e `0.85`. Conferma che l'AI comprende le gerarchie del mercato umano (FVA) ma se ne discosta abbastanza da scovare inefficienze ("I veri Affari").
* **Distribuzione della Ricchezza (Pareto):** Il modello ti dirà quanto budget assorbe matematicamente il 20% dei Top Player. La statistica spingerà questo valore oltre il 90% (strategia *Stars and Scrubs*), confermando che al Fantacalcio i veri campioni valgono quasi tutto il montepremi a disposizione.

### 3. Il Listone Definitivo
Al termine dello script, il sistema salverà automaticamente il file finale con le valutazioni ottimali in:

    data/04_results/listone_vorp_prices.csv

Questo file contiene il **Valore AI Intrinseco** perfetto per ogni giocatore e il **Differenziale** (Valore AI - FVA Mercato). I giocatori con il differenziale positivo più alto sono le nostre "prede" per l'asta.