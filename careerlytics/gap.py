from __future__ import annotations

import numpy as np
import pandas as pd

from . import analytics
from .skills import CATEGORY, PREREQS, SKILL_INDEX, SKILL_LIST, WEEKS

HIGH, MEDIUM = 60, 30

def level(score: float) -> str:
    return "High" if score >= HIGH else "Medium" if score >= MEDIUM else "Low"

def skill_gap(matcher, profile, ranked, jobs, js, top_k: int = 50, model=None, lift_for: int = 10) -> pd.DataFrame:
    have = set(profile.skills)
    demand = analytics.skill_demand(jobs, js, role=profile.targets or None).set_index("skill")["share"]
    top = ranked.head(top_k)
    rows = np.flatnonzero(matcher.jobs["job_id"].isin(top["job_id"]).to_numpy())
    weights = top.set_index("job_id").loc[matcher.jobs["job_id"].iloc[rows], "score"].to_numpy()
    relevance = (matcher.J[rows] * weights[:, None]).sum(0) / max(weights.sum(), 1e-9)
    trend = analytics.demand_change(jobs, js).set_index("skill")["delta"]
    out = []
    for skill in SKILL_LIST:
        if skill in have:
            continue
        d, r = float(demand.get(skill, 0)), float(relevance[SKILL_INDEX[skill]])
        if d <= 0 and r <= 0:
            continue
        boost = 1 + float(np.clip(trend.get(skill, 0) * 3, 0, 0.3))
        out.append({"skill": skill, "category": CATEGORY[skill], "market_demand": d, "job_relevance": r, "trend": float(trend.get(skill, 0)), "raw": d * r * boost})
    df = pd.DataFrame(out)
    if df.empty:
        return df.assign(priority=[], level=[], lift=[])
    df["priority"] = (100 * df["raw"] / df["raw"].max()).round(1)
    df["level"] = df["priority"].map(level)
    df = df.sort_values("priority", ascending=False).drop(columns="raw").reset_index(drop=True)
    df["lift"] = np.nan
    if model is not None:
        base = matcher.simulate(profile, model, [])
        for i in range(min(lift_for, len(df))):
            df.loc[i, "lift"] = (matcher.simulate(profile, model, [df.loc[i, "skill"]]) - base) * 100
    return df

def roadmap(gap: pd.DataFrame, profile, max_items: int = 8) -> pd.DataFrame:
    have, order = set(profile.skills), []

    def add(skill, reason):
        if skill not in order and skill not in have:
            for pre in PREREQS.get(skill, []):
                add(pre, f"prerequisite for {skill}")
            order.append(skill)
            reasons[skill] = reason

    reasons: dict[str, str] = {}
    pr = gap.set_index("skill")["priority"].to_dict() if not gap.empty else {}
    for s in gap["skill"].head(max_items) if not gap.empty else []:
        add(s, "high market demand" if pr.get(s, 0) >= HIGH else "relevant to your top matches")
    weeks = [WEEKS.get(CATEGORY[s], 3) for s in order]
    return pd.DataFrame({
        "step": range(1, len(order) + 1), "skill": order, "category": [CATEGORY[s] for s in order],
        "why": [reasons[s] for s in order], "weeks": weeks, "cumulative_weeks": np.cumsum(weeks),
        "priority": [pr.get(s, np.nan) for s in order],
    })
