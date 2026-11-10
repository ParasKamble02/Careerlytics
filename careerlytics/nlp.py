from __future__ import annotations

import re
from collections import Counter
from datetime import date

from .skills import TAXONOMY

#skill extraction
_ALIAS_TO_SKILL: dict[str, str] = {}
for _skill, (_cat, _aliases) in TAXONOMY.items():
    for _a in {_skill.lower(), *_aliases}:
        _ALIAS_TO_SKILL[_a] = _skill

_SKILL_RE = re.compile(
    r"(?<![\w+#])(" + "|".join(re.escape(a) for a in sorted(_ALIAS_TO_SKILL, key=len, reverse=True)) + r")(?![\w+#])",
    re.IGNORECASE,
)

def count_skills(text: str) -> Counter:
    """Return {canonical skill: number of mentions}."""
    return Counter(_ALIAS_TO_SKILL[m.group(1).lower()] for m in _SKILL_RE.finditer(text or ""))

def extract_skills(text: str) -> list[str]:
    return sorted(count_skills(text))

def extract_job_skills(description: str) -> list[tuple[str, int]]:
    parts = re.split(r"good to have\s*:|nice to have\s*:|preferred\s*:", description, maxsplit=1, flags=re.I)
    core = set(count_skills(parts[0]))
    optional = set(count_skills(parts[1])) - core if len(parts) > 1 else set()
    return [(s, 1) for s in sorted(core)] + [(s, 0) for s in sorted(optional)]


#resume parsing
_SECTION_KEYS = [
    ("skills", ("technical skills", "skills", "core competencies", "competencies")),
    ("projects", ("academic projects", "personal projects", "projects", "project")),
    ("education", ("education", "academics", "academic background")),
    ("experience", ("work experience", "professional experience", "experience", "internships", "internship")),
    ("certifications", ("certifications", "certification", "courses")),
    ("achievements", ("achievements", "awards")),
    ("summary", ("summary", "profile", "objective", "about me")),
]
_HEAD_RE = re.compile(
    r"^(?P<h>" + "|".join(k for _, ks in _SECTION_KEYS for k in sorted(ks, key=len, reverse=True)) + r")\s*(?P<colon>:)?\s*(?P<rest>.*)$",
    re.IGNORECASE,
)


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {"header": []}
    current = "header"
    for raw in text.splitlines():
        line = raw.strip().lstrip("#*-_ ").rstrip("*_ ")
        m = _HEAD_RE.match(line)
        if m and (m.group("colon") or not m.group("rest")):
            h = m.group("h").lower()
            current = next(name for name, ks in _SECTION_KEYS if h in ks)
            sections.setdefault(current, [])
            if m.group("rest"):
                sections[current].append(m.group("rest"))
            continue
        sections.setdefault(current, []).append(raw)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


_EDU_LEVELS = [
    (4, "PhD", r"\bph\.?d\b|doctorate"),
    (3, "Master", r"\bm\.?tech\b|\bm\.?sc\b|\bm\.s\b|\bmca\b|\bmba\b|\bm\.e\b|\bmaster"),
    (2, "Bachelor", r"\bb\.?tech\b|\bb\.?sc\b|\bb\.e\b|\bbca\b|\bbba\b|\bb\.?com\b|\bbachelor"),
    (1, "Diploma", r"\bdiploma\b"),
]


def detect_education(text: str) -> tuple[int, str]:
    for level, label, pattern in _EDU_LEVELS:
        if re.search(pattern, text, re.IGNORECASE):
            return level, label
    return 2, "Bachelor"


_MONTHS = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
_RANGE_RE = re.compile(
    r"\b(?:(?P<m1>[A-Za-z]{3,9})\.?\s+)?(?P<y1>(?:19|20)\d{2})\s*(?:-|–|—|to)\s*"
    r"(?:(?P<m2>[A-Za-z]{3,9})\.?\s+)?(?P<y2>(?:19|20)\d{2}|present|current|till date)", re.I)


def estimate_experience(text: str, sections: dict[str, str]) -> float:
    """Years of experience: explicit '3 years of experience' wins, else sum the date ranges in the Experience section."""
    stated = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\b(?:\s+of)?\s+(?:\w+\s+){0,2}experience", text, re.I)]
    if stated:
        return max(stated)
    today, total = date.today(), 0.0
    for line in sections.get("experience", "").splitlines():
        for m in _RANGE_RE.finditer(line):
            y1, y2 = int(m["y1"]), (today.year if not m["y2"].isdigit() else int(m["y2"]))
            m1 = _MONTHS.get((m["m1"] or "jan")[:3].lower(), 1)
            m2 = today.month if not m["y2"].isdigit() else _MONTHS.get((m["m2"] or "jan")[:3].lower(), 1)
            months = max(1, (y2 - y1) * 12 + (m2 - m1) + 1)
            total += months / 12 * (0.8 if "intern" in line.lower() else 1.0)
    return round(min(total, 20) * 2) / 2


def extract_projects(sections: dict[str, str]) -> list[str]:
    """Project titles. If the resume uses 'Title | tools' lines, only those are titles; otherwise short non-bullet lines."""
    lines = [ln.strip() for ln in sections.get("projects", "").splitlines() if ln.strip()]
    piped = [ln for ln in lines if "|" in ln]
    out = []
    for ln in (piped or lines):
        if ln[0] in "-•*–·▪" or ln[0].islower() or ln.endswith((".", ",", ";")):
            continue
        title = ln.split("|")[0].strip(" –-:")
        if 2 <= len(title.split()) <= 12 and len(title) <= 90:
            out.append(title)
    return list(dict.fromkeys(out))[:8]


_NUM_RE = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?\s?(?:%|[kKmM]\b|x\b|\+)|\b\d{1,3}(?:,\d{3})+\b|\b\d{2,}\b")


def count_quantified(text: str) -> int:
    """Numbers that quantify impact (%, 1,470 records, 50k ...) - ignoring years, phone numbers, emails and links."""
    t = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+|https?://\S+|\+?\d[\d\s-]{8,}\d|\b(?:19|20)\d{2}\b", " ", text)
    return len(_NUM_RE.findall(t))


def parse_resume(text: str) -> dict:
    """Turn raw resume text into a structured dict (skills with evidence strength, education, projects...)."""
    sections = split_sections(text)
    total = count_skills(text)
    in_projects = count_skills(sections.get("projects", ""))
    in_experience = count_skills(sections.get("experience", ""))
    strength = {
        s: int(min(100, 35 + 12 * min(n - 1, 3) + 18 * min(in_projects[s], 2) + 12 * min(in_experience[s], 2)))
        for s, n in total.items()
    }
    edu_level, edu_label = detect_education(sections.get("education") or text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    first = lines[0].lstrip("# ").strip() if lines else ""
    name = first if 1 <= len(first.split()) <= 4 and not re.search(r"[@\d:]", first) else "Candidate"
    quantified = count_quantified(text)
    return {
        "name": name,
        "skills": strength,
        "experience": estimate_experience(text, sections),
        "education_level": edu_level,
        "education_label": edu_label,
        "projects": extract_projects(sections),
        "projects_text": sections.get("projects", ""),
        "sections_found": [k for k in ("skills", "projects", "education", "experience", "certifications") if sections.get(k)],
        "quantified": quantified,
        "has_email": bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)),
        "has_phone": bool(re.search(r"\+\d{1,3}[\s-]?\d{5}[\s-]?\d{5}|\b\d{10}\b|\b\d{5}[\s-]\d{5}\b", text)),
        "has_links": bool(re.search(r"github|linkedin", text, re.I)),
        "word_count": len(text.split()),
        "text": text,
    }


def score_resume(parsed: dict, market_alignment: float = 0.5) -> tuple[float, dict]:
    """Resume score out of 100 with a transparent breakdown."""
    sections = parsed["sections_found"]
    b = {
        "Skill breadth": 25 * min(1, len(parsed["skills"]) / 15),
        "Market alignment": 20 * float(market_alignment),
        "Projects": 15 * min(1, len(parsed["projects"]) / 4),
        "Education & experience": (7 if "education" in sections else 0) + (8 if ("experience" in sections or parsed["experience"] > 0) else 0),
        "Quantified impact": 15 * min(1, parsed["quantified"] / 6),
        "Contact & links": 4 * parsed["has_email"] + 2 * parsed["has_phone"] + 4 * parsed["has_links"],
    }
    b = {k: round(v, 1) for k, v in b.items()}
    return round(sum(b.values()), 1), b


def resume_feedback(parsed: dict, breakdown: dict) -> tuple[list[str], list[str]]:
    """(strengths, improvements) in plain English."""
    good, fix = [], []
    n = len(parsed["skills"])
    (good if n >= 10 else fix).append(f"{n} recognised skills" + ("" if n >= 10 else " - aim for 10-15 relevant ones"))
    (good if len(parsed["projects"]) >= 2 else fix).append(
        f"{len(parsed['projects'])} project(s) listed" + ("" if len(parsed["projects"]) >= 2 else " - add 2-3 projects with tools used"))
    (good if parsed["quantified"] >= 3 else fix).append(
        "Quantified achievements present" if parsed["quantified"] >= 3 else "Add numbers to bullets (e.g. 'reduced report time by 40%')")
    if not parsed["has_links"]:
        fix.append("Add your GitHub / LinkedIn link")
    if breakdown["Market alignment"] >= 12:
        good.append("Skills align well with current market demand")
    elif breakdown["Market alignment"] < 8:
        fix.append("Few of the most in-demand skills are covered - see Skill Gap")
    return good, fix


def _read_docx(data: bytes) -> str:
    """Plain-text extraction from a .docx (a zip of XML) using only the standard library."""
    import io
    import zipfile
    from xml.etree import ElementTree as ET

    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        root = ET.fromstring(z.read("word/document.xml"))
        rels = z.read("word/_rels/document.xml.rels").decode("utf-8", "ignore") if "word/_rels/document.xml.rels" in z.namelist() else ""
    paras = ["".join(t.text or "" for t in p.iter(ns + "t")) for p in root.iter(ns + "p")]
    # keep GitHub / LinkedIn hyperlinks (stored as relationship targets, not as visible text)
    paras += sorted({m.lower() for m in re.findall(r"https?://(?:www\.)?((?:github|linkedin)\.com)", rels, re.I)})
    return "\n".join(paras)


def read_resume_bytes(data: bytes, filename: str) -> str:
    """Extract text from an uploaded resume: PDF (PyMuPDF, falling back to pypdf), DOCX, or plain text."""
    name = filename.lower()
    if name.endswith(".docx"):
        return _read_docx(data)
    if name.endswith(".pdf"):
        try:  # PyMuPDF (newer versions import as `pymupdf`, older as `fitz`)
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            with fitz.open(stream=data, filetype="pdf") as doc:
                return "\n".join(page.get_text() for page in doc)
        except ImportError:
            pass
        try:
            import io

            from pypdf import PdfReader

            return "\n".join((pg.extract_text() or "") for pg in PdfReader(io.BytesIO(data)).pages)
        except ImportError:
            raise RuntimeError("No PDF reader installed. Run:  python -m pip install pymupdf pypdf  then restart the app.") from None
    return data.decode("utf-8", errors="ignore")
