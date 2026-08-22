# Procedura di Aggiornamento Dati Asta

I prezzi, le probabilità di titolarità e i Fanta Valori (FVA) cambiano continuamente fino all'inizio del campionato a causa del calciomercato. 
Segui questi passaggi per aggiornare il dataset locale prima di lanciare i modelli.

## Step 1: Recuperare il Token di Autorizzazione
Il token di FantaLab scade periodicamente per motivi di sicurezza. È l'unica cosa che devi aggiornare manualmente.

1. Apri Google Chrome/Safari e accedi a [FantaLab](https://app.fantalab.it/).
2. Apri i **Developer Tools** (Premi `F12` o `Ctrl+Shift+I` / `Cmd+Option+I`).
3. Vai nella tab **Network** (Rete).
4. Ricarica la pagina (Premi `F5`).
5. Clicca su una chiamata qualsiasi (es. `get-new-prices` o `ratings`).
6. Scorri nel pannello a destra fino alla sezione **Request Headers**.
7. Cerca la voce **`Authorization`**. 
8. Copia il valore intero (solitamente inizia con `Bearer ...` o è una lunga stringa alfanumerica).

## Step 2: Inserire il Token nel file .env
1. Apri il file `.env` nella root del progetto.
2. Sostituisci il valore della variabile `FANTALAB_TOKEN` con il token appena copiato:
   `FANTALAB_TOKEN="Bearer TUO_NUOVO_TOKEN"`
3. Salva il file.