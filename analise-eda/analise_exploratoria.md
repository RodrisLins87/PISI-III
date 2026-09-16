# Análise Exploratória de Dados (EDA) — VittaFlow
## Previsão de Absenteísmo em Consultas Médicas

## 1. Fonte e Qualidade dos Dados

**Fonte original:** [Kaggle — Medical Appointment No Shows](https://www.kaggle.com/datasets/joniarroba/noshowappointments)
**Período:** abril a junho de 2016
**Origem:** consultas médicas do serviço público de saúde de Vitória, Espírito Santo, Brasil

| Métrica | Valor |
|---|---|
| Registros originais | 110.527 |
| Valores nulos encontrados | 0 |
| Linhas duplicadas encontradas | 0 |
| Registros com idade negativa removidos | 1 |
| **Registros na base final** | **110.526** |
| Pacientes únicos | 62.298 |
| Média de consultas por paciente | 1,77 |
| Faixa de idade | 0 a 115 anos (7 registros acima de 100 anos, plausíveis) |

## 2. Distribuição da Variável Alvo

- **Compareceu:** 88.207 consultas (79,8%)
- **Faltou:** 22.319 consultas (20,2%)

Percentual consistente com o reportado por Pereira (2020) na mesma base de dados.

![Distribuição de comparecimento x falta](graficos/fig01_distribuicao_alvo.png)

*Figura 1. Distribuição de comparecimento e falta na base de dados.*


## 3. Tempo de Antecedência do Agendamento (fator mais forte)

| Antecedência | % de falta | N |
|---|---|---|
| 0 dias | 4,7% | 38.567 |
| 1 dia | 21,4% | 5.213 |
| 2-3 dias | 23,7% | 9.462 |
| 4-7 dias | 25,2% | 17.510 |
| 8-14 dias | 30,5% | 12.025 |
| 15-30 dias | 32,6% | 17.371 |
| **31-60 dias** | **34,2%** | 8.283 |
| 60+ dias | 28,4% | 2.095 |

Correlação (point-biserial) com falta: **r=0,186, p-valor<0,001** (altamente significativo)

![Taxa de falta por antecedência do agendamento](graficos/fig02_falta_antecedencia.png)

*Figura 2. Taxa de falta por tempo de antecedência do agendamento.*

## 4. Histórico Prévio do Paciente

Pacientes com histórico (≥1 consulta anterior): 48.228 (43,6% da base)

- **Nunca faltou antes** → falta agora: 15,3%
- **Já faltou antes** → falta agora: 26,6%

Correlação (PriorNoShows x Falta): r=0,084, p-valor<0,001

![Taxa de falta conforme histórico do paciente](graficos/fig03_falta_historico.png)

*Figura 3. Taxa de falta conforme histórico prévio do paciente.*


## 5. SMS: Efeito Bruto vs Efeito Controlado (Paradoxo de Simpson)

**Sem controle:** Não recebeu SMS: 16,7% | Recebeu SMS: 27,6%
→ Olhando assim, *parece* que SMS aumenta a falta.

**Controlando pela faixa de antecedência** (comparação dentro do mesmo nível de espera):

| Antecedência | Sem SMS | Com SMS |
|---|---|---|
| 2-3 dias | 24,0% | 21,3% |
| 4-7 dias | 27,1% | 24,0% |
| 8-14 dias | 33,8% | 28,1% |
| 15-30 dias | 36,9% | 29,8% |
| 31-60 dias | 38,4% | 31,5% |
| 60+ dias | 33,9% | 25,5% |

**Dentro de cada faixa de antecedência, quem recebe SMS falta MENOS.** Isso é um **Paradoxo de Simpson**: a variável escondida (antecedência) invertia o resultado agregado, porque quem recebe SMS é, em média, quem tem mais antecedência (correlação SMS x DayDifference = 0,40) — e é esse grupo que mais falta de qualquer forma. Controlando esse fator, o SMS tem sim um efeito protetor real.

![Efeito do SMS controlando pela antecedência](graficos/fig04_sms_controlado.png)

*Figura 4. Efeito do SMS na falta, controlando pela antecedência (Paradoxo de Simpson).*

## 6. Gênero

- Feminino: 20,3%
- Masculino: 20,0%

Qui-quadrado: chi2=1,9, p-valor=0,173 → **NÃO significativo**

![Taxa de falta por gênero](graficos/fig05_falta_genero.png)

*Figura 5. Taxa de falta por gênero.*