import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# --- 1. DIZIONARIO TRADUZIONI ---
lang_dict = {
    "Italiano": {
        "title": "Recycling Energy Comparator: Monovite vs Bivite",
        "tech_comp": "📊 Parametri Energetici e Produttivi",
        "fin_comp": "💰 Analisi Economica e Margini",
        "res_title": "🏁 Risultato del Confronto Energetico",
        "line_a": "Sistema Monovite (Standard)",
        "line_b": "Sistema Bivite (High Efficiency)",
        "t_prod": "Produzione Annua (Tonnellate)",
        "t_sec": "Consumo Specifico (kWh/kg)",
        "energy_sav": "Risparmio Energetico Annuo",
        "co2_sav": "Riduzione Emissioni CO2 (T/anno)",
        "payback_label": "Rientro Investimento Totale (Anni)",
        "crossover_title": "Rendimento Cumulativo (Profitto Netto)",
        "market_settings": "Parametri Mercato e Utility"
    },
    "English": {
        "title": "Recycling Energy Comparator: Single vs Twin Screw",
        "tech_comp": "📊 Energy & Production Metrics",
        "fin_comp": "💰 Economic & Margin Analysis",
        "res_title": "🏁 Energy Comparison Result",
        "line_a": "Single Screw (Standard)",
        "line_b": "Twin Screw (High Efficiency)",
        "t_prod": "Annual Production (Tons)",
        "t_sec": "Spec. Consumption (kWh/kg)",
        "energy_sav": "Annual Energy Saving",
        "co2_sav": "CO2 Reduction (Tons/yr)",
        "payback_label": "Total Investment Payback (Years)",
        "crossover_title": "Cumulative Yield (Net Profit)",
        "market_settings": "Market & Utility Settings"
    }
}

st.set_page_config(page_title="Recycling ROI Tool", layout="wide")
lingua = st.sidebar.selectbox("Language", list(lang_dict.keys()), index=0)
t = lang_dict[lingua]

# --- COLORS ---
color_mono = "#636EFA" 
color_twin = "#00CC96" 

# --- 2. SIDEBAR: PARAMETRI COMUNI ---
st.sidebar.header(f"🌍 {t['market_settings']}")

# Nuovi parametri richiesti
c_waste = st.sidebar.number_input("Costo Materia Prima (€/kg)", value=0.45, step=0.05)
p_sell = st.sidebar.number_input("Prezzo Vendita Granulo (€/kg)", value=1.10, step=0.05)

st.sidebar.markdown("---")
c_ene = st.sidebar.number_input("Costo Energia (€/kWh)", value=0.22)
co2_factor = st.sidebar.number_input("Fattore CO2 (kg CO2/kWh)", value=0.45)
h_an = st.sidebar.number_input("Ore di Lavoro Annue", value=7500)

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Parametri Finanziari")
interest_rate = st.sidebar.slider("Tasso di Interesse (%)", 0.0, 10.0, 3.0) / 100
depreciation_yrs = 5

# --- 3. INPUT COMPARISON (Portata Identica) ---
st.info("💡 Portata (kg/h) ed efficienza (OEE) sono ipotizzate identiche per isolare il vantaggio energetico.")
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
def get_full_metrics(cap, sec):
    kg_yr = p_shared * h_an * (o_shared / 100)
    ton_yr = kg_yr / 1000
    
    # Ricavi e Costi Materia (Uguali per entrambi)
    revenue = kg_yr * p_sell
    raw_material_cost = kg_yr * c_waste
    
    # Costo Energia (Variabile tra i due)
    energy_cost = kg_yr * sec * c_ene
    
    # Altri costi stimati (Manutenzione 2% CAPEX + Ammortamento)
    maint = cap * 0.02
    depreciation = cap / depreciation_yrs
    interest = cap * interest_rate
    
    # Margine Netto (EBT)
    total_op_cost = raw_material_cost + energy_cost + maint + interest
    margin = revenue - total_op_cost - depreciation
    
    annual_co2 = (kg_yr * sec * co2_factor) / 1000
    
    # Payback basato su Cash Flow (Margine + Ammortamento)
    pb = cap / (margin + depreciation) if (margin + depreciation) > 0 else 0
    
    return ton_yr, margin, energy_cost, annual_co2, pb

ton_yr, marg_a, cost_ene_a, co2_a, pb_a = get_full_metrics(ca, seca)
ton_yr, marg_b, cost_ene_b, co2_b, pb_b = get_full_metrics(cb, secb)

annual_energy_saving = cost_ene_a - cost_ene_b

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
    "Indicator": ["Margine Annuo (EBT)", "Costo Energia Annuo", t['energy_sav'], t['co2_sav'], t['payback_label']],
    "Monovite": [f"€ {marg_a:,.0f}", f"€ {cost_ene_a:,.0f}", "-", "-", f"{pb_a:.2f} anni"],
    "Bivite": [f"€ {marg_b:,.0f}", f"€ {cost_ene_b:,.0f}", f"€ {annual_energy_saving:,.0f}", f"{co2_a - co2_b:.1f} T", f"{pb_b:.2f} anni"]
}
st.table(pd.DataFrame(fin_data))

# --- 6. CHARTS ---
st.header(t['res_title'])
c1, c2 = st.columns(2)

with c1:
    # Confronto Margine Annuo
    fig_marg = go.Figure(go.Bar(
        x=[t['line_a'], t['line_b']],
        y=[marg_a, marg_b],
        marker_color=[color_mono, color_twin],
        text=[f"€ {marg_a:,.0f}", f"€ {marg_b:,.0f}"],
        textposition='auto',
    ))
    fig_marg.update_layout(title="Confronto Utile Annuo Netto (EBT)")
    st.plotly_chart(fig_marg, use_container_width=True)

with c2:
    # Crossover Chart: Profitto Cumulativo
    yrs = [i for i in range(11)]
    # Cumulativo = -CAPEX + (Margine + Ammortamento) * anni
    cum_a = [-ca + (marg_a + ca/5) * y for y in yrs]
    cum_b = [-cb + (marg_b + cb/5) * y for y in yrs]
    
    fig_cross = go.Figure()
    fig_cross.add_trace(go.Scatter(x=yrs, y=cum_a, name=t['line_a'], line=dict(color=color_mono, width=3)))
    fig_cross.add_trace(go.Scatter(x=yrs, y=cum_b, name=t['line_b'], line=dict(color=color_twin, width=4)))
    fig_cross.add_hline(y=0, line_dash="dash", line_color="black")
    fig_cross.update_layout(title=t['crossover_title'], xaxis_title="Anni", yaxis_title="€ Profitto Cumulativo")
    st.plotly_chart(fig_cross, use_container_width=True)
