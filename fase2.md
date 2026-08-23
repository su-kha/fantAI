# Fase 2: Motore Statistico e Calcolo VORP

## Obiettivo Principale
Abbandonare le valutazioni soggettive e costruire il cuore matematico del sistema. Calcoleremo gli Expected Points (EP) stagionali di ogni giocatore, traducendoli nel parametro sabermetrico VORP (Value Over Replacement Player). Questo valore genererà un "Prezzo AI" puro, che incrociato con l'hype pubblico (FVA) farà emergere i veri differenziali (giocatori sottovalutati o sopravvalutati).

---

## Gestione Avanzata del Contesto (Context Bias)
Per evitare distorsioni nei dati (giocatori trasferiti in top club o riserve che l'anno scorso erano titolari altrove), il motore applica due regole auree:
1. **Presenze Stimate (Futuro > Passato):** Il calcolo dei punti non si basa sui minuti giocati l'anno scorso, ma sull'Indice di Titolarità attuale di FantaLab, scalato su 38 partite. Questo riflette le reali gerarchie di oggi, penalizzando chi ha perso il posto da titolare.
2. **Il Caso Portieri e Trasferimenti:** Il talento del singolo (dribbling, passaggi) viene estratto dallo storico FBRef, ma viene calibrato tramite l'Expected Fantamedia attuale per assorbire l'impatto della nuova squadra. Per i portieri, fortemente dipendenti dalla solidità del reparto difensivo, la proiezione attuale avrà priorità assoluta rispetto ai gol subiti nel passato in altre squadre.

---

## Pipeline di Calcolo

### Passaggio 2.1: Calcolo degli Expected Points (EP)
* **Azione:** Stimare i punti stagionali puri. Creeremo una Fantamedia Ibrida che fonde la Media Storica (FBRef) per il talento puro e l'Expected (FantaLab) per il contesto attuale. Moltiplicheremo questo valore per le presenze stimate.

### Passaggio 2.2: Il Boost del Modificatore Difesa
* **Azione:** Trasformare la probabilità di un buon voto in punti reali. Isoleremo la Media Voto pura: se MV >= 6.15, calcoleremo l'impatto sul modificatore proporzionato alle presenze stimate, aggiungendo questi "Punti Nascosti" agli EP base dei difensori.

### Passaggio 2.3: Determinazione della Baseline (Il Replacement)
* **Azione:** Individuare il livello zero. In una lega a 10 partecipanti, calcoleremo il punteggio dell'ultimo titolare/riserva utile per ogni ruolo (es. il 75esimo difensore o il 55esimo attaccante). Questo punteggio farà da spartiacque tra i giocatori utili e i panchinari da 1 credito.

### Passaggio 2.4: Calcolo VORP e Distribuzione Budget
* **Azione:** Generare il prezzo d'asta. Calcoleremo VORP = Punti Attesi - Baseline Ruolo. Sottrarremo dal budget totale della lega i crediti minimi per riempire le panchine, dividendo il capitale rimanente per la somma di tutti i VORP. Questo fisserà il tasso di cambio esatto da Punti VORP a Crediti AI.

---

## Rischi e Mitigazioni

1. **Inflazione dei Difensori:** Il bonus modificatore potrebbe drogare troppo i prezzi dei difensori top, sbilanciando il budget. 
   * **Mitigazione:** Applicheremo una soglia di attivazione severa e un moltiplicatore logico per simulare l'impatto reale.
2. **Gestione delle Neopromosse (Cold-Start):** Mancanza totale di storico affidabile per chi arriva dalla Serie B. 
   * **Mitigazione:** Il sistema farà un fallback automatico sull'Expected Fantamedia generata da FantaLab, garantendo una valutazione coerente col mercato di Serie A attuale.