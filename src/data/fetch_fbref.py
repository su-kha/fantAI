import soccerdata as sd
import pandas as pd
import os

def process_fbref():
    print("1. Inizializzazione scraper FBRef...")
    
    # Usiamo la stringa ottimizzata che ci ha suggerito il log di soccerdata
    fbref = sd.FBref(
        leagues="Big 5 European Leagues Combined", 
        seasons="2526"
    )
    
    print("2. Download statistiche standard (Minuti, Gol, Assist)...")
    df_stats = fbref.read_player_season_stats(stat_type="standard")
    
    # Appiattiamo le colonne (rimuove il MultiIndex di Pandas)
    df_stats.columns = ['_'.join(col).strip() for col in df_stats.columns.values]
    df_stats = df_stats.reset_index()
    
    print(f"Estratti {len(df_stats)} giocatori europei totali.")
    
    # Usiamo le chiavi esatte restituite dal tuo terminale
    col_minuti = 'Playing Time_Min'
    col_gol = 'Performance_Gls'
    col_assist = 'Performance_Ast'
    
    # Filtriamo chi ha giocato meno di 500 minuti per evitare statistiche drogate
    df_validi = df_stats[df_stats[col_minuti] >= 500].copy()
    
    # Costruiamo il dataset pulito
    df_final = pd.DataFrame({
        'nome_fbref': df_validi['player'],
        'squadra_fbref': df_validi['team'],
        'campionato_fbref': df_validi['league'],
        'minuti_giocati': df_validi[col_minuti],
        'gol_totali': df_validi[col_gol],
        'assist_totali': df_validi[col_assist]
    })
    
    # Normalizzazione Gol e Assist per 90 minuti
    df_final['gol_p90'] = round((df_final['gol_totali'] / df_final['minuti_giocati']) * 90, 3)
    df_final['assist_p90'] = round((df_final['assist_totali'] / df_final['minuti_giocati']) * 90, 3)
    
    output_path = "data/02_interim/stats_fbref_90.csv"
    os.makedirs('data/02_interim', exist_ok=True)
    df_final.to_csv(output_path, index=False)
    
    print(f"3. Successo! Salvate metriche G/90 e A/90 per {len(df_final)} giocatori in {output_path}")

if __name__ == '__main__':
    process_fbref()