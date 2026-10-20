"""
PÁGINA 7 — PERFIS DE PACIENTES (aprendizado de máquina não supervisionado)

Pergunta que a página responde (PP1):
    Dá para identificar perfis distintos de pacientes, com diferentes padrões de falta?

Os números vêm de ml/treinar.py (KMeans), calculados a partir do CSV original.
Os filtros da barra lateral NÃO se aplicam aqui: os perfis foram calculados
sobre todos os pacientes da base.
"""
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.graficos import AZUL, GRADE, LARANJA, TINTA_2, dec, estilizar, mostrar, num, pct

RES = Path(__file__).resolve().parent.parent / "ml" / "resultados"
CORES = ["#2a78d6", "#eb6834", "#2b7f76", "#8e5ea2", "#c9a227", "#7f8c8d"]

st.title("Perfis de pacientes (KMeans)")

if not (RES / "perfis_grupos.csv").exists():
    st.warning("Resultados não encontrados. Rode `python ml/treinar.py` na pasta do dashboard.")
    st.stop()

grupos = pd.read_csv(RES / "perfis_grupos.csv")
k = pd.read_csv(RES / "perfis_k.csv")
pca = pd.read_csv(RES / "perfis_pca.csv")
meta = json.load(open(RES / "perfis_meta.json"))


def nome(r) -> str:
    """Nome do grupo = a característica que o define."""
    if r.bolsa > 0.9:
        return "Bolsa Família"
    if r.defic > 0.9:
        return "Pessoas com deficiência"
    if r.alc > 0.9:
        return "Alcoolismo"
    if r.dia > 0.9:
        return "Idosos com hipertensão e diabetes"
    return "Homens, sem condição marcante" if r.masc > 0.5 else "Mulheres, sem condição marcante"


grupos["perfil"] = grupos.apply(nome, axis=1)
grupos["rotulo"] = "G" + grupos["grupo"].astype(str)

st.markdown(
    "Em vez de olhar um paciente de cada vez, o **KMeans** agrupa pacientes parecidos. "
    "Usamos **uma linha por paciente** (para quem tem muitas consultas não pesar mais) "
    "e as variáveis idade, sexo, Bolsa Família, hipertensão, diabetes, alcoolismo e deficiência, "
    "todas padronizadas. Depois olhamos se os grupos têm taxas de falta diferentes.")

st.info("Os **filtros da barra lateral não se aplicam a esta página**: o cálculo usa todos os pacientes da base.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Pacientes agrupados", num(meta["pacientes"]))
c2.metric("Grupos (k)", "6")
c3.metric("Silhueta (k = 6)", dec(meta["silhueta_k6"], 2))
c4.metric("Taxa geral de falta", pct(meta["taxa_geral"]))

# ---------------- Escolha de k ----------------
st.subheader("1. Quantos grupos? Cotovelo e silhueta")
col_a, col_b = st.columns(2)
with col_a:
    f = go.Figure(go.Scatter(x=k["k"], y=k["wcss"], mode="lines+markers", line=dict(color=AZUL)))
    f.add_vline(x=6, line_dash="dot", line_color=TINTA_2)
    estilizar(f, titulo_y="WCSS (inércia)", altura=300)
    f.update_xaxes(title_text="Número de grupos (k)", dtick=1)
    st.markdown("**Método do cotovelo**")
    mostrar(f)
with col_b:
    f = go.Figure(go.Scatter(x=k["k"], y=k["silhueta"], mode="lines+markers", line=dict(color=LARANJA)))
    f.add_vline(x=6, line_dash="dot", line_color=TINTA_2)
    estilizar(f, titulo_y="Silhueta média", altura=300)
    f.update_xaxes(title_text="Número de grupos (k)", dtick=1)
    st.markdown("**Coeficiente de silhueta**")
    mostrar(f)
st.caption(
    "A WCSS cai muito até k = 6 e depois mais devagar. A silhueta **não** tem máximo em k = 6: "
    "sobe para k maiores porque quase todas as variáveis são 0/1, e o algoritmo passa a isolar "
    "pequenos grupos \"puros\". Escolhemos **k = 6 pelo cotovelo e pela interpretação** "
    "(cada grupo tem uma característica clara).")

# ---------------- Perfis ----------------
st.subheader("2. Os seis perfis")
tab = grupos[["rotulo", "perfil", "pacientes", "pct_pac", "idade", "consultas", "taxa_falta"]].copy()
tab["pacientes"] = tab["pacientes"].map(num)
tab["pct_pac"] = tab["pct_pac"].map(pct)
tab["idade"] = tab["idade"].map(lambda v: dec(v))
tab["consultas"] = tab["consultas"].map(num)
tab["taxa_falta"] = tab["taxa_falta"].map(pct)
tab.columns = ["Grupo", "Perfil", "Pacientes", "% dos pacientes", "Idade média", "Consultas", "Taxa de falta"]
st.dataframe(tab, hide_index=True)

# ---------------- Margem de erro ----------------
st.subheader("3. Taxa de falta por perfil, com margem de erro")
f = go.Figure()
f.add_trace(go.Bar(
    x=grupos["rotulo"], y=grupos["taxa_falta"], marker_color=CORES, marker_cornerradius=4,
    error_y=dict(type="data", symmetric=False,
                 array=grupos["ic_sup"] - grupos["taxa_falta"],
                 arrayminus=grupos["taxa_falta"] - grupos["ic_inf"],
                 color="#0b0b0b", thickness=1.5, width=6),
    text=[pct(v) for v in grupos["taxa_falta"]], textposition="inside", insidetextanchor="start",
    textfont=dict(color="white", size=14),
    customdata=grupos[["perfil", "consultas", "ic_inf", "ic_sup"]].values,
    hovertemplate=("<b>%{x} · %{customdata[0]}</b><br>Taxa de falta: %{y:.1f}%<br>"
                   "Intervalo de 95%: %{customdata[2]:.1f}% a %{customdata[3]:.1f}%<br>"
                   "Consultas: %{customdata[1]:,}<extra></extra>"),
    cliponaxis=False))
f.add_hline(y=meta["taxa_geral"], line_dash="dash", line_color="#52514e",
            annotation_text=f"média geral ({pct(meta['taxa_geral'])})", annotation_position="top right")
estilizar(f, altura=420)
f.update_yaxes(range=[0, 30])
mostrar(f)
st.caption("As barras pretas são o **intervalo de confiança de 95%** da taxa de cada grupo. "
           "Grupos pequenos (G5, G6) têm intervalos largos: a taxa deles é menos certa.")

grupos["largura"] = grupos["ic_sup"] - grupos["ic_inf"]
g3 = grupos.loc[grupos["bolsa"] > 0.9].iloc[0]
g4 = grupos.loc[grupos["dia"] > 0.9].iloc[0]
st.markdown(
    f"**Leitura:** o grupo de **Bolsa Família** falta mais ({pct(g3.taxa_falta)}, intervalo "
    f"{pct(g3.ic_inf)} a {pct(g3.ic_sup)}) e o de **idosos com hipertensão e diabetes** falta menos "
    f"({pct(g4.taxa_falta)}, {pct(g4.ic_inf)} a {pct(g4.ic_sup)}). Os demais ficam perto da média e os "
    f"intervalos se sobrepõem: **não dá para separá-los com segurança**.")
st.info(
    f"A associação entre perfil e falta é estatisticamente significativa "
    f"(qui-quadrado = {dec(meta['qui2'])}; p < 0,001), mas **pequena**: do maior ao menor grupo são só "
    f"{dec(grupos['taxa_falta'].max() - grupos['taxa_falta'].min())} pontos percentuais. "
    "O perfil sozinho explica pouco do comparecimento. Por isso a página seguinte usa também "
    "as características do agendamento.")

# ---------------- PCA ----------------
st.subheader("4. Os perfis em duas dimensões (PCA)")
f = go.Figure()
rot = dict(zip(grupos["grupo"], grupos["rotulo"] + " · " + grupos["perfil"]))
for i, g in enumerate(sorted(pca["grupo"].unique())):
    sub = pca[pca["grupo"] == g]
    f.add_trace(go.Scattergl(x=sub["cp1"], y=sub["cp2"], mode="markers", name=rot[g],
                             marker=dict(size=4, opacity=0.5, color=CORES[i])))
estilizar(f, titulo_y=f"CP2 ({meta['variancia_cp2'] * 100:.0f}% da variância)".replace(".", ","), altura=460)
f.update_xaxes(title_text=f"CP1 ({meta['variancia_cp1'] * 100:.0f}% da variância)".replace(".", ","))
f.update_layout(legend=dict(orientation="v", x=1.01, y=1))
mostrar(f)
st.caption("Amostra de 8.000 pacientes. As faixas horizontais aparecem porque a maioria das variáveis é 0/1. "
           "As duas dimensões explicam menos da metade da variância: o gráfico ajuda a ver, mas não prova nada sozinho.")

# ---------------- Robustez ----------------
st.subheader("5. Os grupos são estáveis?")
c1, c2, c3 = st.columns(3)
c1.metric("Estabilidade (10 sementes)", dec(meta["estabilidade_ari_media"], 2),
          help="ARI médio entre o agrupamento final e 10 outros KMeans com sementes diferentes. 1 = idêntico.")
c2.metric("Ward concorda? (ARI)", dec(meta["ward_ari"], 2),
          help="Clusterização aglomerativa de Ward com k = 6 sobre uma amostra de 10.000 pacientes.")
if "kprototypes_ari" in meta:
    c3.metric("K-Prototypes (ARI)", dec(meta["kprototypes_ari"], 2),
              help="Algoritmo para dados categóricos. ARI baixo = partição muito diferente da do KMeans.")
st.caption(
    "ARI mede a semelhança entre dois agrupamentos (1 = iguais, 0 = sem relação). Com outras sementes o "
    f"KMeans reproduz os grupos com pouca mudança (ARI mínimo {dec(meta['estabilidade_ari_min'], 2)}: algumas "
    "sementes dão uma partição um pouco diferente), e o Ward concorda bastante. O K-Prototypes forma grupos "
    "bem diferentes: **o resultado depende do algoritmo** e do tratamento das variáveis 0/1.")

st.warning(
    "**Cuidado ao generalizar:** a base é de uma rede pública de Vitória (ES), de abril a junho de 2016. "
    "Os perfis valem para essa base e não devem ser tomados como verdade para outra clínica ou época.")
