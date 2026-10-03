# <p align="center"><img src="assets/logo3.png" alt="VittaFlow Logo" width="220"/></p>

# 🩺 VittaFlow — Análise Preditiva e Exploratória de Absenteísmo em Consultas Médicas

[![PISI III](https://img.shields.io/badge/UFRPE-PISI%20III-blue?style=flat)](https://www.ufrpe.br/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Gráficos-3F4F75?style=flat&logo=plotly&logoColor=white)](https://plotly.com/python/)
[![Scikit--Learn](https://img.shields.io/badge/scikit--learn-1.0+-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 1. Visão Geral do Projeto (PISI III)

O **VittaFlow** é um projeto interdisciplinar desenvolvido no âmbito do Bacharelado em Sistemas de Informação da UFRPE focado no estudo e mitigação do **absenteísmo em consultas médicas** (*no-show*).

Nesta etapa correspondente à disciplina de **Projeto Interdisciplinar para Sistemas de Informação III (PISI III)**, o escopo engloba uma **Análise Exploratória de Dados (EDA) aprofundada**, a estruturação do processo de **KDD (Knowledge Discovery in Databases)** e um **Dashboard Interativo de Apoio à Decisão Clínica** (Streamlit + Plotly) que apresenta os achados da análise para gestores de clínicas.

**Base de dados:** [Medical Appointment No Shows (Kaggle)](https://www.kaggle.com/datasets/joniarroba/noshowappointments) — 110.527 consultas da rede pública de Vitória-ES, de abril a junho de 2016.

> 📲 **Integração com a Aplicação Mobile (DSI):** A camada operacional de cadastro e gerenciamento de consultas desenvolvida em React Native / Firebase para a disciplina de Desenvolvimento de Sistemas (DSI) encontra-se em um repositório dedicado: **[Repositório VittaFlow Mobile - DSI](https://github.com/RodrisLins87/DSI-)**.

---

## 🎯 2. Problema vs. Solução

### 🚩 O Problema (Contexto de Saúde)
- **Taxas Elevadas de Absenteísmo:** A taxa média de não comparecimento a consultas no mundo gira em torno de **23%**, subindo para **27,8% na América do Sul** e ultrapassando **38%** em redes públicas metropolitanas brasileiras.
- **Impacto Organizacional e Financeiro:** A ausência não notificada provoca desperdício de recursos, ociosidade da equipe médica e dilatação das filas de espera. A Organização Mundial da Saúde (OMS) estima que **20% a 40% dos gastos em saúde são perdidos por ineficiência de gestão**.
- **Limitação de Ações Genéricas:** Lembretes convencionais atuam de forma pontual e reativa sobre todos os pacientes, sem compreender a relevância de variáveis como a antecedência do agendamento ou condições sociodemográficas.

### 💡 A Solução (VittaFlow - Vertente PISI III)
- **Análise Exploratória Extensiva (EDA):** Diagnóstico estatístico rigoroso sobre 10 eixos analíticos comportamentais e sociodemográficos para fundamentar a tomada de decisão.
- **Engenharia de Dados & KDD:** Modelagem não supervisionada (clusterização) para segmentação de perfis de risco e preparação do pipeline de dados.
- **Dashboard Interativo:** Painel analítico com os indicadores-chave (KPIs) de absenteísmo, filtros por gênero, faixa etária e período, e uma página para cada eixo da análise.

---

## 🔍 3. Análise Exploratória de Dados (EDA) Aprofundada

A análise exploratória foi desenvolvida sobre um universo de **110.526 registros de agendamentos médicos** (após a limpeza e tratamento de inconsistências). A exploração dos dados gerou 10 eixos analíticos detalhados:

### 📊 3.1. Proporção Global da Variável-Alvo
- **Distribuição:** **79,8%** (88.207) de comparecimentos efetivos contra **20,2%** (22.319) de ausências (*no-show*).
- **Implicação Analítica:** Evidencia o desbalanceamento de classes típico de bases clínicas (4:1), justificando o uso de técnicas de reamostragem na fase de modelagem preditiva.

### ⏱️ 3.2. Tempo de Antecedência — *Lead Time*
- **Impacto Direto:** É a **variável de maior poder explicativo**. Consultas agendadas para o mesmo dia registram apenas **4,7%** de ausência. O índice sobe para **21,4% a 25,2%** no intervalo de 1 a 7 dias e atinge o pico de **34,2%** quando a marcação ocorre com 31 a 60 dias de antecedência.

### 📜 3.3. Histórico de Comparecimento do Paciente
- **Comportamento Pregresso:** Pacientes que já faltaram a uma consulta anterior apresentam probabilidade significativamente maior de faltar novamente (**26,6%** contra **15,3%** de quem nunca faltou, e **37,9%** entre quem já faltou 3 vezes ou mais), demonstrando que a conduta passada é um forte preditor individual.

### 📱 3.4. Lembretes por SMS
- **Análise Controlada:** A taxa bruta mostra que quem recebeu SMS faltou mais (27,6% vs. 16,7%). O diagnóstico controlado revela que o SMS é disparado prioritariamente em consultas de longa antecedência (que naturalmente possuem maior índice de falta), e não que a mensagem induza ao absenteísmo. Dentro de uma mesma faixa de antecedência, o SMS reduz a taxa de falta em todas as 6 faixas comparáveis.

### 👥 3.5. Distribuição por Gênero
- **Paridade de Taxa:** As taxas individuais de falta entre homens (**20,0%**) e mulheres (**20,3%**) são praticamente idênticas (teste qui-quadrado, p = 0,173: diferença não significativa). Embora as mulheres representem o maior volume absoluto de agendamentos na base, o risco individual independe do sexo.

### 🎂 3.6. Faixa Etária e Idade
- **Vulnerabilidade por Idade:** Adolescentes e adultos jovens apresentam as maiores taxas de falta (**26,1%** entre 13 e 18 anos). Em contrapartida, idosos apresentam os maiores índices de comparecimento (**15,2%** de falta a partir dos 60 anos), motivados pelo acompanhamento de doenças crônicas e rotina contínua.

### 🏥 3.7. Condições de Saúde e Fatores Socioeconômicos
- **Engajamento Clínico:** Pacientes com Hipertensão (**17,3% de falta**) e Diabetes (**18,0%**) faltam *menos* que pacientes sem essas condições (**20,9%** e **20,4%**, respectivamente).
- **Vulnerabilidade Social:** Beneficiários do Bolsa Família registraram maior taxa de falta (**23,7%** vs. **19,8%**), evidenciando barreiras sociodemográficas como custos de deslocamento e transporte.

### 📅 3.8. Dia da Semana
- **Sazonalidade Semanal:** A taxa de falta permanece estável de segunda a quinta-feira (**19,4% a 20,6%**), sofrendo um aumento na sexta-feira (**21,2%**) e atingindo seu ponto máximo no sábado (**23,1%**).

### 🗺️ 3.9. Análise Geográfica por Bairros
- **Disparidade de Localização:** Entre os bairros com pelo menos 200 consultas, a taxa de falta varia de **14,6%** (Mário Cypreste) a **28,9%** (Santos Dumont), sugerindo que a distância física até o centro de atendimento e a infraestrutura de transporte local influenciam o comparecimento.

### 🔗 3.10. Matriz de Correlação
- **Mapeamento de Atributos:** Permitiu identificar interdependências entre as variáveis numéricas e categóricas encodadas (como a relação entre antecedência, envio de SMS e idade), orientando a seleção de *features* para o treinamento dos modelos.

---

## 🤖 4. Mineração de Dados & Aprendizado de Máquina (Processo KDD)

A etapa de mineração de dados tem como objetivo responder às perguntas de pesquisa formuladas no projeto:

### 🧩 Clusterização (PP1 - Aprendizado Não Supervisionado)
- **Objetivo:** Identificar perfis e subgrupos distintos de pacientes com base em características demográficas, socioeconômicas, localização e histórico de saúde.
- **Técnica:** Agrupamento por **K-Means**.
- **Validação e Ajuste:** Definição da quantidade ideal de clusters por meio do **Método do Cotovelo (*Elbow Method*)** e gráficos de **Silhueta (*Silhouette Score*)**.

### 🎯 Classificação (PP2 - Aprendizado Supervisionado)
- **Objetivo:** Estimar a probabilidade individual de falta ou comparecimento do paciente antes do atendimento agendado.
- **Metodologia:** Experimentos de classificação avaliando diferentes técnicas de aprendizado supervisionado, combinadas ao tratamento do desbalanceamento de classes por reamostragem sintética (SMOTE).

---

## 📊 5. Dashboard Interativo

Painel em **Streamlit + Plotly** que apresenta os achados da EDA para gestores clínicos. Todos os números são calculados em tempo real a partir da base original do Kaggle, sem nenhum valor digitado à mão.

### ▶️ Como rodar

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

O navegador abre sozinho em `http://localhost:8501`.

### 🧭 Páginas

| # | Página | Pergunta que responde |
|---|--------|-----------------------|
| 1 | Visão geral | Qual o tamanho do problema? |
| 2 | Antecedência do agendamento | Esperar mais dias aumenta a falta? |
| 3 | Lembrete por SMS | O lembrete por SMS funciona? |
| 4 | Perfil do paciente | Idade, gênero e condições de saúde mudam a falta? |
| 5 | Histórico e dia da semana | Quem já faltou falta de novo? Há dia pior? |
| 6 | Bairros | Onde se falta mais? |

### 🎛️ Filtros (barra lateral, valem para todas as páginas)
- **Gênero**
- **Faixa etária**
- **Período da consulta** (29/04/2016 a 08/06/2016)

### 🗂️ Estrutura

```
dashboard/
├── app.py                      → navegação + filtros da barra lateral
├── requirements.txt
├── .streamlit/config.toml      → tema
├── data/KaggleV2-May-2016.csv  → base original, sem alteração
├── utils/
│   ├── dados.py                → leitura e limpeza da base (compartilhado)
│   └── graficos.py             → cores e estilo padrão dos gráficos (compartilhado)
└── paginas/
    ├── 1_visao_geral.py
    ├── 2_antecedencia.py
    ├── 3_sms.py
    ├── 4_perfil_paciente.py
    ├── 5_historico.py
    └── 6_bairros.py
```

### 📏 Regras do grupo
1. **Só dados reais:** todo número vem do CSV original, calculado no código.
2. **Não mexer em `utils/`** sem avisar no grupo: todas as páginas dependem desses arquivos.
3. **Usar as funções de `utils/graficos.py`** (`barras_taxa`, `barras_agrupadas`, `mostrar`) para manter o mesmo visual. Cores: 1 série = azul; 2 séries = azul e laranja.
4. **Testar antes de subir:** rodar o app, abrir a sua página e mexer nos filtros (inclusive desmarcar tudo) para ver se nada quebra.

---

## 👥 6. Equipe do Projeto

Projetado e desenvolvido por estudantes da **Universidade Federal Rural de Pernambuco (UFRPE)**:

* **Bruno Rodrigo Silva Lins** — [Github](https://github.com/RodrisLins87)
* **Guilherme Abraão Teixeira Bezerra** — [Github](https://github.com/teixeiraguilherme)
* **Laura Alcântara de Miranda** — [Github](https://github.com/laura-amiranda)
* **Maria Eduarda Alves de Oliveira** — [Github](https://github.com/MariaEduardaAlves835)
* **Matheus Julio da Silva** — [Github](https://github.com/MatheusJS12)
* **Thyago Murilo dos Santos** — [Github](https://github.com/ThyagomMurilo09)

---
*Projeto interdisciplinar desenvolvido para as disciplinas de Engenharia de Software, Projetos Interdisciplinares III e Desenvolvimento de Sistemas ( ES / PISI III / DSI ) - UFRPE.*