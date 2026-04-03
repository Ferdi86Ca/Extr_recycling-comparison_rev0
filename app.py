import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# --- 1. CONFIGURAZIONE E TRADUZIONI ---
st.set_page_config(page_title="Twin Screw Advantage", layout="wide")
t = {
    "title": "Analisi Efficienza: Il Vantaggio Bivite",
    "opex_chart": "Confronto Costi Operativi Annuali (OPEX)",
    "extra_invest": "Recupero dell'Extra-Investimento Bivite",
    "saving_ann": "Risparmio Energetico Annuo",
    "payback_extra": "Payback dell'Extra-CAPEX"
}

# --- 2. SIDEBAR PARAMETERS ---
st.sidebar.header("🌍 Parametri di Mercato")
c_waste = st.sidebar.number_input("Costo Acquisto Rifiuto (€/kg)", value=0.55)
p_sell = st.sidebar.number_input("Prezzo Vendita Granulo (€/kg)", value=1.05)
process_loss = st.sidebar.slider("Perdita di Processo (%)", 0, 25, 12) / 100
c_ene = st.sidebar.number_input("Costo Energia (€/kWh)", value=0.22)
h_an = st.sidebar.number_input("Ore/Anno", value=7000)

# --- 3. INPUT COMPARISON ---
st.header(t["title"])
p_shared = st.number_input("Portata Oraria (kg/h)", value=500)
o_shared = st.slider("Efficienza OEE (%)", 50, 100, 85)

col1, col2 = st.columns(2)
with col1:
    st.subheader("🔄 Monovite")
    ca = st.number_input("CAPEX Monovite (€)", value=400000)
    seca = st.number_input("SEC Monovite (kWh/kg)", value=0.35)
with col2:
    st.subheader("⚡ Bivite")
    cb = st.number_input("CAPEX Bivite (€)", value=600000)
    secb = st.number_input("SEC Bivite (kWh/kg)", value=0.21)

# --- 4. CALCOLI ---
kg_yr = p_shared * h_an * (o_shared / 100)
ene_a = kg_yr * seca * c_ene
ene_b = kg_yr * secb * c_ene
annual_saving = ene_a - ene_b
extra_capex = cb - ca
years_to_recover_extra = extra_capex / annual_saving if annual_saving > 0 else 0

# --- 5. GRAFICI ---
c1, c2 = st.columns(2)

with c1:
    # GRAFICO 1: WATERFALL / BARRE COSTI ENERGETICI
    st.subheader(t["opex_chart"])
    fig_opex = go.Figure()
    fig_opex.add_trace(go.Bar(
        name="Costo Energia",
        x=["Monovite", "Bivite"],
        y=[ene_a, ene_b],
        marker_color=["#636EFA", "#00CC96"],
        text=[f"€ {ene_a:,.0f}", f"€ {ene_b:,.0f}"],
        textposition='auto'
    ))
    fig_opex.update_layout(yaxis_title="Euro/Anno", showlegend=False)
    st.plotly_chart(fig_opex, use_container_width=True)
    st.success(f"✅ Risparmio energetico annuo: **€ {annual_saving:,.0f}**")

with c2:
    # GRAFICO 2: RECUPERO EXTRA-INVESTIMENTO
    st.subheader(t["extra_invest"])
    yrs = list(range(max(1, int(years_to_recover_extra * 2)) + 2))
    recovery = [-extra_capex + (annual_saving * y) for y in yrs]
    
    fig_rec = go.Figure()
    fig_rec.add_trace(go.Scatter(
        x=yrs, y=recovery, 
        mode='lines+markers',
        line=dict(color='#00CC96', width=4),
        fill='tozeroy',
        name="Recupero"
    ))
    fig_rec.add_hline(y=0, line_dash="dash", line_color="red")
    fig_rec.update_layout(
        xaxis_title="Anni",
        yaxis_title="Euro (€)",
        hovermode="x unified"
    )
    st.plotly_chart(fig_rec, use_container_width=True)
    st.warning(f"⏱️ L'extra-costo di € {extra_capex:,.0f} si ripaga in **{years_to_recover_extra:.1f} anni** solo col risparmio energetico.")

# --- 6. DETTAGLIO ---
st.divider()
st.info(f"""
**Perché la Bivite vince?**
* **Efficienza Termica:** La bivite lavora più per conduzione che per attrito meccanico, abbattendo il SEC.
* **Qualità:** Minore stress termico significa granulo di valore superiore (non calcolato qui, ma è un bonus).
* **Margine:** Ogni kg prodotto con la bivite ti costa **{ (seca-secb)*c_ene :.3f} €** in meno di sola corrente.
""")
