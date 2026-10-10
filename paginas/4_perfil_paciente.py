"""
PÁGINA 4 — PERFIL DO PACIENTE
Responsável: Bruno Lins____________________

Pergunta que a página responde:
    Idade, gênero, condições de saúde e Bolsa Família mudam a chance de faltar?
"""
import streamlit as st

from utils.dados import ORDEM_IDADE, base_filtrada, taxa_falta
from utils.graficos import barras_taxa, mostrar, pct

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
