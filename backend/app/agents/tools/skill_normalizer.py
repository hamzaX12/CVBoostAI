"""
CVBoost AI — Skill Normalizer Tool
Canonicalizes skill names (e.g. "PowerBI" → "Power BI", "python3" → "Python").
"""
from __future__ import annotations

import re
from langchain_core.tools import tool

# Known canonical forms (case-insensitive lookup → canonical)
_CANONICAL_MAP: dict[str, str] = {
    "powerbi": "Power BI",
    "power bi": "Power BI",
    "power-bi": "Power BI",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node js": "Node.js",
    "reactjs": "React",
    "react.js": "React",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angularjs": "Angular",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "docker": "Docker",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "aws": "Amazon Web Services",
    "amazon web services": "Amazon Web Services",
    "azure": "Microsoft Azure",
    "ms azure": "Microsoft Azure",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "natural language processing": "NLP",
    "nlp": "NLP",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",  # ambiguous but common in AI context
    "python3": "Python",
    "python 3": "Python",
    "r language": "R",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "tableau": "Tableau",
    "looker": "Looker",
    "dbt": "dbt",
    "apache spark": "Apache Spark",
    "pyspark": "PySpark",
    "hadoop": "Hadoop",
    "airflow": "Apache Airflow",
    "apache airflow": "Apache Airflow",
    "mlflow": "MLflow",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "langchain": "LangChain",
    "openai": "OpenAI",
    "huggingface": "Hugging Face",
    "hugging face": "Hugging Face",
    "excel": "Microsoft Excel",
    "ms excel": "Microsoft Excel",
    "word": "Microsoft Word",
    "powerpoint": "Microsoft PowerPoint",
    "linux": "Linux",
    "bash": "Bash",
    "shell scripting": "Shell Scripting",
    "sql": "SQL",
    "nosql": "NoSQL",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "kafka": "Apache Kafka",
    "apache kafka": "Apache Kafka",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "agile": "Agile",
    "scrum": "Scrum",
    "jira": "Jira",
    "confluence": "Confluence",
    "figma": "Figma",
    "adobe": "Adobe Creative Suite",
}


@tool
def normalize_skill(skill: str) -> str:
    """
    Normalize a skill name to its canonical form.
    Example: 'powerbi' → 'Power BI', 'sklearn' → 'scikit-learn'
    Returns the canonical name if found, otherwise title-cases the input.
    """
    key = skill.strip().lower()
    if key in _CANONICAL_MAP:
        return _CANONICAL_MAP[key]
    # Try without special chars
    clean_key = re.sub(r"[^a-z0-9\s]", "", key).strip()
    if clean_key in _CANONICAL_MAP:
        return _CANONICAL_MAP[clean_key]
    # Default: title-case with some smart rules
    return _smart_title_case(skill.strip())


def _smart_title_case(s: str) -> str:
    """Title-case but keep known acronyms uppercase."""
    _ACRONYMS = {"ai", "ml", "nlp", "api", "sql", "nosql", "iot", "bi", "erp", "crm", "etl", "dbt"}
    words = s.split()
    result = []
    for w in words:
        if w.lower() in _ACRONYMS:
            result.append(w.upper())
        else:
            result.append(w.capitalize())
    return " ".join(result)
