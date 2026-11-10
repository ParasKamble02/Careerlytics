# 📈 Careerlytics: An AI-Powered Career Intelligence and Job Recommendation Platform

> An interactive career-analytics web application that reads your resume, compares it with the job market for your chosen target role, recommends the best-matching jobs with an explainable score, and shows exactly which skills to learn next. Built with Python, SQL, NLP, machine learning and Streamlit.

[📊 GitHub Repository](https://github.com/ParasKamble02/Careerlytics)

## Table of Contents

- [Overview](#overview)
- [Screenshots](#screenshots)
- [Project Objectives](#-project-objectives)
- [Analytics Workflow](#-analytics-workflow)
- [Features](#features)
- [How the Metrics Work](#how-the-metrics-work)
- [Machine Learning Model](#machine-learning-model)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Dataset](#dataset)
- [Configuration](#configuration)
- [Database and SQL](#database-and-sql)
- [Limitations](#limitations)
- [Project Scope](#project-scope)
- [Roadmap](#roadmap)
- [Author](#author)
- [License](#license)

---

## Overview

**Careerlytics** is an interactive career-intelligence web application built using Python, pandas, scikit-learn, Plotly, SQL and Streamlit. A user signs up, uploads a resume (PDF, DOCX or TXT) and picks a target role. The application extracts skills with NLP, scores the resume, ranks job postings with a machine-learning-assisted match score, analyses the job market for the chosen role, and turns the gap between the resume and the market into a prioritised learning roadmap.

**Questions the app helps answer**

- How strong is my resume, and what does it say about me?
- Which jobs fit my skills, experience and education best, and why?
- What does the job market demand for my target role, in skills, experience, salary and location?
- Which skills am I missing, and which should I learn first?
- How much would my matches improve if I learned a specific skill?

---

## Screenshots

> Save your screenshots in a `screenshots/` folder using these names and they will appear here.

| Dashboard | Resume Insights |
|---|---|
| ![Dashboard](screenshots/Dashboard.png) | ![Resume Insights](screenshots/ResumeInsights.png) |

| Job Market | Job Matcher |
|---|---|
| ![Job Market](screenshots/JobMarket.png) | ![Job Matcher](screenshots/JobMatcher.png) |

| Skill Gap & Roadmap | Upload Resume |
|---|---|
| ![Skill Gap](screenshots/SkillGap.png) | ![Upload Resume](screenshots/UploadResume.png) |

---

## 🎯 Project Objectives

- Extract skills, education, experience and projects from a resume using NLP
- Score a resume with a transparent, rule-based breakdown
- Analyse the job market for a specific target role
- Recommend jobs with an explainable match score
- Predict match strength with a machine-learning model
- Identify skill gaps and rank them by priority
- Build a prerequisite-aware learning roadmap
- Let users test "what if I learned this skill?" before investing time
- Provide secure, per-user accounts with saved resume analyses

---

## 📊 Analytics Workflow

```
Sign up / Log in
        ↓
Upload Resume (PDF / DOCX / TXT) + choose Target Role
        ↓
NLP: skills, education, experience, projects
        ↓
Resume score + strengths / improvements
        ↓
Job postings (SQL database) → NLP skill extraction per posting
        ↓
Feature engineering (coverage, experience, education, text similarity, role fit)
        ↓
Random Forest match probability + blended match score
        ↓
Ranked job recommendations with explanations
        ↓
Skill-gap analysis → priority → learning roadmap → what-if simulation
```

---

## Features

The sidebar follows the user journey: **Upload Resume → Dashboard → Resume Insights → Job Market → Job Matcher → Skill Gap & Roadmap**. Until a resume is analysed, only Upload Resume is available.

### 🔐 Accounts

- Sign up with username, email and password; log in to restore the saved analysis
- Passwords are stored as salted PBKDF2-SHA256 hashes, never as plain text
- Each user's resume analysis and saved jobs belong to their own account

### 📄 Upload Resume

- Upload a **PDF, DOCX or TXT** resume, or paste text
- Choose a **target role**. It is applied automatically on Job Market, Job Matcher and Skill Gap, and can be changed here or in Settings

### 📊 Dashboard

- **KPI cards:** resume score, skills recognised, experience, education
- **Your Career Fit:** resume score, skill coverage and top-10 match as bubbles
- **Top Recommended Jobs** for the target role
- **Matches by Role** donut and **Recommended Actions**

### 🧾 Resume Insights

- **Resume Skills** with evidence strength (mentions plus use in projects and experience)
- **Score breakdown** across six components
- **Strengths**, **Improve** suggestions, **Missing skills for your target** and **Projects detected**

### 🌍 Job Market

Everything on this page is filtered to the target role. Location and period filters are available.

- **Skills:** most demanded skills (marked by whether you have them) and what the job demands from applicants: typical experience, education asked, and essential, commonly requested and nice-to-have skills
- **Roles & locations:** role distribution across the market with the target role highlighted, and location demand for the role
- **Salary:** total jobs, average, minimum and maximum salary, plus median salary by experience band and by location

### 🎯 Job Matcher

- Ranked jobs with role, location, match-level and minimum-score filters (role pre-set to the target role)
- Click a job to see matched and missing skills, the ML match probability and a component-by-component **"Why this score"** chart
- Save jobs to your applications list

### 🧭 Skill Gap & Roadmap

- **Skill gap** donut against the role's 10 most requested skills, and an **Extracted skills** card
- **High / Medium / Low** priority skills with demand, relevance, 30-day trend and match lift
- **Recommended learning order** with prerequisites placed first and an estimated number of weeks
- **What-if simulator:** pick skills to add and see the effect on the average top-20 match and the number of strong matches

### ⚙️ Settings

- Update target role, locations, experience, education and skills at any time

---

## How the Metrics Work

| Metric | Definition |
|---|---|
| **Match score** | 45% ML match probability + 20% skill coverage + 10% role fit + 10% location fit + 10% experience fit + 5% resume-text similarity (`SCORE_WEIGHTS` in `careerlytics/config.py`) |
| **Match level** | **Strong** ≥ 75%, **Good** ≥ 60%, **Stretch** below 60% |
| **Skill coverage** | Required skills found on the resume ÷ skills required by the job |
| **Core-skill coverage** | Same, counting only must-have skills (text before "Good to have") |
| **Resume score (100)** | Skill breadth 25 + Market alignment 20 + Projects 15 + Education & experience 15 + Quantified impact 15 + Contact & links 10 |
| **Evidence strength** | Base 35, plus mentions, use in projects and use in experience (capped at 100) |
| **Skill priority** | Market demand in the target role × relevance to your top-50 jobs × gap, with up to +30% for skills whose demand is rising |
| **Priority level** | **High** ≥ 60, **Medium** ≥ 30, **Low** below 30 (scores are scaled so the top skill is 100) |
| **Match lift** | Increase in your average top-20 match score if you learned that single skill |
| **ML probability limits** | Clipped to 2%–98% so that near-perfect matches still rank distinctly |

---

## Machine Learning Model

| Item | Detail |
|---|---|
| **Algorithm** | Random Forest (250 trees, max depth 10), compared with a logistic-regression baseline |
| **Training data** | 30,000 synthetic candidate-job pairs |
| **Features** | skill match, core-skill match, demand-weighted match, experience fit, education fit, TF-IDF text similarity, role fit, breadth |
| **Hold-out results** | Accuracy about 95%, ROC-AUC about 0.99 |
| **Labels** | Defined by a documented fit rubric plus threshold rules and noise (see `careerlytics/ml_model.py`) |

> **Important:** no public dataset of real hiring outcomes exists, so labels are synthetic. The model learns the scoring rubric, not real recruiter behaviour, and a simple logistic baseline performs almost as well. Replace the labels with real interview or offer outcomes to turn this into a genuinely predictive model.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Application logic |
| **Streamlit** | Web application, multi-page layout and sessions |
| **pandas / NumPy** | Data processing and analysis |
| **scikit-learn** | Random Forest model, TF-IDF text similarity |
| **Plotly** | Interactive charts |
| **PyMuPDF / pypdf** | PDF text extraction |
| **SQLite / MySQL** | Job, user and application storage |
| **Regex-based NLP** | Skill, education, experience and project extraction |
| **HTML / CSS / SVG** | Custom theme, cards and logo |
| **Git & GitHub** | Version control and hosting |

---

## Project Structure

```
Careerlytics/
├── README.md
├── app.py                        # Entry point: login gate, resume gate, navigation
├── requirements.txt
├── .streamlit/
│   └── config.toml               # Theme and server settings
├── careerlytics/                 # Core package
│   ├── config.py                 # Paths, score weights, match levels
│   ├── skills.py                 # Skill taxonomy, prerequisites, learning weeks
│   ├── nlp.py                    # Skill extraction, resume parsing and scoring
│   ├── profile.py                # Candidate profile
│   ├── data_gen.py               # Synthetic job-posting generator
│   ├── db.py                     # SQLite / MySQL database layer
│   ├── auth.py                   # Password hashing, sign-up, log-in
│   ├── matching.py               # Feature engineering, ranking, explanations
│   ├── ml_model.py               # Random Forest training
│   ├── analytics.py              # Market analytics
│   ├── gap.py                    # Skill-gap priority and roadmap
│   ├── service.py                # Profile building and target-role inference
│   ├── bootstrap.py              # Database seeding
│   ├── state.py                  # Cached loaders and per-run context
│   ├── nav.py                    # Page registry
│   └── ui.py                     # Theme, components, chart helpers
├── views/                        # One module per page
│   ├── login.py
│   ├── resume.py                 # Upload Resume
│   ├── dashboard.py
│   ├── insights.py               # Resume Insights
│   ├── market.py                 # Job Market
│   ├── matcher.py                # Job Matcher
│   ├── skillgap.py               # Skill Gap & Roadmap
│   └── settings.py
├── sql/
│   ├── schema_mysql.sql          # MySQL schema
│   └── analytics_queries.sql     # Example analytical queries
├── tests/
│   └── test_core.py
└── screenshots/
```

The database (`data/careerlytics.db`) and the trained model (`models/match_model.joblib`) are created automatically on first run.

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ParasKamble02/Careerlytics.git
cd Careerlytics
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

`requirements.txt` contains:

```
streamlit>=1.40,<1.50
pandas>=2.0
numpy>=1.26
scikit-learn>=1.3
plotly>=5.20
joblib>=1.3
pymupdf>=1.24
pypdf>=4.0
```

### 4. Run the app

```bash
python -m streamlit run app.py
```

Open `http://localhost:8501`. The first launch takes about 10 to 15 seconds while the job database is created and the model is trained.

### 5. Use it

1. **Sign up**, then **upload your resume** and choose a **target role**.
2. You land on the **Dashboard**, then follow the sidebar through Resume Insights, Job Market, Job Matcher and Skill Gap & Roadmap.

### Run the tests

```bash
python -m pip install pytest
python -m pytest -q
```

---

## Dataset

The job market is a **synthetic dataset generated by `careerlytics/data_gen.py`**: 1,240 postings with fictional companies.

| Area | Detail |
|---|---|
| **Roles (8)** | Data Analyst, BI Analyst, Business Analyst, Data Scientist, ML Engineer, Data Engineer, Python Developer, Full Stack Developer |
| **Locations (7)** | Bangalore, Pune, Mumbai, Hyderabad, Delhi NCR, Chennai, Remote |
| **Fields** | title, role, company, location, salary (LPA), experience range, education, description, posted date |
| **Skills** | 70 skills in 9 categories, extracted from each description by NLP (must-have vs good-to-have) |
| **Trends** | Some skills (for example Power BI, Docker, LLMs) are generated more often in recent postings |

Skills are written inside free-text descriptions, sometimes as aliases (for example "MS Excel" or "PySpark"), so the NLP extractor works the way it would on scraped postings. To use real postings, insert them into the `jobs` table and run the same skill extraction.

---

## Configuration

Theme and server settings live in `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#4F5BD5"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F3F4FA"
textColor = "#2B2F4A"
font = "sans serif"
```

Score weights, match levels and the number of seeded jobs are in `careerlytics/config.py`.

**Use MySQL instead of SQLite (optional)**

```bash
python -m pip install sqlalchemy pymysql
mysql -u root -p -e "CREATE DATABASE careerlytics"
# Windows PowerShell:  $env:CAREERLYTICS_DB_URL="mysql+pymysql://user:password@localhost:3306/careerlytics"
# macOS / Linux:       export CAREERLYTICS_DB_URL="mysql+pymysql://user:password@localhost:3306/careerlytics"
python -m streamlit run app.py
```

---

## Database and SQL

| Table | Purpose |
|---|---|
| `jobs` | Job postings (title, role, company, location, salary, experience, education, description, date) |
| `job_skills` | Skills required by each job, flagged as core or optional |
| `users` | Accounts: username, email, password hash and salt, saved profile |
| `resume_skills` | Skills extracted from each user's resume |
| `applications` | Jobs a user has saved, with the match score |

The schema for MySQL is in [`sql/schema_mysql.sql`](sql/schema_mysql.sql), and example analytical queries (skill demand, role salary statistics, top skills per role, salary by skill count) are in [`sql/analytics_queries.sql`](sql/analytics_queries.sql). All application SQL uses named parameters, so the same statements run on SQLite and MySQL.

---

## Limitations

- **Job postings are synthetic.** Percentages, salaries and role shares describe the generated data, not the real job market.
- **ML labels are synthetic**, as described in [Machine Learning Model](#machine-learning-model).
- **Skill extraction is dictionary-based** (70 skills). Skills outside the taxonomy are ignored, and scanned PDFs need OCR.
- **Accounts are basic:** no email verification or password reset, and a browser refresh ends the session (the saved resume analysis returns on the next log-in).
- **No scraping or live feeds** are included.
- Small groups (for example one role in one city) can produce shares that move several points from run to run.

---

## Project Scope

**Included**

- Resume parsing, scoring and feedback
- Role-specific job-market analytics
- Explainable job recommendations with an ML-assisted score
- Skill-gap prioritisation, roadmap and what-if simulation
- Secure per-user accounts and saved applications

**Future Enhancement**

- Real job-posting ingestion (APIs or CSV import)
- Real hiring-outcome labels for the model
- OCR for scanned resumes
- Email verification and password reset
- Multiple target roles and role comparison
- PDF export of the career report
- Deployment on Streamlit Community Cloud

---

## Roadmap

- [x] Skill taxonomy and NLP extraction
- [x] Resume parsing and scoring (PDF, DOCX, TXT)
- [x] SQL database (SQLite and MySQL)
- [x] Match engine and Random Forest model
- [x] Job-market analytics for the target role
- [x] Skill-gap priority, roadmap and what-if simulator
- [x] User accounts and saved resume analysis
- [x] Custom dashboard theme and logo
- [x] Deployment

---

## Author

**Paras Kamble**
B.Tech — Artificial Intelligence & Data Science
Loknete Shamrao Peje Government College of Engineering, Ratnagiri, Maharashtra

Areas of interest: Data Analytics, Data Science, Python, SQL, Data Visualization, Machine Learning

---

## License

This project is intended for educational, portfolio and demonstration purposes.
