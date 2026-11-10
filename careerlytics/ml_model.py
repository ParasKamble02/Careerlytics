from __future__ import annotations

import json

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

from . import config
from .data_gen import ROLE_NAMES, ROLE_WEIGHTS
from .matching import FEATURES, Matcher
from .skills import SKILL_LIST

RUBRIC = dict(core_match=4.2, skill_match=1.8, weighted_match=1.0, exp_match=1.2, edu_match=0.6, project_match=0.7, role_match=0.8, breadth=0.4)
POSITIVE_SHARE = 0.34

def build_training_set(matcher: Matcher, n_candidates: int = 2500, pairs_per: int = 12, seed: int = config.RANDOM_SEED):
    rng = np.random.default_rng(seed)
    role_share = {r: matcher.J[matcher.roles == r].mean(0) for r in ROLE_NAMES}
    texts, cands = [], []
    for _ in range(n_candidates):
        role = str(rng.choice(ROLE_NAMES, p=ROLE_WEIGHTS))
        share = role_share[role]
        keep = rng.beta(2.2, 1.6)
        p_i = np.where(share > 0.02, np.clip(keep + 0.25 * (share - 0.3), 0.02, 0.98), 0.0)
        cvec = rng.random(len(SKILL_LIST)) < p_i
        cvec |= rng.random(len(SKILL_LIST)) < (2 / len(SKILL_LIST))        # a few unrelated skills
        skills = [SKILL_LIST[i] for i in np.flatnonzero(cvec)]
        texts.append(" ".join(skills + [f"{role} project using " + " ".join(skills[:3])]))
        cands.append((role, cvec, float(rng.choice([0, 0, 0, 1, 1, 2, 3, 4, 6])), int(rng.choice([2, 2, 2, 3]))))
    sims = (matcher.tfidf.transform(texts) @ matcher.D.T).toarray()
    by_role = {r: np.flatnonzero(matcher.roles == r) for r in ROLE_NAMES}
    X = []
    for (role, cvec, exp, edu), sim in zip(cands, sims):
        F = matcher.features(cvec, exp, edu, sim, [role])
        idx = np.concatenate([rng.choice(by_role[role], int(pairs_per * .6)), rng.choice(len(matcher.jobs), pairs_per - int(pairs_per * .6))])
        X.append(F[idx])
    X = np.vstack(X)
    latent = sum(RUBRIC[f] * X[:, i] for i, f in enumerate(FEATURES))
    f = {name: X[:, i] for i, name in enumerate(FEATURES)}
    latent += 2.0 * (f["core_match"] >= 0.8) - 2.5 * (f["core_match"] < 0.4) - 1.5 * (f["exp_match"] < 0.5) + rng.normal(0, 0.8, len(X))
    y = (latent > np.quantile(latent, 1 - POSITIVE_SHARE)).astype(int)
    return X, y

def train(matcher: Matcher) -> dict:
    X, y = build_training_set(matcher)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=config.RANDOM_SEED, stratify=y)
    rf = RandomForestClassifier(n_estimators=250, max_depth=10, min_samples_leaf=5, n_jobs=-1, random_state=config.RANDOM_SEED).fit(Xtr, ytr)
    lr = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
    pr = rf.predict_proba(Xte)[:, 1]
    metrics = {
        "samples": int(len(X)), "positive_share": round(float(y.mean()), 3),
        "rf_accuracy": round(accuracy_score(yte, pr > .5), 3), "rf_f1": round(f1_score(yte, pr > .5), 3),
        "rf_auc": round(roc_auc_score(yte, pr), 3), "logreg_auc": round(roc_auc_score(yte, lr.predict_proba(Xte)[:, 1]), 3),
        "importances": {f: round(float(v), 3) for f, v in sorted(zip(FEATURES, rf.feature_importances_), key=lambda t: -t[1])},
        "features": FEATURES,
    }
    config.MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": rf, "metrics": metrics}, config.MODEL_PATH)
    return {"model": rf, "metrics": metrics}

def load_or_train(matcher: Matcher) -> dict:
    if config.MODEL_PATH.exists():
        try:
            bundle = joblib.load(config.MODEL_PATH)
            if bundle["metrics"].get("features") == FEATURES:
                return bundle
        except Exception:
            pass
    return train(matcher)

if __name__ == "__main__":  
    from .bootstrap import build_matcher
    print(json.dumps(train(build_matcher())["metrics"], indent=2))
