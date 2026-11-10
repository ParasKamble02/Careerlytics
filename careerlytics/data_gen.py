from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from .skills import ALIASES

ROLES = {
    "Data Analyst": dict(w=.30, fam="analytics", base=5.5, must=["SQL", "Excel"],
        pool=["Python", "Power BI", "Tableau", "Pandas", "Statistics", "Data Visualization", "Communication"], k=(2, 4),
        opt=["DAX", "AWS", "Power Query", "A/B Testing", "Git", "VBA", "Agile", "MySQL", "NumPy"], m=(1, 3), exp=[0, 0, 1, 1, 2, 3],
        resp=["turn raw business data into dashboards and weekly insights", "partner with product teams to answer questions with data"]),
    "BI Analyst": dict(w=.14, fam="analytics", base=6.5, must=["SQL", "Power BI"],
        pool=["DAX", "Excel", "Tableau", "Data Modeling", "Power Query", "Data Warehousing", "Data Visualization"], k=(2, 4),
        opt=["Python", "Azure", "ETL", "Stakeholder Management", "Snowflake", "Agile"], m=(1, 3), exp=[1, 2, 2, 3, 4, 5],
        resp=["design and maintain executive reporting dashboards", "build semantic models and automate refreshes"]),
    "Business Analyst": dict(w=.08, fam="analytics", base=6.0, must=["Excel", "SQL"],
        pool=["Requirements Gathering", "Stakeholder Management", "Jira", "Agile", "Power BI", "Communication", "Tableau"], k=(2, 4),
        opt=["Python", "Data Visualization", "Statistics"], m=(1, 2), exp=[0, 1, 2, 3, 5],
        resp=["translate business needs into clear requirements", "track KPIs and recommend process improvements"]),
    "Data Scientist": dict(w=.14, fam="ds", base=10.0, must=["Python", "Machine Learning"],
        pool=["SQL", "Pandas", "NumPy", "Scikit-learn", "Statistics", "Feature Engineering", "Matplotlib", "NLP", "Deep Learning"], k=(3, 5),
        opt=["TensorFlow", "PyTorch", "AWS", "Docker", "Git", "XGBoost", "Time Series", "LLMs", "Spark", "Streamlit"], m=(2, 4), exp=[0, 1, 2, 3, 4, 6],
        resp=["build and evaluate predictive models for customer problems", "run experiments and communicate findings to leadership"]),
    "ML Engineer": dict(w=.09, fam="ds", base=13.0, must=["Python", "Machine Learning"],
        pool=["Docker", "AWS", "PyTorch", "TensorFlow", "MLOps", "Deep Learning", "Scikit-learn", "FastAPI", "Git", "SQL"], k=(3, 5),
        opt=["Kubernetes", "Kafka", "LLMs", "Spark", "CI/CD", "GCP", "Computer Vision", "NLP"], m=(2, 4), exp=[1, 2, 3, 4, 5],
        resp=["productionise models and own their serving infrastructure", "monitor model quality and automate retraining"]),
    "Data Engineer": dict(w=.10, fam="eng", base=11.0, must=["SQL", "Python"],
        pool=["Spark", "Airflow", "ETL", "AWS", "Data Warehousing", "Snowflake", "Kafka", "dbt", "Azure", "Databricks"], k=(3, 5),
        opt=["Docker", "Kubernetes", "Git", "CI/CD", "BigQuery", "Hadoop", "Linux", "Scala"], m=(2, 3), exp=[1, 2, 3, 4, 5, 6],
        resp=["build reliable batch and streaming data pipelines", "model warehouse tables that analysts can trust"]),
    "Python Developer": dict(w=.06, fam="eng", base=7.0, must=["Python"],
        pool=["Django", "Flask", "FastAPI", "REST APIs", "SQL", "PostgreSQL", "Git", "Docker", "Linux"], k=(3, 5),
        opt=["AWS", "Redis", "MongoDB", "CI/CD", "Kubernetes"], m=(1, 3), exp=[0, 1, 2, 3, 4],
        resp=["develop and test backend services and internal tools", "write clean, documented APIs used by other teams"]),
    "Full Stack Developer": dict(w=.09, fam="eng", base=9.0, must=["JavaScript", "React"],
        pool=["Node.js", "MongoDB", "HTML/CSS", "REST APIs", "TypeScript", "SQL", "Git", "Docker", "PostgreSQL"], k=(3, 5),
        opt=["AWS", "Python", "Redis", "CI/CD", "Kubernetes", "Agile"], m=(1, 3), exp=[0, 1, 2, 3, 4, 5],
        resp=["ship features end to end across web UI and APIs", "improve performance and accessibility of our customer apps"]),
}
ROLE_NAMES = list(ROLES)
ROLE_WEIGHTS = np.array([ROLES[r]["w"] for r in ROLE_NAMES])
FAMILY = {r: v["fam"] for r, v in ROLES.items()}

LOCATIONS = ["Bangalore", "Pune", "Mumbai", "Hyderabad", "Delhi NCR", "Chennai", "Remote"]
LOC_W = np.array([.30, .21, .16, .13, .12, .05, .03])
LOC_MULT = {"Bangalore": 1.15, "Pune": 1.0, "Mumbai": 1.08, "Hyderabad": 1.05, "Delhi NCR": 1.04, "Chennai": .96, "Remote": 1.10}

TRENDING = {"Power BI": .35, "DAX": .40, "Docker": .30, "AWS": .25, "LLMs": .80, "dbt": .50,
            "Snowflake": .40, "FastAPI": .40, "MLOps": .50, "Databricks": .50, "Kubernetes": .30}

_PRE = ["Nimbus", "Quanta", "Veridian", "Aster", "Cobalt", "Helix", "Lumen", "Zephyr", "Pinnacle", "Maple", "Ember", "Atlas", "Vertex", "Solace", "Kinetic", "Mosaic"]
_SUF = ["Analytics", "Technologies", "Labs", "Systems", "Digital", "Insights", "Cloud"]
BOILERPLATE = ["We offer flexible hours and a collaborative culture.", "You will join a friendly team with strong mentoring.",
               "We value ownership, curiosity and learning on the job."]

def companies(rng: np.random.Generator, n: int = 48) -> list[str]:
    combos = [f"{p} {s}" for p in _PRE for s in _SUF]
    return list(rng.choice(combos, size=n, replace=False))

def _surface(skill: str, rng: np.random.Generator) -> str:
    """Write a skill the way a recruiter might (30% of the time use an alias)."""
    return str(rng.choice(ALIASES[skill])) if rng.random() < .3 else skill

def _pick(pool, k, rng, recency):
    w = np.array([1 + TRENDING.get(s, 0) * recency for s in pool], dtype=float)
    k = min(k, len(pool))
    return list(rng.choice(pool, size=k, replace=False, p=w / w.sum()))

def generate_jobs(n: int, rng: np.random.Generator, start_id: int = 1, today: date | None = None,
                  source: str = "seed", role_bias: str | None = None, max_age: int = 120) -> pd.DataFrame:
    today = today or date.today()
    comps = companies(np.random.default_rng(7))
    rows = []
    for i in range(n):
        role = role_bias if (role_bias and rng.random() < .45) else str(rng.choice(ROLE_NAMES, p=ROLE_WEIGHTS))
        spec = ROLES[role]
        age = 0 if source == "live" else int(max_age * rng.random() ** 1.6)
        recency = 1 - age / max_age
        core = spec["must"] + _pick([s for s in spec["pool"] if s not in spec["must"]], int(rng.integers(*spec["k"])), rng, recency)
        opt = _pick([s for s in spec["opt"] if s not in core], int(rng.integers(*spec["m"])), rng, recency)
        exp_min = int(rng.choice(spec["exp"]))
        exp_max = exp_min + int(rng.choice([1, 2, 3]))
        loc = str(rng.choice(LOCATIONS, p=LOC_W))
        edu = "Master" if (spec["fam"] == "ds" and rng.random() < .4) else "Bachelor"
        prefix = "Junior " if exp_min == 0 and rng.random() < .5 else ("Senior " if exp_min >= 5 else "")
        title = f"{prefix}{role}"
        salary = spec["base"] * (1 + .14 * (exp_min + exp_max) / 2) * LOC_MULT[loc] * (1 + .015 * (len(core) + len(opt) - 6)) * rng.lognormal(0, .12)
        company = str(rng.choice(comps))
        desc = (f"{company} is hiring a {title} for our {loc} team. In this role you will {rng.choice(spec['resp'])}. "
                f"Experience: {exp_min}-{exp_max} years. Education: {edu}'s degree in Computer Science, Mathematics or a related field. "
                f"Must have: {', '.join(_surface(s, rng) for s in core)}. "
                f"Good to have: {', '.join(_surface(s, rng) for s in opt)}. {rng.choice(BOILERPLATE)}")
        rows.append(dict(job_id=start_id + i, title=title, role=role, company=company, location=loc,
                         salary_lpa=round(round(salary * 2) / 2, 1), exp_min=exp_min, exp_max=exp_max, education=edu,
                         description=desc, posted_date=(today - timedelta(days=age)).isoformat(), source=source))
    return pd.DataFrame(rows)
