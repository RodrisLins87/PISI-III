"""
PÁGINA 6 — BAIRROS

Pergunta que a página responde:
    Onde se falta mais?
"""

import streamlit as st
from utils.dados import base_filtrada

# 1. Carrega os dados respeitando os filtros globais da barra lateral
df = base_filtrada()

# 2. Título principal e descrição da página
st.title("Onde se falta mais?")
st.markdown(
    "Análise da taxa de absenteísmo e volume de faltas distribuídos pelos "
    "bairros de Vitória-ES. Os filtros da barra lateral valem para esta página também."
)

# 3. Tratamento para caso os filtros resultem em base vazia
if df.empty:
    st.warning(
        "Nenhuma consulta com os filtros escolhidos. "
        "Ajuste os filtros na barra lateral."
    )
    st.stop()

# 4. Mensagem temporária de validação da estrutura inicial (Dia 1)
st.info(
    
    "A base de dados foi carregada com sucesso nesta página.\n\n"
    "(mínimo de 200 consultas por bairro) e os gráficos de ranking."
)