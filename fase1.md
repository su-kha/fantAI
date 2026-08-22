# Fase 1: Data Ingestion & Entity Resolution

## Obiettivo Principale
Ottenere una pipeline automatizzata (`update_pipeline.py`) che genera un dataset unificato e "pronto per il calcolo". Ogni giocatore del listone attuale di Serie A avrà un ID univoco associato alle sue statistiche storiche (Serie A) o convertite (estero), e alla sua quotazione di mercato (FVA) aggiornata.

---

## Passaggio 1.1: Scraping del Listone e FVA (Dinamico)
Questo modulo deve poter girare quotidianamente per recepire i trasferimenti e le oscillazioni di hype.
* **Azione:** Sviluppare uno scraper per scaricare il listone ufficiale aggiornato e i FVA (Fanta Valore Asta).
* **Dati da estrarre:** Nome, Squadra, Ruolo, Quotazione Iniziale, FVA (parametrizzato per la vostra lega, es. 8 partecipanti, 500 crediti).
* **Output:** `data/01_raw/listone_corrente.csv` (Sovrascritto a ogni esecuzione).

## Passaggio 1.2: Acquisizione Storico Serie A (Statico)
I dati degli anni precedenti non cambiano. Si esegue una sola volta.
* **Azione:** Recuperare i log delle ultime 2-3 stagioni (voti puri, modificatori, presenze).
* **Feature Engineering:** Calcolo di: 
  * Media Voto e Fantamedia.
  * Deviazione Standard del voto.
  * $P(Voto \ge 6.25)$ e $P(Voto \ge 6.5)$ per stimare il peso del modificatore difesa.
  * Affidabilità (tasso di assenza/S.V.).
* **Output:** `data/02_interim/storico_serie_a.csv`.

## Passaggio 1.3: Acquisizione Dati FBRef (Statico)
Fondamentale per superare il bias dei voti storici e valutare i nuovi arrivati (Cold-Start Problem).
* **Azione:** Scraping (es. tramite `soccerdata`) delle statistiche avanzate delle ultime 2 stagioni per i top 5 campionati + Serie B.
* **Filtri:** Esclusione di giocatori con meno di 500 minuti giocati per evitare outlier statistici.
* **Dati (Normalizzati per 90 min):** xG, xA, Key Passes, Big Chances Missed.
* **Output:** `data/02_interim/stats_fbref_90.csv`.

## Passaggio 1.4: Entity Resolution Engine (La Pipeline di Merge)
Il cuore della Fase 1. Unisce i dati dinamici del listone con gli storici statici.
* **Azione:** Allineare i nomi da fonti diverse (es. "Khvicha Kvaratskhelia" da FBRef vs "KVARATSKHELIA" dal listone).
* **Logica a cascata:**
  1. *Exact Match:* Pulizia stringhe (lowercase, no accenti) e join diretto.
  2. *Fuzzy Match:* Utilizzo di `thefuzz` (Levenshtein Distance) > 85% di similarità, usando la "Squadra" come chiave di validazione.
  3. *Dictionary Lookup:* Applicazione di un file `manual_mapping.json` per i casi storici salvati.
  4. *Human in the Loop:* Se lo script trova nuovi giocatori non matchati sotto la soglia di sicurezza, li stampa a terminale per un inserimento manuale, aggiornando automaticamente il `manual_mapping.json`.
* **Output Finale:** `data/03_processed/master_dataset.csv`.

---

## Rischi e Mitigazioni
1. **Dati Mancanti/Outlier:** Verranno applicate soglie minime di minutaggio (es. min 500 minuti) per validare le metriche per 90 minuti.
2. **Cambi di Ruolo Storici:** Un giocatore listato difensore l'anno scorso potrebbe essere centrocampista oggi. *Mitigazione:* Il ruolo ufficiale farà sempre fede a `listone_corrente.csv`.
3. **Mantenibilità del Mapping:** I nomi sudamericani e le abbreviazioni manderanno in crisi il fuzzy match. *Mitigazione:* Il file `manual_mapping.json` agirà da "memoria": ogni lavoro manuale fatto oggi non dovrà essere ripetuto la mattina del 17 settembre quando aggiornerai il listone.