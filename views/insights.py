from __future__ import annotations

import streamlit as st

from careerlytics import ui
from careerlytics.nav import go

def render(ctx) -> None:
    p = ctx.profile
    role = p.targets[0] if p.targets else "your target role"
    ui.page_title("Resume Insights")

    left, right = st.columns([1.3, 1])
    with left:
        with st.container(key="card_skills_ev"):
            ui.card_header("Resume Skills", sub="Evidence strength: mentions + use in projects / experience")
            top = sorted(p.skills.items(), key=lambda kv: -kv[1])[:14]
            ui.progress_rows([(s, v, f"{v}", None) for s, v in top])
            if not p.skills:
                st.caption("No known skills were detected.")
    with right:
        with st.container(key="card_score"):
            ui.card_header("Score breakdown", f"{p.resume_score:.0f}%", sub="Transparent, rule-based score (max 100)")
            maxes = {"Skill breadth": 25, "Market alignment": 20, "Projects": 15, "Education & experience": 15, "Quantified impact": 15, "Contact & links": 10}
            ui.progress_rows([(n, 100 * v / maxes.get(n, 1), f"{v:g}/{maxes.get(n, '')}", None) for n, v in p.score_breakdown.items()])

    s1, s2, s3 = st.columns(3)
    with s1:
        with st.container(key="card_strengths"):
            ui.card_header("Strengths")
            ui.html("".join(f'<div class="row"><span class="pdot" style="background:{ui.GREEN}"></span><div class="grow">{ui.esc(t)}</div></div>' for t in p.strengths)
                    or "<div class='c-sub'>-</div>")
    with s2:
        with st.container(key="card_improve"):
            ui.card_header("Improve")
            ui.html("".join(f'<div class="row"><span class="pdot" style="background:{ui.ORANGE}"></span><div class="grow">{ui.esc(t)}</div></div>' for t in p.improvements)
                    or "<div class='c-sub'>Nothing urgent - nice resume.</div>")
    with s3:
        with st.container(key="card_missing"):
            gap = ctx.gap()
            ui.card_header("Missing skills for your target", sub=role)
            if gap.empty:
                st.caption("No gaps found.")
            else:
                ui.html(ui.chips(gap["skill"].head(8), "miss"))
                st.button("Open skill-gap roadmap", key="vr_insights_gap", on_click=go, args=("Skill Gap & Roadmap",))

    with st.container(key="card_projects"):
        ui.card_header("Projects detected")
        ui.html(ui.chips(p.projects, "neutral") or "<div class='c-sub'>No projects section found. Add a 'Projects' heading with one title per project.</div>")
