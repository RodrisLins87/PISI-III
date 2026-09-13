import re

import pandas as pd


def load_data(file):
    name = getattr(file, "name", str(file))

    if name.endswith(".csv"):
        df = pd.read_csv(file)
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file)
    else:
        raise ValueError("Formato nao suportado. Use CSV ou Excel (.xlsx/.xls).")

    return df


def basic_clean(df):
    df = df.copy()

    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")

    for col in df.select_dtypes(include="object").columns:
        try:
            parsed = pd.to_datetime(df[col], errors="coerce", utc=True)
            taxa_sucesso = parsed.notna().mean()
            if taxa_sucesso > 0.9:
                df[col] = parsed.dt.tz_localize(None)
        except Exception:
            pass

    return df


def get_column_types(df, max_categories=100):
    categorical_cols = []
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    datetime_cols = df.select_dtypes(include="datetime").columns.tolist()

    for col in df.select_dtypes(include="object").columns:
        if df[col].nunique() <= max_categories:
            categorical_cols.append(col)

    return {
        "categorical": categorical_cols,
        "numeric": numeric_cols,
        "datetime": datetime_cols,
    }


def get_binary_outcome_column(df, categorical_cols):
    palavras_chave = ["falt", "show", "outcome", "target", "cancel", "default", "churn", "desfecho", "evas"]

    for col in categorical_cols:
        if df[col].nunique() == 2 and any(p in col.lower() for p in palavras_chave):
            return col

    for col in categorical_cols:
        if df[col].nunique() == 2:
            return col

    return None


def get_binary_numeric_columns(df, numeric_cols):
    return [col for col in numeric_cols if df[col].nunique() == 2]


def drop_id_columns(df):
    padrao_id = re.compile(r"(?:^|[ _])id(?:[ _]|$)|id$", re.IGNORECASE)
    colunas_id = [col for col in df.columns if padrao_id.search(col.strip())]
    return df.drop(columns=colunas_id, errors="ignore")


def get_comparable_factor_columns(df, categorical_cols, numeric_cols, outcome_col, max_categories=10):
    binarias_numericas = get_binary_numeric_columns(df, numeric_cols)

    categoricas_comparaveis = [
        col
        for col in categorical_cols
        if col != outcome_col and 1 < df[col].nunique() <= max_categories
    ]

    return binarias_numericas + categoricas_comparaveis


def factor_analysis(df, outcome_col, positive_value, factor_cols):
    linhas = []
    for col in factor_cols:
        if col == outcome_col:
            continue
        grupos = df.groupby(col)[outcome_col].apply(lambda s: (s == positive_value).mean() * 100)
        for grupo, taxa in grupos.items():
            linhas.append({"Fator": col, "Grupo": str(grupo), "Taxa (%)": round(taxa, 1)})

    return pd.DataFrame(linhas)


COLUMN_TRANSLATIONS = {
    "PatientId": "ID do Paciente",
    "AppointmentID": "ID da Consulta",
    "Gender": "Genero",
    "ScheduledDay": "Dia do Agendamento",
    "AppointmentDay": "Dia da Consulta",
    "Age": "Idade",
    "Neighbourhood": "Bairro",
    "Scholarship": "Bolsa Familia",
    "Hipertension": "Hipertensao",
    "Diabetes": "Diabetes",
    "Alcoholism": "Alcoolismo",
    "Handcap": "Deficiencia",
    "SMS_received": "Recebeu SMS",
    "No-show": "Faltou",
}


def translate_columns(df):
    df = df.copy()

    def _formatar(col):
        if col in COLUMN_TRANSLATIONS:
            return COLUMN_TRANSLATIONS[col]
        return col.replace("_", " ").replace("-", " ").strip().title()

    df.columns = [_formatar(c) for c in df.columns]
    return df
