from __future__ import annotations

import numpy as np

from . import config, data_gen, nlp
from .db import Database
from .matching import Matcher

def skill_rows(jobs_df) -> list[tuple[int, str, int]]:
    """Run the NLP extractor over every job description rows."""
    return [(int(r.job_id), s, c) for r in jobs_df.itertuples() for s, c in nlp.extract_job_skills(r.description)]

def seed_database(db: Database, n: int = config.SEED_JOBS, seed: int = config.RANDOM_SEED) -> int:
    db.clear_jobs()
    jobs = data_gen.generate_jobs(n, np.random.default_rng(seed), start_id=1, source="seed")
    db.insert_jobs(jobs, skill_rows(jobs))
    return len(jobs)

def ensure_seeded(db: Database) -> bool:
    if db.is_empty():
        seed_database(db)
        return True
    return False

def build_matcher(db: Database | None = None) -> Matcher:
    db = db or Database()
    ensure_seeded(db)
    return Matcher(db.jobs(), db.job_skills())

if __name__ == "__main__":  
    from . import ml_model
    d = Database()
    print(f"Seeded {seed_database(d)} jobs into {d.path if d.kind == 'sqlite' else d.url}")
    m = Matcher(d.jobs(), d.job_skills())
    print("Model metrics:", ml_model.train(m)["metrics"])
