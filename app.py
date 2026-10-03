"""
Dashboard de Absenteísmo em Consultas Médicas — VittaFlow (PISI 3)

Como rodar:
    pip install -r requirements.txt
    streamlit run app.py

Este arquivo só monta a navegação e os filtros da barra lateral.
Cada integrante do grupo cuida de UM arquivo dentro da pasta paginas/.
"""
from pathlib import Path

import streamlit as st

from utils.dados import ORDEM_IDADE, carregar_dados

st.set_page_config(page_title="VittaFlow · Faltas em consultas", page_icon="🩺", layout="wide")

df = carregar_dados()

# ------------------------------------------------------------------
# Filtros globais (valem para TODAS as páginas)
# ------------------------------------------------------------------
with st.sidebar:
    st.header("Filtros")
    generos = st.multiselect("Gênero", ["Feminino", "Masculino"],
                             default=["Feminino", "Masculino"], key="f_genero")
    faixas = st.multiselect("Faixa etária", ORDEM_IDADE, default=ORDEM_IDADE, key="f_idade")
    data_min, data_max = df["DataConsulta"].min(), df["DataConsulta"].max()
    periodo = st.date_input("Período da consulta", value=(data_min, data_max),
                            min_value=data_min, max_value=data_max,
                            format="DD/MM/YYYY", key="f_periodo")
    st.caption("Fonte: Medical Appointment No Shows (Kaggle) — "
               "110.527 consultas em Vitória-ES, abr–jun/2016.")

# date_input devolve 1 data enquanto o usuário ainda está escolhendo o intervalo
if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
    inicio, fim = periodo
else:
    inicio, fim = data_min, data_max

filtro = (df["GeneroNome"].isin(generos)
          & df["FaixaEtaria"].isin(faixas)
          & df["DataConsulta"].between(inicio, fim))
st.session_state["df_filtrado"] = df[filtro]

# ------------------------------------------------------------------
# Páginas (1 por integrante)
# ------------------------------------------------------------------
# Só entram no menu as páginas cujo arquivo já existe: cada integrante sobe
# o seu arquivo e a página aparece sozinha, sem precisar editar este app.py.
PASTA = Path(__file__).parent
CATALOGO = [
    ("paginas/1_visao_geral.py", "Visão geral", "📊"),
    ("paginas/2_antecedencia.py", "Antecedência do agendamento", "📅"),
    ("paginas/3_sms.py", "Lembrete por SMS", "💬"),
    ("paginas/4_perfil_paciente.py", "Perfil do paciente", "🧑‍⚕️"),
    ("paginas/5_historico.py", "Histórico e dia da semana", "🔁"),
    ("paginas/6_bairros.py", "Bairros", "📍"),
]
paginas = [st.Page(arq, title=titulo, icon=icone)
           for arq, titulo, icone in CATALOGO if (PASTA / arq).exists()]

if not paginas:
    st.info("Nenhuma página criada ainda na pasta paginas/.")
    st.stop()
st.navigation(paginas).run()
