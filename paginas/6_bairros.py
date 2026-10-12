"""
PÁGINA 6 — BAIRROS

Pergunta que a página responde:
    Onde se falta mais?
"""

import streamlit as st

from utils.dados import base_filtrada, taxa_falta
from utils.graficos import barras_taxa, mostrar, num, pct

# 1. Carregamento dos dados respeitando os filtros globais
df = base_filtrada()

# 2. Cabeçalho principal com hierarquia clara
st.title("Onde se falta mais?")
st.markdown(
    "Análise da distribuição espacial do absenteísmo pelos bairros de Vitória-ES. "
    "Descubra quais regiões apresentam maior concentração de faltas e entenda o "
    "impacto do tamanho da amostra na análise."
)

if df.empty:
    st.warning("Nenhuma consulta encontrada com os filtros selecionados na barra lateral.")
    st.stop()

# ---------------- 1. Preparação e Agrupamento dos Dados ----------------
tabela_bairros = taxa_falta(df, "Bairro")

# Ajuste visual de design: Converte nomes de ALL CAPS para Title Case (ex: "Santos Dumont")
tabela_bairros["BairroExibicao"] = tabela_bairros["Bairro"].astype(str).str.title()
# Ajuste fino de preposições em português
preposicoes = {" De ": " de ", " Da ": " da ", " Do ": " do ", " Dos ": " dos ", " Das ": " das "}
for orig, subst in preposicoes.items():
    tabela_bairros["BairroExibicao"] = tabela_bairros["BairroExibicao"].str.replace(orig, subst)

# Filtro de Amostra Mínima (mínimo de 200 consultas para evitar distorções estatísticas)
MIN_CONSULTAS = 200
tabela_filtrada = tabela_bairros[tabela_bairros["consultas"] >= MIN_CONSULTAS].copy()
tabela_filtrada = tabela_filtrada.sort_values("taxa", ascending=False)

total_bairros = len(tabela_bairros)
bairros_validos = len(tabela_filtrada)

# ---------------- 2. Cartões de Métricas (KPIs) ----------------
if not tabela_filtrada.empty:
    pior_bairro = tabela_filtrada.iloc[0]
    melhor_bairro = tabela_filtrada.iloc[-1]
    amplitude = pior_bairro["taxa"] - melhor_bairro["taxa"]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        label="Bairros analisados",
        value=f"{bairros_validos} / {total_bairros}",
        help=f"Bairros com pelo menos {MIN_CONSULTAS} consultas registradas.",
    )
    c2.metric(
        label="Amostra mínima",
        value=f"≥ {MIN_CONSULTAS}",
        delta="consultas / bairro",
        delta_color="off",
    )
    c3.metric(
        label=f"Maior falta ({pior_bairro['BairroExibicao']})",
        value=pct(pior_bairro["taxa"]),
        delta=f"{num(pior_bairro['consultas'])} consultas",
        delta_color="off",
    )
    c4.metric(
        label=f"Menor falta ({melhor_bairro['BairroExibicao']})",
        value=pct(melhor_bairro["taxa"]),
        delta=f"{num(melhor_bairro['consultas'])} consultas",
        delta_color="off",
    )

    # Destaque de Insight (Callout Box)
    st.markdown(
        f"💡 **Destaque:** Entre os bairros com amostra representativa (≥ {MIN_CONSULTAS} consultas), "
        f"a taxa de falta varia de **{pct(melhor_bairro['taxa'])}** ({melhor_bairro['BairroExibicao']}) "
        f"a **{pct(pior_bairro['taxa'])}** ({pior_bairro['BairroExibicao']}) — uma variação "
        f"de **{amplitude:.1f} p.p.** entre diferentes regiões da cidade."
    )

st.divider()

# ---------------- 3. Top 10 Bairros com Maior Taxa de Falta ----------------
st.subheader("Bairros com maior taxa de falta")
st.caption(
    f"Top 10 bairros com maior taxa de absenteísmo (mínimo de {MIN_CONSULTAS} consultas)."
)

top10_piores = tabela_filtrada.head(10).copy()
fig_piores = barras_taxa(
    top10_piores, x="BairroExibicao", titulo_x="Bairro", horizontal=True, altura=400
)
mostrar(
    fig_piores,
    top10_piores[["BairroExibicao", "consultas", "faltas", "taxa"]].rename(
        columns={"BairroExibicao": "Bairro"}
    ),
    "Ver dados dos 10 piores bairros",
)

st.divider()

# ---------------- 4. Top 10 Bairros com Menor Taxa de Falta ----------------
st.subheader("Bairros com menor taxa de falta")
st.caption(
    f"Top 10 bairros com melhor nível de comparecimento (mínimo de {MIN_CONSULTAS} consultas)."
)

top10_melhores = tabela_filtrada.tail(10).sort_values("taxa", ascending=True).copy()
fig_melhores = barras_taxa(
    top10_melhores, x="BairroExibicao", titulo_x="Bairro", horizontal=True, altura=400
)
mostrar(
    fig_melhores,
    top10_melhores[["BairroExibicao", "consultas", "faltas", "taxa"]].rename(
        columns={"BairroExibicao": "Bairro"}
    ),
    "Ver dados dos 10 melhores bairros",
)

# ---------------- 5. Bloco Explicativo e Metodológico ----------------
st.info(
    "**Por que usamos um limite de amostra mínima?**\n\n"
    "Bairros com volume muito pequeno de consultas (ex: 10 ou 15 consultas) podem apresentar "
    "taxas de falta extremas (como 0% ou 50%) por mero acaso estatístico. "
    "Ao estipular o limite de pelo menos 200 consultas, garantimos análises confiáveis "
    "para direcionar ações da gestão pública onde o impacto é real."
)

st.caption(
    f"Base analisada nesta página: {num(len(df))} consultas distribuídas em {total_bairros} bairros. "
    "Os valores são recalculados automaticamente conforme os filtros da barra lateral."
)