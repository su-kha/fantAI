import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

def run_vorp_engine():
    print("Avvio Motore VORP: Modello di Equilibrio Economico Puro...")
    
    load_dotenv()
    budget_singolo = int(os.getenv('BUDGET_LEGA', 500))
    partecipanti = int(os.getenv('PARTECIPANTI_LEGA', 10))
    budget_totale_lega = budget_singolo * partecipanti
    
    df = pd.read_csv("data/03_processed/master_dataset.csv")
    
    # ---------------------------------------------------------
    # 1. PUNTI ATTESI DELLO SLOT
    # ---------------------------------------------------------
    if df['indice_titolarita'].max() <= 5.0:
        df['presenze_stimate'] = (df['indice_titolarita'] / 5.0) * 38
    else:
        df['presenze_stimate'] = (df['indice_titolarita'] / 100.0) * 38
        
    df['presenze_stimate'] = df['presenze_stimate'].fillna(0).clip(lower=0, upper=38).round(1)
    df['partite_saltate'] = 38 - df['presenze_stimate']
    
    df['fmv_ibrida'] = np.where(
        df['fmv_media_storica'].notna(),
        (df['fmv_media_storica'] * 0.4) + (df['expected_fantamedia'] * 0.6),
        df['expected_fantamedia']
    )
    df['fmv_ibrida'] = df['fmv_ibrida'].fillna(df['fmv_media_storica']).fillna(6.0)
    
    fmv_panchinaro = {'P': 4.5, 'D': 5.8, 'C': 5.9, 'A': 6.0}
    df['fmv_riserva'] = df['ruolo'].map(fmv_panchinaro)
    
    df['punti_titolare'] = df['fmv_ibrida'] * df['presenze_stimate']
    df['punti_panchina'] = df['fmv_riserva'] * df['partite_saltate']
    df['punti_attesi_base'] = df['punti_titolare'] + df['punti_panchina']
    
    # ---------------------------------------------------------
    # 2. MODIFICATORE DIFESA
    # ---------------------------------------------------------
    df['bonus_modificatore_pti'] = 0.0
    df['mv_pura_valida'] = df['mv_media_storica'].fillna(6.0)
    cond_modificatore = (df['ruolo'] == 'D') & (df['mv_pura_valida'] >= 6.15)
    
    df.loc[cond_modificatore, 'bonus_modificatore_pti'] = (
        (df.loc[cond_modificatore, 'mv_pura_valida'] - 6.0) * 0.9 * df.loc[cond_modificatore, 'presenze_stimate']
    )
    df['punti_attesi_totali'] = df['punti_attesi_base'] + df['bonus_modificatore_pti']
    
    # ---------------------------------------------------------
    # 3. BASELINE SUGLI STARTER REALI (Titolari di giornata)
    # ---------------------------------------------------------
    starter_reali = {
        'P': int(partecipanti * 1.0),   # 10 portieri titolari
        'D': int(partecipanti * 3.5),   # 35 difensori titolari
        'C': int(partecipanti * 3.5),   # 35 centrocampisti titolari
        'A': int(partecipanti * 2.5)    # 25 attaccanti titolari
    }
    
    df['punti_baseline'] = 0.0
    for ruolo, rank_soglia in starter_reali.items():
        df_ruolo = df[df['ruolo'] == ruolo].sort_values(by='punti_attesi_totali', ascending=False)
        if len(df_ruolo) >= rank_soglia:
            baseline_punti = df_ruolo.iloc[rank_soglia - 1]['punti_attesi_totali']
        else:
            baseline_punti = df_ruolo['punti_attesi_totali'].min()
        df.loc[df['ruolo'] == ruolo, 'punti_baseline'] = baseline_punti

    df['vorp'] = (df['punti_attesi_totali'] - df['punti_baseline']).clip(lower=0)
    
    # ---------------------------------------------------------
    # 4. PRICING A EQUILIBRIO DI MERCATO (Relazione Globale)
    # ---------------------------------------------------------
    # Togliamo 1 credito per ogni slot acquistato (25 giocatori x partecipanti)
    crediti_vincolati = 25 * partecipanti
    budget_asta_totale = budget_totale_lega - crediti_vincolati
    
    # Curva di scarsità naturale (1.20 riflette l'utilità marginale senza forzature)
    df['vorp_pesato'] = df['vorp'] ** 1.20
    somma_vorp_totale = df['vorp_pesato'].sum()
    
    costo_per_punto = budget_asta_totale / somma_vorp_totale
    
    # Prezzo = 1 credito base + quota parte del montepremi di lega
    df['prezzo_ai'] = 1 + (df['vorp_pesato'] * costo_per_punto)
    df['prezzo_ai'] = df['prezzo_ai'].round(1)
    
    df['differenziale'] = df['prezzo_ai'] - df['fva_mercato']
    
    # ---------------------------------------------------------
    # SALVATAGGIO E REPORT
    # ---------------------------------------------------------
    df.to_csv("data/04_results/listone_vorp_prices.csv", index=False)
    
    cols_preview = ['nome', 'ruolo', 'punti_attesi_totali', 'vorp', 'prezzo_ai', 'fva_mercato', 'differenziale']
    
    print("\n💎 I TOP PER REPARTO:")
    top_p = df[df['ruolo'] == 'P'].sort_values(by='prezzo_ai', ascending=False).head(1)
    top_d = df[df['ruolo'] == 'D'].sort_values(by='prezzo_ai', ascending=False).head(1)
    top_c = df[df['ruolo'] == 'C'].sort_values(by='prezzo_ai', ascending=False).head(1)
    top_a = df[df['ruolo'] == 'A'].sort_values(by='prezzo_ai', ascending=False).head(1)
    print(pd.concat([top_p, top_d, top_c, top_a])[cols_preview].to_string(index=False))
    
    print("\n🎯 FOCUS ATTACCANTI TOP/SECONDI SLOT (Kean, Hojlund, Yildiz, Ramos G.):")
    focus_att = df[df['nome'].str.contains("Kean|Hojlund|Yildiz|Ramos G.|Lautaro|Malen", case=False, na=False)]
    print(focus_att.sort_values(by='prezzo_ai', ascending=False)[cols_preview].to_string(index=False))

    return df

if __name__ == "__main__":
    run_vorp_engine()