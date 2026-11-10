import numpy as np
from careerlytics import analytics, gap, ml_model, nlp, service
from careerlytics.bootstrap import skill_rows
from careerlytics.data_gen import generate_jobs
from careerlytics.db import Database
from careerlytics.matching import Matcher

def _setup(tmp_path):
    db = Database(path=tmp_path / "t.db")
    jobs = generate_jobs(400, np.random.default_rng(1))
    db.insert_jobs(jobs, skill_rows(jobs))
    return db, db.jobs(), db.job_skills()

def test_skill_extraction_handles_aliases_and_symbols():
    got = nlp.extract_skills("MS Excel, PySpark, node.js, C++ and Postgres; not Excellent or Scalable")
    assert {"Excel", "Spark", "Node.js", "C++", "PostgreSQL"} <= set(got) and "Scala" not in got

def test_resume_parse_and_score():
    p = nlp.parse_resume("Jane Roe\nSKILLS\nPython, SQL\nEDUCATION\nM.Tech CS\nEXPERIENCE\nAnalyst, Acme, Jan 2022 - Jan 2024\n")
    assert p["education_label"] == "Master" and p["experience"] == 2.0 and set(p["skills"]) == {"Python", "SQL"}
    assert 0 <= nlp.score_resume(p)[0] <= 100

def test_pipeline_end_to_end(tmp_path):
    db, jobs, js = _setup(tmp_path)
    m = Matcher(jobs, js)
    bundle = ml_model.train(m)
    assert bundle["metrics"]["rf_auc"] > 0.9
    prof = service.build_profile("Ann\nSkills: Python, SQL, Excel, Power BI\nEducation\nB.Tech\n", m, jobs, js)
    ranked = m.rank(prof, bundle["model"])
    assert ranked["score"].between(0, 1).all() and ranked["score"].is_monotonic_decreasing
    g = gap.skill_gap(m, prof, ranked, jobs, js)
    assert not set(g["skill"]) & set(prof.skills)
    assert analytics.skill_demand(jobs, js)["share"].max() <= 1

def test_auth_signup_login(tmp_path):
    from careerlytics import auth

    db = Database(path=tmp_path / "a.db")
    user, err = auth.sign_up(db, "Asha", "Asha@Example.com", "password1", "password1")
    assert err is None and user["email"] == "asha@example.com"
    assert auth.sign_up(db, "Asha", "asha@example.com", "password1", "password1")[1]       
    assert auth.log_in(db, "asha@example.com", "wrong")[0] is None
    assert auth.log_in(db, "ASHA@example.com", "password1")[0]["id"] == user["id"]
