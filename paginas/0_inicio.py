import json
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.dados import carregar_dados
from utils.graficos import dec, num, pct

RAIZ = Path(__file__).resolve().parent.parent
RES = RAIZ / "ml" / "resultados"

df = carregar_dados()

total = len(df)
pacientes = df["PatientId"].nunique()
taxa = df["Falta"].mean() * 100
faltas = int(df["Falta"].sum())
inicio, fim = df["DataConsulta"].min(), df["DataConsulta"].max()

taxa_mesmo_dia = df.loc[df["Antecedencia"] == 0, "Falta"].mean() * 100
taxa_espera = df.loc[df["Antecedencia"] > 0, "Falta"].mean() * 100

hist = df.groupby("Historico")["Falta"].mean() * 100
idade = df.groupby("FaixaEtaria", observed=True)["Falta"].mean() * 100

st.title("🩺 VittaFlow · Faltas em consultas médicas")
st.markdown(
    "#### Por que tantos pacientes marcam consulta e não aparecem? E dá para prever quem vai faltar?")
st.markdown(
    "Este dashboard analisa o *absenteísmo* em consultas da rede pública de *Vitória-ES* e "
    "apoia o aplicativo *VittaFlow*, que ajuda clínicas a organizar médicos, agendas e "
    "consultas com o objetivo de *reduzir as faltas*.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Consultas analisadas", num(total))
c2.metric("Pacientes", num(pacientes))
c3.metric("Faltas", num(faltas))
c4.metric("Taxa de falta", pct(taxa))
st.caption(f"Período: {inicio:%d/%m/%Y} a {fim:%d/%m/%Y}. "
           f"Em média, *1 a cada {round(100 / taxa)} consultas* termina em falta: "
           "um horário de médico que poderia ter atendido outro paciente.")

st.divider()

st.subheader("O que os dados mostram")
a1, a2, a3 = st.columns(3)
with a1.container(border=True):
    st.markdown("*📅 A espera é o fator mais forte*")
    st.markdown(f"Quem é atendido no mesmo dia falta *{pct(taxa_mesmo_dia)}*. "
                f"Quem marca com antecedência falta *{pct(taxa_espera)}*, "
                f"cerca de *{dec(taxa_espera / taxa_mesmo_dia)}×* mais.")
with a2.container(border=True):
    st.markdown("*🔁 Quem já faltou tende a faltar de novo*")
    if {"Já faltou antes", "Nunca faltou antes"} <= set(hist.index):
        st.markdown(f"Pacientes que já faltaram antes têm taxa de *{pct(hist['Já faltou antes'])}*, "
                    f"contra *{pct(hist['Nunca faltou antes'])}* de quem sempre compareceu.")
with a3.container(border=True):
    st.markdown("*🧑‍⚕️ Jovens faltam mais que idosos*")
    st.markdown(f"A maior taxa é na faixa *{idade.idxmax()} anos* ({pct(idade.max())}); "
                f"a menor, entre *{idade.idxmin()} anos* ({pct(idade.min())}).")

b1, b2 = st.columns(2)
with b1.container(border=True):
    st.markdown("*💬 O SMS parece piorar, mas ajuda*")
    st.markdown("Olhando por cima, quem recebe SMS falta mais. Comparando dentro da mesma "
                "antecedência, o efeito se inverte: é um *Paradoxo de Simpson*.")
with b2.container(border=True):
    st.markdown("*🤖 O aprendizado de máquina confirma*")
    if (RES / "modelos_teste.csv").exists() and (RES / "shap_importancia.csv").exists():
        m = pd.read_csv(RES / "modelos_teste.csv")
        m = m[m["final"] == 1].iloc[0]
        top = pd.read_csv(RES / "shap_importancia.csv").iloc[0]["variavel"]
        st.markdown(f"O modelo final (*{m['modelo']}*) encontra cerca de "
                    f"*{round(m['recall_falta'] * 10)} em cada 10 faltas* (AUC {dec(m['auc'], 2)}). "
                    f"A variável mais importante é *{top.lower()}*.")
    else:
        st.markdown("Resultados do modelo ainda não disponíveis em ml/resultados/.")

st.divider()

st.subheader("Explore o dashboard")
PAGINAS = [
    ("paginas/1_visao_geral.py", "Visão geral", "📊", "Tamanho do problema e evolução diária"),
    ("paginas/2_antecedencia.py", "Antecedência", "📅", "Esperar mais dias aumenta a falta?"),
    ("paginas/3_sms.py", "Lembrete por SMS", "💬", "O SMS funciona? (Paradoxo de Simpson)"),
    ("paginas/4_perfil_paciente.py", "Perfil do paciente", "🧑‍⚕️", "Idade, gênero, saúde e Bolsa Família"),
    ("paginas/5_historico.py", "Histórico e dia da semana", "🔁", "Quem já faltou falta de novo?"),
    ("paginas/6_bairros.py", "Bairros", "📍", "Onde se falta mais?"),
    ("paginas/7_perfis.py", "Perfis de pacientes (ML)", "🧩", "Grupos de pacientes com KMeans"),
    ("paginas/8_previsao.py", "Previsão de faltas (ML)", "🤖", "Modelos, SMOTE, ROC e SHAP"),
    ("paginas/9_simulador.py", "Simulador de risco (ML)", "🧮", "Preencha os dados e veja o risco"),
]
existentes = [p for p in PAGINAS if (RAIZ / p[0]).exists()]
cols = st.columns(3)
for i, (arq, titulo, icone, desc) in enumerate(existentes):
    with cols[i % 3].container(border=True):
        try:
            st.page_link(arq, label=titulo, icon=icone)
        except Exception:  # página ainda não está no menu do app.py
            st.markdown(f"{icone} *{titulo}*")
        st.caption(desc)

st.divider()

e1, e2 = st.columns([3, 2])
with e1:
    st.subheader("Sobre os dados")
    st.markdown(
        "- *Fonte:* Medical Appointment No Shows (Kaggle), dados reais da rede pública de Vitória-ES.\n"
        "- *Limpeza:* 1 registro com idade negativa removido; colunas renomeadas para português.\n"
        "- *Variáveis:* idade, sexo, bairro, condições de saúde, Bolsa Família, SMS, data de "
        "marcação e data da consulta.\n"
        "- *Regra do grupo:* todo número do painel é calculado no código a partir do CSV, nada digitado à mão.")
with e2:
    st.subheader("Equipe")
    st.markdown(
        "Bruno Lins · Guilherme Teixeira · Laura Miranda · "
        "Maria Eduarda Alves · Matheus Júlio · Thyago Murilo")
    st.caption("PISI 3 · UFRPE")

st.info("Use os *filtros da barra lateral* para recortar a análise por gênero, faixa etária e período. "
        "Os números desta tela usam sempre a base completa.")