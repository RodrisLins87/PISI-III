"""
PÁGINA 8 — PREVISÃO DE FALTAS (aprendizado de máquina supervisionado)

Pergunta que a página responde (PP2):
    É possível prever, antes da consulta, se o paciente vai faltar?

Os números vêm de ml/treinar.py, calculados a partir do CSV original.
Os filtros da barra lateral NÃO se aplicam aqui: o modelo foi treinado e testado
em toda a base.
"""
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.graficos import AZUL, LARANJA, TINTA_2, dec, estilizar, mostrar, num, pct

RES = Path(__file__).resolve().parent.parent / "ml" / "resultados"

st.title("Previsão de faltas")

if not (RES / "modelos_teste.csv").exists():
    st.warning("Resultados não encontrados. Rode `python ml/treinar.py` na pasta do dashboard.")
    st.stop()

mod = pd.read_csv(RES / "modelos_teste.csv")
fin = json.load(open(RES / "modelo_final.json"))
roc = pd.read_csv(RES / "roc_final.csv")
shap = pd.read_csv(RES / "shap_importancia.csv")
final = fin["modelo_final"]
ic = fin["ic95_bootstrap_por_paciente"]

st.markdown(
    "Aqui o alvo é conhecido (faltou ou compareceu), então usamos **aprendizado supervisionado**. "
    "Comparamos três algoritmos, cada um com e sem **SMOTE** (técnica que equilibra as classes, "
    "já que só ~20% das consultas são faltas).")

st.info("Os **filtros da barra lateral não se aplicam a esta página**: o modelo foi treinado e testado em toda a base.")

c1, c2, c3 = st.columns(3)
c1.metric("Consultas no treino", num(fin["n_treino"]))
c2.metric("Consultas no teste", num(fin["n_teste"]))
c3.metric("Pacientes em comum", "0",
          help="Treino e teste são separados por paciente: o mesmo paciente nunca aparece nos dois.")
st.caption("**Sem vazamento:** a separação é por paciente, o histórico de faltas usa só consultas "
           "anteriores à marcação, e o SMOTE é aplicado apenas dentro do treino.")

# ---------------- Comparação ----------------
st.subheader("1. Comparação dos modelos no teste")
f = go.Figure()
f.add_trace(go.Bar(name="Faltas encontradas (recall)", x=mod["modelo"], y=mod["recall_falta"] * 100,
                   marker_color=AZUL, marker_cornerradius=4,
                   text=[pct(v * 100, 0) for v in mod["recall_falta"]], textposition="outside"))
f.add_trace(go.Bar(name="Alertas que eram falta (precisão)", x=mod["modelo"], y=mod["precisao_falta"] * 100,
                   marker_color=LARANJA, marker_cornerradius=4,
                   text=[pct(v * 100, 0) for v in mod["precisao_falta"]], textposition="outside"))
estilizar(f, titulo_y="%", altura=420)
f.update_layout(barmode="group")
f.update_yaxes(range=[0, 105])
f.update_xaxes(tickangle=-20)
mostrar(f)
st.caption("**Sem SMOTE, os modelos quase não acham faltas** (acertam a maioria porque quase todo mundo "
           "comparece). Com SMOTE, o recall sobe muito e a precisão cai: é uma troca.")

tab = mod[["modelo", "auc", "recall_falta", "precisao_falta", "f1_falta", "cv_f1_falta"]].copy()
tab["modelo"] = [("⭐ " if f_ else "") + m for m, f_ in zip(tab["modelo"], mod["final"])]
for c in ["recall_falta", "precisao_falta", "f1_falta", "cv_f1_falta"]:
    tab[c] = tab[c].map(lambda v: dec(v, 2))
tab["auc"] = tab["auc"].map(lambda v: dec(v, 3))
tab.columns = ["Modelo", "AUC (teste)", "Recall falta", "Precisão falta", "F1 falta", "F1 falta (validação cruzada)"]
st.dataframe(tab, hide_index=True)
st.caption(f"⭐ **Modelo final: {final}**, escolhido pelo maior F1 da classe \"falta\" na validação cruzada "
           "(feita só no treino, agrupada por paciente), nunca olhando o teste.")

with st.expander("Overfitting: treino × teste"):
    o = mod[["modelo", "auc_treino", "auc", "f1_falta_treino", "f1_falta"]].copy()
    for c in o.columns[1:]:
        o[c] = o[c].map(lambda v: dec(v, 3))
    o.columns = ["Modelo", "AUC treino", "AUC teste", "F1 falta treino", "F1 falta teste"]
    st.dataframe(o, hide_index=True)
    st.caption("Diferença pequena entre treino e teste: os modelos foram limitados (profundidade escolhida "
               "por validação cruzada) e não decoraram o treino.")

# ---------------- Modelo final ----------------
st.subheader(f"2. Modelo final com margem de erro: {final}")
st.markdown("Margem de erro = intervalo de 95% por *bootstrap por paciente* (300 sorteios) sobre o teste.")


def faixa(chave, dec_=2):
    lo, hi = ic[chave]
    return f"{dec(lo, dec_)} a {dec(hi, dec_)}"


r = mod[mod["modelo"] == final].iloc[0]
c1, c2, c3, c4 = st.columns(4)
c1.metric("AUC", dec(r["auc"], 2), help=f"Intervalo de 95%: {faixa('auc')}")
c2.metric("Recall (falta)", dec(r["recall_falta"], 2), help=f"Intervalo de 95%: {faixa('recall_falta')}")
c3.metric("Precisão (falta)", dec(r["precisao_falta"], 2), help=f"Intervalo de 95%: {faixa('precisao_falta')}")
c4.metric("F1 (falta)", dec(r["f1_falta"], 2), help=f"Intervalo de 95%: {faixa('f1_falta')}")
st.caption(f"Intervalos de 95%: AUC {faixa('auc')} · recall {faixa('recall_falta')} · "
           f"precisão {faixa('precisao_falta')} · F1 {faixa('f1_falta')}.")

cm = fin["matriz_confusao"]
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Matriz de confusão (teste)**")
    z = [[cm["verdadeiro_negativo"], cm["falso_positivo"]], [cm["falso_negativo"], cm["verdadeiro_positivo"]]]
    f = go.Figure(go.Heatmap(z=z, x=["Previu: compareceu", "Previu: faltou"],
                             y=["Real: compareceu", "Real: faltou"], colorscale=[[0, "#f4f4f1"], [1, AZUL]],
                             text=[[num(v) for v in lin] for lin in z], texttemplate="%{text}",
                             showscale=False, hoverinfo="skip"))
    estilizar(f, titulo_y="", altura=320)
    f.update_yaxes(autorange="reversed", title_text="")
    mostrar(f)
with col_b:
    st.markdown("**Curva ROC**")
    f = go.Figure()
    f.add_trace(go.Scatter(x=roc["fpr"], y=roc["tpr"], mode="lines", line=dict(color=AZUL, width=2.5), name="Modelo"))
    f.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(color=TINTA_2, dash="dash"), name="Acaso"))
    estilizar(f, titulo_y="Faltas encontradas (taxa)", altura=320)
    f.update_xaxes(title_text="Falsos alertas (taxa)")
    mostrar(f)

st.info(f"Em palavras: de cada 10 faltas reais, o modelo encontra cerca de {round(r['recall_falta'] * 10)}; "
        f"e de cada 3 alertas, cerca de {round(r['precisao_falta'] * 3)} é falta de verdade. "
        "Isso serve para **priorizar quem recebe lembrete reforçado**, não para decisões automáticas.")

# ---------------- SHAP ----------------
st.subheader("3. O que mais pesa na previsão? (SHAP)")
top = shap.head(10).iloc[::-1]
f = go.Figure(go.Bar(x=top["importancia_shap"], y=top["variavel"], orientation="h",
                     marker_color=AZUL, marker_cornerradius=4))
estilizar(f, titulo_y="", altura=420)
f.update_xaxes(title_text="Importância média (|SHAP|)", showgrid=True)
f.update_yaxes(title_text="", type="category")
mostrar(f)
primeira, segunda = shap.iloc[0], shap.iloc[1]
st.caption(f"SHAP calculado só no modelo final, sobre 2.000 consultas do teste. **{primeira['variavel']}** é "
           f"o fator mais importante, cerca de {dec(primeira['importancia_shap'] / segunda['importancia_shap'])}× "
           f"o de {segunda['variavel']} — o mesmo que a análise exploratória já indicava.")

st.warning(
    "**Cuidado ao generalizar:** o modelo foi treinado e testado só nesta base (Vitória-ES, 2016). "
    "Ele ainda **não foi validado em outra clínica** e **não está integrado ao aplicativo**. "
    "O desempenho é moderado: serve de apoio, não de decisão.")
