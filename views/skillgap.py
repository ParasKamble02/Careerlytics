from __future__ import annotations

import pandas as pd
import streamlit as st

from careerlytics import analytics
from careerlytics import gap as gapmod
from careerlytics import ui

COLORS = {"High": ui.RED, "Medium": ui.ORANGE, "Low": ui.GREEN}

def render(ctx) -> None:
    p = ctx.profile
    ui.page_title("Skill Gap & Career Roadmap")
    gap = ctx.gap()
    if gap.empty:
        st.success("You already cover every skill that appears in your recommended jobs.")
        return

    ui.html(f'<div class="note">Skill gaps for your target role: <b>{ui.esc(", ".join(p.targets) or "all roles")}</b>. '
        'Change it on <b>Upload Resume</b> or in <b>Settings</b>.</div>')
    
    #skill gap, target role's requirements, extracted skills
    role = p.targets[0] if p.targets else None
    role_jobs = ctx.jobs[ctx.jobs["role"] == role] if role else ctx.jobs
    required = analytics.skill_requirements(role_jobs, ctx.js).head(10)["skill"].tolist()
    matched = [s for s in required if s in p.skills]
    g1, g2 = st.columns([1.3, 1])
    with g1:
        with st.container(key="card_gap_role"):
            ui.card_header("Skill gap", sub=f"vs {role or 'market'} requirements (10 most requested skills)")
            d1, d2 = st.columns([1, 1.2])
            with d1:
                ui.show(ui.donut(["Matched", "Missing"], [len(matched), len(required) - len(matched)], f"{len(matched)}/{len(required)}", "matched",
                                 height=190, colors=[ui.PRIMARY, "#E3E5F8"], unit="skills"), "gap_role_donut")
            with d2:
                ui.html("".join(
                    f'<div class="row" style="padding:7px 0;border:0"><span class="pdot" style="background:{ui.GREEN if s in p.skills else ui.RED}"></span>'
                    f'<div class="grow">{ui.esc(s)} - <span style="color:{ui.GREEN if s in p.skills else ui.RED}">{"matched" if s in p.skills else "missing"}</span></div></div>'
                    for s in required))
    with g2:
        with st.container(key="card_gap_skills"):
            ui.card_header("Extracted skills", sub=f"{len(p.skills)} skills found in your resume")
            ui.html(ui.chips(sorted(p.skills), "neutral"))

    cols = st.columns(3)
    for col, lvl, icon in zip(cols, ["High", "Medium", "Low"], ["🔴", "🟠", "🟢"]):
        sub = gap[gap["level"] == lvl]
        with col:
            with st.container(key=f"card_gap_{lvl}"):
                ui.card_header(f"{icon} {lvl} priority", f"{len(sub)} skills")
                ui.html("".join(
                    f'<div class="row"><div class="grow"><div class="t">{ui.esc(r.skill)}</div><div class="s">{ui.esc(r.category)} · demand {r.market_demand:.0%}</div></div>'
                    f'<div class="r">{r.priority:.0f}</div></div>' for r in sub.head(5).itertuples()) or '<div class="s">None</div>')

    left, right = st.columns([1.1, 1])
    with left:
        with st.container(key="card_gap_table"):
            ui.card_header("Skill gap details", sub="Match lift = increase in your average top-20 match score if you learned that skill")
            show = gap.head(20).assign(market_demand=lambda d: d["market_demand"] * 100, job_relevance=lambda d: d["job_relevance"] * 100,
                                       trend=lambda d: d["trend"] * 100)
            show = show.rename(columns={"skill": "Skill", "category": "Category", "market_demand": "Demand", "job_relevance": "Relevance",
                                        "trend": "30d trend", "priority": "Priority", "level": "Level", "lift": "Match lift"})
            st.dataframe(show, hide_index=True, height=420, use_container_width=True, column_config={
                "Demand": st.column_config.NumberColumn(format="%.0f%%", help="Share of postings in your target roles"),
                "Relevance": st.column_config.NumberColumn(format="%.0f%%", help="Score-weighted share of your top-50 jobs"),
                "30d trend": st.column_config.NumberColumn(format="%+.1f pts"),
                "Priority": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f", help="Higher = learn sooner. Based on how often employers ask for the skill, how relevant it is to your best-matching jobs, and whether demand is rising."),
                "Match lift": st.column_config.NumberColumn(format="+%.1f pts"),
            })
    with right:
        with st.container(key="card_gap_road"):
            road = gapmod.roadmap(gap, p)
            ui.card_header("Recommended learning order", f"≈ {int(road['weeks'].sum())} weeks", sub="Prerequisites are placed before the skills that need them")
            def _badge(r):
                if pd.isna(r.priority):
                    return '<span class="chip neutral">prerequisite</span>'
                return f'<span class="chip {gapmod.level(r.priority).lower()}">{gapmod.level(r.priority)}</span>'

            ui.html("".join(
                f'<div class="step"><span class="num">{r.step}</span><div style="flex:1"><div style="font-weight:500">{ui.esc(r.skill)} {_badge(r)}</div>'
                f'<div style="color:#9AA0B8;font-size:11px">{ui.esc(r.category)} · {ui.esc(r.why)}</div></div>'
                f'<div style="font-size:11px;color:#9AA0B8;text-align:right">{r.weeks} wk<br>total {r.cumulative_weeks}</div></div>'
                for r in road.itertuples()))

    with st.container(key="card_gap_sim"):
        ui.card_header("What-if simulator", sub="Pick skills you plan to learn and see how your recommendations change")
        picks = st.multiselect("Skills to add", list(gap["skill"].head(25)), default=list(gap["skill"].head(2)), key="whatif")
        base_rank = ctx.ranked
        new_rank = ctx.matcher.rank(p.with_skills(picks), ctx.model, with_lists=False) if picks else base_rank
        b_avg, n_avg = base_rank["score"].head(20).mean(), new_rank["score"].head(20).mean()
        b_strong, n_strong = int((base_rank["tier"] == "Strong").sum()), int((new_rank["tier"] == "Strong").sum())
        m = st.columns(3)
        m[0].metric("Avg. top-20 match", f"{n_avg:.0%}", f"{(n_avg - b_avg) * 100:+.1f} pts")
        m[1].metric("Strong matches", n_strong, f"{n_strong - b_strong:+d}")
        m[2].metric("Best match", f"{new_rank['score'].iloc[0]:.0%}" if len(new_rank) else "-")
