import plotly.express as px
import streamlit as st

from utils.dados import ORDEM_ANTECEDENCIA, base_filtrada, taxa_falta
from utils.graficos import AZUL, LARANJA, barras_agrupadas, dec ,estilizar, mostrar

ORDEM_SMS = ["Sem SMS", "Com SMS"]

df = base_filtrada()

st.title("O SMS de lembrete funciona?")

if df.empty:
    st.warning("Nenhuma consulta com os filtros escolhidos.")
    st.stop()

# ---------------- Passo 1: visão ingênua ----------------
st.subheader("1. Olhando por cima: quem recebe SMS falta mais")
geral = taxa_falta(df, "SMS", ORDEM_SMS)
fig = px.bar(geral, x="SMS", y="taxa", color="SMS", text="taxa",
             category_orders={"SMS": ORDEM_SMS}, color_discrete_sequence=[AZUL, LARANJA],
             custom_data=["consultas", "faltas"])
fig.update_traces(marker_cornerradius=4, texttemplate="%{text:.1f}%", textposition="outside",
                  cliponaxis=False, showlegend=False,
                  hovertemplate="<b>%{x}</b><br>Taxa de falta: %{y:.1f}%<br>"
                                "Consultas: %{customdata[0]:,}<br>Faltas: %{customdata[1]:,}<extra></extra>")
estilizar(fig, altura=320)
fig.update_xaxes(title_text="")
mostrar(fig, geral)

st.markdown("Se parássemos aqui, a conclusão seria *\"SMS aumenta a falta\"*. **Isso está errado.**")

# ---------------- Passo 2: quem recebe SMS ----------------
st.subheader("2. Por quê? O SMS só é enviado para quem marca com antecedência")
envio = (df.groupby("FaixaAntecedencia", observed=True)["RecebeuSMS"].mean() * 100).round(1).reset_index()
envio.columns = ["FaixaAntecedencia", "pct_sms"]
fig2 = px.bar(envio, x="FaixaAntecedencia", y="pct_sms", text="pct_sms",
              category_orders={"FaixaAntecedencia": ORDEM_ANTECEDENCIA})
fig2.update_traces(marker_color=AZUL, marker_cornerradius=4, texttemplate="%{text:.0f}%",
                   textposition="outside", cliponaxis=False,
                   hovertemplate="<b>%{x}</b><br>Receberam SMS: %{y:.1f}%<extra></extra>")
estilizar(fig2, titulo_y="% que recebeu SMS", altura=320)
fig2.update_xaxes(title_text="Dias entre marcar e a consulta")
mostrar(fig2, envio.rename(columns={"pct_sms": "% que recebeu SMS"}))
st.markdown("Consultas marcadas para o mesmo dia ou o dia seguinte **nunca** recebem SMS, e são justamente "
            "as que menos faltam (ver página *Antecedência*). Isso puxa a taxa do grupo \"Sem SMS\" para baixo.")


# ---------------- Passo 3: comparação justa ----------------
st.subheader("3. Comparando dentro da mesma faixa de antecedência")
com_sms_possivel = df[df["Antecedencia"] >= 2]
tabela = (com_sms_possivel.groupby(["FaixaAntecedencia", "SMS"], observed=True)["Falta"]
          .agg(consultas="count", faltas="sum").reset_index())
tabela["taxa"] = (tabela["faltas"] / tabela["consultas"] * 100).round(1)

if tabela.empty:
    st.info("Não há consultas com 2+ dias de antecedência nos filtros escolhidos.")
    st.stop()

mostrar(barras_agrupadas(tabela, "FaixaAntecedencia", "SMS", ORDEM_SMS,
                         "Dias entre marcar e a consulta"), tabela)

pivo = tabela.pivot(index="FaixaAntecedencia", columns="SMS", values="taxa").dropna()
if {"Sem SMS", "Com SMS"} <= set(pivo.columns) and len(pivo):
    menores = int((pivo["Com SMS"] < pivo["Sem SMS"]).sum())
    reducao = (pivo["Sem SMS"] - pivo["Com SMS"]).mean()
    if reducao > 0:
        st.success(
            f"Em **{menores} de {len(pivo)}** faixas de antecedência, quem recebeu SMS faltou **menos**, "
            f"uma redução média de **{dec(reducao)} pontos percentuais**."
        )
    else:
        st.warning(
            f"Com os filtros escolhidos, o SMS não reduziu a falta: em **{menores} de {len(pivo)}** faixas "
            f"a taxa foi menor com SMS, e a diferença média foi de **{dec(reducao)} pontos percentuais**."
        )

with st.expander("O que é o Paradoxo de Simpson?"):
    st.markdown(
        "É quando uma tendência que aparece nos dados agrupados **se inverte** quando olhamos "
        "dentro de cada subgrupo. Aqui, a variável escondida é a **antecedência**: ela influencia "
        "ao mesmo tempo quem recebe SMS e quem falta. Controlando por ela, o SMS tem efeito protetor."
    )