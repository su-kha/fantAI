## Fase 3: Ottimizzazione Sequenziale Dinamica e Strategia d'Asta Live (Giorni 15-21)

Questa fase trasforma i valori statici della Fase 2 in limiti di spesa reali (Max Bid), tenendo conto del budget rimanente, degli slot vuoti e delle azioni degli avversari.

### 3.1 Calcolo Automatico dei Budget per Reparto
Il sistema non richiederà input umani per decidere quanto spendere per ruolo. All'avvio, il modello calcolerà la distribuzione ideale del budget:
1. **Aggregazione VORP:** Somma del VORP totale dei giocatori "Titolari Base" per ogni ruolo (P, D, C, A).
2. **Distribuzione Frazionaria:** Suddivisione del budget iniziale (es. 500 crediti) nei 4 reparti proporzionalmente al VORP generato.
3. **Inizializzazione Stato:** Creazione del database locale (Stato dell'Asta) che traccia il budget assegnato a ciascun reparto per il nostro team.

### 3.2 Motore di Ricalcolo Dinamico (Dynamic Pricer)
Ogni volta che un giocatore viene acquistato (da noi o dagli avversari), il motore aggiorna le stime:
1. **Spillover (Effetto Cascata):** Se un target viene acquistato a un prezzo inferiore al suo Valore AI, il credito risparmiato viene spalmato proporzionalmente sui reparti successivi.
2. **Calcolo del Max Bid Reale:** Il sistema incrocia il Valore AI del giocatore con i crediti residui del nostro team e gli slot vuoti. Il suggerimento di offerta non supererà mai la soglia che impedirebbe di completare la rosa a 1 credito per giocatore.
3. **Gestione Incroci Portieri:** Identificazione automatica del vice-portiere o calcolo del bonus VORP (+15%) per coppie di portieri con perfetta alternanza casa/trasferta.

### 3.3 Tracking Avversari e Indice di Inflazione
Il sistema monitorerà lo stato finanziario della lega per sfruttare i momenti di carenza di liquidità:
1. **Aggiornamento Portafogli:** Inserimento rapido degli acquisti superiori a 5 crediti per tracciare il budget residuo dei singoli avversari.
2. **Deflazione Automatica:** Se gli avversari esauriscono i crediti rapidamente (pagando sovrapprezzi per i primi giocatori), l'Indice di Inflazione scende sotto 1.0. Il sistema abbasserà il Max Bid consigliato per i Top Player rimanenti, permettendoti di acquistarli al ribasso.

### 3.4 Interfaccia Live (Streamlit Dashboard)
Creazione di un'applicazione web locale ottimizzata per la velocità operativa durante l'asta:
1. **Barra di Ricerca Rapida:** Autocomplete istantaneo per trovare il giocatore chiamato dal banditore.
2. **Pannello Suggerimenti:** Visualizzazione immediata di 3 valori: FVA Mercato (Costo Stimato), Valore AI (Valore Intrinseco), e Max Bid (Il tuo limite massimo invalicabile in quel momento).
3. **Registrazione Acquisto:** Pulsanti rapidi "Mio" o "Avversario" per registrare la transazione, aggiornare il database e innescare il ricalcolo degli step 3.2 e 3.3.