"""
PÁGINA 1 — VISÃO GERAL
Responsável: Laura Miranda

Pergunta que a página responde:
    Qual o tamanho do problema das faltas e como ele se comporta ao longo do período?
"""
import plotly.express as px
import streamlit as st

from utils.dados import base_filtrada, carregar_dados, taxa_falta
from utils.graficos import AZUL, estilizar, mostrar, num, pct

df = base_filtrada()

st.title("Faltas em consultas médicas")
st.markdown(
    "Painel sobre o **absenteísmo** (pacientes que marcam e não comparecem) em consultas "
    "da rede pública de Vitória-ES. Use os filtros da barra lateral: eles valem para todas as páginas."
)

if df.empty:
    st.warning("Nenhuma consulta com os filtros escolhidos. Ajuste os filtros na barra lateral.")
    st.stop()

# ---------------- Indicadores principais ----------------
total = len(df)
faltas = int(df["Falta"].sum())
taxa = faltas / total * 100
taxa_base = carregar_dados()["Falta"].mean() * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Consultas", num(total))
c2.metric("Pacientes únicos", num(df["PatientId"].nunique()))
c3.metric("Faltas", num(faltas))
diferenca = taxa - taxa_base
c4.metric("Taxa de falta", pct(taxa),
          delta=(f"{diferenca:+.1f}".replace(".", ",") + " p.p. vs. base completa")
          if abs(diferenca) >= 0.05 else None,
          delta_color="inverse")

if taxa > 0:
    st.markdown(
        f"**Em média, 1 a cada {round(100 / taxa)} consultas marcadas termina em falta.** "
        "Cada falta é um horário de médico que poderia ter atendido outro paciente."
    )

st.divider()

# ---------------- Evolução diária ----------------
st.subheader("Taxa de falta por dia de consulta")
por_dia = taxa_falta(df, "DataConsulta").sort_values("DataConsulta")
fig = px.line(por_dia, x="DataConsulta", y="taxa", markers=True,
              custom_data=["consultas", "faltas"])
fig.update_traces(line=dict(color=AZUL, width=2), marker=dict(size=8, color=AZUL,
                  line=dict(width=2, color="#fcfcfb")),
                  hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Taxa de falta: %{y:.1f}%<br>"
                                "Consultas: %{customdata[0]:,}<br>Faltas: %{customdata[1]:,}<extra></extra>")
estilizar(fig)
fig.update_xaxes(title_text="Data da consulta", tickformat="%d/%m")
fig.update_yaxes(range=[0, max(40, por_dia["taxa"].max() * 1.2)])  # começa no 0 para não exagerar a oscilação
fig.update_layout(hovermode="x unified")
mostrar(fig, por_dia)

st.caption("Na base completa, a taxa oscila pouco ao longo do período (entre ~17% e ~24%): o problema é constante, não um evento isolado.")

# ---------------- Volume diário ----------------
st.subheader("Quantidade de consultas por dia")
fig2 = px.bar(por_dia, x="DataConsulta", y="consultas")
fig2.update_traces(marker_color=AZUL, marker_cornerradius=4,
                   hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Consultas: %{y:,}<extra></extra>")
estilizar(fig2, titulo_y="Consultas", altura=320)
fig2.update_xaxes(title_text="Data da consulta", tickformat="%d/%m")
mostrar(fig2)
