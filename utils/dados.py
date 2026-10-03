"""
Carregamento e preparação dos dados — COMPARTILHADO por todas as páginas.

Fonte: Medical Appointment No Shows (Kaggle)
https://www.kaggle.com/datasets/joniarroba/noshowappointments
110.527 consultas de Vitória-ES, abril a junho de 2016.

⚠️ Não alterar este arquivo sem avisar o grupo: todas as páginas dependem dele.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

CAMINHO_CSV = Path(__file__).resolve().parent.parent / "data" / "KaggleV2-May-2016.csv"

ORDEM_ANTECEDENCIA = ["Mesmo dia", "1 dia", "2-3 dias", "4-7 dias", "8-14 dias",
                      "15-30 dias", "31-60 dias", "60+ dias"]
ORDEM_IDADE = ["0-5", "6-12", "13-18", "19-30", "31-45", "46-60", "60+"]
ORDEM_DIA_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]


@st.cache_data(show_spinner="Carregando dados...")
def carregar_dados() -> pd.DataFrame:
    """Lê o CSV original do Kaggle e devolve a base limpa com colunas derivadas."""
    df = pd.read_csv(CAMINHO_CSV)

    # 1. Corrigir nomes de colunas com erro de digitação no dataset original
    df = df.rename(columns={
        "Hipertension": "Hipertensao",
        "Handcap": "Deficiencia",
        "No-show": "NoShow",
        "Alcoholism": "Alcoolismo",
        "Scholarship": "BolsaFamilia",
        "Neighbourhood": "Bairro",
        "Gender": "Genero",
        "Age": "Idade",
        "SMS_received": "RecebeuSMS",
    })

    # 2. Datas
    df["ScheduledDay"] = pd.to_datetime(df["ScheduledDay"]).dt.tz_localize(None)
    df["AppointmentDay"] = pd.to_datetime(df["AppointmentDay"]).dt.tz_localize(None)

    # 3. Limpeza: 1 registro com idade negativa (-1) é removido
    df = df[df["Idade"] >= 0].copy()

    # 4. Variável-alvo: 1 = faltou, 0 = compareceu
    df["Falta"] = (df["NoShow"] == "Yes").astype(int)

    # 5. Antecedência (dias entre marcar e a consulta). Valores negativos = mesmo dia.
    df["Antecedencia"] = (df["AppointmentDay"].dt.normalize()
                          - df["ScheduledDay"].dt.normalize()).dt.days.clip(lower=0)
    df["FaixaAntecedencia"] = pd.cut(
        df["Antecedencia"], bins=[-1, 0, 1, 3, 7, 14, 30, 60, 1000],
        labels=ORDEM_ANTECEDENCIA)

    # 6. Faixa etária
    df["FaixaEtaria"] = pd.cut(df["Idade"], bins=[-1, 5, 12, 18, 30, 45, 60, 200],
                               labels=ORDEM_IDADE)

    # 7. Rótulos legíveis
    df["GeneroNome"] = df["Genero"].map({"F": "Feminino", "M": "Masculino"})
    df["SMS"] = df["RecebeuSMS"].map({0: "Sem SMS", 1: "Com SMS"})
    dias = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}
    df["DiaSemana"] = df["AppointmentDay"].dt.dayofweek.map(dias)
    df["DataConsulta"] = df["AppointmentDay"].dt.date

    # 8. Histórico do paciente — só olha consultas MARCADAS ANTES (sem vazamento do futuro)
    df = df.sort_values(["PatientId", "ScheduledDay"]).reset_index(drop=True)
    df["ConsultasAnteriores"] = df.groupby("PatientId").cumcount()
    df["FaltasAnteriores"] = df.groupby("PatientId")["Falta"].cumsum() - df["Falta"]
    df["Historico"] = "Primeira consulta"
    df.loc[(df["ConsultasAnteriores"] > 0) & (df["FaltasAnteriores"] == 0), "Historico"] = "Nunca faltou antes"
    df.loc[df["FaltasAnteriores"] > 0, "Historico"] = "Já faltou antes"

    return df


def taxa_falta(df: pd.DataFrame, coluna: str, ordem: list | None = None) -> pd.DataFrame:
    """Taxa de falta (%) e nº de consultas agrupados por uma coluna."""
    t = (df.groupby(coluna, observed=True)["Falta"]
           .agg(consultas="count", faltas="sum")
           .reset_index())
    t["taxa"] = (t["faltas"] / t["consultas"] * 100).round(1)
    if ordem is not None:
        t[coluna] = pd.Categorical(t[coluna], categories=ordem, ordered=True)
        t = t.sort_values(coluna)
    return t


def base_filtrada() -> pd.DataFrame:
    """Devolve a base já com os filtros da barra lateral aplicados (definidos em app.py)."""
    return st.session_state.get("df_filtrado", carregar_dados())
