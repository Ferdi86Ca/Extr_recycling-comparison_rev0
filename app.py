import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# --- 1. DIZIONARIO TRADUZIONI ---
lang_dict = {
    "Italiano": {
        "title": "Recycling Energy Comparator: Monovite vs Bivite",
        "tech_comp": "📊 Parametri Energetici e Produttivi",
        "fin_comp": "💰 Analisi Economica del Risparmio",
        "res_title": "🏁 Risultato del Confronto Energetico",
        "line_a": "Sistema Monovite (Standard)",
        "line_b": "Sistema Bivite (High Efficiency)",
        "t_prod": "Produzione Annua (Tonnellate)",
        "t_sec": "Consumo Specifico (kWh/kg)",
        "energy_sav": "Risparmio Energetico Annuo",
        "co2_sav": "Riduzione Emissioni CO2 (T/anno)",
        "payback_label": "Rientro Extra-Investimento (Anni)",
        "crossover_title": "Rendimento Cumulativo del Risparmio",
        "market_settings": "Parametri Energetici e Costi"
    },
    "English": {
        "title": "Recycling Energy Comparator: Single vs Twin Screw",
        "tech_comp": "📊 Energy & Production Metrics",
        "fin_comp": "💰 Economic Saving Analysis",
        "res_title": "🏁 Energy Comparison Result",
        "line_a": "Single Screw (Standard)",
        "line_b": "Twin Screw (High Efficiency)",
        "t_prod": "Annual Production (Tons)",
        "t_sec": "Spec. Consumption (kWh/kg)",
        "energy_sav": "Annual Energy Saving",
        "co2_sav": "CO2 Reduction (Tons/yr)",
        "payback_label": "Extra-Investment Payback (Years)",
        "crossover_title": "Cumulative Saving Yield",
        "market_settings": "Energy & Cost Settings"
    }
}

st.set_page_config(page_title="Energy Efficiency Tool", layout="wide")
lingua = st.sidebar.selectbox("Language", list(lang_dict.keys()), index=0)
t = lang_dict[lingua]

# --- COLORS ---
color_mono = "#636EFA" 
color_twin = "#00CC96" 

# --- 2. SIDEBAR: PARAMETRI FISSI ---
st.sidebar.header(f"🌍 {t['market_settings']}")
c_ene = st.sidebar.number_input("Costo Energia (€/kWh)", value=0.22)
co2_factor = st.sidebar.number_input("Fattore CO2 (kg CO2/kWh)", value=0.45)
h_an = st.sidebar.number_input("Ore di Lavoro Annue", value=7500)

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Parametri Finanziari")
interest_rate = st.sidebar.slider("Tasso di Interesse (%)", 0.0, 10.0, 3.0) / 100
depreciation_yrs = 5

# --- 3. INPUT COMPARISON (Portata Identica) ---
st.info("💡 In questo modello la portata (kg/h) è ipotizzata identica per entrambi i sistemi.")
p_shared = st.number_input("Portata Oraria Condivisa (kg/h)", value=1000)
o_shared = st.slider("Efficienza OEE (%)", 50, 100, 85)

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"🔄 {t['line_a']}")
    ca = st.number_input("CAPEX Monovite (€)", value=800000)
    seca = st.number_input("SEC Monovite (kWh/kg)", value=0.32, format="%.2f")

with col2:
    st.subheader(f"⚡ {t['line_b']}")
    cb = st.number_input("CAPEX Bivite (€)", value=1100000)
    secb = st.number_input("SEC Bivite (kWh/kg)", value=0.21, format="%.2f")

# --- 4. CALCULATIONS ---
def get_energy_metrics(cap, sec):
    kg_yr = p_shared * h_an * (o_shared / 100)
    ton_yr = kg_yr / 1000
    
    annual_energy_cost = kg_yr * sec * c_ene
    annual_co2 = (kg_yr * sec * co2_factor) / 1000
    
    # Calcolo margine semplificato basato solo sul risparmio
    # (Usiamo il risparmio energetico come "guadagno" per il payback)
    return ton_yr, annual_energy_cost, annual_co2

ton_yr, cost_a, co2_a = get_energy_metrics(ca, seca)
ton_yr, cost_b, co2_b = get_energy_metrics(cb, secb)

annual_saving = cost_a - cost_b
extra_capex = cb - ca
payback_extra = extra_capex / annual_saving if annual_saving > 0 else 0

# --- 5. TABLES ---
st.subheader(t['tech_comp'])
tech_data = {
    "Metric": [t['t_prod'], t['t_sec'], "Consumo Annuo (MWh)"],
    "Monovite": [f"{ton_yr:,.0f} T", f"{seca}", f"{(p_shared*h_an*(o_shared/100)*seca)/1000:,.0f}"],
    "Bivite": [f"{ton_yr:,.0f} T", f"{secb}", f"{(p_shared*h_an*(o_shared/100)*secb)/1000:,.0f}"]
}
st.table(pd.DataFrame(tech_data))

st.subheader(t['fin_comp'])
fin_data = {
    "Indicator": ["Costo Energia Annuo", t['energy_sav'], t['co2_sav'], t['payback_label']],
    "Monovite": [f"€ {cost_a:,.0f}", "-", "-", "-"],
    "Bivite": [f"€ {cost_b:,.0f}", f"€ {annual_saving:,.0f}", f"{co2_a - co2_b:.1f} T", f"{payback_extra:.2f} anni"]
}
st.table(pd.DataFrame(fin_data))

# --- 6. CHARTS ---
st.header(t['res_title'])
c1, c2 = st.columns(2)

with c1:
    # Grafico a barre del risparmio
    fig_sav = go.Figure(go.Bar(
        x=[t['line_a'], t['line_b']],
        y=[cost_a, cost_b],
        marker_color=[color_mono, color_twin],
        text=[f"€ {cost_a:,.0f}", f"€ {cost_b:,.0f}"],
        textposition='auto',
    ))
    fig_sav.update_layout(title="Confronto Spesa Energetica Annua (€)")
    st.plotly_chart(fig_sav, use_container_width=True)

with c2:
    # Grafico Crossover dell'extra-investimento
    yrs = [i for i in range(11)]
    # Calcolo del recupero dell'extra-capex nel tempo
    cum_saving = [(-extra_capex + (annual_saving * y)) for y in yrs]
    
    fig_cross = go.Figure()
    fig_cross.add_trace(go.Scatter(x=yrs, y=cum_saving, name="Recupero Extra-CAPEX", line=dict(color=color_twin, width=4)))
    fig_cross.add_hline(y=0, line_dash="dash", line_color="red")
    fig_cross.update_layout(title=t['crossover_title'], xaxis_title="Anni", yaxis_title="€")
    st.plotly_chart(fig_cross, use_container_width=True)
