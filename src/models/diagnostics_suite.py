import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

def run_simulation(df_raw, p_storico, mod_mult, base_D, base_C, base_A, partecipanti, budget_singolo):
    df = df_raw.copy()
    
    # Presenze
    if df['indice_titolarita'].max() <= 5.0:
        df['presenze_stimate'] = (df['indice_titolarita'] / 5.0) * 38
    else:
        df['presenze_stimate'] = (df['indice_titolarita'] / 100.0) * 38
    df['presenze_stimate'] = df['presenze_stimate'].fillna(0).clip(lower=0, upper=38).round(1)
    df['partite_saltate'] = 38 - df['presenze_stimate']
    
    # Ibrida
    p_exp = 1.0 - p_storico
    df['fmv_ibrida'] = np.where(
        df['fmv_media_storica'].notna(),
        (df['fmv_media_storica'] * p_storico) + (df['expected_fantamedia'] * p_exp),
        df['expected_fantamedia']
    )
    df['fmv_ibrida'] = df['fmv_ibrida'].fillna(df['fmv_media_storica']).fillna(6.0)
    
    fmv_panchinaro = {'P': 4.5, 'D': 5.8, 'C': 5.9, 'A': 6.0}
    df['fmv_riserva'] = df['ruolo'].map(fmv_panchinaro)
    df['punti_attesi_base'] = (df['fmv_ibrida'] * df['presenze_stimate']) + (df['fmv_riserva'] * df['partite_saltate'])
    
    # Modificatore
    cond_mod = (df['ruolo'] == 'D') & (df['mv_media_storica'].fillna(6.0) >= 6.15)
    df['bonus_mod'] = 0.0
    df.loc[cond_mod, 'bonus_mod'] = (df.loc[cond_mod, 'mv_media_storica'].fillna(6.0) - 6.0) * mod_mult * df.loc[cond_mod, 'presenze_stimate']
    df['punti_tot'] = df['punti_attesi_base'] + df['bonus_mod']
    
    # Baseline
    starter_reali = {'P': int(partecipanti * 1.0), 'D': base_D, 'C': base_C, 'A': base_A}
    df['baseline'] = 0.0
    for ruolo, rank_soglia in starter_reali.items():
        df_r = df[df['ruolo'] == ruolo].sort_values(by='punti_tot', ascending=False)
        if len(df_r) >= rank_soglia:
            df.loc[df['ruolo'] == ruolo, 'baseline'] = df_r.iloc[rank_soglia - 1]['punti_tot']
        else:
            df.loc[df['ruolo'] == ruolo, 'baseline'] = df_r['punti_tot'].min()

    df['vorp'] = (df['punti_tot'] - df['baseline']).clip(lower=0)
    
    budget_disp = (budget_singolo * partecipanti) - (25 * partecipanti)
    if df['vorp'].sum() > 0:
        df['valore_ai'] = 1 + (df['vorp'] * (budget_disp / df['vorp'].sum()))
    else:
        df['valore_ai'] = 1.0
        
    df['valore_ai'] = df['valore_ai'].round(1)
    
    # Calcolo Metriche
    corr = df[df['fva_mercato']>0]['valore_ai'].corr(df[df['fva_mercato']>0]['fva_mercato'], method='spearman')
    max_price = df['valore_ai'].max()
    
    return {
        'p_storico': p_storico, 'mod_mult': mod_mult, 
        'base_D': base_D, 'base_C': base_C, 'base_A': base_A,
        'corr': corr, 'max_price': max_price,
        'df_result': df
    }

def run_suite():
    print("🚀 Avvio Testing Suite Globale (Grid Search + Diagnostics)...\n")
    
    load_dotenv()
    budget_singolo = int(os.getenv('BUDGET_LEGA', 500))
    partecipanti = int(os.getenv('PARTECIPANTI_LEGA', 10))
    uso_mod = os.getenv('USO_MODIFICATORE', 'True').lower() in ('true', '1', 't')
    
    df_raw = pd.read_csv("data/03_processed/master_dataset.csv")
    
    # Griglia Iperparametri (adattata per la dimensione della lega)
    pesi_storico = [0.3, 0.4]
    # Se la lega usa il modificatore testiamo i moltiplicatori, altrimenti lo azzeriamo
    if uso_mod:
        mod_multipliers = [0.8, 1.0]
    else:
        mod_multipliers = [0.0]    

    # Scaliamo le baseline di test in base ai partecipanti
    baselines_D = [int(partecipanti * 3.0), int(partecipanti * 3.5)]
    baselines_C = [int(partecipanti * 3.0), int(partecipanti * 3.5)]
    baselines_A = [int(partecipanti * 2.5), int(partecipanti * 3.0)]
    
    risultati = []
    
    print("Esecuzione simulazioni su tutte le combinazioni di reparti...")
    for p_s in pesi_storico:
        for m_m in mod_multipliers:
            for b_D in baselines_D:
                for b_C in baselines_C:
                    for b_A in baselines_A:
                        res = run_simulation(df_raw, p_s, m_m, b_D, b_C, b_A, partecipanti, budget_singolo)
                        risultati.append(res)
    
    df_res = pd.DataFrame(risultati)
    # Regola d'asta: il massimo spendibile è il budget totale meno 1 credito per ogni altro slot (24)
    cap_matematico_assoluto = budget_singolo - 24
    best_models = df_res[df_res['max_price'] < cap_matematico_assoluto].sort_values(by='corr', ascending=False)
    
    if best_models.empty:
        best_model = df_res.sort_values(by='corr', ascending=False).iloc[0]
    else:
        best_model = best_models.iloc[0]
        
    print("\n🏆 MIGLIOR CONFIGURAZIONE GLOBALE TROVATA:")
    print(f"- Peso Storico: {best_model['p_storico']}")
    print(f"- Multiplicatore Modificatore: {best_model['mod_mult']}")
    print(f"- Titolari Base (D, C, A): {best_model['base_D']}, {best_model['base_C']}, {best_model['base_A']}")
    print(f"- Correlazione Globale: {best_model['corr']:.3f} | Prezzo Max: {best_model['max_price']}")
    
    df_best = best_model['df_result']
    df_best.to_csv("data/04_results/listone_vorp_prices.csv", index=False)
    print("\n✅ Listone definitivo salvato in data/04_results/listone_vorp_prices.csv")

if __name__ == "__main__":
    run_suite()