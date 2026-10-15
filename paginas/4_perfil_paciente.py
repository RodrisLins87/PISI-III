"""
PÁGINA 4 — PERFIL DO PACIENTE
Responsável: Bruno Lins

Pergunta que a página responde:
    Idade, gênero, condições de saúde e Bolsa Família mudam a chance de faltar?
"""
import pandas as pd
import streamlit as st
from scipy import stats
from utils.dados import ORDEM_IDADE, base_filtrada, taxa_falta
from utils.graficos import barras_taxa, dec, mostrar, num, pct

df = base_filtrada()

st.title("Perfil do paciente")

if df.empty:
    st.warning("Nenhuma consulta com os filtros escolhidos.")
    st.stop()

# ---------------- Faixa etária ----------------
st.subheader("Taxa de falta por faixa etária")
idade = taxa_falta(df, "FaixaEtaria", ORDEM_IDADE)
mostrar(barras_taxa(idade, "FaixaEtaria", "Faixa etária (anos)"), idade)
if len(idade) > 1:
    maior = idade.loc[idade["taxa"].idxmax()]
    menor = idade.loc[idade["taxa"].idxmin()]
    st.caption(f"Maior taxa: **{maior['FaixaEtaria']} anos** ({pct(maior['taxa'])}). "
               f"Menor taxa: **{menor['FaixaEtaria']} anos** ({pct(menor['taxa'])}). "
               "Na base completa, adolescentes e jovens adultos faltam mais; idosos, menos.")

st.divider()
 
# ---------------- Gênero ----------------
st.subheader("Gênero")
genero = taxa_falta(df, "GeneroNome")
cols = st.columns(max(len(genero), 1) + 1)
for i, linha in enumerate(genero.itertuples()):
    cols[i].metric(linha.GeneroNome, pct(linha.taxa), help=f"{num(linha.consultas)} consultas")
if df["GeneroNome"].nunique() == 2:
    chi2, p, _, _ = stats.chi2_contingency(pd.crosstab(df["GeneroNome"], df["Falta"]))
    signif = "é" if p < 0.05 else "**não** é"
    cols[-1].metric("Teste qui-quadrado (p-valor)", dec(p, 3))
    conclusao = " Gênero, sozinho, não ajuda a prever faltas." if p >= 0.05 else ""
    st.markdown(f"A diferença entre gêneros {signif} estatisticamente significativa (α = 0,05).{conclusao}")
 
