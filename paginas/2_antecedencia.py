```python
"""
PÁGINA 2 — ANTECEDÊNCIA DO AGENDAMENTO

Pergunta que a página responde:
    Esperar mais dias aumenta a falta?

A página usa somente os dados e funções já preparados em utils/ e respeita
os filtros globais definidos em app.py.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.dados import ORDEM_ANTECEDENCIA, base_filtrada, taxa_falta
from utils.graficos import AZUL, estilizar, mostrar, num, pct, dec


df = base_filtrada()

st.title("Antecedência do agendamento")
st.markdown(
    "**Esperar mais dias aumenta a falta?** Nesta análise, comparamos a taxa de "
    "não comparecimento conforme o intervalo entre o agendamento e a consulta. "
    "Os filtros da barra lateral valem para esta página também."
)

if df.empty:
    st.warning(
        "Nenhuma consulta com os filtros escolhidos. "
        "Ajuste os filtros na barra lateral."
    )
    st.stop()

# Indicadores principais
tabela = taxa_falta(df, "FaixaAntecedencia", ORDEM_ANTECEDENCIA)

mesmo_dia = df.loc[df["Antecedencia"] == 0, "Falta"].mean() * 100
um_dia_ou_mais = df.loc[df["Antecedencia"] >= 1, "Falta"].mean() * 100

linha_pico = tabela.loc[tabela["taxa"].idxmax()]
pico_taxa = float(linha_pico["taxa"])
pico_faixa = str(linha_pico["FaixaAntecedencia"])

if pd.notna(mesmo_dia) and pd.notna(um_dia_ou_mais) and mesmo_dia > 0:
    multiplicador = um_dia_ou_mais / mesmo_dia
else:
    multiplicador = None

correlacao = df["Antecedencia"].corr(df["Falta"])

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Mesmo dia",
    pct(mesmo_dia) if pd.notna(mesmo_dia) else "—"
)
c2.metric(
    "1 dia ou mais",
    pct(um_dia_ou_mais) if pd.notna(um_dia_ou_mais) else "—"
)
c3.metric(
    "Aumento relativo",
    f"{dec(multiplicador)}×" if multiplicador is not None else "—",
    help=(
        "Razão entre a taxa de falta de quem espera 1 dia ou mais "
        "e a taxa de quem marca para o mesmo dia."
    ),
)
c4.metric(
    "Maior taxa",
    pct(pico_taxa),
    help=f"Faixa com maior taxa de falta: {pico_faixa}."
)

if multiplicador is not None:
    st.markdown(
        f"**A taxa de falta passa de {pct(mesmo_dia)} para "
        f"{pct(um_dia_ou_mais)} quando há pelo menos 1 dia de espera — "
        f"cerca de {dec(multiplicador)}× maior.**"
    )

st.divider()

# Gráfico 1: taxa de falta por faixa de antecedência
st.subheader("Quanto maior a antecedência, maior a taxa de falta")

fig = px.bar(
    tabela,
    x="FaixaAntecedencia",
    y="taxa",
    text="taxa",
    custom_data=["consultas", "faltas"],
    category_orders={"FaixaAntecedencia": ORDEM_ANTECEDENCIA},
)

fig.update_traces(
    marker_color=AZUL,
    marker_cornerradius=4,
    texttemplate="%{text:.1f}%",
    textposition="outside",
    textfont=dict(color="#52514e"),
    cliponaxis=False,
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Taxa de falta: %{y:.1f}%<br>"
        "Consultas: %{customdata[0]:,}<br>"
        "Faltas: %{customdata[1]:,}"
        "<extra></extra>"
    ),
)

estilizar(fig, altura=430)
fig.update_xaxes(title_text="Antecedência do agendamento")
fig.update_yaxes(
    title_text="Taxa de falta (%)",
    range=[0, max(40, float(tabela["taxa"].max()) * 1.2)],
)

mostrar(fig, tabela, "Ver dados por faixa de antecedência")

if len(tabela) >= 2:
    maior_taxa = float(tabela["taxa"].max())
    faixa_maior = str(
        tabela.loc[tabela["taxa"].idxmax(), "FaixaAntecedencia"]
    )
    st.caption(
        f"A taxa varia conforme a antecedência e atinge {pct(maior_taxa)} "
        f"na faixa de {faixa_maior}. "
        "Os valores apresentados são calculados diretamente da base."
    )

# Gráfico 2: comparação entre mesmo dia e 1 dia ou mais
st.subheader("O efeito aparece já a partir de 1 dia de espera")

comparacao = pd.DataFrame(
    {
        "AntecedenciaResumo": ["Mesmo dia", "1 dia ou mais"],
        "taxa": [mesmo_dia, um_dia_ou_mais],
        "consultas": [
            int((df["Antecedencia"] == 0).sum()),
            int((df["Antecedencia"] >= 1).sum()),
        ],
        "faltas": [
            int(df.loc[df["Antecedencia"] == 0, "Falta"].sum()),
            int(df.loc[df["Antecedencia"] >= 1, "Falta"].sum()),
        ],
    }
)

fig2 = px.bar(
    comparacao,
    x="AntecedenciaResumo",
    y="taxa",
    text="taxa",
    custom_data=["consultas", "faltas"],
)

fig2.update_traces(
    marker_color=AZUL,
    marker_cornerradius=4,
    texttemplate="%{text:.1f}%",
    textposition="outside",
    textfont=dict(color="#52514e"),
    cliponaxis=False,
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Taxa de falta: %{y:.1f}%<br>"
        "Consultas: %{customdata[0]:,}<br>"
        "Faltas: %{customdata[1]:,}"
        "<extra></extra>"
    ),
)

estilizar(fig2, altura=350)
fig2.update_xaxes(title_text="Tempo de espera")
fig2.update_yaxes(
    title_text="Taxa de falta (%)",
    range=[0, max(35, float(comparacao["taxa"].max()) * 1.2)],
)

mostrar(
    fig2,
    comparacao.rename(columns={"AntecedenciaResumo": "Antecedência"}),
    "Ver comparação",
)

# Correlação e interpretação
st.subheader("O que os dados indicam?")

if pd.notna(correlacao):
    st.markdown(
        f"A correlação entre **dias de antecedência** e **falta** é de "
        f"**r = {dec(correlacao, 3)}**. Isso indica uma associação positiva: "
        "na base analisada, consultas marcadas com maior antecedência tendem "
        "a apresentar taxas de falta maiores."
    )
else:
    st.info("Não foi possível calcular a correlação com os filtros atuais.")

st.info(
    "**Leitura principal:** o tempo de espera é um dos fatores mais "
    "associados à falta nesta base. A relação não cresce indefinidamente: "
    "a faixa de 31–60 dias apresenta a maior taxa, enquanto a faixa de "
    "60+ dias apresenta uma redução."
)

st.caption(
    f"Base analisada nesta tela: {num(len(df))} consultas. "
    "Os valores são recalculados conforme os filtros da barra lateral."
)
```
