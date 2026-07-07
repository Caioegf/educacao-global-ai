"""
Bônus: Dashboard Streamlit.

Permite selecionar países e indicadores, comparar, ver ranking e ler o
último relatório gerado pela IA.

Uso:
    streamlit run app/streamlit_app.py
"""

import glob
import os

import pandas as pd
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

st.set_page_config(page_title="Inteligência Global em Educação", layout="wide")
st.title("🌍 Agente de Inteligência Global em Educação")
st.caption("World Bank Education Statistics · pipeline Python + n8n + IA")

clean_path = os.path.join(DATA_DIR, "processed", "education_clean.csv")
if not os.path.exists(clean_path):
    st.warning("Rode o pipeline primeiro: `python src/pipeline.py --offline`")
    st.stop()

df = pd.read_csv(clean_path)
ranking = pd.read_csv(os.path.join(DATA_DIR, "processed", "ranking.csv"))

# ---- Seleção (funcionalidades mínimas: selecionar países e indicadores)
paises = sorted(df["country"].unique())
indicadores = sorted(df["indicator"].unique())

col1, col2 = st.columns(2)
sel_paises = col1.multiselect("Países", paises, default=paises[:5])
sel_ind = col2.selectbox("Indicador", indicadores)

sub = df[(df["country"].isin(sel_paises)) & (df["indicator"] == sel_ind)]

# ---- Comparação (série temporal)
st.subheader("📈 Comparação entre países")
if not sub.empty:
    chart_df = sub.pivot_table(index="year", columns="country", values="value")
    st.line_chart(chart_df)

# ---- Ranking
st.subheader("🏆 Ranking")
rk = ranking[ranking["indicator"] == sel_ind][
    ["country", "last_value", "abs_change", "rank_valor_atual", "rank_evolucao"]
].sort_values("rank_valor_atual")
st.dataframe(rk, use_container_width=True, hide_index=True)

# ---- Relatório da IA
st.subheader("🧠 Último relatório gerado pela IA")
reports = sorted(glob.glob(os.path.join(DATA_DIR, "reports", "relatorio*.md")))
if reports:
    with open(reports[-1], encoding="utf-8") as f:
        st.markdown(f.read())
else:
    st.info("Nenhum relatório ainda. Execute o workflow do n8n ou `python src/insights.py`.")
