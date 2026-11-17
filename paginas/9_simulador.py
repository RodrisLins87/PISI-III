import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.graficos import AZUL, LARANJA, TINTA_2, dec, estilizar, pct

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "data" / "KaggleV2-May-2016.csv"
RES = RAIZ / "ml" / "resultados"
SEMENTE = 42
DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]

NUM = ["Age", "lead", "hora_agend", "hist_n", "hist_falta", "hist_taxa"]
BINAR = ["M", "Scholarship", "Hipertensao", "Diabetes", "Alcoholism", "handcap_bin", "SMS_received"]

st.title("Simulador de risco de falta")
st.markdown("Preencha os dados de uma consulta e veja o *risco de o paciente faltar*, "
            "calculado pelo modelo final da página Previsão de faltas.")

try:
    from imblearn.over_sampling import SMOTE
    from imblearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import GroupShuffleSplit
    from sklearn.preprocessing import OneHotEncoder, StandardScaler, TargetEncoder
except ImportError:
    st.warning("Esta página precisa das bibliotecas de ML. Rode no terminal:\n\n"
               "python -m pip install -r ml/requirements-ml.txt")
    st.stop()


# ---------------------------------------------------------------- preparo dos dados
# Mesmo preparo de ml/treinar.py, para o modelo ser o mesmo avaliado na página 8.
def preparar() -> pd.DataFrame:
    d = pd.read_csv(CSV).rename(columns={"No-show": "NoShow", "Hipertension": "Hipertensao"})
    d["ScheduledDay"] = pd.to_datetime(d["ScheduledDay"]).dt.tz_localize(None)
    d["AppointmentDay"] = pd.to_datetime(d["AppointmentDay"]).dt.tz_localize(None)
    d = d[d["Age"] >= 0].copy()
    d["falta"] = (d["NoShow"] == "Yes").astype(int)
    d["sched_date"] = d["ScheduledDay"].dt.normalize()
    d["lead"] = (d["AppointmentDay"].dt.normalize() - d["sched_date"]).dt.days
    d["dow"] = d["AppointmentDay"].dt.dayofweek
    d["hora_agend"] = d["ScheduledDay"].dt.hour
    d["M"] = (d["Gender"] == "M").astype(int)
    d["handcap_bin"] = (d["Handcap"] > 0).astype(int)
    d = d[d.lead >= 0].copy().reset_index(drop=True)

    # histórico: só consultas que já tinham acontecido na data do agendamento
    d["hist_n"] = 0
    d["hist_falta"] = 0
    for _, g in d.groupby("PatientId"):
        if len(g) == 1:
            continue
        ap = g.AppointmentDay.dt.normalize().values
        ordem = np.argsort(ap)
        cf = np.concatenate([[0], np.cumsum(g.falta.values[ordem])])
        k = np.searchsorted(ap[ordem], g.sched_date.values, side="left")
        d.loc[g.index, "hist_n"] = k
        d.loc[g.index, "hist_falta"] = cf[k]
    d["hist_taxa"] = np.where(d.hist_n > 0, d.hist_falta / d.hist_n.clip(lower=1), 0.0)
    return d


@st.cache_resource(show_spinner="Treinando o modelo (só na primeira vez, leva cerca de 1 minuto)...")
def treinar_modelo():
    d = preparar()
    X = d[NUM + BINAR + ["dow", "Neighbourhood"]]
    y, grp = d.falta.values, d.PatientId.values
    tr, te = next(GroupShuffleSplit(1, test_size=0.2, random_state=SEMENTE).split(X, y, grp))

    prof = 12
    if (RES / "modelo_final.json").exists():
        prof = json.load(open(RES / "modelo_final.json")).get("profundidade_rf", 12)

    prep = ColumnTransformer([
        ("num", StandardScaler(), NUM),
        ("bin", "passthrough", BINAR),
        ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["dow"]),
        ("te", TargetEncoder(target_type="binary", random_state=SEMENTE), ["Neighbourhood"])])
    modelo = Pipeline([
        ("prep", prep),
        ("smote", SMOTE(random_state=SEMENTE)),
        ("clf", RandomForestClassifier(300, max_depth=prof, min_samples_leaf=20,
                                       n_jobs=-1, random_state=SEMENTE))])
    modelo.fit(X.iloc[tr], y[tr])

    # riscos das consultas do teste, para comparar a consulta simulada com casos reais
    risco_teste = modelo.predict_proba(X.iloc[te])[:, 1]
    bairros = sorted(d["Neighbourhood"].unique())
    return modelo, risco_teste, bairros


modelo, risco_teste, bairros = treinar_modelo()

# ---------------------------------------------------------------- formulário
with st.form("simulador"):
    st.subheader("Dados do paciente")
    c1, c2, c3 = st.columns(3)
    idade = c1.number_input("Idade", 0, 115, 30)
    sexo = c2.radio("Sexo", ["Feminino", "Masculino"], horizontal=True)
    bairro = c3.selectbox("Bairro da unidade", bairros,
                          index=bairros.index("JARDIM CAMBURI") if "JARDIM CAMBURI" in bairros else 0)

    c1, c2, c3, c4, c5 = st.columns(5)
    bolsa = c1.checkbox("Bolsa Família")
    hip = c2.checkbox("Hipertensão")
    dia = c3.checkbox("Diabetes")
    alc = c4.checkbox("Alcoolismo")
    defic = c5.checkbox("Deficiência")

    st.subheader("Histórico do paciente")
    c1, c2 = st.columns(2)
    n_ant = c1.number_input("Consultas anteriores", 0, 100, 0)
    f_ant = c2.number_input("Faltas nessas consultas", 0, 100, 0)

    st.subheader("Dados da consulta")
    c1, c2, c3, c4 = st.columns(4)
    lead = c1.number_input("Dias entre marcar e a consulta", 0, 180, 10)
    hora = c2.slider("Hora em que foi marcada", 6, 21, 10)
    dow = c3.selectbox("Dia da semana da consulta", DIAS)
    sms = c4.checkbox("Recebeu SMS de lembrete")

    enviar = st.form_submit_button("Calcular risco", type="primary")

if not enviar:
    st.info("Preencha os campos e clique em *Calcular risco*.")
    st.stop()

if f_ant > n_ant:
    st.error("O número de faltas não pode ser maior que o de consultas anteriores.")
    st.stop()

entrada = pd.DataFrame([{
    "Age": idade, "lead": lead, "hora_agend": hora,
    "hist_n": n_ant, "hist_falta": f_ant, "hist_taxa": f_ant / n_ant if n_ant else 0.0,
    "M": int(sexo == "Masculino"), "Scholarship": int(bolsa), "Hipertensao": int(hip),
    "Diabetes": int(dia), "Alcoholism": int(alc), "handcap_bin": int(defic),
    "SMS_received": int(sms), "dow": DIAS.index(dow), "Neighbourhood": bairro}])

risco = float(modelo.predict_proba(entrada)[0, 1])
posicao = float((risco_teste < risco).mean() * 100)

# ---------------------------------------------------------------- resultado
st.divider()
st.subheader("Resultado")
alto = risco >= 0.5
c1, c2, c3 = st.columns(3)
c1.metric("Pontuação de risco", pct(risco * 100))
c2.metric("Classificação", "Risco ALTO" if alto else "Risco baixo")
c3.metric("Mais arriscada que", pct(posicao, 0) + " das consultas",
          help="Comparação com as consultas reais do conjunto de teste.")

f = go.Figure(go.Indicator(
    mode="gauge+number", value=risco * 100, number={"suffix": "%", "valueformat": ".1f"},
    gauge={"axis": {"range": [0, 100]},
           "bar": {"color": LARANJA if alto else AZUL},
           "threshold": {"line": {"color": TINTA_2, "width": 3}, "value": 50}}))
estilizar(f, titulo_y="", altura=260)
st.plotly_chart(f, theme=None, config={"displayModeBar": False})

if alto:
    st.warning("O modelo *prevê falta* para esta consulta. Sugestão: reforçar o lembrete "
               "(ligação ou SMS extra) ou oferecer um horário mais próximo.")
else:
    st.success("O modelo *prevê comparecimento* para esta consulta.")

aviso = ("A linha no medidor marca o limite de 50%, o mesmo usado na avaliação da página 8. "
         "Como o modelo foi treinado com SMOTE (que equilibra faltas e comparecimentos), a pontuação "
         "*não é a chance exata* de faltar: ela serve para *ordenar* quem tem mais risco. "
         "Por isso a comparação com as consultas reais é a leitura mais segura.")
if (RES / "modelos_teste.csv").exists():
    m = pd.read_csv(RES / "modelos_teste.csv")
    m = m[m["final"] == 1].iloc[0]
    aviso += (f" No teste, o modelo encontrou cerca de {round(m['recall_falta'] * 10)} em cada 10 faltas, "
              f"com precisão de {dec(m['precisao_falta'], 2)} (muitos falsos alertas).")
st.caption(aviso)