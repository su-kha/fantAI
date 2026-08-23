import pandas as pd
import unicodedata
import os
import json
from thefuzz import fuzz

LEAGUE_WEIGHTS = {
    'ENG-Premier League': 1.00, 'ESP-La Liga': 0.95, 'ITA-Serie A': 0.95,
    'GER-Bundesliga': 0.90, 'FRA-Ligue 1': 0.85
}

def clean_name_for_matching(name: str) -> str:
    """Normalizza stringhe: minuscolo, sostituisce caratteri speciali e rimuove accenti."""
    if not isinstance(name, str): return ""
    name = name.lower()
    name = name.replace('ð', 'd').replace('ø', 'o').replace('ı', 'i').replace('æ', 'ae')
    
    nfkd = unicodedata.normalize('NFKD', name)
    name_ascii = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return name_ascii.replace('.', '').strip()

def get_or_create_mapping() -> dict:
    mapping_path = "data/manual_mapping.json"
    if not os.path.exists(mapping_path):
        os.makedirs("data", exist_ok=True)
        with open(mapping_path, "w") as f:
            json.dump({}, f, indent=4)
        return {}
    with open(mapping_path, "r") as f:
        return json.load(f)

def check_iniziali_omonimi(nome_fantalab, nome_fbref):
    """Check severo per le doppie iniziali (es. F.P. Esposito)."""
    parti_fanta = nome_fantalab.split()
    if len(parti_fanta) > 1:
        ultima_parte = parti_fanta[-1].replace('.', '')
        if len(ultima_parte) <= 2:
            iniziale = ultima_parte[0].lower()
            parti_fbref = nome_fbref.lower().split()
            if not any(w.startswith(iniziale) for w in parti_fbref):
                return False
    return True

def custom_scorer(s1, s2):
    """Motore che penalizza i match parziali tra nomi singoli e doppi."""
    if s1 == s2:
        return 100
        
    s1_words = s1.split()
    s2_words = s2.split()
    
    if len(s1_words) == 1 and len(s2_words) > 1:
        if s1_words[0] == s2_words[-1]:
            return 95 
        else:
            return 75 
            
    if len(s1_words) > 1 and len(s2_words) == 1:
        return 75 
                
    set_score = fuzz.token_set_ratio(s1, s2)
    sort_score = fuzz.token_sort_ratio(s1, s2)
    return (set_score + sort_score) / 2

def match_entity_resolution(df_target: pd.DataFrame, df_source: pd.DataFrame, threshold: int = 82):
    manual_map = get_or_create_mapping()
    
    fbref_lookup = {}
    for _, row in df_source.iterrows():
        clean_n = clean_name_for_matching(row['nome_fbref'])
        fbref_lookup[clean_n] = row

    matched_data = []
    diagnostics = []
    matches_found = 0

    for _, row in df_target.iterrows():
        target_name = row['nome']
        target_name_clean = clean_name_for_matching(target_name)
        fbref_row = None
        final_score = 0
        is_manual = False
        
        # A. MANUAL MAPPING (Blindato con token_sort_ratio)
        if target_name in manual_map:
            mapped_clean = clean_name_for_matching(manual_map[target_name])
            valid_manual = []
            for fbref_clean, candidate_row in fbref_lookup.items():
                if fuzz.token_sort_ratio(mapped_clean, fbref_clean) >= 90:
                    valid_manual.append(candidate_row)
            
            if valid_manual:
                fbref_row = valid_manual[0]
                final_score = 100
                is_manual = True

        # B. FUZZY MATCHING (Automatico)
        if fbref_row is None:
            valid_candidates = []
            for fbref_clean, candidate_row in fbref_lookup.items():
                score = custom_scorer(target_name_clean, fbref_clean)
                
                if score >= threshold:
                    if check_iniziali_omonimi(target_name, candidate_row['nome_fbref']):
                        is_serie_a = 1 if candidate_row['campionato_fbref'] == 'ITA-Serie A' else 0
                        valid_candidates.append((candidate_row, score, is_serie_a))
            
            if valid_candidates:
                valid_candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
                fbref_row = valid_candidates[0][0]
                final_score = valid_candidates[0][1]

        # C. SALVATAGGIO INFORMAZIONI
        if fbref_row is not None:
            camp = fbref_row['campionato_fbref']
            weight = LEAGUE_WEIGHTS.get(camp, 0.80)
            
            matched_data.append({
                'id': row['id'], 
                'campionato_fbref': camp,
                'minuti_giocati_2526': fbref_row['minuti_giocati'],
                'gol_p90_pesati': round(fbref_row['gol_p90'] * weight, 3),
                'assist_p90_pesati': round(fbref_row['assist_p90'] * weight, 3),
                'nome_fbref_associato': fbref_row['nome_fbref'],
                'is_manual_match': is_manual
            })
            diagnostics.append({
                'nome_fantalab': target_name, 'nome_fbref_associato': fbref_row['nome_fbref'],
                'squadra_fbref': fbref_row['squadra_fbref'], 'score_confidenza': final_score, 'is_manual_mapping': is_manual
            })
            matches_found += 1
        else:
            matched_data.append({
                'id': row['id'], 'campionato_fbref': None, 'minuti_giocati_2526': None, 
                'gol_p90_pesati': None, 'assist_p90_pesati': None,
                'nome_fbref_associato': None, 'is_manual_match': False
            })
            diagnostics.append({
                'nome_fantalab': target_name, 'nome_fbref_associato': "NESSUN MATCH",
                'squadra_fbref': "N/A", 'score_confidenza': 0, 'is_manual_mapping': is_manual
            })
            
    df_diag = pd.DataFrame(diagnostics)
    df_diag.to_csv("data/03_processed/match_diagnostics.csv", index=False)
    
    print(f"   -> Trovati {matches_found}/{len(df_target)} match validi.")
    return pd.DataFrame(matched_data)

def qa_report(df_master):
    print("\n" + "="*60)
    print(" QA REPORT: AUDIT TOP PLAYER (FVA > 15, Esclusi Portieri)")
    print("="*60)
    
    # 1. NON MATCHATI
    missed_top = df_master[
        (df_master['campionato_fbref'].isna()) & 
        (df_master['fva_mercato'] > 15) & 
        (df_master['ruolo'] != 'P')
    ].copy()
    
    if not missed_top.empty:
        print(f"\n⚠️ {len(missed_top)} TOP PLAYER SENZA STATISTICHE FBREF:")
        print("   (Se sono infortunati cronici min<500 o da campionati minori, ignora)")
        print(missed_top[['nome', 'ruolo', 'fva_mercato']].to_string(index=False))
    else:
        print("\n✅ Tutti i Top Player sono stati matchati con successo!")
        
    # 2. MATCHATI IN AUTOMATICO (Rischio Falsi Positivi)
    auto_top = df_master[
        (df_master['campionato_fbref'].notna()) & 
        (df_master['is_manual_match'] == False) & 
        (df_master['fva_mercato'] > 15) & 
        (df_master['ruolo'] != 'P')
    ].copy()
    
    if not auto_top.empty:
        print(f"\n🔍 AUDIT: {len(auto_top)} TOP PLAYER MATCHATI IN AUTOMATICO:")
        print("   (Controlla che l'accoppiamento sia corretto. Se c'è un errore, aggiungilo al JSON)")
        auto_top['MATCH (FantaLab -> FBRef)'] = auto_top['nome'] + "  ->  " + auto_top['nome_fbref_associato']
        
        # Stampiamo in ordine alfabetico per facilitare la lettura
        auto_top = auto_top.sort_values(by='nome')
        print(auto_top[['MATCH (FantaLab -> FBRef)', 'fva_mercato']].to_string(index=False))
    else:
        print("\n✅ Nessun Top Player matchato in automatico (Tutti blindati dal JSON!).")
        
    print("="*60 + "\n")

def build_master_dataset():
    print("\n--- FASE 1.4: MERGE E ENTITY RESOLUTION ---")
    df_listone = pd.read_csv("data/01_raw/listone_corrente.csv")
    df_storico = pd.read_csv("data/02_interim/storico_serie_a.csv")
    df_fbref = pd.read_csv("data/02_interim/stats_fbref_90.csv")
    
    df_master = df_listone.merge(df_storico, on='id', how='left')
    df_matched_fbref = match_entity_resolution(df_listone, df_fbref, threshold=82)
    df_master = df_master.merge(df_matched_fbref, on='id', how='left')
    
    os.makedirs('data/03_processed', exist_ok=True)
    df_master.to_csv("data/03_processed/master_dataset.csv", index=False)
    
    print(f"\n✅ Master Dataset generato in: data/03_processed/master_dataset.csv")
    print(f"✅ File Diagnostico salvato in: data/03_processed/match_diagnostics.csv")
    print(f"   Righe totali (Giocatori in A): {len(df_master)}")
    
    qa_report(df_master)

if __name__ == '__main__':
    build_master_dataset()