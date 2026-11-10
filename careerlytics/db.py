from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime

import pandas as pd

from . import config

SQLITE_DDL = [
    """CREATE TABLE IF NOT EXISTS jobs (
        job_id INTEGER PRIMARY KEY, title TEXT NOT NULL, role TEXT NOT NULL, company TEXT NOT NULL,
        location TEXT NOT NULL, salary_lpa REAL, exp_min INTEGER, exp_max INTEGER, education TEXT,
        description TEXT, posted_date TEXT NOT NULL, source TEXT DEFAULT 'seed')""",
    """CREATE TABLE IF NOT EXISTS job_skills (
        job_id INTEGER NOT NULL, skill TEXT NOT NULL, is_core INTEGER NOT NULL DEFAULT 1,
        PRIMARY KEY (job_id, skill))""",
    "CREATE INDEX IF NOT EXISTS idx_js_skill ON job_skills(skill)",
    "CREATE INDEX IF NOT EXISTS idx_jobs_role ON jobs(role)",
    """CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL, salt TEXT NOT NULL, created_at TEXT, profile_json TEXT)""",
    """CREATE TABLE IF NOT EXISTS resume_skills (
        user_id INTEGER NOT NULL, skill TEXT NOT NULL, strength INTEGER, PRIMARY KEY (user_id, skill))""",
    """CREATE TABLE IF NOT EXISTS applications (
        user_id INTEGER NOT NULL, job_id INTEGER NOT NULL, match_score REAL, status TEXT DEFAULT 'Saved',
        saved_at TEXT, PRIMARY KEY (user_id, job_id))""",
    """CREATE TABLE IF NOT EXISTS feed_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, kind TEXT, message TEXT)""",
]

class Database:
    def __init__(self, url: str | None = None, path=None):
        self.url = url if url is not None else config.DB_URL
        if self.url:
            from sqlalchemy import create_engine  

            self.engine = create_engine(self.url, pool_pre_ping=True)
            self.kind = "sql"
        else:
            self.path = path or config.SQLITE_PATH
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.kind = "sqlite"
        self.ensure_schema()

    #primitives
    def ensure_schema(self):
        if self.kind == "sqlite":
            with closing(sqlite3.connect(self.path, timeout=30)) as c:
                cols = [r[1] for r in c.execute("PRAGMA table_info(users)")]
                if cols and "email" not in cols:
                    for t in ("users", "resume_skills", "applications"):
                        c.execute(f"DROP TABLE IF EXISTS {t}")
                for stmt in SQLITE_DDL:
                    c.execute(stmt)
                c.commit()
        else:
            from sqlalchemy import text

            script = (config.ROOT / "sql" / "schema_mysql.sql").read_text()
            statements = [s.strip() for s in "\n".join(l for l in script.splitlines() if not l.strip().startswith("--")).split(";") if s.strip()]
            with self.engine.begin() as c:
                for stmt in statements:
                    c.execute(text(stmt))

    def executemany(self, sql: str, rows: list[dict]):
        if not rows:
            return
        if self.kind == "sqlite":
            with closing(sqlite3.connect(self.path, timeout=30)) as c:
                c.executemany(sql, rows)
                c.commit()
        else:
            from sqlalchemy import text

            with self.engine.begin() as c:
                c.execute(text(sql), rows)

    def execute(self, sql: str, params: dict | None = None):
        if self.kind == "sqlite":
            with closing(sqlite3.connect(self.path, timeout=30)) as c:
                c.execute(sql, params or {})
                c.commit()
        else:
            from sqlalchemy import text

            with self.engine.begin() as c:
                c.execute(text(sql), params or {})

    def read_df(self, sql: str, params: dict | None = None) -> pd.DataFrame:
        if self.kind == "sqlite":
            with closing(sqlite3.connect(self.path, timeout=30)) as c:
                return pd.read_sql_query(sql, c, params=params or {})
        from sqlalchemy import text

        with self.engine.connect() as c:
            return pd.read_sql_query(text(sql), c, params=params or {})

    #jobs
    def is_empty(self) -> bool:
        return int(self.read_df("SELECT COUNT(*) AS n FROM jobs")["n"][0]) == 0

    def version(self) -> tuple[int, int]:
        """Cheap fingerprint of the jobs table; used as a cache key so the UI refreshes after new jobs arrive."""
        r = self.read_df("SELECT COUNT(*) AS n, COALESCE(MAX(job_id), 0) AS m FROM jobs")
        return int(r["n"][0]), int(r["m"][0])

    def next_job_id(self) -> int:
        return self.version()[1] + 1

    def jobs(self) -> pd.DataFrame:
        df = self.read_df("SELECT * FROM jobs ORDER BY job_id")
        df["posted_date"] = pd.to_datetime(df["posted_date"])
        df["salary_lpa"] = df["salary_lpa"].astype(float)
        return df

    def job_skills(self) -> pd.DataFrame:
        return self.read_df("SELECT job_id, skill, is_core FROM job_skills")

    def insert_jobs(self, jobs: pd.DataFrame, skill_rows: list[tuple[int, str, int]]):
        cols = ["job_id", "title", "role", "company", "location", "salary_lpa", "exp_min", "exp_max", "education", "description", "posted_date", "source"]
        self.executemany(
            f"INSERT INTO jobs ({', '.join(cols)}) VALUES ({', '.join(':' + c for c in cols)})",
            jobs[cols].to_dict("records"),
        )
        self.executemany(
            "INSERT INTO job_skills (job_id, skill, is_core) VALUES (:job_id, :skill, :is_core)",
            [dict(job_id=j, skill=s, is_core=c) for j, s, c in skill_rows],
        )

    def delete_live(self):
        self.execute("DELETE FROM job_skills WHERE job_id IN (SELECT job_id FROM jobs WHERE source = 'live')")
        self.execute("DELETE FROM jobs WHERE source = 'live'")
        self.execute("DELETE FROM feed_events")

    def clear_jobs(self):
        for t in ("job_skills", "jobs", "feed_events"):
            self.execute(f"DELETE FROM {t}")

    #accounts
    def create_user(self, username: str, email: str, password_hash: str, salt: str) -> int:
        email = email.strip().lower()
        if not self.read_df("SELECT 1 AS x FROM users WHERE email = :e", {"e": email}).empty:
            raise ValueError("An account with this email already exists.")
        self.execute(
            "INSERT INTO users (username, email, password_hash, salt, created_at) VALUES (:u, :e, :h, :s, :t)",
            {"u": username.strip(), "e": email, "h": password_hash, "s": salt, "t": datetime.now().strftime("%Y-%m-%d %H:%M")},
        )
        return int(self.read_df("SELECT user_id FROM users WHERE email = :e", {"e": email})["user_id"][0])

    def get_user_by_email(self, email: str) -> dict | None:
        df = self.read_df("SELECT user_id, username, email, password_hash, salt FROM users WHERE email = :e", {"e": email.strip().lower()})
        return None if df.empty else df.iloc[0].to_dict()

    def get_profile_json(self, user_id: int) -> str | None:
        v = self.read_df("SELECT profile_json FROM users WHERE user_id = :u", {"u": int(user_id)})["profile_json"]
        return v.iloc[0] if len(v) and isinstance(v.iloc[0], str) else None

    #profile / applications (per user)
    def save_profile(self, user_id: int, p) -> None:
        uid = int(user_id)
        self.execute("UPDATE users SET profile_json = :j WHERE user_id = :u", {"j": p.key(), "u": uid})
        self.execute("DELETE FROM resume_skills WHERE user_id = :u", {"u": uid})
        self.executemany(
            "INSERT INTO resume_skills (user_id, skill, strength) VALUES (:u, :s, :v)",
            [{"u": uid, "s": s, "v": int(v)} for s, v in p.skills.items()],
        )

    def save_application(self, user_id: int, job_id: int, score: float, status: str = "Saved"):
        self.execute("DELETE FROM applications WHERE user_id = :u AND job_id = :j", {"u": int(user_id), "j": int(job_id)})
        self.execute(
            "INSERT INTO applications (user_id, job_id, match_score, status, saved_at) VALUES (:u, :j, :s, :st, :t)",
            {"u": int(user_id), "j": int(job_id), "s": float(score), "st": status, "t": datetime.now().strftime("%Y-%m-%d %H:%M")},
        )

    def applications(self, user_id: int) -> pd.DataFrame:
        return self.read_df(
            "SELECT a.job_id, j.title, j.company, j.location, a.match_score, a.status, a.saved_at "
            "FROM applications a JOIN jobs j ON j.job_id = a.job_id WHERE a.user_id = :u ORDER BY a.saved_at DESC",
            {"u": int(user_id)},
        )

    #live feed log
    def add_event(self, kind: str, message: str):
        self.execute(
            "INSERT INTO feed_events (created_at, kind, message) VALUES (:t, :k, :m)",
            {"t": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "k": kind, "m": message},
        )

    def events(self, limit: int = 30) -> pd.DataFrame:
        return self.read_df(f"SELECT created_at, kind, message FROM feed_events ORDER BY event_id DESC LIMIT {int(limit)}")
