import pandas as pd
import streamlit as st

from utils.dados import ORDEM_DIA_SEMANA, base_filtrada, taxa_falta
from utils.graficos import barras_taxa, dec, mostrar, pct

ORDEM_HISTORICO = ["Primeira consulta", "Nunca faltou antes", "Já faltou antes"]

df = base_filtrada()

st.title("Histórico do paciente e dia da semana")

if df.empty:
    st.warning("Nenhuma consulta com os filtros escolhidos.")
    st.stop()

st.subheader("Taxa de falta pelo histórico do paciente")
st.markdown("O histórico considera apenas consultas **marcadas antes** da consulta atual "
            "(não usamos informação do futuro).")
hist = taxa_falta(df, "Historico", ORDEM_HISTORICO)
mostrar(barras_taxa(hist, "Historico", ""), hist)

t = hist.set_index("Historico")["taxa"]
if {"Nunca faltou antes", "Já faltou antes"} <= set(t.index):
    st.markdown(f"**Quem já faltou alguma vez tem taxa de {pct(t['Já faltou antes'])}**, contra "
                f"{pct(t['Nunca faltou antes'])} de quem sempre compareceu: "
                f"{dec(t['Já faltou antes'] / t['Nunca faltou antes'])}× mais.")

st.subheader("Quanto mais faltas anteriores, maior a chance de faltar de novo?")
com_hist = df[df["ConsultasAnteriores"] > 0].copy()
com_hist["NumFaltasAnt"] = pd.cut(com_hist["FaltasAnteriores"], bins=[-1, 0, 1, 2, 1000],
                                  labels=["0", "1", "2", "3 ou mais"])
num = taxa_falta(com_hist, "NumFaltasAnt", ["0", "1", "2", "3 ou mais"])
mostrar(barras_taxa(num, "NumFaltasAnt", "Nº de faltas anteriores"), num)
extremos = num.set_index("NumFaltasAnt")["taxa"]
if {"0", "3 ou mais"} <= set(extremos.index):
    st.markdown(f"Quem já faltou **3 ou mais vezes** falta **{pct(extremos['3 ou mais'])}** das vezes, "
                f"contra {pct(extremos['0'])} de quem nunca faltou. O histórico é um bom sinal de alerta.")
st.caption("Considera apenas pacientes que já tinham ao menos uma consulta anterior.")

st.divider()

st.subheader("Taxa de falta por dia da semana da consulta")
dia = taxa_falta(df, "DiaSemana", ORDEM_DIA_SEMANA)
mostrar(barras_taxa(dia, "DiaSemana", "Dia da semana"), dia)
sab = dia[dia["DiaSemana"] == "Sábado"]
st.caption(
    "Na base completa, de segunda a sexta a taxa fica entre 19% e 21%: o dia da semana tem pouco efeito."
    + (f" Atenção: sábado tem só **{int(sab['consultas'].iloc[0])} consultas**, "
       "amostra pequena demais para tirar conclusão." if len(sab) else "")
)
