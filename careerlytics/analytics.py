from __future__ import annotations

import numpy as np
import pandas as pd

def _ids(jobs, role=None, location=None, since=None, until=None):
    m = pd.Series(True, index=jobs.index)
    if role:
        m &= jobs["role"].isin([role] if isinstance(role, str) else role)
    if location:
        m &= jobs["location"].isin([location] if isinstance(location, str) else location)
    if since is not None:
        m &= jobs["posted_date"] >= pd.Timestamp(since)
    if until is not None:
        m &= jobs["posted_date"] <= pd.Timestamp(until)
    return jobs.loc[m, "job_id"]

filter_ids = _ids

def skill_demand(jobs, js, **filters) -> pd.DataFrame:
    """% of (filtered) postings that require each skill."""
    ids = _ids(jobs, **filters)
    n = max(len(ids), 1)
    d = js[js["job_id"].isin(ids)].groupby("skill").size().rename("postings").reset_index()
    d["share"] = d["postings"] / n
    return d.sort_values("share", ascending=False).reset_index(drop=True)

def demand_change(jobs, js, window: int = 30) -> pd.DataFrame:
    """Skill demand in the last `window` days vs the `window` days before that."""
    end = jobs["posted_date"].max()
    now = skill_demand(jobs, js, since=end - pd.Timedelta(days=window - 1)).set_index("skill")["share"]
    prev = skill_demand(jobs, js, since=end - pd.Timedelta(days=2 * window - 1), until=end - pd.Timedelta(days=window)).set_index("skill")["share"]
    out = pd.concat([now.rename("now"), prev.rename("prev")], axis=1).fillna(0)
    out["delta"] = out["now"] - out["prev"]
    return out.sort_values("delta", ascending=False).reset_index(names="skill")

def distribution(jobs, col: str) -> pd.DataFrame:
    d = jobs[col].value_counts().rename_axis(col).reset_index(name="jobs")
    d["share"] = d["jobs"] / d["jobs"].sum()
    return d

def salary_stats(jobs, by: str) -> pd.DataFrame:
    g = jobs.groupby(by)["salary_lpa"]
    return pd.DataFrame({"jobs": g.size(), "mean": g.mean(), "median": g.median(), "p25": g.quantile(.25), "p75": g.quantile(.75)}).reset_index().sort_values("median", ascending=False)

def salary_by_experience(jobs) -> pd.DataFrame:
    band = pd.cut(jobs["exp_min"], [-1, 0, 2, 4, 99], labels=["Fresher (0)", "1-2 yrs", "3-4 yrs", "5+ yrs"])
    return jobs.assign(band=band).groupby("band", observed=True)["salary_lpa"].agg(["size", "mean", "median"]).reset_index()

def skills_vs_salary(jobs, js) -> tuple[pd.DataFrame, float]:
    n = js.groupby("job_id").size().rename("n_skills")
    d = jobs.merge(n, left_on="job_id", right_index=True)[["job_id", "role", "salary_lpa", "n_skills"]]
    return d, float(d["n_skills"].corr(d["salary_lpa"]))

def weekly_postings(jobs) -> pd.DataFrame:
    s = jobs.set_index("posted_date").resample("W").size().rename("jobs").reset_index()
    return s.iloc[1:] if len(s) > 2 else s  

def daily_compare(jobs, days: int = 12, role=None) -> dict:
    j = jobs if role is None else jobs[jobs["role"].isin(role)]
    end = jobs["posted_date"].max().normalize()
    idx_now = pd.date_range(end - pd.Timedelta(days=days - 1), end)
    idx_prev = idx_now - pd.Timedelta(days=days)
    c = j.groupby(j["posted_date"].dt.normalize()).size()
    now = c.reindex(idx_now, fill_value=0).to_numpy()
    prev = c.reindex(idx_prev, fill_value=0).to_numpy()
    pct = (now.sum() - prev.sum()) / max(prev.sum(), 1) * 100
    return {"dates": idx_now, "now": now, "prev": prev, "total_now": int(now.sum()), "total_prev": int(prev.sum()), "pct": float(pct)}

def skill_trend(jobs, js, skills, freq_days: int = 14) -> pd.DataFrame:
    end = jobs["posted_date"].max().normalize()
    rows = []
    for k in range(6):
        hi, lo = end - pd.Timedelta(days=k * freq_days), end - pd.Timedelta(days=(k + 1) * freq_days - 1)
        d = skill_demand(jobs, js, since=lo, until=hi).set_index("skill")["share"]
        for s in skills:
            rows.append({"period_end": hi, "skill": s, "share": float(d.get(s, 0))})
    return pd.DataFrame(rows).sort_values("period_end")

def market_summary(jobs, js) -> dict:
    sd = skill_demand(jobs, js)
    return {
        "jobs": len(jobs), "companies": jobs["company"].nunique(), "median_salary": float(jobs["salary_lpa"].median()),
        "top_role": jobs["role"].value_counts().idxmax(), "top_location": jobs["location"].value_counts().idxmax(),
        "top_skill": sd.iloc[0]["skill"], "top_skill_share": float(sd.iloc[0]["share"]),
    }

def skill_requirements(jobs, js) -> pd.DataFrame:
    """For the given postings: share of postings asking for each skill and how often it is a must-have (core)."""
    n = max(len(jobs), 1)
    d = js[js["job_id"].isin(jobs["job_id"])]
    g = d.groupby("skill").agg(postings=("job_id", "size"), core=("is_core", "sum"))
    g["share"] = g["postings"] / n
    g["core_share"] = g["core"] / g["postings"]
    return g.reset_index().sort_values("share", ascending=False).reset_index(drop=True)
