from __future__ import annotations

import json
import streamlit as st

from careerlytics import auth, ui

def start_session(db, user: dict) -> None:
    st.session_state["user"] = user
    saved = db.get_profile_json(user["id"])
    if saved:
        st.session_state["profile"] = json.loads(saved)
        st.session_state["page"] = "Dashboard"
    else:
        st.session_state.pop("profile", None)
        st.session_state["page"] = "Upload Resume"


def render(db) -> None:
    st.markdown("<style>section[data-testid='stSidebar'],[data-testid='stExpandSidebarButton'],[data-testid='stSidebarCollapsedControl']{display:none!important}</style>",
                unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.15, 1])
    with mid:
        ui.html(ui.brand_html("margin:40px 0 14px 0") + '<div class="page-title" style="border:0;margin:6px 0 4px">Welcome</div>')
        with st.container(key="card_auth"):
            t_in, t_up = st.tabs(["Log in", "Sign up"])
            with t_in:
                with st.form("login_form"):
                    email = st.text_input("Email")
                    pw = st.text_input("Password", type="password")
                    go_in = st.form_submit_button("Log in", type="primary")
                if go_in:
                    user, err = auth.log_in(db, email, pw)
                    if err:
                        st.error(err)
                    else:
                        start_session(db, user)
                        st.rerun()
            with t_up:
                with st.form("signup_form"):
                    username = st.text_input("Username")
                    email2 = st.text_input("Email", key="su_email")
                    pw2 = st.text_input("Password (min. 8 characters)", type="password", key="su_pw")
                    pw3 = st.text_input("Confirm password", type="password", key="su_pw2")
                    go_up = st.form_submit_button("Create account", type="primary")
                if go_up:
                    user, err = auth.sign_up(db, username, email2, pw2, pw3)
                    if err:
                        st.error(err)
                    else:
                        start_session(db, user)
                        st.rerun()
