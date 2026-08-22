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
BUDGET_LEGA = int(os.getenv('BUDGET_LEGA', 500)) # Default a 500 se non specificato

if not AUTH_TOKEN:
    raise ValueError("ERRORE: FANTALAB_TOKEN non trovato. Assicurati di aver creato il file .env e inserito il token.")
# ==========================================

def get_headers(is_cross_site=False):
    """Genera gli headers standard. I ratings usano cross-site perché su CDN esterna."""
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
    
    # 1. URLs
    url_info = "https://api.fantalab.it/players/get-season-info-cached-25"
    url_prices = "https://manager.fantalab.it/get-new-prices"
    url_ratings = "https://api-cdn.falsesoftware.com/v2/ratings"
    
    # 2. Generazione parametri dinamici
    current_timestamp = str(int(time.time() * 1000)) # Genera il timestamp attuale
    
    params_data_players = {'lastUpdate': current_timestamp}
    json_data_prices = {'season_id': 17}
    
    # 3. Chiamate API
    print("1/3 - Scaricamento anagrafica e storico...")
    res_info = requests.get(url_info, headers=get_headers(), params=params_data_players) 
    res_info.raise_for_status()
    
    lista_giocatori = [
        {'player_id': info['player_id'], 'name': info['name'], 'role': info['role']}
        for pid, info in res_info.json().items()
    ]
    df_players = pd.DataFrame(lista_giocatori)

    print("2/3 - Scaricamento quotazioni attuali...")
    res_prices = requests.post(url_prices, headers=get_headers(), json=json_data_prices)
    res_prices.raise_for_status()
    df_prices = pd.DataFrame(res_prices.json())
    
    print("3/3 - Scaricamento indici e FVA...")
    res_ratings = requests.get(url_ratings, headers=get_headers(is_cross_site=True))
    res_ratings.raise_for_status()
    df_ratings = pd.DataFrame(res_ratings.json()['data'])

    # 4. Merge e Pulizia
    print("Eseguo il merge dei dati...")
    df_master = df_players.merge(df_prices, on='player_id', how='left')
    df_master = df_master.merge(df_ratings, on='player_id', how='left')
    
    # Filtro giocatori attivi nel listone
    df_master = df_master[df_master['in_listone'] == True].copy()
    
    # Calcolo FVA Assoluto (Lega a 10 con Modificatore)
    df_master['fva_assoluto'] = (df_master['perc_classic_10_mod'] / 100) * BUDGET_LEGA
    df_master['fva_assoluto'] = df_master['fva_assoluto'].round(0)
    
    colonne_finali = {
        'player_id': 'id',
        'name': 'nome',
        'role': 'ruolo',
        'price': 'quotazione_iniziale',
        'fva_assoluto': 'fva_mercato',
        'xfmv': 'expected_fantamedia',
        'tit_index': 'indice_titolarita',
        'aff_index': 'indice_affidabilita',
        'inf_index': 'indice_infortuni'
    }
    
    df_final = df_master[list(colonne_finali.keys())].rename(columns=colonne_finali)
    
    # 5. Salvataggio
    os.makedirs('data/01_raw', exist_ok=True)
    output_path = "data/01_raw/listone_corrente.csv"
    df_final.to_csv(output_path, index=False)
    
    print(f"Successo! Salvati {len(df_final)} giocatori in {output_path}")

if __name__ == '__main__':
    fetch_and_merge_listone()