import streamlit as st
import pandas as pd
from dynamic_pricer import AuctionEngine

# Configurazione della pagina (deve essere la prima riga Streamlit)
st.set_page_config(page_title="FantAI - Asta Live", page_icon="⚽", layout="wide")

# ==========================================
# 1. INIZIALIZZAZIONE MOTORE
# ==========================================
@st.cache_resource
def init_engine():
    return AuctionEngine()

engine = init_engine()
# Forza la rilettura del JSON ad ogni ricaricamento della pagina
engine.load_state()

# Liste per le selectbox
giocatori_comprati = [p['nome'] for p in engine.state["mio_team"]["giocatori_acquistati"]]
for opp in engine.state["avversari"].values():
    giocatori_comprati.extend([p['nome'] for p in opp["giocatori_acquistati"]])

df_liberi = engine.df_listone[~engine.df_listone['nome'].isin(giocatori_comprati)]
lista_nomi_liberi = df_liberi['nome'].sort_values().tolist()
lista_avversari = list(engine.state["avversari"].keys())

# ==========================================
# 2. LAYOUT INTESTAZIONE & STATO SQUADRA
# ==========================================
st.title("🎯 FantAI - Dashboard Asta Live")

# Metriche del "Mio Team"
st.sidebar.header("📊 Il Mio Team")
budget_rimasto = engine.state["mio_team"]["budget_residuo"]
slot_rimasti = sum(engine.state["mio_team"]["slot_residui"].values())
inflazione = engine.calculate_inflation_index()

st.sidebar.metric(label="💰 Budget Residuo", value=f"{budget_rimasto} cr.")
st.sidebar.metric(label="👥 Slot Vuoti", value=slot_rimasti)
st.sidebar.metric(label="📈 Indice Inflazione", value=f"{inflazione}x", 
                  help="< 1.0 significa che il mercato è povero. > 1.0 il mercato è drogato.")

st.sidebar.divider()
st.sidebar.subheader("Target di Reparto")
for ruolo, target in engine.state["mio_team"]["target_spesa"].items():
    slot_ruolo = engine.state["mio_team"]["slot_residui"][ruolo]
    st.sidebar.text(f"Ruolo {ruolo}: {target} cr. (Slot: {slot_ruolo})")

# ==========================================
# 3. RICERCA E VALUTAZIONE LIVE
# ==========================================
st.subheader("🔍 Cerca Giocatore")
col_search, col_empty = st.columns([1, 1])

with col_search:
    selected_player = st.selectbox(
        "Digita il nome del giocatore chiamato:", 
        options=[""] + lista_nomi_liberi,
        index=0
    )

st.divider()

# Mostra i dati se un giocatore è selezionato
if selected_player:
    valutazione = engine.evaluate_player(selected_player)
    
    if valutazione.get("status") == "Disponibile":
        # --- PANNELLO VALUTAZIONI (IL CERVELLO) ---
        col_info, col_bid, col_enemy = st.columns(3)
        
        with col_info:
            st.markdown(f"### {valutazione['nome']}")
            st.markdown(f"**Ruolo:** {valutazione['ruolo']} | **Squadra:** {valutazione['squadra']}")
            st.markdown(f"**Valore AI Live:** `{valutazione['valore_ai_LIVE']} cr.`")
            
            # Gestione grafica dell'avviso tattico
            avviso = valutazione['avviso_tattico']
            if "🎯" in avviso or "✅" in avviso or "🛡️" in avviso:
                st.success(avviso)
            elif "⚠️" in avviso:
                st.warning(avviso)
            elif "🚫" in avviso or "❌" in avviso:
                st.error(avviso)
            else:
                st.info(avviso)
                
        with col_bid:
            st.markdown("### IL TUO LIMITE")
            max_bid = valutazione['max_bid_consigliato']
            # Se è 0, colore rosso. Altrimenti verde.
            if max_bid == 0:
                st.error(f"🛑 MAX BID: {max_bid} cr.")
                st.caption("Il motore sconsiglia l'acquisto!")
            else:
                st.success(f"🟢 MAX BID: {max_bid} cr.")
                st.caption(f"Limite Assoluto Portafoglio: {valutazione['max_bid_assoluto']} cr.")
                
        with col_enemy:
            st.markdown("### PERICOLO NEMICO")
            st.warning(f"⚠️ Rilancio Max: {valutazione['pericolo_max_nemico']} cr.")
            st.caption(f"Avversario più ricco: {valutazione['nemico_piu_ricco']}")

        st.divider()
        
        # --- PANNELLO ACQUISTO (L'AZIONE) ---
        st.subheader("🛒 Registra Acquisto")
        col_price, col_btn_mine, col_btn_enemy, col_who_enemy = st.columns([1, 1, 1, 1])
        
        with col_price:
            prezzo_acquisto = st.number_input("Prezzo Battuto:", min_value=1, step=1, value=1)
            
        with col_btn_mine:
            st.write("") # Spaziatura
            st.write("")
            if st.button("✅ COMPRATO (MIO TEAM)", use_container_width=True, type="primary"):
                engine.register_purchase(selected_player, prezzo_acquisto, "mio_team")
                st.rerun()
                
        with col_who_enemy:
            avversario_selezionato = st.selectbox("Chi l'ha preso?", options=lista_avversari)
            
        with col_btn_enemy:
            st.write("")
            st.write("")
            if st.button("❌ PRESO DA AVVERSARI", use_container_width=True):
                engine.register_purchase(selected_player, prezzo_acquisto, avversario_selezionato)
                st.rerun()

else:
    st.info("👈 Seleziona un giocatore dalla barra di ricerca per visualizzare le stime AI in tempo reale.")