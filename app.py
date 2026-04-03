import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# --- 1. DIZIONARIO TRADUZIONI ---
lang_dict = {
    "Italiano": {
        "title": "Recycling ROI Advisor: Monovite vs Bivite",
        "tech_comp": "📊 Dati Tecnici e Consumi",
        "fin_comp": "💰 Conto Economico e Payback",
        "res_title": "🏁 Analisi del Rientro",
        "line_a": "Monovite (Standard)",
        "line_b": "Bivite (High Efficiency)",
        "market_settings": "Parametri di Business"
    }
}

st.set_page_config(page_title="Recycling ROI Tool", layout="wide")
t = lang_dict["Italiano"]

# --- 2. SIDEBAR: BUSINESS CASE ---
st.sidebar.header(f"🌍 {t['market_settings']}")
c_waste = st.sidebar.number_input("Costo Acquisto Rifiuto (€/kg)", value=0.55)
p_sell = st.sidebar.number_input("Prezzo Vendita Granulo (€/kg)", value=1.05)
process_loss = st.sidebar.slider("Perdita di Processo/Scarto (%)", 0, 25, 12) / 100
c_disposal = st.sidebar.number_input("Costo Smaltimento Scarto (€/kg)", value=0.15)

st.sidebar.markdown("---")
fixed_costs_yr = st.sidebar.number_input("Costi Fissi Annui (Staff, Affitto, etc. €)", value=180000)
tax_rate = st.sidebar.slider("Aliquota Tasse (%)", 0, 50, 24) / 100
c_ene = st.sidebar.number_input("Costo Energia (€/kWh)", value=0.22)
h_an = st.sidebar.number_input("Ore di Lavoro Annue", value=7000)

# --- 3. INPUT COMPARISON ---
p_shared = st.number_input("Input Materiale Orario (kg/h)", value=500)
o_shared = st.slider("Efficienza Impianto (OEE %)", 50, 100, 85)

col1, col2 = st.columns(2)
with col1:
    st.subheader(f"🔄 {t['line_a']}")
    # CAPEX Variabile con default a 400k
    ca = st.number_input("CAPEX Monovite (€)", value=400000, step=10000)
    seca = st.number_input("SEC Monovite (kWh/kg)", value=0.35, format="%.2f")

with col2:
    st.subheader(f"⚡ {t['line_b']}")
    # CAPEX Variabile con default a 600k
    cb = st.number_input("CAPEX Bivite (€)", value=600000, step=10000)
    secb = st.number_input("SEC Bivite (kWh/kg)", value=0.22, format="%.2f")

# --- 4. CALCOLI FINANZIARI ---
def get_detailed_metrics(cap, sec):
    input_kg_yr = p_shared * h_an * (o_shared / 100)
    output_kg_yr = input_kg_yr * (1 - process_loss)
    scarto_kg_yr = input_kg_yr * process_loss
    
    # --- OPEX VARIABILI ---
    cost_raw = input_kg_yr * c_waste
    cost_ene = input_kg_yr * sec * c_ene
    cost_disp = scarto_kg_yr * c_disposal
    maint_costs = cap * 0.04 # Manutenzione stimata sull'investimento
    
    total_opex = cost_raw + cost_ene + cost_disp + maint_costs + fixed_costs_yr
    
    # --- REVENUE ---
    revenue = output_kg_yr * p_sell
    
    # --- MARGINI ---
    ebitda = revenue - total_opex
    depreciation = cap / 5 # Ammortamento 5 anni
    ebt = ebitda - depreciation
    
    # Tasse e Utile Netto
    taxes = ebt * tax_rate if ebt > 0 else 0
    net_profit = ebt - taxes
    
    # Cash Flow Netto (Utile + Ammortamento)
    cash_flow = net_profit + depreciation
    
    # Calcolo Payback
    pb = cap / cash_flow if cash_flow > 0 else 0
    return output_kg_yr/1000, ebitda, net_profit, cost_ene, pb

ton_a, ebitda_a, net_a, ene_a, pb_a = get_detailed_metrics(ca, seca)
ton_b, ebitda_b, net_b, ene_b, pb_b = get_detailed_metrics(cb, secb)

# --- 5. TABELLA RISULTATI ---
st.subheader(t['fin_comp'])
res_df = pd.DataFrame({
    "Voce": ["Produzione Netta", "Costo Energia Annuo", "Utile Netto (Post-Tasse)", "Payback Reale (Anni)"],
    "Monovite": [f"{ton_a:,.0f} T", f"€ {ene_a:,.0f}", f"€ {net_a:,.0f}", f"{pb_a:.2f}"],
    "Bivite": [f"{ton_b:,.0f} T", f"€ {ene_b:,.0f}", f"€ {net_b:,.0f}", f"{pb_b:.2f}"]
})
st.table(res_df)

# --- 6. GRAFICO CASH FLOW ---
yrs = list(range(11)) # Esteso a 10 anni per vedere meglio il lungo termine
cum_a = [-ca + (net_a + ca/5) * y for y in yrs]
cum_b = [-cb + (net_b + cb/5) * y for y in yrs]

fig = go.Figure()
fig.add_trace(go.Scatter(x=yrs, y=cum_a, name="Monovite", line=dict(color='blue', dash='dot')))
fig.add_trace(go.Scatter(x=yrs, y=cum_b, name="Bivite", line=dict(color='green', width=4)))
fig.add_hline(y=0, line_dash="dash", line_color="red")
fig.update_layout(
    title="Rientro dell'investimento: Cash Flow Netto Cumulativo",
    xaxis_title="Anni",
    yaxis_title="Euro (€)",
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)

st.info(f"💡 Il risparmio energetico annuo della Bivite è di € {ene_a - ene_b:,.0f} rispetto alla Monovite.")
