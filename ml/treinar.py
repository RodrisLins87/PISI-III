"""
Aprendizado de máquina do VittaFlow (PISI 3) — gera os resultados lidos pelas
páginas 7 (Perfis de pacientes) e 8 (Previsão de faltas) do dashboard.

Como rodar (uma vez, na pasta do dashboard; leva alguns minutos):
    pip install -r ml/requirements-ml.txt
    python ml/treinar.py

Saída: arquivos em ml/resultados/ (CSV/JSON pequenos, versionados no Git).
Tudo é calculado a partir do CSV original em data/. Nada é digitado à mão.

PP1 (perfis): KMeans (k=6) sobre os pacientes, com margem de erro e estabilidade.
PP2 (previsão): Regressão Logística, Árvore de Decisão e Random Forest,
                com e sem SMOTE, treino/teste separados por paciente, e SHAP.
"""
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (adjusted_rand_score, f1_score, precision_score,
                             recall_score, roc_auc_score, roc_curve, silhouette_score,
                             accuracy_score)
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.preprocessing import OneHotEncoder, StandardScaler, TargetEncoder
from sklearn.tree import DecisionTreeClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline

warnings.filterwarnings("ignore")

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "data" / "KaggleV2-May-2016.csv"
SAIDA = RAIZ / "ml" / "resultados"
SAIDA.mkdir(parents=True, exist_ok=True)
SEMENTE = 42
T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:6.0f}s]", *a, flush=True)


# ---------------------------------------------------------------- dados
def carregar() -> pd.DataFrame:
    d = pd.read_csv(CSV).rename(columns={"No-show": "NoShow", "Hipertension": "Hipertensao"})
    d["ScheduledDay"] = pd.to_datetime(d["ScheduledDay"]).dt.tz_localize(None)
    d["AppointmentDay"] = pd.to_datetime(d["AppointmentDay"]).dt.tz_localize(None)
    d = d[d["Age"] >= 0].copy()                      # 1 registro com idade -1
    d["falta"] = (d["NoShow"] == "Yes").astype(int)
    d["sched_date"] = d["ScheduledDay"].dt.normalize()
    d["lead"] = (d["AppointmentDay"].dt.normalize() - d["sched_date"]).dt.days
    d["dow"] = d["AppointmentDay"].dt.dayofweek
    d["hora_agend"] = d["ScheduledDay"].dt.hour
    d["M"] = (d["Gender"] == "M").astype(int)
    d["handcap_bin"] = (d["Handcap"] > 0).astype(int)  # deficiência: 0-4 vira sim/não
    return d


def ic_proporcao(faltas, n):
    """Intervalo de confiança de 95% (normal) para uma proporção."""
    p = faltas / n
    m = 1.96 * np.sqrt(p * (1 - p) / n)
    return p, max(p - m, 0), min(p + m, 1)


# ---------------------------------------------------------------- PP1: perfis
def perfis(d: pd.DataFrame):
    g = d.groupby("PatientId")
    P = pd.DataFrame({
        "idade": g.Age.mean(), "masc": g.M.max(), "bolsa": g.Scholarship.max(),
        "hip": g.Hipertensao.max(), "dia": g.Diabetes.max(), "alc": g.Alcoholism.max(),
        "defic": g.handcap_bin.max(), "n_cons": g.size(), "n_faltas": g.falta.sum()})
    feats = ["idade", "masc", "bolsa", "hip", "dia", "alc", "defic"]
    X = StandardScaler().fit_transform(P[feats])   # padroniza: idade não domina as binárias
    rng = np.random.RandomState(SEMENTE)
    amostra = rng.choice(len(P), 10000, replace=False)

    # cotovelo e silhueta (k de 2 a 10)
    linhas = []
    for k in range(2, 11):
        km = KMeans(k, n_init=10, random_state=SEMENTE).fit(X)
        sil = silhouette_score(X[amostra], km.labels_[amostra])
        linhas.append({"k": k, "wcss": km.inertia_, "silhueta": sil})
        log("k =", k, "silhueta", round(sil, 3))
    pd.DataFrame(linhas).to_csv(SAIDA / "perfis_k.csv", index=False)

    # modelo final: k = 6
    K = 6
    km = KMeans(K, n_init=10, random_state=SEMENTE).fit(X)
    P["c"] = km.labels_
    sil6 = silhouette_score(X[amostra], km.labels_[amostra])
    t = P.groupby("c").agg(pacientes=("idade", "size"), idade=("idade", "mean"),
                           masc=("masc", "mean"), bolsa=("bolsa", "mean"), hip=("hip", "mean"),
                           dia=("dia", "mean"), alc=("alc", "mean"), defic=("defic", "mean"),
                           consultas=("n_cons", "sum"), faltas=("n_faltas", "sum"))
    ordem = t.sort_values("pacientes", ascending=False).index.tolist()
    mapa = {o: i + 1 for i, o in enumerate(ordem)}          # G1 = maior grupo
    P["grupo"] = P.c.map(mapa)
    t.index = t.index.map(mapa)
    t = t.sort_index()
    ics = [ic_proporcao(r.faltas, r.consultas) for r in t.itertuples()]
    t["taxa_falta"] = [i[0] * 100 for i in ics]
    t["ic_inf"] = [i[1] * 100 for i in ics]
    t["ic_sup"] = [i[2] * 100 for i in ics]
    t["pct_pac"] = t.pacientes / len(P) * 100
    t.index.name = "grupo"
    t.round(4).to_csv(SAIDA / "perfis_grupos.csv")

    chi2, p, dof, _ = chi2_contingency(
        np.array([[r.faltas, r.consultas - r.faltas] for r in t.itertuples()]))

    # PCA (amostra de 8000 pacientes para o gráfico)
    pca = PCA(2, random_state=SEMENTE).fit(X)
    Z = pca.transform(X)
    s = rng.choice(len(P), 8000, replace=False)
    pd.DataFrame({"cp1": Z[s, 0], "cp2": Z[s, 1], "grupo": P.grupo.values[s]}) \
        .round(4).to_csv(SAIDA / "perfis_pca.csv", index=False)

    # estabilidade: o KMeans com outras sementes forma os mesmos grupos?
    aris = []
    for sem in range(1, 11):
        outro = KMeans(K, n_init=10, random_state=sem).fit(X)
        aris.append(adjusted_rand_score(km.labels_, outro.labels_))
    log("estabilidade ARI", np.round(aris, 3))

    # robustez com outros algoritmos (amostra, por custo)
    sa = rng.choice(len(P), 10000, replace=False)
    lk = km.labels_[sa]
    ward = AgglomerativeClustering(K, linkage="ward").fit(X[sa])
    meta = {
        "pacientes": int(len(P)), "silhueta_k6": float(sil6),
        "qui2": float(chi2), "p_valor": float(p), "gl": int(dof),
        "variancia_cp1": float(pca.explained_variance_ratio_[0]),
        "variancia_cp2": float(pca.explained_variance_ratio_[1]),
        "estabilidade_ari_media": float(np.mean(aris)),
        "estabilidade_ari_min": float(np.min(aris)),
        "ward_ari": float(adjusted_rand_score(lk, ward.labels_)),
        "ward_silhueta": float(silhouette_score(X[sa], ward.labels_)),
        "taxa_geral": float(d.falta.mean() * 100),
    }
    try:  # K-Prototypes é opcional (pip install kmodes)
        from kmodes.kprototypes import KPrototypes
        Ps = P.iloc[sa][feats].copy()
        kp = KPrototypes(n_clusters=K, init="Cao", n_init=1, random_state=SEMENTE, n_jobs=1)
        lab = kp.fit_predict(Ps.values.astype(object), categorical=[1, 2, 3, 4, 5, 6])
        meta["kprototypes_ari"] = float(adjusted_rand_score(lk, lab))
    except Exception as e:  # noqa: BLE001
        log("K-Prototypes não executado:", e)
    json.dump(meta, open(SAIDA / "perfis_meta.json", "w"), indent=1)
    log("perfis ok")


# ---------------------------------------------------------------- PP2: previsão
def previsao(d: pd.DataFrame):
    d = d[d.lead >= 0].copy().reset_index(drop=True)   # remove 5 consultas anteriores ao agendamento
    # histórico do paciente: só consultas cujo dia já tinha passado no agendamento (sem vazamento)
    d["hist_n"] = 0
    d["hist_falta"] = 0
    for _, gdf in d.groupby("PatientId"):
        if len(gdf) == 1:
            continue
        ap = gdf.AppointmentDay.dt.normalize().values
        ordem = np.argsort(ap)
        aps = ap[ordem]
        cf = np.concatenate([[0], np.cumsum(gdf.falta.values[ordem])])
        k = np.searchsorted(aps, gdf.sched_date.values, side="left")
        d.loc[gdf.index, "hist_n"] = k
        d.loc[gdf.index, "hist_falta"] = cf[k]
    d["hist_taxa"] = np.where(d.hist_n > 0, d.hist_falta / d.hist_n.clip(lower=1), 0.0)

    num = ["Age", "lead", "hora_agend", "hist_n", "hist_falta", "hist_taxa"]
    binar = ["M", "Scholarship", "Hipertensao", "Diabetes", "Alcoholism", "handcap_bin", "SMS_received"]
    X = d[num + binar + ["dow", "Neighbourhood"]].copy()
    y, grp = d.falta.values, d.PatientId.values

    # treino/teste separados POR PACIENTE (o mesmo paciente nunca está nos dois)
    tr, te = next(GroupShuffleSplit(1, test_size=0.2, random_state=SEMENTE).split(X, y, grp))
    Xtr, Xte, ytr, yte, gtr = X.iloc[tr], X.iloc[te], y[tr], y[te], grp[tr]
    assert not (set(grp[tr]) & set(grp[te]))
    log("treino", len(tr), "teste", len(te))

    def preparo():
        return ColumnTransformer([
            ("num", StandardScaler(), num),
            ("bin", "passthrough", binar),
            ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["dow"]),
            ("te", TargetEncoder(target_type="binary", random_state=SEMENTE), ["Neighbourhood"])])

    def montar(clf, smote):
        passos = [("prep", preparo())]
        if smote:                       # SMOTE só dentro do treino de cada divisão
            passos.append(("smote", SMOTE(random_state=SEMENTE)))
        passos.append(("clf", clf))
        return Pipeline(passos)

    gkf = GroupKFold(3)

    def cv(fabrica):
        aucs, f1s = [], []
        for a, b in gkf.split(Xtr, ytr, gtr):
            m = fabrica().fit(Xtr.iloc[a], ytr[a])
            p = m.predict_proba(Xtr.iloc[b])[:, 1]
            aucs.append(roc_auc_score(ytr[b], p))
            f1s.append(f1_score(ytr[b], (p >= .5).astype(int)))
        return float(np.mean(aucs)), float(np.mean(f1s))

    # ajuste de hiperparâmetros (profundidade) por validação cruzada agrupada, só no treino
    melhor_dt = max([4, 6, 8, 12], key=lambda p: cv(lambda: montar(
        DecisionTreeClassifier(max_depth=p, min_samples_leaf=50, random_state=SEMENTE), False))[0])
    melhor_rf = max([8, 12, 16], key=lambda p: cv(lambda: montar(
        RandomForestClassifier(150, max_depth=p, min_samples_leaf=20, n_jobs=2,
                               random_state=SEMENTE), False))[0])
    log("profundidade escolhida: DT", melhor_dt, "RF", melhor_rf)

    cfg = {
        "Regressão Logística": (lambda: LogisticRegression(max_iter=2000), False),
        "Regressão Logística + SMOTE": (lambda: LogisticRegression(max_iter=2000), True),
        "Árvore de Decisão": (lambda: DecisionTreeClassifier(
            max_depth=melhor_dt, min_samples_leaf=50, random_state=SEMENTE), False),
        "Árvore de Decisão + SMOTE": (lambda: DecisionTreeClassifier(
            max_depth=melhor_dt, min_samples_leaf=50, random_state=SEMENTE), True),
        "Random Forest": (lambda: RandomForestClassifier(
            300, max_depth=melhor_rf, min_samples_leaf=20, n_jobs=2, random_state=SEMENTE), False),
        "Random Forest + SMOTE": (lambda: RandomForestClassifier(
            300, max_depth=melhor_rf, min_samples_leaf=20, n_jobs=2, random_state=SEMENTE), True),
    }
    # modelo final = maior F1 da classe "falta" na validação cruzada (nunca no teste)
    cvres = {n: cv(lambda c=c, s=s: montar(c(), s)) for n, (c, s) in cfg.items()}
    final = max(cvres, key=lambda n: cvres[n][1])
    log("modelo final:", final)

    linhas, modelos, probas = [], {}, {}
    for n, (c, s) in cfg.items():
        m = montar(c(), s).fit(Xtr, ytr)
        modelos[n] = m
        pp = m.predict_proba(Xte)[:, 1]
        probas[n] = pp
        yp = (pp >= .5).astype(int)
        # treino (para checar overfitting), sem reamostrar
        pt = m.predict_proba(Xtr)[:, 1]
        linhas.append({
            "modelo": n, "final": int(n == final),
            "auc": roc_auc_score(yte, pp),
            "recall_falta": recall_score(yte, yp), "precisao_falta": precision_score(yte, yp, zero_division=0),
            "f1_falta": f1_score(yte, yp), "acuracia": accuracy_score(yte, yp),
            "auc_treino": roc_auc_score(ytr, pt),
            "f1_falta_treino": f1_score(ytr, (pt >= .5).astype(int)),
            "cv_auc": cvres[n][0], "cv_f1_falta": cvres[n][1]})
        log(n, "AUC teste", round(linhas[-1]["auc"], 4))
    pd.DataFrame(linhas).round(4).to_csv(SAIDA / "modelos_teste.csv", index=False)

    # margem de erro do modelo final: bootstrap por paciente no conjunto de teste
    mf, pf = modelos[final], probas[final]
    gte = grp[te]
    pacientes = np.unique(gte)
    por_pac = {p: np.where(gte == p)[0] for p in pacientes}
    rng = np.random.RandomState(SEMENTE)
    res = {"auc": [], "recall_falta": [], "precisao_falta": [], "f1_falta": []}
    for _ in range(300):
        sel = np.concatenate([por_pac[p] for p in rng.choice(pacientes, len(pacientes))])
        yb, pb = yte[sel], pf[sel]
        yp = (pb >= .5).astype(int)
        res["auc"].append(roc_auc_score(yb, pb))
        res["recall_falta"].append(recall_score(yb, yp))
        res["precisao_falta"].append(precision_score(yb, yp, zero_division=0))
        res["f1_falta"].append(f1_score(yb, yp))
    ic = {k: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for k, v in res.items()}
    yp = (pf >= .5).astype(int)
    tn = int(((yte == 0) & (yp == 0)).sum()); fp = int(((yte == 0) & (yp == 1)).sum())
    fn = int(((yte == 1) & (yp == 0)).sum()); tp = int(((yte == 1) & (yp == 1)).sum())
    json.dump({
        "modelo_final": final, "ic95_bootstrap_por_paciente": ic,
        "matriz_confusao": {"verdadeiro_negativo": tn, "falso_positivo": fp,
                            "falso_negativo": fn, "verdadeiro_positivo": tp},
        "n_treino": int(len(tr)), "n_teste": int(len(te)),
        "pacientes_treino": int(len(set(grp[tr]))), "pacientes_teste": int(len(pacientes)),
        "taxa_falta_teste": float(yte.mean() * 100),
        "profundidade_dt": melhor_dt, "profundidade_rf": melhor_rf,
    }, open(SAIDA / "modelo_final.json", "w"), indent=1, ensure_ascii=False)
    fpr, tpr, _ = roc_curve(yte, pf)
    passo = max(len(fpr) // 300, 1)
    pd.DataFrame({"fpr": fpr[::passo], "tpr": tpr[::passo]}).round(4).to_csv(SAIDA / "roc_final.csv", index=False)

    # SHAP só no modelo final
    import shap
    pre, rf = mf.named_steps["prep"], mf.named_steps["clf"]
    nomes = {"Age": "Idade", "lead": "Antecedência (dias)", "hora_agend": "Hora do agendamento",
             "hist_n": "Consultas anteriores", "hist_falta": "Faltas anteriores",
             "hist_taxa": "Taxa de faltas anterior", "M": "Sexo masculino",
             "Scholarship": "Bolsa Família", "Hipertensao": "Hipertensão", "Diabetes": "Diabetes",
             "Alcoholism": "Alcoolismo", "handcap_bin": "Deficiência", "SMS_received": "SMS recebido",
             "Neighbourhood": "Bairro"}
    cols = num + binar + [f"Dia da semana {c}" for c in pre.named_transformers_["oh"].categories_[0]] + ["Neighbourhood"]
    cols = [nomes.get(c, c) for c in cols]
    Xt = pd.DataFrame(pre.transform(Xte), columns=cols)
    idx = np.random.RandomState(SEMENTE).choice(len(Xt), 2000, replace=False)
    sv = shap.TreeExplainer(rf).shap_values(Xt.iloc[idx], check_additivity=False)
    sv = sv[:, :, 1] if np.ndim(sv) == 3 else (sv[1] if isinstance(sv, list) else sv)
    imp = pd.Series(np.abs(sv).mean(0), index=cols).sort_values(ascending=False)
    imp.rename("importancia_shap").round(5).to_csv(SAIDA / "shap_importancia.csv", index_label="variavel")
    log("SHAP top:", imp.head(3).round(4).to_dict())
    log("previsao ok")


if __name__ == "__main__":
    base = carregar()
    log("linhas", len(base), "taxa de falta", round(base.falta.mean() * 100, 2))
    perfis(base)
    previsao(base)
    log("FIM")
