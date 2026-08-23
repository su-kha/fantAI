import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv

# Carica il token dal file .env
load_dotenv()
AUTH_TOKEN = os.getenv('FANTALAB_TOKEN')

if not AUTH_TOKEN:
    raise ValueError("FANTALAB_TOKEN mancante nel file .env")

def get_headers():
    """Restituisce gli header per la richiesta autenticata."""
    return {
        'Authorization': AUTH_TOKEN,
        'Origin': 'https://app.fantalab.it',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
    }

def fetch_and_process_historical():
    print("1. Lettura del listone corrente (giocatori attivi)...")
    listone_path = "data/01_raw/listone_corrente.csv"
    
    if not os.path.exists(listone_path):
        raise FileNotFoundError(f"Listone non trovato in {listone_path}. Esegui prima fetch_listone.py")
    
    # Carichiamo gli ID dei giocatori attualmente in Serie A
    df_listone = pd.read_csv(listone_path)
    id_attivi = set(df_listone['id'].tolist())
    
    print("2. Scaricamento storico stagioni (get-season-info-cached-25)...")
    current_timestamp = str(int(time.time() * 1000))
    url_info = "https://api.fantalab.it/players/get-season-info-cached-25"
    
    res = requests.get(url_info, headers=get_headers(), params={'lastUpdate': current_timestamp})
    res.raise_for_status()
    data_info = res.json()
    
    print("3. Estrazione e calcolo delle metriche storiche...")
    records = []
    
    for pid, info in data_info.items():
        # SALTIAMO chi non è più in Serie A
        if pid not in id_attivi:
            continue
            
        stats_array = info.get('stats', [])
        
        # Inizializziamo le metriche usando None (che diventerà NaN nel CSV) e non 0.0
        storico = {
            'id': pid,
            'presenze_totali_storiche': 0,
            'mv_media_storica': None,  
            'fmv_media_storica': None, 
            'stagioni_a_voto': 0,      
            'infortuni_storici': 0
        }
        
        if stats_array:
            mv_valide = [s['mv'] for s in stats_array if s.get('mv') is not None]
            fmv_valide = [s['fmv'] for s in stats_array if s.get('fmv') is not None]
            infortuni = [s['injured'] for s in stats_array if s.get('injured') is not None]
            
            storico['presenze_totali_storiche'] = sum(s.get('presenze', 0) for s in stats_array)
            storico['infortuni_storici'] = sum(infortuni)
            storico['stagioni_a_voto'] = len(mv_valide)
            
            # Se ha almeno una stagione con voti validi in Serie A, calcoliamo la media
            if mv_valide:
                storico['mv_media_storica'] = round(sum(mv_valide) / len(mv_valide), 2)
            if fmv_valide:
                storico['fmv_media_storica'] = round(sum(fmv_valide) / len(fmv_valide), 2)
                
        records.append(storico)
        
    df_storico = pd.DataFrame(records)
    
    # Salvataggio nella cartella interim
    os.makedirs('data/02_interim', exist_ok=True)
    output_path = "data/02_interim/storico_serie_a.csv"
    df_storico.to_csv(output_path, index=False)
    
    print(f"Successo! Storico elaborato per {len(df_storico)} giocatori attivi.")
    print(f"File salvato in: {output_path}")

if __name__ == '__main__':
    fetch_and_process_historical()