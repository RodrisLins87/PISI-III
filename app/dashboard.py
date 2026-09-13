import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.etl import (
    load_data,
    basic_clean,
    get_column_types,
    get_binary_outcome_column,
    get_binary_numeric_columns,
    get_comparable_factor_columns,
    drop_id_columns,
    factor_analysis,
    translate_columns,
)

st.set_page_config(page_title="Analise de Absenteismo", layout="wide")

st.title("Dashboard de Analise de Absenteismo em Consultas Medicas")
st.caption("Exploracao dos fatores associados a falta em consultas agendadas.")

uploaded_file = st.sidebar.file_uploader("Envie seu dataset (CSV ou Excel)", type=["csv", "xlsx", "xls"])

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "dataset.csv"

if uploaded_file is not None:
    df_raw = load_data(uploaded_file)
elif DEFAULT_PATH.exists():
    df_raw = load_data(DEFAULT_PATH)
    st.sidebar.info(f"Usando dataset padrao: {DEFAULT_PATH.name}")
else:
    st.info("Envie um arquivo CSV ou Excel na barra lateral para comecar.")
    st.stop()

df = basic_clean(df_raw)
df = translate_columns(df)
df = drop_id_columns(df)
col_types = get_column_types(df)

st.sidebar.header("Filtros")
df_filtered = df.copy()

for col in col_types["categorical"]:
    options = sorted(df[col].dropna().unique().tolist())
    selected = st.sidebar.multiselect(f"{col}", options, default=[])
    if selected:
        df_filtered = df_filtered[df_filtered[col].isin(selected)]

for col in col_types["numeric"]:
    min_val, max_val = float(df[col].min()), float(df[col].max())
    if min_val < max_val:
        selected_range = st.sidebar.slider(f"{col}", min_val, max_val, (min_val, max_val))
        df_filtered = df_filtered[df_filtered[col].between(*selected_range)]

for col in col_types["datetime"]:
    min_date, max_date = df[col].min(), df[col].max()
    if pd.notnull(min_date) and pd.notnull(max_date):
        selected_dates = st.sidebar.date_input(f"{col}", (min_date, max_date))
        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
            start, end = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
            df_filtered = df_filtered[df_filtered[col].between(start, end)]

outcome_col = get_binary_outcome_column(df, col_types["categorical"])

st.subheader("Indicadores Gerais")
kpi_cols = st.columns(4)

kpi_cols[0].metric("Registros (filtrado)", f"{len(df_filtered):,}".replace(",", "."))
kpi_cols[1].metric("Registros (total)", f"{len(df):,}".replace(",", "."))

if outcome_col:
    valor_ref = df_filtered[outcome_col].value_counts().idxmax()
    taxa = (df_filtered[outcome_col] == valor_ref).mean() * 100
    kpi_cols[2].metric(f"Taxa de '{outcome_col} = {valor_ref}'", f"{taxa:.1f}%")

if col_types["numeric"]:
    primeira_num = col_types["numeric"][0]
    kpi_cols[3].metric(f"Media de {primeira_num}", f"{df_filtered[primeira_num].mean():.1f}")

st.divider()

st.subheader("Distribuicao por Desfecho (Diagrama de Caixas)")
st.caption(
    "Compara a distribuicao de uma variavel numerica entre os grupos do desfecho, "
    "evidenciando diferencas de mediana, dispersao e outliers."
)

colunas_continuas = [
    c for c in col_types["numeric"] if c not in get_binary_numeric_columns(df, col_types["numeric"])
]

if outcome_col and colunas_continuas:
    col_box, col_config = st.columns([3, 1])

    with col_config:
        num_col_box = st.selectbox("Variavel numerica", colunas_continuas, key="box_numeric")
        mostrar_pontos = st.checkbox("Mostrar pontos (outliers)", value=False)

    with col_box:
        fig_box = px.box(
            df_filtered,
            x=outcome_col,
            y=num_col_box,
            color=outcome_col,
            points="outliers" if mostrar_pontos else False,
            title=f"{num_col_box} por {outcome_col}",
        )
        st.plotly_chart(fig_box, width='stretch')
else:
    st.info("E necessario haver uma coluna de desfecho binario e uma coluna numerica continua para gerar o diagrama de caixas.")

st.divider()

st.subheader("Taxa do Desfecho por Fator")
st.caption(
    "Compara a taxa do desfecho entre os grupos de cada fator selecionado "
    "(ex: genero, condicoes de saude, indicadores de vulnerabilidade social)."
)

if outcome_col:
    valores_desfecho = sorted(df[outcome_col].dropna().unique().tolist())
    valor_positivo = st.selectbox(
        f"Valor de '{outcome_col}' considerado o desfecho de interesse",
        valores_desfecho,
        index=0,
        key="valor_positivo",
    )

    fatores_disponiveis = get_comparable_factor_columns(
        df, col_types["categorical"], col_types["numeric"], outcome_col
    )

    if fatores_disponiveis:
        fatores_selecionados = st.multiselect(
            "Fatores para comparar",
            fatores_disponiveis,
            default=fatores_disponiveis,
            key="fatores_selecionados",
        )

        if fatores_selecionados:
            df_fatores = factor_analysis(df_filtered, outcome_col, valor_positivo, fatores_selecionados)
            fig_fatores = px.bar(
                df_fatores,
                x="Fator",
                y="Taxa (%)",
                color="Grupo",
                barmode="group",
                title=f"Taxa de '{outcome_col} = {valor_positivo}' por fator",
            )
            st.plotly_chart(fig_fatores, width='stretch')
    else:
        st.info("Nenhum fator comparavel (binario ou categorico de baixa cardinalidade) foi encontrado.")
else:
    st.info("Nenhuma coluna de desfecho binario foi identificada no dataset.")

st.divider()

st.subheader("Exploracao Livre")

if col_types["categorical"]:
    cat_col = st.selectbox("Distribuicao de coluna categorica", col_types["categorical"], key="cat_chart")
    contagem = df_filtered[cat_col].value_counts().reset_index()
    contagem.columns = [cat_col, "quantidade"]
    fig_livre = px.bar(contagem, x=cat_col, y="quantidade", title=f"Distribuicao de {cat_col}")
    st.plotly_chart(fig_livre, width='stretch')

st.divider()

st.subheader("Dados")
st.dataframe(df_filtered, width='stretch')
