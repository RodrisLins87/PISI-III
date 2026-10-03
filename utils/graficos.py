"""
Estilo visual COMPARTILHADO dos gráficos — use estas funções em vez de montar
o gráfico do zero, assim todas as páginas ficam com a mesma cara.

Cores validadas para daltonismo (azul/laranja passam em todas as checagens de
contraste e separação). Regra: 1 série = sempre AZUL; 2 séries = AZUL e LARANJA.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

AZUL = "#2a78d6"      # série 1 (ou única série)
LARANJA = "#eb6834"   # série 2
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
TINTA_FRACA = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"
FUNDO = "#fcfcfb"
FONTE = 'system-ui, -apple-system, "Segoe UI", sans-serif'


def estilizar(fig: go.Figure, titulo_y: str = "Taxa de falta (%)", altura: int = 380) -> go.Figure:
    """Aplica o visual padrão: fundo claro, grade fina, sem poluição."""
    fig.update_layout(
        height=altura,
        font=dict(family=FONTE, size=13, color=TINTA_2),
        paper_bgcolor=FUNDO,
        plot_bgcolor=FUNDO,
        margin=dict(l=70, r=20, t=40, b=70),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    title_text="", font=dict(color=TINTA_2)),
        hoverlabel=dict(bgcolor="white", font=dict(family=FONTE, color=TINTA)),
        bargap=0.25,
        bargroupgap=0.08,
        separators=",.",  # padrão brasileiro: 34,2% e 1.234 consultas
    )
    fig.update_xaxes(showgrid=False, linecolor=EIXO, tickfont=dict(color=TINTA_2),
                     title_font=dict(color=TINTA_2), automargin=True, title_standoff=12)
    fig.update_yaxes(gridcolor=GRADE, zeroline=False, linecolor=EIXO,
                     tickfont=dict(color=TINTA_FRACA), title_text=titulo_y,
                     title_font=dict(color=TINTA_2), automargin=True, title_standoff=10)
    return fig


def barras_taxa(tabela: pd.DataFrame, x: str, titulo_x: str = "",
                horizontal: bool = False, altura: int = 380) -> go.Figure:
    """Barras de taxa de falta para UMA série (todas as barras em azul, com rótulo)."""
    if horizontal:
        fig = px.bar(tabela, x="taxa", y=x, orientation="h", text="taxa",
                     custom_data=["consultas", "faltas"])
    else:
        fig = px.bar(tabela, x=x, y="taxa", text="taxa",
                     custom_data=["consultas", "faltas"])
    fig.update_traces(
        marker_color=AZUL, marker_cornerradius=4,
        texttemplate="%{text:.1f}%", textposition="outside",
        textfont=dict(color=TINTA_2),
        cliponaxis=False,
        hovertemplate=(f"<b>%{{{'y' if horizontal else 'x'}}}</b><br>"
                       f"Taxa de falta: %{{{'x' if horizontal else 'y'}:.1f}}%<br>"
                       "Consultas: %{customdata[0]:,}<br>Faltas: %{customdata[1]:,}"
                       "<extra></extra>"),
    )
    estilizar(fig, altura=altura)
    teto = max(float(tabela["taxa"].max()) * 1.2, 5)  # folga para o rótulo não ser cortado
    if horizontal:
        fig.update_xaxes(title_text="Taxa de falta (%)", showgrid=True, gridcolor=GRADE,
                         range=[0, teto])
        # type="category": impede o Plotly de tratar rótulos como "0", "1", "2" como números
        fig.update_yaxes(title_text=titulo_x, gridcolor="rgba(0,0,0,0)", type="category",
                         autorange="reversed", tickfont=dict(color=TINTA_2))
    else:
        fig.update_xaxes(title_text=titulo_x, type="category")
        fig.update_yaxes(range=[0, teto])
    return fig


def barras_agrupadas(tabela: pd.DataFrame, x: str, grupo: str, ordem_grupo: list,
                     titulo_x: str = "", altura: int = 400) -> go.Figure:
    """Barras lado a lado para DUAS séries (azul = 1ª, laranja = 2ª)."""
    fig = px.bar(tabela, x=x, y="taxa", color=grupo, barmode="group",
                 category_orders={grupo: ordem_grupo},
                 color_discrete_sequence=[AZUL, LARANJA],
                 custom_data=[grupo, "consultas", "faltas"])
    fig.update_traces(
        marker_cornerradius=4,
        hovertemplate=("<b>%{x}</b> — %{customdata[0]}<br>"
                       "Taxa de falta: %{y:.1f}%<br>"
                       "Consultas: %{customdata[1]:,}<br>Faltas: %{customdata[2]:,}"
                       "<extra></extra>"),
    )
    estilizar(fig, altura=altura)
    fig.update_xaxes(title_text=titulo_x, type="category")
    return fig


def mostrar(fig: go.Figure, tabela: pd.DataFrame | None = None, nome_tabela: str = "Ver dados em tabela"):
    """Mostra o gráfico e, embaixo, uma tabela opcional com os números exatos."""
    st.plotly_chart(fig, theme=None, config={"displayModeBar": False})
    if tabela is not None:
        with st.expander(nome_tabela):
            st.dataframe(renomear_tabela(tabela), hide_index=True)


def pct(valor: float, casas: int = 1) -> str:
    """34.21 -> '34,2%'"""
    return f"{valor:.{casas}f}%".replace(".", ",")


def num(valor: float) -> str:
    """110526 -> '110.526'"""
    return f"{int(valor):,}".replace(",", ".")


def dec(valor: float, casas: int = 1) -> str:
    """6.34 -> '6,3'"""
    return f"{valor:.{casas}f}".replace(".", ",")


def renomear_tabela(t: pd.DataFrame) -> pd.DataFrame:
    return t.rename(columns={"consultas": "Consultas", "faltas": "Faltas",
                             "taxa": "Taxa de falta (%)"})
