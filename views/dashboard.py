from __future__ import annotations

import streamlit as st

from careerlytics import ui
from careerlytics.nav import go

def _view_report(key: str, page: str) -> None:
    st.button("View Report", key=f"vr_{key}", on_click=go, args=(page,))

def render(ctx) -> None:
    p, ranked = ctx.profile, ctx.ranked
    role = p.targets[0] if p.targets else None
    ui.page_title("Dashboard")
    if msg := st.session_state.pop("flash", None):
        st.success(msg)

    #KPI cards
    kpis = [("Resume score", f"{p.resume_score:.0f}/100"), ("Skills recognised", str(len(p.skills))),
            ("Experience", f"{p.experience:g} yrs"), ("Education", p.education_label)]
    for col, (label, val) in zip(st.columns(4), kpis):
        with col:
            with st.container(key=f"card_kpi_{label[:4]}"):
                ui.html(f'<div class="kpi">{ui.esc(label)}<b>{ui.esc(val)}</b></div>')

    good_plus = ranked[ranked["tier"].isin(["Strong", "Good"])]
    for_role = ranked[ranked["role"] == role] if role else ranked
    for_role = for_role if len(for_role) else ranked

    #row 2
    c_fit, c_top, c_roles = st.columns([1, 1.15, 1])
    with c_fit:
        with st.container(key="card_fit"):
            ui.card_header("Your Career Fit", sub="Resume quality, market skills and match quality")
            top10 = float(for_role["score"].head(10).mean() * 100)
            cov = float(for_role["skill_match"].head(10).mean() * 100)
            ui.html(ui.bubbles_svg([("Resume score", p.resume_score, ui.PURPLE), ("Skill coverage", cov, ui.CYAN), ("Top-10 match", top10, ui.ORANGE)]))
    with c_top:
        with st.container(key="card_top"):
            a, b = st.columns([3, 2])
            with a:
                ui.card_header("Top Recommended Jobs", sub=f"Best matches for {role}" if role else "Ranked by blended match score")
            with b:
                _view_report("matcher", "Job Matcher")
            rows = []
            for i, r in enumerate(for_role.head(4).itertuples()):
                rows.append(
                    f'<div class="row">{ui.avatar(r.company, i)}<div class="grow"><div class="t">{ui.esc(r.title)}</div>'
                    f'<div class="s">{ui.esc(r.company)} · {ui.esc(r.location)}</div></div>'
                    f'<div class="r">{r.score:.0%}<div class="s">₹{r.salary_lpa:.1f}L</div></div></div>')
            ui.html("".join(rows))
    with c_roles:
        with st.container(key="card_roles"):
            ui.card_header("Matches by Role", sub=f"{len(good_plus):,} strong + good matches")
            by_role = good_plus["role"].value_counts()
            top3 = by_role.head(3)
            labels = list(top3.index) + (["Other"] if len(by_role) > 3 else [])
            values = list(top3.values) + ([int(by_role.iloc[3:].sum())] if len(by_role) > 3 else [])
            if values:
                ui.show(ui.donut(labels, values, f"{int(sum(values))}", "matched jobs"), "dash_donut")
                total = max(sum(values), 1)
                ui.legend([(ui.DONUT[i], l, f"{v / total:.0%}") for i, (l, v) in enumerate(zip(labels, values))])
            else:
                st.caption("No strong or good matches yet - add skills in Settings.")

    #row 3
    with st.container(key="card_actions"):
        ui.card_header("Recommended Actions", sub=f"Target role: {role}" if role else "")
        gap = ctx.gap()
        items = []
        if not gap.empty:
            g = gap.iloc[0]
            import pandas as pd
            lift = f" (+{g['lift']:.1f} pts avg. match)" if pd.notna(g["lift"]) else ""
            items.append((ui.RED, f"Learn <b>{ui.esc(g['skill'])}</b>{lift}", "Highest-priority skill gap"))
        if len(for_role):
            r = for_role.iloc[0]
            items.append((ui.GREEN, f"Apply to <b>{ui.esc(r['title'])}</b> at {ui.esc(r['company'])}", f"{r['score']:.0%} match · {r['location']}"))
        if p.improvements:
            items.append((ui.ORANGE, ui.esc(p.improvements[0]), "Resume improvement"))
        items.append((ui.PRIMARY, f"Explore the {ui.esc(role or 'job')} market: skills, salaries and locations", "Job Market page"))
        ui.html("".join(f'<div class="row"><span class="pdot" style="background:{c}"></span><div class="grow"><div class="t" style="white-space:normal">{t}</div><div class="s">{s}</div></div></div>' for c, t, s in items))
