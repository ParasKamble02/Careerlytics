from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from . import config, gap as gapmod, ml_model
from .bootstrap import ensure_seeded
from .db import Database
from .matching import Matcher
from .profile import Profile

@st.cache_resource(show_spinner="Preparing the job-market database...")
def get_db() -> Database:
    db = Database()
    ensure_seeded(db)
    return db

@st.cache_resource(show_spinner="Indexing job postings...")
def get_matcher(_db: Database, version: tuple) -> Matcher:
    return Matcher(_db.jobs(), _db.job_skills())

@st.cache_resource(show_spinner="Training the match model (first run only)...")
def get_model(_matcher: Matcher, version: tuple) -> dict:
    return ml_model.load_or_train(_matcher)

@st.cache_data(show_spinner=False)
def get_market(_db: Database, version: tuple):
    return _db.jobs(), _db.job_skills()

@st.cache_data(show_spinner=False)
def get_ranked(_matcher: Matcher, _model, version: tuple, profile_key: str) -> pd.DataFrame:
    import json
    return _matcher.rank(Profile.from_dict(json.loads(profile_key)), _model)

@st.cache_data(show_spinner="Analysing your skill gaps...")
def get_gap(_matcher: Matcher, _model, _jobs, _js, version: tuple, profile_key: str) -> pd.DataFrame:
    import json
    p = Profile.from_dict(json.loads(profile_key))
    ranked = _matcher.rank(p, _model)
    return gapmod.skill_gap(_matcher, p, ranked, _jobs, _js, model=_model)

@dataclass
class Ctx:
    db: Database
    matcher: Matcher
    model: object
    metrics: dict
    jobs: pd.DataFrame
    js: pd.DataFrame
    profile: Profile
    ranked: pd.DataFrame
    version: tuple
    user: dict
    has_resume: bool

    def gap(self) -> pd.DataFrame:
        if not self.has_resume:
            return pd.DataFrame()
        return get_gap(self.matcher, self.model, self.jobs, self.js, self.version, self.profile.key())

def load_ctx() -> Ctx:
    db = get_db()
    version = db.version()
    matcher = get_matcher(db, version)
    bundle = get_model(matcher, (config.SEED_JOBS,))
    jobs, js = get_market(db, version)
    pdict = st.session_state.get("profile")
    if pdict:
        profile = Profile.from_dict(pdict)
        ranked = get_ranked(matcher, bundle["model"], version, profile.key())
    else:
        profile, ranked = Profile(), pd.DataFrame()
    return Ctx(db, matcher, bundle["model"], bundle["metrics"], jobs, js, profile, ranked, version,
               st.session_state["user"], bool(pdict))

def set_profile(ctx: Ctx, p: Profile) -> None:
    st.session_state["profile"] = p.to_dict()
    ctx.db.save_profile(ctx.user["id"], p)
