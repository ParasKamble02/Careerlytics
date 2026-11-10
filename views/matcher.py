from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from careerlytics import data_gen, ui
from careerlytics.matching import explain

def render(ctx) -> None:
    p, ranked = ctx.profile, ctx.ranked
    ui.page_title("Job Matcher")

    f1, f2, f3, f4 = st.columns([2, 2, 1.2, 1.4])
    roles = f1.multiselect("Role", data_gen.ROLE_NAMES, default=p.targets, placeholder="All roles", key="mj_role_" + "_".join(p.targets))
    locs = f2.multiselect("Location", data_gen.LOCATIONS, default=p.locations, placeholder="Anywhere", key="mj_loc_" + "_".join(p.locations))
    tier = f3.selectbox("Match level", ["All", "Strong", "Good", "Stretch"])
    min_score = f4.slider("Min. match %", 0, 100, 40, 5)

    df = ranked
    if roles:
        df = df[df["role"].isin(roles)]
    if locs:
        df = df[df["location"].isin(locs)]
    if tier != "All":
        df = df[df["tier"] == tier]
    df = df[df["score"] * 100 >= min_score].reset_index(drop=True)
    if df.empty:
        st.info("No jobs match these filters. Try lowering the minimum match or clearing a filter.")
        return

    left, right = st.columns([1.15, 1])
    with left:
        with st.container(key="card_mj_list"):
            ui.card_header("Recommended jobs", f"{len(df):,} matches", sub="Click a row to see why it was ranked here")
            view = df.head(100).assign(
                Match=lambda d: (d["score"] * 100).round(0), ML=lambda d: (d["ml_prob"] * 100).round(0),
                Salary=lambda d: d["salary_lpa"], Posted=lambda d: d["posted_date"].dt.strftime("%d %b"))
            view = view[["title", "company", "location", "Salary", "Posted", "Match", "ML", "tier"]].rename(
                columns={"title": "Job", "company": "Company", "location": "Location", "tier": "Level"})
            ev = st.dataframe(
                view, hide_index=True, height=520, use_container_width=True, on_select="rerun", selection_mode="single-row", key="mj_table",
                column_config={
                    "Match": st.column_config.ProgressColumn("Match %", min_value=0, max_value=100, format="%d%%"),
                    "ML": st.column_config.NumberColumn("ML prob.", format="%d%%"),
                    "Salary": st.column_config.NumberColumn("₹ LPA", format="%.1f"),
                })
            rows = ev.selection.rows if ev is not None and hasattr(ev, "selection") else []
    sel = df.iloc[rows[0]] if rows else df.iloc[0]

    with right:
        with st.container(key="card_mj_detail"):
            a, b = st.columns([3, 1])
            with a:
                ui.card_header(sel["title"], sub=f"{sel['company']} · {sel['location']} · ₹{sel['salary_lpa']:.1f} LPA · {int(sel['exp_min'])}-{int(sel['exp_max'])} yrs · posted {sel['posted_date']:%d %b %Y}")
            with b:
                ui.html(f'<div style="text-align:right;margin-top:4px">{ui.tier_chip(sel["tier"])}</div>')
            m1, m2 = st.columns(2)
            with m1:
                ui.html(f'<div class="kpi">Overall match<b>{sel["score"]:.0%}</b></div>')
            with m2:
                ui.html(f'<div class="kpi">ML match probability<b>{sel["ml_prob"]:.0%}</b></div>')

            ui.html('<div class="c-label" style="margin-top:14px">Skills</div>')
            ui.html(ui.chips([f"✓ {s}" for s in sel["matched"]], "ok") + ui.chips([f"✗ {s}" for s in sel["missing"]], "miss")
                    or '<span class="s">No skills detected for this posting.</span>')
            total = len(sel["matched"]) + len(sel["missing"])
            st.caption(f"{len(sel['matched'])} of {total} required skills matched" + (f" · missing core: {', '.join(sel['missing_core'])}" if sel["missing_core"] else ""))

            ex = explain(sel)
            fig = go.Figure(go.Bar(x=ex["points"], y=ex["component"], orientation="h", marker_color=ui.PRIMARY,
                                   text=[f"{v:.1f} / {w * 100:.0f}" for v, w in zip(ex["points"], ex["weight"])], textposition="outside", cliponaxis=False))
            fig.update_yaxes(autorange="reversed", showgrid=False)
            fig.update_xaxes(visible=False, range=[0, 62])
            ui.html('<div class="c-label">Why this score</div>')
            ui.show(ui.style(fig, 190, grid=False), f"mj_why_{int(sel['job_id'])}")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Save to my applications", type="primary", key=f"save_{int(sel['job_id'])}"):
                    ctx.db.save_application(ctx.user["id"], int(sel["job_id"]), float(sel["score"]))
                    st.toast("Saved to applications")
            with c2:
                with st.popover("Job description"):
                    st.write(ctx.matcher.description(int(sel["job_id"])))

    saved = ctx.db.applications(ctx.user["id"])
    if not saved.empty:
        with st.expander(f"My saved jobs ({len(saved)})"):
            st.dataframe(saved.assign(match_score=(saved["match_score"] * 100).round(0)), hide_index=True, use_container_width=True)
