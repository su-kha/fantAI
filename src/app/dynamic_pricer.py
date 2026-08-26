import pandas as pd
import json
import os

STATE_PATH = "data/05_auction/state.json"
LISTONE_PATH = "data/04_results/listone_vorp_prices.csv"

# Matrice sovrapposizioni portieri (partite in casa in contemporanea)
MATRICE_PORTIERI = {
    'Atalanta': {'Bologna': 6, 'Cagliari': 6, 'Como': 10, 'Fiorentina': 8, 'Frosinone': 5, 'Genoa': 8, 'Inter': 8, 'Juventus': 10, 'Lazio': 12, 'Lecce': 13, 'Milan': 11, 'Monza': 7, 'Napoli': 11, 'Parma': 7, 'Roma': 7, 'Sassuolo': 14, 'Torino': 9, 'Udinese': 10, 'Venezia': 9},
    'Bologna': {'Atalanta': 6, 'Cagliari': 9, 'Como': 12, 'Fiorentina': 10, 'Frosinone': 11, 'Genoa': 7, 'Inter': 9, 'Juventus': 11, 'Lazio': 7, 'Lecce': 6, 'Milan': 10, 'Monza': 13, 'Napoli': 6, 'Parma': 11, 'Roma': 12, 'Sassuolo': 6, 'Torino': 8, 'Udinese': 10, 'Venezia': 7},
    'Cagliari': {'Atalanta': 6, 'Bologna': 9, 'Como': 11, 'Fiorentina': 6, 'Frosinone': 8, 'Genoa': 10, 'Inter': 12, 'Juventus': 8, 'Lazio': 11, 'Lecce': 10, 'Milan': 7, 'Monza': 9, 'Napoli': 12, 'Parma': 10, 'Roma': 8, 'Sassuolo': 8, 'Torino': 11, 'Udinese': 9, 'Venezia': 6},
    'Como': {'Atalanta': 10, 'Bologna': 12, 'Cagliari': 11, 'Fiorentina': 6, 'Frosinone': 6, 'Genoa': 7, 'Inter': 10, 'Juventus': 8, 'Lazio': 10, 'Lecce': 13, 'Milan': 9, 'Monza': 9, 'Napoli': 7, 'Parma': 7, 'Roma': 9, 'Sassuolo': 11, 'Torino': 11, 'Udinese': 8, 'Venezia': 7},
    'Fiorentina': {'Atalanta': 8, 'Bologna': 10, 'Cagliari': 6, 'Como': 6, 'Frosinone': 10, 'Genoa': 8, 'Inter': 10, 'Juventus': 11, 'Lazio': 6, 'Lecce': 6, 'Milan': 9, 'Monza': 12, 'Napoli': 7, 'Parma': 12, 'Roma': 13, 'Sassuolo': 7, 'Torino': 8, 'Udinese': 11, 'Venezia': 11},
    'Frosinone': {'Atalanta': 5, 'Bologna': 11, 'Cagliari': 8, 'Como': 6, 'Fiorentina': 10, 'Genoa': 14, 'Inter': 10, 'Juventus': 9, 'Lazio': 7, 'Lecce': 7, 'Milan': 9, 'Monza': 7, 'Napoli': 6, 'Parma': 11, 'Roma': 12, 'Sassuolo': 6, 'Torino': 10, 'Udinese': 10, 'Venezia': 13},
    'Genoa': {'Atalanta': 8, 'Bologna': 7, 'Cagliari': 10, 'Como': 7, 'Fiorentina': 8, 'Frosinone': 14, 'Inter': 12, 'Juventus': 5, 'Lazio': 9, 'Lecce': 8, 'Milan': 7, 'Monza': 7, 'Napoli': 10, 'Parma': 9, 'Roma': 10, 'Sassuolo': 7, 'Torino': 14, 'Udinese': 7, 'Venezia': 12},
    'Inter': {'Atalanta': 8, 'Bologna': 9, 'Cagliari': 12, 'Como': 10, 'Fiorentina': 10, 'Frosinone': 10, 'Genoa': 12, 'Juventus': 7, 'Lazio': 7, 'Lecce': 8, 'Milan': 0, 'Monza': 7, 'Napoli': 10, 'Parma': 13, 'Roma': 12, 'Sassuolo': 4, 'Torino': 12, 'Udinese': 12, 'Venezia': 8},
    'Juventus': {'Atalanta': 10, 'Bologna': 11, 'Cagliari': 8, 'Como': 8, 'Fiorentina': 11, 'Frosinone': 9, 'Genoa': 5, 'Inter': 7, 'Lazio': 13, 'Lecce': 12, 'Milan': 12, 'Monza': 10, 'Napoli': 12, 'Parma': 10, 'Roma': 6, 'Sassuolo': 10, 'Torino': 0, 'Udinese': 9, 'Venezia': 8},
    'Lazio': {'Atalanta': 12, 'Bologna': 7, 'Cagliari': 11, 'Como': 10, 'Fiorentina': 6, 'Frosinone': 7, 'Genoa': 9, 'Inter': 7, 'Juventus': 13, 'Lecce': 13, 'Milan': 12, 'Monza': 7, 'Napoli': 16, 'Parma': 7, 'Roma': 0, 'Sassuolo': 12, 'Torino': 6, 'Udinese': 8, 'Venezia': 8},
    'Lecce': {'Atalanta': 13, 'Bologna': 6, 'Cagliari': 10, 'Como': 13, 'Fiorentina': 6, 'Frosinone': 7, 'Genoa': 8, 'Inter': 8, 'Juventus': 12, 'Lazio': 13, 'Milan': 11, 'Monza': 6, 'Napoli': 11, 'Parma': 4, 'Roma': 6, 'Sassuolo': 14, 'Torino': 7, 'Udinese': 7, 'Venezia': 9},
    'Milan': {'Atalanta': 11, 'Bologna': 10, 'Cagliari': 7, 'Como': 9, 'Fiorentina': 9, 'Frosinone': 9, 'Genoa': 7, 'Inter': 0, 'Juventus': 12, 'Lazio': 12, 'Lecce': 11, 'Monza': 12, 'Napoli': 9, 'Parma': 6, 'Roma': 7, 'Sassuolo': 15, 'Torino': 7, 'Udinese': 7, 'Venezia': 11},
    'Monza': {'Atalanta': 7, 'Bologna': 13, 'Cagliari': 9, 'Como': 9, 'Fiorentina': 12, 'Frosinone': 7, 'Genoa': 7, 'Inter': 7, 'Juventus': 10, 'Lazio': 7, 'Lecce': 6, 'Milan': 12, 'Napoli': 10, 'Parma': 9, 'Roma': 12, 'Sassuolo': 10, 'Torino': 9, 'Udinese': 9, 'Venezia': 6},
    'Napoli': {'Atalanta': 11, 'Bologna': 6, 'Cagliari': 12, 'Como': 7, 'Fiorentina': 7, 'Frosinone': 6, 'Genoa': 10, 'Inter': 10, 'Juventus': 12, 'Lazio': 16, 'Lecce': 11, 'Milan': 9, 'Monza': 10, 'Parma': 8, 'Roma': 3, 'Sassuolo': 11, 'Torino': 7, 'Udinese': 8, 'Venezia': 7},
    'Parma': {'Atalanta': 7, 'Bologna': 11, 'Cagliari': 10, 'Como': 7, 'Fiorentina': 12, 'Frosinone': 11, 'Genoa': 9, 'Inter': 13, 'Juventus': 10, 'Lazio': 7, 'Lecce': 4, 'Milan': 6, 'Monza': 9, 'Napoli': 8, 'Roma': 12, 'Sassuolo': 4, 'Torino': 9, 'Udinese': 11, 'Venezia': 11},
    'Roma': {'Atalanta': 7, 'Bologna': 12, 'Cagliari': 8, 'Como': 9, 'Fiorentina': 13, 'Frosinone': 12, 'Genoa': 10, 'Inter': 12, 'Juventus': 6, 'Lazio': 0, 'Lecce': 6, 'Milan': 7, 'Monza': 12, 'Napoli': 3, 'Parma': 12, 'Sassuolo': 7, 'Torino': 13, 'Udinese': 11, 'Venezia': 11},
    'Sassuolo': {'Atalanta': 14, 'Bologna': 6, 'Cagliari': 8, 'Como': 11, 'Fiorentina': 7, 'Frosinone': 6, 'Genoa': 7, 'Inter': 4, 'Juventus': 10, 'Lazio': 12, 'Lecce': 14, 'Milan': 15, 'Monza': 10, 'Napoli': 11, 'Parma': 4, 'Roma': 7, 'Torino': 9, 'Udinese': 7, 'Venezia': 9},
    'Torino': {'Atalanta': 9, 'Bologna': 8, 'Cagliari': 11, 'Como': 11, 'Fiorentina': 8, 'Frosinone': 10, 'Genoa': 14, 'Inter': 12, 'Juventus': 0, 'Lazio': 6, 'Lecce': 7, 'Milan': 7, 'Monza': 9, 'Napoli': 7, 'Parma': 9, 'Roma': 13, 'Sassuolo': 9, 'Udinese': 10, 'Venezia': 11},
    'Udinese': {'Atalanta': 10, 'Bologna': 10, 'Cagliari': 9, 'Como': 8, 'Fiorentina': 11, 'Frosinone': 10, 'Genoa': 7, 'Inter': 12, 'Juventus': 9, 'Lazio': 8, 'Lecce': 7, 'Milan': 7, 'Monza': 9, 'Napoli': 8, 'Parma': 11, 'Roma': 11, 'Sassuolo': 7, 'Torino': 10, 'Venezia': 7},
    'Venezia': {'Atalanta': 9, 'Bologna': 7, 'Cagliari': 6, 'Como': 7, 'Fiorentina': 11, 'Frosinone': 13, 'Genoa': 12, 'Inter': 8, 'Juventus': 8, 'Lazio': 8, 'Lecce': 9, 'Milan': 11, 'Monza': 6, 'Napoli': 7, 'Parma': 11, 'Roma': 11, 'Sassuolo': 9, 'Torino': 11, 'Udinese': 7}
}

def get_sovrapposizioni(squadra1, squadra2):
    if squadra1 in MATRICE_PORTIERI and squadra2 in MATRICE_PORTIERI[squadra1]:
        return MATRICE_PORTIERI[squadra1][squadra2]
    if squadra2 in MATRICE_PORTIERI and squadra1 in MATRICE_PORTIERI[squadra2]:
        return MATRICE_PORTIERI[squadra2][squadra1]
    return 10

class AuctionEngine:
    def __init__(self):
        self.df_listone = pd.read_csv(LISTONE_PATH)
        self.load_state()
        
    def load_state(self):
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            self.state = json.load(f)
            
    def save_state(self):
        with open(STATE_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=4)

    def register_purchase(self, player_name, price, buyer_id):
        if player_name not in self.df_listone['nome'].values:
            return

        giocatore_info = self.df_listone[self.df_listone['nome'] == player_name].iloc[0]
        ruolo = giocatore_info['ruolo']
        squadra = giocatore_info['squadra']
        
        acquisto = {
            "nome": player_name,
            "ruolo": ruolo,
            "squadra": squadra,
            "costo": price,
            "valore_ai_originale": float(giocatore_info['valore_ai'])
        }
        
        if buyer_id == "mio_team":
            self.state["mio_team"]["giocatori_acquistati"].append(acquisto)
            self.state["mio_team"]["budget_residuo"] -= price
            self.state["mio_team"]["slot_residui"][ruolo] -= 1
            
            budget_rimasto_reparto = self.state["mio_team"]["target_spesa"][ruolo] - price
            self.state["mio_team"]["target_spesa"][ruolo] = max(0, budget_rimasto_reparto)
            
            if self.state["mio_team"]["slot_residui"][ruolo] == 0 and budget_rimasto_reparto > 0:
                if ruolo != 'A':
                    self.state["mio_team"]["target_spesa"]['A'] += budget_rimasto_reparto
        elif buyer_id in self.state["avversari"]:
            self.state["avversari"][buyer_id]["giocatori_acquistati"].append(acquisto)
            self.state["avversari"][buyer_id]["budget_residuo"] -= price
            self.state["avversari"][buyer_id]["slot_residui"][ruolo] -= 1
            
        self.save_state()

    def calculate_inflation_index(self):
        budget_lega = self.state["config"]["budget_iniziale"] * self.state["config"]["partecipanti"]
        budget_discrezionale_iniziale = budget_lega - (25 * self.state["config"]["partecipanti"])
        vorp_totale_iniziale = self.df_listone['vorp'].sum()
        
        costo_per_vorp_iniziale = budget_discrezionale_iniziale / vorp_totale_iniziale if vorp_totale_iniziale > 0 else 1
        
        budget_residuo_mio = self.state["mio_team"]["budget_residuo"]
        budget_residuo_avversari = sum([opp["budget_residuo"] for opp in self.state["avversari"].values()])
        budget_totale_rimasto = budget_residuo_mio + budget_residuo_avversari
        
        giocatori_comprati = [p['nome'] for p in self.state["mio_team"]["giocatori_acquistati"]]
        for opp in self.state["avversari"].values():
            giocatori_comprati.extend([p['nome'] for p in opp["giocatori_acquistati"]])
                             
        df_liberi = self.df_listone[~self.df_listone['nome'].isin(giocatori_comprati)]
        vorp_totale_rimasto = df_liberi['vorp'].sum()
        
        slot_vuoti_miei = sum(self.state["mio_team"]["slot_residui"].values())
        slot_vuoti_avversari = sum([sum(opp["slot_residui"].values()) for opp in self.state["avversari"].values()])
        slot_vuoti_totali = slot_vuoti_miei + slot_vuoti_avversari
        
        budget_discrezionale_rimasto = budget_totale_rimasto - slot_vuoti_totali
        if budget_discrezionale_rimasto <= 0 or vorp_totale_rimasto <= 0: return 0.5 
            
        costo_per_vorp_attuale = budget_discrezionale_rimasto / vorp_totale_rimasto
        return round(costo_per_vorp_attuale / costo_per_vorp_iniziale, 2)

    def get_max_bid_avversari(self, ruolo):
        max_bid = 0
        avversario_ricco = "Nessuno"
        for opp_id, opp_data in self.state["avversari"].items():
            if opp_data["slot_residui"][ruolo] > 0:
                slot_vuoti_totali = sum(opp_data["slot_residui"].values())
                bid_possibile = opp_data["budget_residuo"] - (slot_vuoti_totali - 1)
                if bid_possibile > max_bid:
                    max_bid = bid_possibile
                    avversario_ricco = opp_id
        return max_bid, avversario_ricco

    def apply_strategic_modifiers(self, player, base_live_value):
        ruolo = player['ruolo']
        squadra = player['squadra']
        miei_giocatori = self.state["mio_team"]["giocatori_acquistati"]
        
        multiplier = 1.0
        messaggio_tattico = "Nessun avviso tattico"
        
        if ruolo == 'P':
            miei_portieri = [p for p in miei_giocatori if p['ruolo'] == 'P']
            squadre_miei_portieri = [p['squadra'] for p in miei_portieri]
            
            # Contiamo QUANTI portieri di questa squadra abbiamo già
            omonimi_squadra = squadre_miei_portieri.count(squadra)
            
            if omonimi_squadra == 1:
                messaggio_tattico = "🎯 VICE PORTIERE! (Prendilo a 1 credito)"
                multiplier = 1.3 
            elif omonimi_squadra >= 2:
                messaggio_tattico = "🚫 SLOT SPRECATO! Hai già 2 portieri di questo club, usa l'ultimo slot per l'incrocio."
                multiplier = 0.50 # Farà scattare il Max Bid a 0 grazie alla logica di blocco
            elif len(miei_portieri) > 0:
                squadra_primo_portiere = squadre_miei_portieri[0]
                sovrapposizioni = get_sovrapposizioni(squadra, squadra_primo_portiere)
                
                if sovrapposizioni == 0:
                    messaggio_tattico = f"🛡️ INCROCIO PERFETTO con {squadra_primo_portiere} (0 sovrapposizioni)"
                    multiplier = 1.20
                elif sovrapposizioni <= 6:
                    messaggio_tattico = f"✅ OTTIMO INCROCIO con {squadra_primo_portiere} ({sovrapposizioni} sovrapposizioni)"
                    multiplier = 1.10
                elif sovrapposizioni >= 13:
                    messaggio_tattico = f"❌ PESSIMO INCROCIO con {squadra_primo_portiere} ({sovrapposizioni} sovrapposizioni, evitalo!)"
                    multiplier = 0.70
        else:
            miei_stesso_ruolo = [p for p in miei_giocatori if p['ruolo'] == ruolo]
            omonimi_squadra = len([p for p in miei_stesso_ruolo if p['squadra'] == squadra])
            
            if omonimi_squadra == 1:
                multiplier = 0.90 
                messaggio_tattico = "⚠️ Hai già un giocatore di questa squadra in questo ruolo."
            elif omonimi_squadra >= 2:
                multiplier = 0.50 
                messaggio_tattico = "🚫 BLOCCO SQUADRA! Troppi giocatori dello stesso club, EVITARE."

        return base_live_value * multiplier, messaggio_tattico

    def evaluate_player(self, player_name):
        giocatori_comprati = [p['nome'] for p in self.state["mio_team"]["giocatori_acquistati"]]
        for opp in self.state["avversari"].values():
            giocatori_comprati.extend([p['nome'] for p in opp["giocatori_acquistati"]])
            
        df_liberi = self.df_listone[~self.df_listone['nome'].isin(giocatori_comprati)]
        if player_name not in df_liberi['nome'].values:
            return {"status": "Già acquistato o non trovato"}
            
        player = df_liberi[df_liberi['nome'] == player_name].iloc[0]
        ruolo = player['ruolo']
        
        # --- FIX: IL PARADOSSO DEL BALLOTTAGGIO PORTIERI ---
        # Se il VORP ha ucciso il valore di un portiere per via delle presenze spaccate, 
        # lo "salviamo" usando il FVA (Fanta Valore Assoluto) di FantaLab.
        valore_base = player['valore_ai']
        if ruolo == 'P' and valore_base < player['fva_mercato']:
            valore_base = player['fva_mercato']
            
        inflazione = self.calculate_inflation_index()
        valore_ai_live = valore_base * inflazione
        
        valore_ai_tattico, avviso = self.apply_strategic_modifiers(player, valore_ai_live)
        
        slot_vuoti_reparto = self.state["mio_team"]["slot_residui"][ruolo]
        slot_vuoti_totali = sum(self.state["mio_team"]["slot_residui"].values())
        budget_reparto = self.state["mio_team"]["target_spesa"][ruolo]
        budget_totale = self.state["mio_team"]["budget_residuo"]
        
        limite_budget_reparto = max(1, budget_reparto - (slot_vuoti_reparto - 1)) if slot_vuoti_reparto > 0 else 0
        
        if limite_budget_reparto > 0:
            tetto_tattico = int(valore_ai_tattico)
            max_bid_consigliato = min(limite_budget_reparto, tetto_tattico)
            
            # --- FIX: INTERCETTAZIONE UNIVERSALE DEI DIVIETI ---
            # Se c'è un'emoji di stop o errore, il Max Bid diventa categoricamente 0.
            if "🚫" in avviso or "❌" in avviso:
                max_bid_consigliato = 0
            elif max_bid_consigliato < 1:
                max_bid_consigliato = 1
        else:
            max_bid_consigliato = 0
            
        max_bid_nemico, nome_nemico = self.get_max_bid_avversari(ruolo)
        
        return {
            "status": "Disponibile",
            "nome": player['nome'],
            "ruolo": ruolo,
            "squadra": player['squadra'],
            "avviso_tattico": avviso,
            "valore_ai_LIVE": round(valore_ai_tattico, 1),
            "max_bid_consigliato": max_bid_consigliato,
            "max_bid_assoluto": budget_totale - (slot_vuoti_totali - 1),
            "pericolo_max_nemico": max_bid_nemico,
            "nemico_piu_ricco": nome_nemico
        }


# --- BLOCCO DI TEST VERO E RIGOROSO ---
if __name__ == "__main__":
    import pprint
    
    engine = AuctionEngine()
    df = engine.df_listone
    print("🔥 INIZIO STRESS TEST DEL MOTORE D'ASTA 🔥\n")
    
    # === TEST 1: VALUTAZIONE PURA DI UN TOP PLAYER ===
    # Prendiamo il miglior attaccante per VORP
    top_a = df[df['ruolo'] == 'A'].sort_values('valore_ai', ascending=False).iloc[0]
    print(f"1️⃣ TEST TOP PLAYER (Mercato intatto): {top_a['nome']}")
    print("Ci aspettiamo che il Max Bid sia dettato dal Valore AI puro (poiché abbiamo tutto il budget).")
    pprint.pprint(engine.evaluate_player(top_a['nome']), sort_dicts=False)
    
    # === TEST 2: CROLLO DELL'INFLAZIONE ===
    print("\n👉 Gli avversari impazziscono: Avversario_1 e Avversario_2 pagano 150 crediti a testa per due mediani scarsi.")
    mediani = df[df['ruolo'] == 'C'].sort_values('valore_ai', ascending=True).head(2)['nome'].tolist()
    engine.register_purchase(mediani[0], 150, "Avversario_1")
    engine.register_purchase(mediani[1], 150, "Avversario_2")
    
    print(f"\n2️⃣ TEST DEFLAZIONE SUL TOP PLAYER: {top_a['nome']}")
    print("Il mercato si è impoverito. Il Valore AI Live (e quindi il Max Bid Consigliato) DEVE crollare.")
    pprint.pprint(engine.evaluate_player(top_a['nome']), sort_dicts=False)
    
    # === TEST 3: ESAURIMENTO BUDGET DI REPARTO ===
    # Compro l'attaccante top spendendo un sacco di crediti
    print(f"\n👉 Compro {top_a['nome']} a 180 crediti.")
    engine.register_purchase(top_a['nome'], 180, "mio_team")
    
    top_a2 = df[(df['ruolo'] == 'A') & (df['nome'] != top_a['nome'])].sort_values('valore_ai', ascending=False).iloc[0]
    print(f"\n3️⃣ TEST BUDGET A SECCO: {top_a2['nome']}")
    print("Questo è un altro top attaccante, MA avendo speso 180 crediti per l'Attacco, il Max Bid DEVE bloccarsi ai soldi rimasti per il reparto (nonostante il suo Valore AI sia alto).")
    pprint.pprint(engine.evaluate_player(top_a2['nome']), sort_dicts=False)
    
    # === TEST 4: BLOCCO SQUADRA (IL RIFIUTO) ===
    difensori_juve = df[(df['ruolo'] == 'D') & (df['squadra'] == 'Juventus')]['nome'].tolist()
    print("\n👉 Compro due difensori della Juventus a 10 crediti l'uno.")
    engine.register_purchase(difensori_juve[0], 10, "mio_team")
    engine.register_purchase(difensori_juve[1], 10, "mio_team")
    
    print(f"\n4️⃣ TEST BLOCCO SQUADRA: {difensori_juve[2]}")
    print("Terzo difensore Juve. Il motore DEVE dare il malus 'Evitare' e il Max Bid DEVE essere 0, anche se ho soldi in cassa.")
    pprint.pprint(engine.evaluate_player(difensori_juve[2]), sort_dicts=False)

    # === TEST 5: INCROCI PORTIERI E SPILLOVER ===
    print("\n👉 Compro il portiere titolare del Frosinone a 5 crediti.")
    p_frosinone = df[(df['squadra'] == 'Frosinone') & (df['ruolo'] == 'P')].iloc[0]
    engine.register_purchase(p_frosinone['nome'], 5, "mio_team")
    
    p_atalanta = df[(df['squadra'] == 'Atalanta') & (df['ruolo'] == 'P')].iloc[0]
    print(f"\n5️⃣ TEST INCROCIO OTTIMO: {p_atalanta['nome']} (Atalanta)")
    print("Frosinone e Atalanta hanno 5 sovrapposizioni. Il motore deve dare il Bonus Incrocio e alzare il Valore AI.")
    pprint.pprint(engine.evaluate_player(p_atalanta['nome']), sort_dicts=False)