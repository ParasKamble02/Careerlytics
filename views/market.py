from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from careerlytics import analytics, data_gen, ui

def _kpi(key: str, label: str, value: str) -> None:
    with st.container(key=f"card_{key}"):
        ui.html(f'<div class="kpi">{ui.esc(label)}<b>{ui.esc(value)}</b></div>')

def render(ctx) -> None:
    p, jobs_all, js_all = ctx.profile, ctx.jobs, ctx.js
    role = p.targets[0] if p.targets else None
    ui.page_title("Job Market")
    ui.html(f'<div class="note">Showing the job market for your target role: <b>{ui.esc(role or "all roles")}</b>. '
            'Change it on <b>Upload Resume</b> or in <b>Settings</b>.</div>')

    f1, f2 = st.columns([3, 1])
    locs = f1.multiselect("Locations", data_gen.LOCATIONS, default=[], placeholder="All locations")
    days = f2.selectbox("Period", [30, 60, 90, 120], index=3, format_func=lambda d: f"Last {d} days")

    since = jobs_all["posted_date"].max() - pd.Timedelta(days=days - 1)
    market_ids = analytics.filter_ids(jobs_all, location=locs or None, since=since)       # all roles (context for the role chart)
    role_ids = analytics.filter_ids(jobs_all, role=role, location=locs or None, since=since)
    market = jobs_all[jobs_all["job_id"].isin(market_ids)]
    jobs = jobs_all[jobs_all["job_id"].isin(role_ids)]
    js = js_all[js_all["job_id"].isin(role_ids)]
    if jobs.empty:
        st.warning("No postings match these filters.")
        return

    summ = analytics.market_summary(jobs, js)
    exp_txt = f"{jobs['exp_min'].median():.0f}-{jobs['exp_max'].median():.0f} yrs"
    for col, (key, label, val) in zip(st.columns(4), [
            ("mk_a", "Hiring companies", f"{summ['companies']}"), ("mk_b", "Top skill", f"{summ['top_skill']} · {summ['top_skill_share']:.0%}"),
            ("mk_c", "Top location", summ["top_location"]), ("mk_d", "Typical experience", exp_txt)]):
        with col:
            _kpi(key, label, val)

    t_skills, t_roles, t_salary = st.tabs(["Skills", "Roles & locations", "Salary"])

    #skills
    with t_skills:
        req = analytics.skill_requirements(jobs, js)
        c1, c2 = st.columns([1.2, 1])
        with c1:
            with st.container(key="card_mk_skills"):
                ui.card_header("Most demanded skills", sub=f"% of {len(jobs):,} {role or ''} postings requiring the skill")
                top = req.head(15)
                colors = [ui.PRIMARY if s in p.skills else ui.GRAY_BAR for s in top["skill"]]
                ui.show(ui.hbar(list(top["skill"]), list(top["share"]), colors, height=440), "mk_skills")
                ui.legend([(ui.PRIMARY, "You have it", None), (ui.GRAY_BAR, "You don't", None)])
        with c2:
            with st.container(key="card_mk_demands"):
                ui.card_header("What this job demands from applicants", sub=f"Based on {len(jobs):,} postings")
                edu = jobs["education"].value_counts(normalize=True)
                ui.html(f'<div class="row"><div class="grow"><div class="s">Typical experience</div><div class="t">{exp_txt}</div></div>'
                        f'<div class="grow"><div class="s">Education asked</div><div class="t">'
                        + " · ".join(f"{k} {v:.0%}" for k, v in edu.items()) + "</div></div></div>")
                groups = [("Essential (in 50%+ of postings)", req[req["share"] >= .5]),
                          ("Commonly requested (20-50%)", req[(req["share"] >= .2) & (req["share"] < .5)]),
                          ("Nice to have", req[req["share"] < .2].head(8))]
                for title, g in groups:
                    if g.empty:
                        continue
                    ui.html(f'<div class="c-label" style="margin:12px 0 6px">{title}</div>' + "".join(
                        f'<span class="chip {"ok" if r.skill in p.skills else "miss"}">{"✓" if r.skill in p.skills else "✗"} {ui.esc(r.skill)} {r.share:.0%}</span>'
                        for r in g.itertuples()))

    #roles & locations
    with t_roles:
        c1, c2 = st.columns(2)
        rd, ld = analytics.distribution(market, "role"), analytics.distribution(jobs, "location")
        with c1:
            with st.container(key="card_mk_roles"):
                ui.card_header("Role distribution", sub=f"All roles in the market · {role} highlighted")
                fig = px.pie(rd, names="role", values="jobs", hole=0.62, color_discrete_sequence=ui.AVATARS + ui.DONUT)
                fig.update_traces(textinfo="percent", sort=False, pull=[0.08 if r == role else 0 for r in rd["role"]])
                ui.show(ui.style(fig, 330, legend_on=True, grid=False), "mk_roles")
        with c2:
            with st.container(key="card_mk_locs"):
                ui.card_header("Location demand", sub=f"Where {role} jobs are posted")
                fig = px.bar(ld, x="location", y="share", text=ld["share"].map("{:.0%}".format), color_discrete_sequence=[ui.PRIMARY])
                fig.update_traces(textposition="outside", cliponaxis=False)
                fig.update_yaxes(visible=False)
                fig.update_xaxes(title=None)
                ui.show(ui.style(fig, 330, grid=False), "mk_locs")

    #salary
    with t_salary:
        sal = jobs["salary_lpa"]
        for col, (key, label, val) in zip(st.columns(4), [
                ("sal_a", "Total jobs", f"{len(jobs):,}"), ("sal_b", "Average salary", f"₹{sal.mean():.1f} LPA"),
                ("sal_c", "Minimum salary", f"₹{sal.min():.1f} LPA"), ("sal_d", "Maximum salary", f"₹{sal.max():.1f} LPA")]):
            with col:
                _kpi(key, label, val)
        c1, c2 = st.columns(2)
        with c1:
            with st.container(key="card_mk_sal_exp"):
                ui.card_header("Median salary by experience (LPA)")
                se = analytics.salary_by_experience(jobs)
                fig = px.bar(se, x="band", y="median", text=se["median"].map("{:.1f}".format), color_discrete_sequence=[ui.PRIMARY])
                fig.update_traces(textposition="outside", cliponaxis=False)
                fig.update_xaxes(title=None)
                fig.update_yaxes(visible=False)
                ui.show(ui.style(fig, 320, grid=False), "mk_sal_exp")
        with c2:
            with st.container(key="card_mk_sal_loc"):
                ui.card_header("Median salary by location (LPA)")
                sl = analytics.salary_stats(jobs, "location")
                ui.show(ui.hbar(list(sl["location"]), list(sl["median"]), ui.PRIMARY, height=320, fmt="{:.1f}"), "mk_sal_loc")
