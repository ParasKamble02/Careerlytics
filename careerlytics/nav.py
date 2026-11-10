import streamlit as st

MENU = [
    ("Upload Resume", ":material/upload_file:"),
    ("Dashboard", ":material/dashboard:"),
    ("Resume Insights", ":material/fact_check:"),
    ("Job Market", ":material/insights:"),
    ("Job Matcher", ":material/work:"),
    ("Skill Gap & Roadmap", ":material/alt_route:"),
]
OTHERS = [("Settings", ":material/settings:")]
ALL_PAGES = [p for p, _ in MENU + OTHERS]
OPEN_WITHOUT_RESUME = {"Upload Resume"}

def go(page: str) -> None:
    st.session_state["page"] = page
