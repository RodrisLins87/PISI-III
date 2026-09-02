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
    factor_analysis,
    translate_columns,
)

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("Dashboard Interativo")
st.caption("Versao inicial (MVP)")

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

st.subheader("Resumo")
kpi_cols = st.columns(4)

kpi_cols[0].metric("Linhas (filtrado)", f"{len(df_filtered):,}".replace(",", "."))
kpi_cols[1].metric("Linhas (total)", f"{len(df):,}".replace(",", "."))

outcome_col = get_binary_outcome_column(df, col_types["categorical"])
if outcome_col:
    valor_ref = df_filtered[outcome_col].value_counts().idxmax()
    taxa = (df_filtered[outcome_col] == valor_ref).mean() * 100
    kpi_cols[2].metric(f"{outcome_col} = {valor_ref}", f"{taxa:.1f}%")
elif col_types["numeric"]:
    primeira_num = col_types["numeric"][0]
    kpi_cols[2].metric(f"Media de {primeira_num}", f"{df_filtered[primeira_num].mean():.2f}")

if col_types["numeric"]:
    primeira_num = col_types["numeric"][0]
    kpi_cols[3].metric(f"Media de {primeira_num}", f"{df_filtered[primeira_num].mean():.2f}")

st.subheader("Visualizacoes")
col_a, col_b = st.columns(2)

if col_types["categorical"]:
    with col_a:
        cat_col = st.selectbox("Coluna categorica", col_types["categorical"], key="cat_chart")
        contagem = df_filtered[cat_col].value_counts().reset_index()
        contagem.columns = [cat_col, "quantidade"]
        fig1 = px.bar(contagem, x=cat_col, y="quantidade", title=f"Distribuicao de {cat_col}")
        st.plotly_chart(fig1, use_container_width=True)

with col_b:
    if col_types["datetime"] and col_types["numeric"]:
        date_col = col_types["datetime"][0]
        num_col = st.selectbox("Coluna numerica", col_types["numeric"], key="num_chart")
        serie = df_filtered.groupby(date_col)[num_col].sum().reset_index()
        fig2 = px.line(serie, x=date_col, y=num_col, title=f"{num_col} ao longo do tempo")
        st.plotly_chart(fig2, use_container_width=True)
    elif col_types["numeric"]:
        num_col = st.selectbox("Coluna numerica", col_types["numeric"], key="num_chart")
        fig2 = px.histogram(df_filtered, x=num_col, title=f"Distribuicao de {num_col}")
        st.plotly_chart(fig2, use_container_width=True)

if outcome_col:
    st.subheader(f"Analise por fator - {outcome_col}")

    valores_desfecho = sorted(df[outcome_col].dropna().unique().tolist())
    valor_positivo = st.selectbox(
        f"Valor de '{outcome_col}' considerado o desfecho de interesse",
        valores_desfecho,
        index=0,
        key="valor_positivo",
    )

    fatores_disponiveis = get_binary_numeric_columns(df, col_types["numeric"])
    fatores_disponiveis = [c for c in fatores_disponiveis if c != outcome_col]

    if fatores_disponiveis:
        fatores_selecionados = st.multiselect(
            "Fatores para comparar",
            fatores_disponiveis,
            default=fatores_disponiveis,
            key="fatores_selecionados",
        )

        if fatores_selecionados:
            df_fatores = factor_analysis(df_filtered, outcome_col, valor_positivo, fatores_selecionados)
            fig3 = px.bar(
                df_fatores,
                x="Fator",
                y="Taxa (%)",
                color="Grupo",
                barmode="group",
                title=f"Taxa de '{outcome_col} = {valor_positivo}' por fator (0 = nao tem, 1 = tem)",
            )
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Nenhuma coluna numerica binaria (0/1) encontrada para comparar.")

st.subheader("Dados")
st.dataframe(df_filtered, use_container_width=True)
