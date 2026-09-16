# <p align="center"><img src="assets/logo3.png" alt="VittaFlow Logo" width="220"/></p>

# 🩺 VittaFlow — Análise Preditiva e Exploratória de Absenteísmo em Consultas Médicas

[![PISI III](https://img.shields.io/badge/UFRPE-PISI%20III-blue?style=flat)](https://www.ufrpe.br/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Scikit--Learn](https://img.shields.io/badge/scikit--learn-1.0+-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 1. Visão Geral do Projeto (PISI III)

O **VittaFlow** é um projeto interdisciplinar desenvolvido no âmbito do Bacharelado em Sistemas de Informação da UFRPE focado no estudo e mitigação do **absenteísmo em consultas médicas** (*no-show*). 

Nesta etapa correspondente à disciplina de **Projeto Interdisciplinar para Sistemas de Informação III (PISI III)**, o escopo engloba uma **Análise Exploratória de Dados (EDA) aprofundada** e a estruturação do processo de **KDD (Knowledge Discovery in Databases)**. O objetivo é extrair inteligência a partir de históricos de agendamentos para subsidiar a criação de um **futuro Dashboard Interativo de Apoio à Decisão Clínica** e integrar os achados comportamentais à gestão de saúde.

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
- **Base para Futuro Dashboard:** Estruturação dos indicadores chaves de desempenho (KPIs) de absenteísmo que alimentarão o painel analítico gerencial para clínicas.

---

## 🔍 3. Análise Exploratória de Dados (EDA) Aprofundada

A análise exploratória foi desenvolvida sobre um universo de **110.526 registros de agendamentos médicos** (após a limpeza e tratamento de inconsistências). A exploração dos dados gerou 10 eixos analíticos detalhados:

### 📊 3.1. Proporção Global da Variável-Alvo
- **Distribuição:** **79,8%** (88.207) de comparecimentos efetivos contra **20,2%** (22.319) de ausências (*no-show*).
- **Implicação Analítica:** Evidencia o desbalanceamento de classes típico de bases clínicas (4:1), justificando o uso de técnicas de reamostragem na fase de modelagem preditiva.

### ⏱️ 3.2. Tempo de Antecedência — *Lead Time*
- **Impacto Direto:** É a **variável de maior poder explicativo**. Consultas agendadas para o mesmo dia registram apenas **4,7%** de ausência. O índice sobe para cerca de **20%** no intervalo de 1 a 7 dias e atinge o pico de **34,2%** quando a marcação ocorre com 31 a 60 dias de antecedência.

### 📜 3.3. Histórico de Comparecimento do Paciente
- **Comportamento Pregresso:** Pacientes com histórico recorrente de não comparecimento em agendamentos anteriores apresentam probabilidade significativamente maior de faltar novamente, demonstrando que a conduta passada do paciente é um forte preditor individual.

### 📱 3.4. Lembretes por SMS
- **Análise Controlada:** A taxa bruta mostra que quem recebeu SMS faltou mais (27,6% vs. 16,7%). O diagnóstico controlado revela que o SMS é disparado prioritariamente em consultas de longa antecedência (que naturalmente possuem maior índice de falta), e não que a mensagem induza ao absenteísmo.

### 👥 3.5. Distribuição por Gênero
- **Paridade de Taxa:** As taxas individuais de falta entre homens (**20,0%**) e mulheres (**20,3%**) são praticamente idênticas. Embora as mulheres representem o maior volume absoluto de agendamentos na base, o risco individual independe do sexo.

### 🎂 3.6. Faixa Etária e Idade
- **Vulnerabilidade por Idade:** Crianças/Jovens e adultos jovens apresentam maior volatilidade e taxa de falta. Em contrapartida, idosos apresentam maiores índices de comparecimento, motivados pelo acompanhamento de doenças crônicas e rotina contínua.

### 🏥 3.7. Condições de Saúde e Fatores Socioeconômicos
- **Engajamento Clínico:** Pacientes com Hipertensão (**17,3% de falta**) e Diabetes (**18,0%**) faltam *menos* que a média geral sem essas condições (**20,8%**).
- **Vulnerabilidade Social:** Beneficiários do Bolsa Família registraram maior taxa de falta (**23,7%** vs. **19,8%**), evidenciando barreiras sociodemográficas como custos de deslocamento e transporte.

### 📅 3.8. Dia da Semana
- **Sazonalidade Semanal:** A taxa de falta permanece estável de segunda a quinta-feira (**19,4% a 20,6%**), sofrendo um aumento na sexta-feira e atingindo seu ponto máximo no sábado (**23,1%**).

### 🗺️ 3.9. Análise Geográfica por Bairros
- **Disparidade de Localização:** A análise dos bairros com maior volume de agendamentos revelou variações relevantes na taxa de absenteísmo, sugerindo que a distância física até o centro de atendimento e a infraestrutura de transporte local influenciam o comparecimento.

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

## 📊 5. Diretrizes para o Futuro Dashboard Analítico

Os insights gerados na etapa de EDA fundamentam os requisitos de negócio para a construção do **Dashboard de Monitoramento e Prevenção do Absenteísmo**, voltado aos gestores clínicos:

* **Painel de Indicadores Gerais (KPIs):** Taxa geral de *no-show*, volume de atendimentos previstos no dia e estimativa de ociosidade financeira.
* **Filtro Preditivo por Risco de Antecedência:** Sinalização automática de consultas marcadas com mais de 30 dias de antecedência (*Lead Time* elevado) para priorização de confirmações ativas.
* **Segmentação por Perfis de Vulnerabilidade:** Métricas filtradas por grupo socioeconômico e condições crônicas de saúde para ações humanizadas de acompanhamento.
* **Sazonalidade Semanal e Geográfica:** Visualização de picos de absenteísmo por dia da semana e mapa de calor por bairro/distrito.

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
