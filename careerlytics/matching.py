from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from . import config
from .data_gen import FAMILY
from .skills import SKILL_INDEX, SKILL_LIST

FEATURES = ["skill_match", "core_match", "weighted_match", "exp_match", "edu_match", "project_match", "role_match", "breadth"]
FEATURE_LABELS = {
    "skill_match": "Skill coverage", "core_match": "Core-skill coverage", "weighted_match": "Demand-weighted coverage",
    "exp_match": "Experience fit", "edu_match": "Education fit", "project_match": "Resume-text similarity (TF-IDF)",
    "role_match": "Role fit", "breadth": "Extra skills (breadth)",
}
EDU_RANK = {"Diploma": 1, "Any": 0, "Bachelor": 2, "Master": 3, "PhD": 4}
SIM_SCALE = 0.20  

class Matcher:
    def __init__(self, jobs: pd.DataFrame, job_skills: pd.DataFrame):
        self.jobs = jobs.reset_index(drop=True)
        n, v = len(self.jobs), len(SKILL_LIST)
        row = {jid: i for i, jid in enumerate(self.jobs["job_id"])}
        self.J = np.zeros((n, v), dtype=bool)
        self.Jc = np.zeros((n, v), dtype=bool)
        for jid, skill, core in job_skills.itertuples(index=False):
            if jid in row and skill in SKILL_INDEX:
                self.J[row[jid], SKILL_INDEX[skill]] = True
                if core:
                    self.Jc[row[jid], SKILL_INDEX[skill]] = True
        self.demand = self.J.mean(0)                      
        self.w = 0.5 + self.demand                        
        self.exp_min = self.jobs["exp_min"].to_numpy(float)
        self.exp_max = self.jobs["exp_max"].to_numpy(float)
        self.edu_req = self.jobs["education"].map(EDU_RANK).fillna(2).to_numpy(float)
        self.roles = self.jobs["role"].to_numpy()
        self.fam = np.array([FAMILY.get(r) for r in self.roles])
        self.tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=2, sublinear_tf=True)
        self.D = self.tfidf.fit_transform(self.jobs["description"])

    #helpers
    @staticmethod
    def vec(skills) -> np.ndarray:
        v = np.zeros(len(SKILL_LIST), dtype=bool)
        for s in skills:
            if s in SKILL_INDEX:
                v[SKILL_INDEX[s]] = True
        return v

    def sim(self, text: str) -> np.ndarray:
        return (self.D @ self.tfidf.transform([text]).T).toarray().ravel()

    def role_scores(self, targets) -> np.ndarray:
        if not targets:
            return np.full(len(self.jobs), 0.5)
        best = np.zeros(len(self.jobs))
        for t in targets:
            s = np.where(self.roles == t, 1.0, np.where(self.fam == FAMILY.get(t), 0.6, 0.0))
            best = np.maximum(best, s)
        return best

    def loc_scores(self, locations) -> np.ndarray:
        if not locations:
            return np.ones(len(self.jobs))
        loc = self.jobs["location"].to_numpy()
        return np.where(np.isin(loc, list(locations)), 1.0, np.where(loc == "Remote", 0.8, 0.2))

    #features
    def features(self, cvec, exp, edu, sim, targets) -> np.ndarray:
        inter = self.J & cvec
        req = np.maximum(self.J.sum(1), 1)
        skill = inter.sum(1) / req
        core_req = self.Jc.sum(1)
        core = np.where(core_req > 0, (self.Jc & cvec).sum(1) / np.maximum(core_req, 1), skill)
        weighted = (inter * self.w).sum(1) / np.maximum((self.J * self.w).sum(1), 1e-9)
        expm = np.where(self.exp_min <= exp, 1.0, np.clip(1 - (self.exp_min - exp) / np.maximum(self.exp_min, 1), 0, 1))
        expm = np.where(exp > self.exp_max + 3, expm * 0.8, expm)
        edum = np.where(edu >= self.edu_req, 1.0, np.where(edu == self.edu_req - 1, 0.5, 0.0))
        proj = np.clip(sim / SIM_SCALE, 0, 1)
        breadth = np.clip((cvec & ~self.J).sum(1) / 10, 0, 1)
        return np.column_stack([skill, core, weighted, expm, edum, proj, self.role_scores(targets), breadth])

    def profile_features(self, p) -> np.ndarray:
        return self.features(self.vec(p.skills), p.experience, p.education_level, self.sim(p.match_text()), p.targets)

    #ranking
    def rank(self, p, model, with_lists: bool = True) -> pd.DataFrame:
        F = self.profile_features(p)
        prob = np.clip(model.predict_proba(F)[:, 1], 0.02, 0.98)  
        cw = config.SCORE_WEIGHTS
        F_ = dict(zip(FEATURES, F.T))
        loc = self.loc_scores(p.locations)
        score = cw["ml"] * prob + cw["skill"] * F_["skill_match"] + cw["role"] * F_["role_match"] + cw["location"] * loc + cw["experience"] * F_["exp_match"] + cw["text"] * F_["project_match"]
        out = self.jobs.drop(columns=["description"]).copy()
        for name, col in F_.items():
            out[name] = col
        out["loc_match"] = loc
        out["ml_prob"] = prob
        out["score"] = np.clip(score, 0, 1)
        out["tier"] = pd.cut(out["score"], [-1] + [t for _, t in reversed(config.TIERS)][1:] + [2],
                             labels=[n for n, _ in reversed(config.TIERS)]).astype(str)
        if with_lists:
            cvec = self.vec(p.skills)
            names = np.array(SKILL_LIST)
            out["matched"] = [list(names[r]) for r in (self.J & cvec)]
            out["missing"] = [list(names[r]) for r in (self.J & ~cvec)]
            out["missing_core"] = [list(names[r]) for r in (self.Jc & ~cvec)]
        return out.sort_values("score", ascending=False).reset_index(drop=True)

    def simulate(self, p, model, extra_skills, top: int = 20) -> float:
        """Average score of the user's top-N jobs if they learned `extra_skills` (what-if analysis)."""
        ranked = self.rank(p.with_skills(extra_skills), model, with_lists=False)
        return float(ranked["score"].head(top).mean())

    def description(self, job_id: int) -> str:
        return str(self.jobs.loc[self.jobs["job_id"] == job_id, "description"].iloc[0])


def explain(row: pd.Series) -> pd.DataFrame:
    cw = config.SCORE_WEIGHTS
    parts = [
        ("ML match probability", cw["ml"], row["ml_prob"]),
        ("Skill coverage", cw["skill"], row["skill_match"]),
        ("Role preference", cw["role"], row["role_match"]),
        ("Location preference", cw["location"], row["loc_match"]),
        ("Experience fit", cw["experience"], row["exp_match"]),
        ("Resume-text similarity", cw["text"], row["project_match"]),
    ]
    return pd.DataFrame([{"component": n, "weight": w, "value": float(v), "points": w * float(v) * 100} for n, w, v in parts])
