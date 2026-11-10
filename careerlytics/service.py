from __future__ import annotations

import numpy as np
import pandas as pd

from . import analytics, nlp
from .data_gen import ROLE_NAMES
from .matching import Matcher
from .profile import Profile

def infer_targets(matcher: Matcher, skills, k: int = 2) -> list[str]:
    """Roles whose postings the resume covers best"""
    cvec = matcher.vec(skills)
    cov = (matcher.J & cvec).sum(1) / np.maximum(matcher.J.sum(1), 1)
    by_role = pd.Series(cov).groupby(matcher.roles).mean().sort_values(ascending=False)
    return list(by_role.index[:k])

def market_alignment(skills, jobs, js, top: int = 20) -> float:
    """Share of the demand carried by the 20 most requested skills that the resume covers."""
    sd = analytics.skill_demand(jobs, js).head(top)
    return float(sd.loc[sd["skill"].isin(skills), "share"].sum() / max(sd["share"].sum(), 1e-9))

def build_profile(text: str, matcher: Matcher, jobs, js, targets=None, locations=None, is_demo: bool = False) -> Profile:
    parsed = nlp.parse_resume(text)
    score, breakdown = nlp.score_resume(parsed, market_alignment(parsed["skills"], jobs, js))
    strengths, improvements = nlp.resume_feedback(parsed, breakdown)
    return Profile(
        name=parsed["name"], skills=parsed["skills"], experience=parsed["experience"],
        education_level=parsed["education_level"], education_label=parsed["education_label"],
        projects=parsed["projects"], projects_text=parsed["projects_text"],
        targets=list(targets) if targets else infer_targets(matcher, parsed["skills"]),
        locations=list(locations or []), resume_score=score, score_breakdown=breakdown,
        strengths=strengths, improvements=improvements, is_demo=is_demo,
    )

def rescore(profile: Profile, jobs, js) -> Profile:
    """Re-score after manual skill edits"""
    br = dict(profile.score_breakdown) or {}
    br["Skill breadth"] = round(25 * min(1, len(profile.skills) / 15), 1)
    br["Market alignment"] = round(20 * market_alignment(profile.skills, jobs, js), 1)
    d = profile.to_dict()
    d.update(resume_score=round(sum(br.values()), 1), score_breakdown=br)
    return Profile(**d)

def role_options() -> list[str]:
    return ROLE_NAMES
