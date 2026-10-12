import plotly.express as px
import streamlit as st

from utils.dados import base_filtrada, taxa_falta
from utils.graficos import AZUL, LARANJA, estilizar, mostrar

ORDEM_SMS = ["Sem SMS", "Com SMS"]

df = base_filtrada()

st.title("O SMS de lembrete funciona?")

if df.empty:
    st.warning("Nenhuma consulta com os filtros escolhidos.")
    st.stop()

# ---------------- Passo 1: visão ingênua ----------------
st.subheader("1. Olhando por cima: quem recebe SMS falta mais")
geral = taxa_falta(df, "SMS", ORDEM_SMS)
fig = px.bar(geral, x="SMS", y="taxa", color="SMS", text="taxa",
             category_orders={"SMS": ORDEM_SMS}, color_discrete_sequence=[AZUL, LARANJA],
             custom_data=["consultas", "faltas"])
fig.update_traces(marker_cornerradius=4, texttemplate="%{text:.1f}%", textposition="outside",
                  cliponaxis=False, showlegend=False,
                  hovertemplate="<b>%{x}</b><br>Taxa de falta: %{y:.1f}%<br>"
                                "Consultas: %{customdata[0]:,}<br>Faltas: %{customdata[1]:,}<extra></extra>")
estilizar(fig, altura=320)
fig.update_xaxes(title_text="")
mostrar(fig, geral)

st.markdown("Se parássemos aqui, a conclusão seria *\"SMS aumenta a falta\"*. **Isso está errado.**")