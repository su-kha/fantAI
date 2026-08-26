import pandas as pd
import json
import os
from dotenv import load_dotenv

SLOT_ROSA = {'P': 3, 'D': 8, 'C': 8, 'A': 6}

def init_auction_state():
    print("Inizializzazione Stato dell'Asta e Calcolo Budget Dinamici...\n")
    
    load_dotenv()
    budget_singolo = int(os.getenv('BUDGET_LEGA', 500))
    partecipanti = int(os.getenv('PARTECIPANTI_LEGA', 10))
    
    try:
        df = pd.read_csv("data/04_results/listone_vorp_prices.csv")
    except FileNotFoundError:
        raise FileNotFoundError("Listone VORP non trovato. Esegui prima la Fase 2.")

    starter_reali = {
        'P': int(partecipanti * 1.0),
        'D': int(partecipanti * 3.5),
        'C': int(partecipanti * 3.5),
        'A': int(partecipanti * 2.5)
    }
    
    vorp_per_reparto = {}
    vorp_totale_lega = 0
    
    for ruolo, rank_soglia in starter_reali.items():
        df_ruolo = df[df['ruolo'] == ruolo].sort_values(by='vorp', ascending=False)
        somma_vorp = df_ruolo.head(rank_soglia)['vorp'].sum()
        vorp_per_reparto[ruolo] = somma_vorp
        vorp_totale_lega += somma_vorp

    budget_bloccato = sum(SLOT_ROSA.values())
    budget_discrezionale = budget_singolo - budget_bloccato
    
    budget_target = {}
    for ruolo in ['P', 'D', 'C', 'A']:
        peso_reparto = vorp_per_reparto[ruolo] / vorp_totale_lega if vorp_totale_lega > 0 else 0
        budget_target[ruolo] = round((budget_discrezionale * peso_reparto) + SLOT_ROSA[ruolo])

    print("📊 TARGET DI BUDGET CALCOLATI DAL MODELLO:")
    for ruolo in ['P', 'D', 'C', 'A']:
        peso_reparto = vorp_per_reparto[ruolo] / vorp_totale_lega if vorp_totale_lega > 0 else 0
        print(f" - {ruolo}: {budget_target[ruolo]} crediti ({peso_reparto*100:.1f}%)")

    differenza = budget_singolo - sum(budget_target.values())
    if differenza != 0:
        budget_target['A'] += differenza

    # --- NOVITÀ: GENERAZIONE AVVERSARI INDIVIDUALI ---
    avversari_dict = {}
    for i in range(1, partecipanti): # Crea N-1 avversari
        nome_avversario = f"Avversario_{i}"
        avversari_dict[nome_avversario] = {
            "budget_residuo": budget_singolo,
            "slot_residui": SLOT_ROSA.copy(),
            "giocatori_acquistati": []
        }

    auction_state = {
        "config": {
            "budget_iniziale": budget_singolo,
            "partecipanti": partecipanti,
            "slot_totali": SLOT_ROSA
        },
        "mio_team": {
            "budget_residuo": budget_singolo,
            "slot_residui": SLOT_ROSA.copy(),
            "target_spesa": budget_target,
            "giocatori_acquistati": []
        },
        "avversari": avversari_dict
    }

    os.makedirs('data/05_auction', exist_ok=True)
    with open('data/05_auction/state.json', 'w', encoding='utf-8') as f:
        json.dump(auction_state, f, indent=4)
        
    print(f"✅ Stato dell'asta inizializzato con 1 Mio Team e {partecipanti-1} Avversari separati.")

if __name__ == "__main__":
    init_auction_state()