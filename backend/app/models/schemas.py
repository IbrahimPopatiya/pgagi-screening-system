from pydantic import BaseModel
from typing import Literal


class ResumeProfile(BaseModel):
    skills: list[str]
    technologies: list[str]
    domains: list[str]
    experience_level: Literal["entry", "mid", "senior"]
