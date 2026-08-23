# Progetto: AI Fanta-Agent (Asta Sequenziale & Modificatore)
**Timeline stimata:** 26 Giorni (Asta: 17 Settembre)

---

## Fase 1: Data Ingestion & Entity Resolution (Giorni 1-7)

* **Acquisizione Dati Multidominio:** Estrazione degli storici voti, listoni attuali e quotazioni FVM (Fanta Valore Mercato). Integrazione da FBRef delle statistiche per 90 minuti (xG, xA, Key Passes), incluse le leghe estere per mappare i nuovi arrivati.
* **Entity Resolution Engine:** Sviluppo dello script di fuzzy matching (es. libreria `thefuzz`) per normalizzare i nomi dei giocatori da fonti diverse e assegnare un ID univoco (il vero collo di bottiglia del data engineering sportivo).
* **Feature Engineering & Proxy Estero:** Calcolo di medie mobili e deviazione standard dei voti storici. Per i nuovi arrivati, applicazione di fattori di conversione alle metriche estere (es. un xG/90 in Eredivisie pesa diversamente da uno in Premier League).

---

## Fase 2: Motore Statistico e VORP (Giorni 8-14)

* **Expected Points (EP):** Addestramento di un modello (o algoritmo euristico) per stimare i punti totali, usando il FVM attuale come *prior* per correggere eventuali anomalie sui giocatori senza storico in Serie A.
* **Probabilità Modificatore:** Analisi della distribuzione dei voti puri dei difensori per estrarre la probabilità esatta di ottenere $\ge 6.25$ o $\ge 6.5$. Trasformazione di questa probabilità in Expected Points extra per la difesa.
* **Calcolo VORP (Value Over Replacement Player):** Conversione degli EP in un valore monetario (*Willingness to Pay*), misurando l'impatto del giocatore rispetto al peggior titolare stimato del suo ruolo all'interno della lega.

---

## Fase 3: Ottimizzazione Sequenziale Dinamica (Giorni 15-21)

* **Budgeting a Cascata (P $\rightarrow$ D $\rightarrow$ C $\rightarrow$ A):** Abbandono del knapsack globale statico per un'allocazione a target flessibili per ruolo. Se si risparmia in un ruolo precedente (es. Difesa), il surplus viene redistribuito matematicamente sui ruoli successivi (Centrocampo/Attacco).
* **Monitoraggio Inflazione (Opponent Tracking):** Tracciamento dei crediti residui degli avversari in tempo reale. Se il mercato sovrapaga i giocatori all'inizio, l'agente deve aggiustare i prezzi stimati dei top player rimanenti.
* **Ricalcolo VORP Real-Time:** Aggiornamento live del valore dei giocatori disponibili basato sugli slot vuoti rimanenti nella tua rosa e nei roster avversari.


* GESTIRE I VICE (PER PORTIERI AD ESEMPIO)
* GESTIRE COPPIE DI PORTIERI IN CASA

---

## Fase 4: Integrazione Live e Fail-Safe (Giorni 22-26)

* **Core CLI:** Creazione di un'interfaccia da terminale a latenza zero per input rapidi (es. `buy kvara 150 team_b`) con output immediato delle prossime *best action*.
* **Listener Asta Live (Opzionale):** Script basato su WebSocket o automazione browser (es. Playwright) per catturare i rilanci e gli acquisti in tempo reale dalla piattaforma dell'asta (es. FantaLab), sincronizzando lo stato dell'agente automaticamente.
* **Persistenza e Mock Draft:** Salvataggio continuo e automatico dello stato dell'asta (es. in SQLite o JSON) per evitare disastri in caso di crash. Sessioni di simulazione (mock draft) per testare i riflessi e la stabilità del sistema sotto stress.