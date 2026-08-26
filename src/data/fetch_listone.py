import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv

# Carica le variabili dal file .env
load_dotenv()

# ==========================================
# CONFIGURAZIONE DINAMICA
# ==========================================
AUTH_TOKEN = os.getenv('FANTALAB_TOKEN')
BUDGET_LEGA = int(os.getenv('BUDGET_LEGA', 500))
PARTECIPANTI_LEGA = int(os.getenv('PARTECIPANTI_LEGA', 10))
USO_MODIFICATORE = os.getenv('USO_MODIFICATORE', 'True').lower() in ('true', '1', 't')
import datetime

# 1. Prende l'anno dal .env, o se manca lo deduce automaticamente dalla data di oggi
anno_default = datetime.datetime.now().year if datetime.datetime.now().month > 6 else datetime.datetime.now().year - 1
ANNO_INIZIO = int(os.getenv('ANNO_INIZIO_CAMPIONATO', anno_default))

# 2. FantaLab usa l'ID 17 per il 2026. Quindi la formula matematica è Anno - 2009
SEASON_ID = ANNO_INIZIO - 2009

# 3. Costruisce la stringa 's_26_27'
SEASON_STR = f"s_{str(ANNO_INIZIO)[-2:]}_{str(ANNO_INIZIO+1)[-2:]}"

if not AUTH_TOKEN:
    raise ValueError("ERRORE: FANTALAB_TOKEN non trovato nel .env")
# ==========================================

def get_headers(is_cross_site=False):
    return {
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Authorization': AUTH_TOKEN,
        'Sec-Fetch-Site': 'cross-site' if is_cross_site else 'same-site',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Fetch-Mode': 'cors',
        'Origin': 'https://app.fantalab.it',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
        'Referer': 'https://app.fantalab.it/',
        'Sec-Fetch-Dest': 'empty',
        'Priority': 'u=3, i',
    }

def fetch_and_merge_listone():
    print("Avvio estrazione dati da FantaLab...")
    
    # URLs
    url_info = "https://api.fantalab.it/players/get-season-info-cached-25"
    url_prices = "https://manager.fantalab.it/get-new-prices"
    url_ratings = "https://api-cdn.falsesoftware.com/v2/ratings"
    url_teams = "https://api-cdn.falsesoftware.com/v2/players/list"
    
    current_timestamp = str(int(time.time() * 1000)) 
    
    # 1. Anagrafica base
    print("1/4 - Scaricamento anagrafica base...")
    res_info = requests.get(url_info, headers=get_headers(), params={'lastUpdate': current_timestamp}) 
    res_info.raise_for_status()
    lista_giocatori = [{'player_id': k, 'name': v['name'], 'role': v['role']} for k, v in res_info.json().items()]
    df_players = pd.DataFrame(lista_giocatori)

    # 2. Quotazioni
    print("2/4 - Scaricamento quotazioni attuali...")
    res_prices = requests.post(url_prices, headers=get_headers(), json={'season_id': SEASON_ID})
    res_prices.raise_for_status()
    df_prices = pd.DataFrame(res_prices.json())
    
    # 3. Indici FVA
    print("3/4 - Scaricamento indici e FVA...")
    res_ratings = requests.get(url_ratings, headers=get_headers(is_cross_site=True))
    res_ratings.raise_for_status()
    df_ratings = pd.DataFrame(res_ratings.json()['data'])

    # 4. Estrazione LIVE Squadre (Aggiramento Impaginazione perfetto)
    print("4/4 - Estrazione LIVE aggiornata delle squadre (Anti-bot attivato)...")
    teams_data = []
    ruoli_fantalab = ['P', 'D', 'C', 'A']
    limit = 50 # Chiediamo 50 giocatori alla volta per essere sicuri
    
    for ruolo in ruoli_fantalab:
        offset = 0
        while True:
            params_teams = {
                'leagues': 'serie_a',
                'limit': str(limit),
                'listone_scope': 'serie_a',
                'offset': str(offset),
                'role': ruolo,
                'season': SEASON_STR,
                'sort_order': 'DESC',
                'sort_stat': 'fmv',
                'stats': 'quotazione' # Inseriamo una statistica minima per far felice il server
            }
            res_teams = requests.get(url_teams, headers=get_headers(is_cross_site=True), params=params_teams)
            res_teams.raise_for_status() # Se c'è un errore si ferma qui e ce lo dice
            
            players_chunk = res_teams.json().get('players', [])
            if not players_chunk:
                break # Nessun giocatore rimasto in questo ruolo
                
            for p in players_chunk:
                teams_data.append({
                    'player_id': p['player_id'],
                    'team': p.get('team_name', 'Sconosciuta')
                })
                
            offset += limit
            time.sleep(0.5) # Pausa tra le richieste per simulare l'umano
            
    df_teams = pd.DataFrame(teams_data).drop_duplicates(subset=['player_id'])

    # === MERGE E PULIZIA ===
    print("Eseguo il merge dei dati...")
    df_master = df_players.merge(df_prices, on='player_id', how='left')
    df_master = df_master.merge(df_ratings, on='player_id', how='left')
    df_master = df_master.merge(df_teams, on='player_id', how='left')
    
    df_master = df_master[df_master['in_listone'] == True].copy()
    
    # Calcolo FVA DINAMICO
    str_mod = "_mod" if USO_MODIFICATORE else "_no_mod"
    partecipanti_fva = PARTECIPANTI_LEGA if PARTECIPANTI_LEGA in [8, 10, 12] else 10
    colonna_fva = f"classic_{partecipanti_fva}{str_mod}_median"
    
    if colonna_fva not in df_master.columns:
        colonna_fva = "classic_10_mod_median"
        
    df_master['fva_assoluto'] = (df_master[colonna_fva] / 100) * BUDGET_LEGA
    df_master['fva_assoluto'] = df_master['fva_assoluto'].round(0)
    
    colonne_finali = {
        'player_id': 'id',
        'name': 'nome',
        'role': 'ruolo',
        'team': 'squadra',
        'price': 'quotazione_iniziale',
        'fva_assoluto': 'fva_mercato',
        'xfmv': 'expected_fantamedia',
        'tit_index': 'indice_titolarita',
        'aff_index': 'indice_affidabilita',
        'inf_index': 'indice_infortuni'
    }
    
    df_final = df_master[list(colonne_finali.keys())].rename(columns=colonne_finali)
    
    os.makedirs('data/01_raw', exist_ok=True)
    output_path = "data/01_raw/listone_corrente.csv"
    df_final.to_csv(output_path, index=False)
    
    print(f"Successo! Salvati {len(df_final)} giocatori in {output_path}")

if __name__ == '__main__':
    fetch_and_merge_listone()