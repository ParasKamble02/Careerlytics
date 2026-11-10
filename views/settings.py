from __future__ import annotations

import streamlit as st

from careerlytics import bootstrap, data_gen, ml_model, service, ui
from careerlytics.skills import SKILL_LIST
from careerlytics.state import set_profile

def render(ctx) -> None:
    p = ctx.profile
    ui.page_title("Settings")
    with st.container(key="card_set_profile"):
        ui.card_header("Career profile", sub="The target role drives Job Market, Job Matcher and Skill Gap")
        c1, c2 = st.columns(2)
        name = c1.text_input("Name", p.name)
        cur = p.targets[0] if p.targets else None
        target = c1.selectbox("Target role", data_gen.ROLE_NAMES, index=data_gen.ROLE_NAMES.index(cur) if cur in data_gen.ROLE_NAMES else 0)
        locs = c1.multiselect("Preferred locations (empty = anywhere)", data_gen.LOCATIONS, default=p.locations)
        exp = c2.number_input("Years of experience", 0.0, 30.0, float(p.experience), 0.5)
        edu_opts = {"Diploma": 1, "Bachelor": 2, "Master": 3, "PhD": 4}
        edu = c2.selectbox("Highest education", list(edu_opts), index=list(edu_opts).index(p.education_label) if p.education_label in edu_opts else 1)
        skills = c2.multiselect("Skills (add or remove)", SKILL_LIST, default=list(p.skills))
        if st.button("Save profile", type="primary", key="save_profile"):
            d = p.to_dict()
            d.update(name=name, targets=[target], locations=locs, experience=exp, education_label=edu, education_level=edu_opts[edu], is_demo=p.is_demo)
            d["skills"] = {s: p.skills.get(s, 60) for s in skills}
            set_profile(ctx, service.rescore(type(p).from_dict(d), ctx.jobs, ctx.js))
            st.success("Profile saved - all pages now use the new settings.")
            st.rerun()
