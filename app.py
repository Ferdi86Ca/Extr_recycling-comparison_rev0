import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# --- 1. DIZIONARIO TRADUZIONI ---
lang_dict = {
    "Italiano": {
        "title": "Recycling ROI Advisor: Analisi Realistica",
        "tech_comp": "📊 Parametri di Processo",
        "fin_comp": "💰 Analisi Economica Reale",
        "res_title": "🏁 Analisi del Flusso di Cassa",
        "line_a": "Monovite (Standard)",
        "line_b": "Bivite (High Efficiency)",
        "t_prod": "Granulo Venduto (T/anno)",
        "t_sec": "Consumo Specifico (kWh/kg)",
        "energy_sav": "Risparmio Energetico",
        "payback_label": "Payback Period (Anni)",
        "market_settings": "Mercato e Processo"
    }
}

st.set_page_config(page_title="Recycling ROI Tool", layout="wide")
t = lang_dict["Italiano"]

# --- 2. SIDEBAR: PARAMETRI DI MERCATO ---
st.sidebar.header(f"🌍 {t['market_settings']}")
c_waste = st.sidebar.number_input("Costo Acquisto Rifiuto (€/kg)", value=0.50, step=0.05)
p_sell = st.sidebar.number_input("Prezzo Vendita Granulo (€/kg)", value=1.05, step=0.05)
process_loss = st.sidebar.slider("Perdita di Processo/Scarto (%)", 0, 30, 10) / 100

st.sidebar.markdown("---")
c_ene = st.sidebar.number_input("Costo Energia (€/kWh)", value=0.22)
h_an = st.sidebar.number_input("Ore di Lavoro Annue", value=7000)

# --- 3. INPUT COMPARISON ---
st.info("Logica: La Bivite riduce il consumo elettrico e migliora la qualità, ma deve ripagare un investimento maggiore.")
p_shared = st.number_input("Input Materiale Orario (kg/h)", value=1000)
o_shared = st.slider("Efficienza Impianto (OEE %)", 50, 100, 80)

col1, col2 = st.columns(2)
with col1:
    st.subheader("🔄 Monovite")
    ca = st.number_input("CAPEX Monovite (€)", value=850000)
    seca = st.number_input("SEC Monovite (kWh/kg)", value=0.35)

with col2:
    st.subheader("⚡ Bivite")
    cb = st.number_input("CAPEX Bivite (€)", value=1250000)
    secb = st.number_input("SEC Bivite (kWh/kg)", value=0.22)

# --- 4. CALCOLI REALI ---
def get_real_metrics(cap, sec):
    # Input totale annuo
    input_kg_yr = p_shared * h_an * (o_shared / 100)
    # Output vendibile (tolto lo scarto)
    output_kg_yr = input_kg_yr * (1 - process_loss)
    
    # COSTI
    costo_materia_totale = input_kg_yr * c_waste
    costo_energia_totale = input_kg_yr * sec * c_ene
    manutenzione_fisso = cap * 0.04 # 4% del valore macchina
    costi_personale_spazio = 120000 # Costo fisso stimato (operatori + capannone)
    
    spese_totali_op = costo_materia_totale + costo_energia_totale + manutenzione_fisso + costi_personale_spazio
    
    # RICAVI
    ricavi_totali = output_kg_yr * p_sell
    
    # EBITDA (Margine Operativo Lordo)
    ebitda = ricavi_totali - spese_totali_op
    
    # AMMORTAMENTO (5 anni)
    depreciation = cap / 5
    
    # UTILE PRIMA DELLE TASSE (EBT)
    ebt = ebitda - depreciation
    
    # PAYBACK (CAPEX / Cash Flow)
    cash_flow = ebt + depreciation
    pb = cap / cash_flow if cash_flow > 0 else 0
    
    return output_kg_yr/1000, ebt, costo_energia_totale, pb

ton_a, ebt_a, ene_a, pb_a = get_real_metrics(ca, seca)
ton_b, ebt_b, ene_b, pb_b = get_real_metrics(cb, secb)

# --- 5. VISUALIZZAZIONE ---
st.subheader("💰 Risultati Economici")
res_data = {
    "Voce di Bilancio": ["Produzione Venduta", "Costo Energia Annuo", "Utile Netto Annuo (EBT)", "Payback Period"],
    "Monovite": [f"{ton_a:,.0f} T", f"€ {ene_a:,.0f}", f"€ {ebt_a:,.0f}", f"{pb_a:.2f} anni"],
    "Bivite": [f"{ton_b:,.0f} T", f"€ {ene_b:,.0f}", f"€ {ebt_b:,.0f}", f"{pb_b:.2f} anni"]
}
st.table(pd.DataFrame(res_data))

# Grafico del Cash Flow Cumulativo
yrs = [0, 1, 2, 3, 4, 5, 6, 7]
cum_a = [-ca + (ebt_a + ca/5) * y for y in yrs]
cum_b = [-cb + (ebt_b + cb/5) * y for y in yrs]

fig = go.Figure()
fig.add_trace(go.Scatter(x=yrs, y=cum_a, name="Monovite", line=dict(color='blue')))
fig.add_trace(go.Scatter(x=yrs, y=cum_b, name="Bivite", line=dict(color='green', width=4)))
fig.add_hline(y=0, line_dash="dash")
fig.update_layout(title="Rientro dell'investimento (Cash Flow Cumulativo)", xaxis_title="Anni", yaxis_title="Euro")
st.plotly_chart(fig, use_container_width=True)
