from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

@dataclass
class Profile:
    name: str = "Demo Student"
    skills: dict = field(default_factory=dict)        # skill -> evidence strength (0-100)
    experience: float = 0.0                           # years
    education_level: int = 2                          # 1 diploma, 2 bachelor, 3 master, 4 phd
    education_label: str = "Bachelor"
    projects: list = field(default_factory=list)
    projects_text: str = ""
    targets: list = field(default_factory=list)       # preferred roles
    locations: list = field(default_factory=list)     # preferred locations 
    resume_score: float = 0.0
    score_breakdown: dict = field(default_factory=dict)
    strengths: list = field(default_factory=list)
    improvements: list = field(default_factory=list)
    is_demo: bool = False

    def match_text(self) -> str:
        """Text used for TF-IDF similarity against job descriptions."""
        return " ".join(list(self.skills) + [self.projects_text])

    def with_skills(self, extra) -> "Profile":
        d = asdict(self)
        d["skills"] = {**self.skills, **{s: 60 for s in extra}}
        return Profile(**d)

    def key(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, default=str)

    @classmethod
    def from_dict(cls, d: dict) -> "Profile":
        return cls(**d)

    def to_dict(self) -> dict:
        return asdict(self)
