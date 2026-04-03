import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# --- 1. DIZIONARIO TRADUZIONI (Recycling Edition) ---
lang_dict = {
    "English": {
        "title": "Recycling ROI Advisor: Single vs Twin Screw",
        "tech_comp": "📊 technical & operational metrics",
        "fin_comp": "💰 Financial Yield & Energy Saving",
        "res_title": "🏁 Investment Analysis",
        "line_a": "Single Screw (Standard)",
        "line_b": "Twin Screw (High Efficiency)",
        "line_c": "Twin Screw (Advanced Degassing)",
        "t_prod": "Annual Pellet Production",
        "t_oee": "Operational Efficiency (OEE)",
        "t_sec": "Specific Consumption (kWh/kg)",
        "t_filt": "Filtration Cost (per kg)",
        "cost_kg": "Production Cost (€/kg)",
        "margin_yr": "Annual Net Margin (EBT)",
        "energy_sav": "Annual Energy Saving (vs Std)",
        "co2_sav": "CO2 Reduction (Tons/yr)",
        "payback_label": "Payback Period (Years)",
        "crossover_title": "Cumulative Profit vs Single Screw",
        "market_settings": "Market & Utility Settings"
    },
    "Italiano": {
        "title": "Recycling ROI Advisor: Monovite vs Bivite",
        "tech_comp": "📊 Metriche Tecniche ed Operative",
        "fin_comp": "💰 Rendimento Finanziario e Risparmio Energetico",
        "res_title": "🏁 Analisi dell'Investimento",
        "line_a": "Monovite (Standard)",
        "line_b": "Bivite (Alta Efficienza)",
        "line_c": "Bivite (Degassaggio Avanzato)",
        "t_prod": "Produzione Annua Granulo",
        "t_oee": "Efficienza Operativa (OEE)",
        "t_sec": "Consumo Specifico (kWh/kg)",
        "t_filt": "Costo Filtrazione (al kg)",
        "cost_kg": "Costo di Trasformazione (€/kg)",
        "margin_yr": "Margine Netto Annuo (EBT)",
        "energy_sav": "Risparmio Energetico Annuo (vs Std)",
        "co2_sav": "Riduzione CO2 (Tonnellate/anno)",
        "payback_label": "Periodo di Payback (Anni)",
        "crossover_title": "Profitto Cumulativo vs Monovite",
        "market_settings": "Impostazioni Mercato e Utility"
    }
}

st.set_page_config(page_title="Recycling ROI Advisor", layout="wide")
lingua = st.sidebar.selectbox("Language", list(lang_dict.keys()), index=1)
t = lang_dict[lingua]

# --- COLORS ---
color_mono = "#636EFA" # Blu per Monovite
color_twin = "#00CC96" # Verde per Bivite
color_adv  = "#AB63FA" # Viola per Bivite Advanced

# --- 2. SIDEBAR: MARKET & UTILITIES ---
st.sidebar.header(f"🌍 {t['market_settings']}")
simbolo = "€"
c_waste = st.sidebar.number_input(f"Waste Material Cost ({simbolo}/kg)", value=0.45)
p_pellet = st.sidebar.number_input(f"Pellet Selling Price ({simbolo}/kg)", value=0.95)
c_ene = st.sidebar.number_input(f"Energy Cost ({simbolo}/kWh)", value=0.22)
co2_factor = st.sidebar.number_input("CO2 Factor (kg CO2/kWh)", value=0.45) # Media europea
h_an = st.sidebar.number_input("Working Hours/Year", value=7500)

st.sidebar.markdown("---")
st.sidebar.subheader("🏢 Fixed Costs (Shared)")
operator_cost = st.sidebar.number_input("Operator Cost/Year", value=50000)
space_cost = st.sidebar.number_input("Space & Insurance/Year", value=30000)
depreciation_yrs = 5
interest_rate = 0.03

show_advanced = st.sidebar.checkbox("Show Advanced Twin Screw", value=False)

# --- 3. INPUT COMPARISON ---
cols = st.columns(3 if show_advanced else 2)

with cols[0]:
    st.subheader(f"🔄 {t['line_a']}")
    ca = st.number_input("CAPEX Monovite", value=800000)
    pa = st.number_input("Output (kg/h) Mono", value=1000)
    oa = st.number_input("OEE (%) Mono", value=85.0)
    seca = st.number_input("SEC (kWh/kg) Mono", value=0.32, format="%.2f")
    filta = st.number_input("Filtrazione (€/kg) Mono", value=0.015, format="%.3f")

with cols[1]:
    st.subheader(f"⚡ {t['line_b']}")
    cb = st.number_input("CAPEX Bivite", value=1100000)
    pb = st.number_input("Output (kg/h) Twin", value=1100) # Spesso la bivite ha output superiore
    ob = st.number_input("OEE (%) Twin", value=88.0)
    secb = st.number_input("SEC (kWh/kg) Twin", value=0.21, format="%.2f") # -34% circa
    filtb = st.number_input("Filtrazione (€/kg) Twin", value=0.012, format="%.3f")

if show_advanced:
    with cols[2]:
        st.subheader(f"🌀 {t['line_c']}")
        cc = st.number_input("CAPEX Bivite Adv", value=1300000)
        pc = st.number_input("Output (kg/h) Adv", value=1100)
        oc = st.number_input("OEE (%) Adv", value=90.0)
        secc = st.number_input("SEC (kWh/kg) Adv", value=0.20, format="%.2f")
        filtc = st.number_input("Filtrazione (€/kg) Adv", value=0.010, format="%.3f")

# --- 4. CALCULATIONS ---
def get_rec_metrics(p, o, sec, filt, cap):
    ton_yr = (p * h_an * (o/100)) / 1000
    kg_yr = ton_yr * 1000
    
    # Costi Variabili
    raw_cost = kg_yr * c_waste
    energy_cost = kg_yr * sec * c_ene
    filt_cost = kg_yr * filt
    maint_cost = cap * 0.03
    
    # Costi Fissi e Finanziari
    fix_cost = operator_cost + space_cost
    depreciation = cap / depreciation_yrs
    interest = cap * interest_rate
    
    total_cost = raw_cost + energy_cost + filt_cost + maint_cost + fix_cost + depreciation + interest
    revenue = kg_yr * p_pellet
    marg = revenue - total_cost
    
    ckg = total_cost / kg_yr if kg_yr > 0 else 0
    pb = cap / (marg + depreciation) if (marg + depreciation) > 0 else 0
    co2 = (kg_yr * sec * co2_factor) / 1000 # Tonnellate CO2
    
    return ton_yr, marg, ckg, pb, energy_cost, co2

ton_a, marg_a, ckg_a, pb_a, ec_a, co2_a = get_rec_metrics(pa, oa, seca, filta, ca)
ton_b, marg_b, ckg_b, pb_b, ec_b, co2_b = get_rec_metrics(pb, ob, secb, filtb, cb)
if show_advanced:
    ton_c, marg_c, ckg_c, pb_c, ec_c, co2_c = get_rec_metrics(pc, oc, secc, filtc, cc)

# --- 5. TABLES ---
st.subheader(t['tech_comp'])
tech_data = {
    "Metric": [t['t_prod'], t['t_oee'], t['t_sec'], t['t_filt']],
    "Monovite": [f"{ton_a:,.0f} T", f"{oa}%", f"{seca}", f"{filta}"],
    "Bivite": [f"{ton_b:,.0f} T", f"{ob}%", f"{secb}", f"{filtb}"]
}
if show_advanced: tech_data["Bivite Adv"] = [f"{ton_c:,.0f} T", f"{oc}%", f"{secc}", f"{filtc}"]
st.table(pd.DataFrame(tech_data))

st.subheader(t['fin_comp'])
fin_data = {
    "Indicator": [t['cost_kg'], t['margin_yr'], t['energy_sav'], t['co2_sav'], t['payback_label']],
    "Monovite": [f"{ckg_a:.3f}", f"{marg_a:,.0f}", "-", "-", f"{pb_a:.2f}"],
    "Bivite": [f"{ckg_b:.3f}", f"{marg_b:,.0f}", f"{simbolo} {ec_a - ec_b:,.0f}", f"{co2_a - co2_b:.1f} T", f"{pb_b:.2f}"]
}
if show_advanced:
    fin_data["Bivite Adv"] = [f"{ckg_c:.3f}", f"{marg_c:,.0f}", f"{simbolo} {ec_a - ec_c:,.0f}", f"{co2_a - co2_c:.1f} T", f"{pb_c:.2f}"]
st.table(pd.DataFrame(fin_data))

# --- 6. CHARTS ---
st.header(t['res_title'])
c1, c2 = st.columns(2)
with c1:
    names = [t['line_a'], t['line_b']]; vals = [pb_a, pb_b]; colors = [color_mono, color_twin]
    if show_advanced:
        names.append(t['line_c']); vals.append(pb_c); colors.append(color_adv)
    fig_pb = go.Figure(go.Bar(y=names, x=vals, orientation='h', marker_color=colors))
    fig_pb.update_layout(title=t['payback_label'], xaxis_title="Years", yaxis={'autorange': "reversed"})
    st.plotly_chart(fig_pb, use_container_width=True)

with c2:
    yrs = [i/2 for i in range(13)]
    fig_cross = go.Figure()
    fig_cross.add_trace(go.Scatter(x=yrs, y=[(-(cb-ca)+(marg_b-marg_a)*y) for y in yrs], name="Twin vs Single", line=dict(color=color_twin, width=4)))
    if show_advanced:
        fig_cross.add_trace(go.Scatter(x=yrs, y=[(-(cc-ca)+(marg_c-marg_a)*y) for y in yrs], name="Adv vs Single", line=dict(color=color_adv, width=4)))
    fig_cross.add_hline(y=0, line_dash="dash", line_color="red")
    fig_cross.update_layout(title=t['crossover_title'], xaxis_title="Years")
    st.plotly_chart(fig_cross, use_container_width=True)

st.divider()
notes = st.text_area(t['notes_label'], placeholder="Binova vs Erema/Starlinger analysis...", height=100)
