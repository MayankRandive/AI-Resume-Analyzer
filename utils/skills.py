# 🔥 Improved Skills Dictionary
skills_dict = {
    "data science": [
        "python", "machine learning", "pandas", "numpy",
        "sql", "data analysis", "data cleaning", "power bi"
    ],

    "data analyst": [
        "excel", "sql", "power bi", "tableau",
        "data visualization", "data cleaning", "statistics"
    ],

    "python_developer": [
        "python", "django", "flask", "api", "sql"
    ],

    "software_developer": [
        "java", "c++", "git", "data structures", "algorithms"
    ],

    "web_developer": [
        "html", "css", "javascript", "react", "node"
    ]
}

# 🔥 IMPORTANT
__all__ = ["skills_dict", "extract_skills", "missing_skills"]

# 🔍 Improved Skill Extraction
def extract_skills(text):
    text = text.lower()
    found = []

    for role_skills in skills_dict.values():
        for skill in role_skills:
            if skill in text:   # 🔥 allows multi-word matching
                found.append(skill)

    return list(set(found))


# 🚨 Improved Missing Skills Logic
def missing_skills(role, found_skills):
    required = skills_dict.get(role, [])

    missing = [skill for skill in required if skill not in found_skills]

    # 🔥 NEW: detect weak resume
    if len(found_skills) < 2:
        return ["⚠️ Profile too weak - add more skills"] + missing

    return missing