import streamlit as st

st.set_page_config(page_title="Careerlytics", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

from careerlytics import nav, ui  
from careerlytics.state import get_db, load_ctx  
from views import dashboard, insights, login, market, matcher, resume, settings, skillgap  

PAGES = {
    "Upload Resume": resume.render, "Dashboard": dashboard.render, "Resume Insights": insights.render, "Job Market": market.render,
    "Job Matcher": matcher.render, "Skill Gap & Roadmap": skillgap.render, "Settings": settings.render,
}
ui.inject_css()

#authentication 
if "user" not in st.session_state:
    login.render(get_db())
    st.stop()

ctx = load_ctx()

#resume upload
page = st.session_state.get("page", "Upload Resume")
if page not in PAGES or (not ctx.has_resume and page not in nav.OPEN_WITHOUT_RESUME):
    page = st.session_state["page"] = "Upload Resume"

def _logout() -> None:
    st.session_state.clear()

def _sidebar() -> None:
    with st.sidebar:
        ui.html(ui.brand_html() + '<div class="menu-label">MENU</div>')
        for name, icon in nav.MENU:
            st.button(name, icon=icon, key=("navon_" if name == page else "nav_") + name, on_click=nav.go, args=(name,),
                      disabled=not ctx.has_resume and name not in nav.OPEN_WITHOUT_RESUME)
        ui.html('<div class="menu-label">OTHERS</div>')
        for name, icon in nav.OTHERS:
            st.button(name, icon=icon, key=("navon_" if name == page else "nav_") + name, on_click=nav.go, args=(name,),
                      disabled=not ctx.has_resume and name not in nav.OPEN_WITHOUT_RESUME)
        st.button("Log out", icon=":material/logout:", key="nav_logout", on_click=_logout)

def _topbar() -> str:
    c_search, c_user = st.columns([7, 2])
    with c_search:
        q = st.text_input("Search", key="search_q", placeholder="Search jobs, companies or skills", label_visibility="collapsed", disabled=not ctx.has_resume)
    with c_user:
        ui.html(f'<div class="user-chip">{ui.avatar(ctx.user["username"], 0)}<span>{ui.esc(ctx.user["username"])}</span></div>')
    return q.strip()

def _search_results(q: str) -> None:
    ui.page_title(f'Search results for "{q}"')
    r = ctx.ranked
    mask = r["title"].str.contains(q, case=False, regex=False) | r["company"].str.contains(q, case=False, regex=False) | r["role"].str.contains(q, case=False, regex=False)
    hit_ids = set(ctx.js.loc[ctx.js["skill"].str.contains(q, case=False, regex=False), "job_id"])
    res = r[mask | r["job_id"].isin(hit_ids)].head(100)
    st.caption(f"{len(res)} shown (best matches first). Clear the search box to return.")
    out = res.assign(Match=(res["score"] * 100).round(0))[["title", "company", "location", "salary_lpa", "Match", "tier"]]
    st.dataframe(out.rename(columns={"title": "Job", "company": "Company", "location": "Location", "salary_lpa": "₹ LPA", "tier": "Level"}),
                 hide_index=True, use_container_width=True,
                 column_config={"Match": st.column_config.ProgressColumn("Match %", min_value=0, max_value=100, format="%d%%")})

_sidebar()
query = _topbar()
if query and ctx.has_resume:
    _search_results(query)
else:
    PAGES[page](ctx)
