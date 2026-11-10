from __future__ import annotations

import streamlit as st

from careerlytics import data_gen, nlp, service, ui
from careerlytics.profile import Profile
from careerlytics.state import set_profile

def _analyze(ctx, text: str, role: str) -> None:
    keep = ctx.has_resume
    p = service.build_profile(text, ctx.matcher, ctx.jobs, ctx.js, targets=[role], locations=ctx.profile.locations if keep else [])
    set_profile(ctx, p)
    st.session_state["flash"] = f"Resume analysed: {len(p.skills)} skills found. Target role: {role}."
    st.session_state["page"] = "Dashboard" 

def render(ctx) -> None:
    p = ctx.profile
    current = p.targets[0] if (ctx.has_resume and p.targets) else None
    ui.page_title("Upload Resume")
    ui.html('<div class="c-sub" style="margin:-6px 0 16px">Upload a PDF, DOCX or TXT resume and pick the target role to analyse against.</div>')

    left, right = st.columns([1.35, 1])
    with right:
        with st.container(key="card_target"):
            ui.card_header("Target role", sub="The job market, matches and skill gaps will be shown for this role.")
        
            role = st.selectbox("Choose a job profile", data_gen.ROLE_NAMES, index=data_gen.ROLE_NAMES.index(current) if current in data_gen.ROLE_NAMES else None,
                                placeholder="Select a target role...", key=f"target_role_{current}")
            if ctx.has_resume and role and role != current: 
                d = p.to_dict()
                d["targets"] = [role]
                set_profile(ctx, Profile.from_dict(d))
                st.rerun()
            ui.html('<div class="c-sub">Once analysed, results appear on Dashboard, Resume Insights, Job Market, Job Matcher and Skill Gap.</div>')

    with left:
        with st.container(key="card_upload"):
            ui.card_header("Resume file", sub="PDF, DOCX or TXT. Processed locally and saved to your account only." if not ctx.has_resume
                           else f"Current resume: {len(p.skills)} skills analysed. Upload again to replace it (target role and locations are kept).")
            f = st.file_uploader("Resume file", type=["pdf", "docx", "txt", "md"], label_visibility="collapsed")
            if st.button("Analyze resume" if not ctx.has_resume else "Re-analyze", type="primary", disabled=f is None or not role, key="an_file", use_container_width=True):
                try:
                    text = nlp.read_resume_bytes(f.getvalue(), f.name)
                    if len(text.split()) < 20:
                        st.warning("Very little text was found. Scanned PDFs need OCR - try a text-based file or paste the text below.")
                    else:
                        _analyze(ctx, text, role)
                        st.rerun()
                except Exception as e:  
                    st.error(f"Could not read this file: {e}")
            if f is not None and not role:
                st.caption("Choose a target role to enable analysis.")
            with st.expander("Or paste resume text"):
                pasted = st.text_area("Resume text", height=140, placeholder="Paste your resume text here...", label_visibility="collapsed")
                if st.button("Analyze pasted text", disabled=len(pasted.split()) < 20 or not role, key="an_text"):
                    _analyze(ctx, pasted, role)
                    st.rerun()
    if not ctx.has_resume:
        ui.html('<div class="note" style="margin-top:14px">Dashboard, Resume Insights, Job Market, Job Matcher and Skill Gap unlock as soon as your resume is analysed.</div>')
