import streamlit as st
import pickle

from utils.text_extraction import extract_text
from utils.preprocessing import clean_resume
from utils.skills import extract_skills, missing_skills, skills_dict

# -------------------------------
# 🔥 Page Config
# -------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="centered"
)

# -------------------------------
# 🔥 Load Model
# -------------------------------
model = pickle.load(open("model.pkl", "rb"))
tfidf = pickle.load(open("tfidf.pkl", "rb"))

# -------------------------------
# 🔥 Multi-role Detection
# -------------------------------
def infer_roles_from_skills(found_skills):
    role_scores = {}

    for role, skills in skills_dict.items():
        match = len([s for s in found_skills if s in skills])
        role_scores[role] = match

    sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_roles[:3]

# -------------------------------
# 🔥 Resume Scoring
# -------------------------------
def calculate_score(found_skills, role):
    required = skills_dict.get(role, [])

    score = 0
    for skill in required:
        if skill in found_skills:
            score += 10

    return min(score, 100)

# -------------------------------
# 🔥 Resume Section Detection
# -------------------------------
def analyze_resume_sections(text):
    text = text.lower()

    return {
        "has_projects": "project" in text,
        "has_experience": "experience" in text or "worked" in text,
        "has_education": "education" in text
    }

# -------------------------------
# 🔥 AI Feedback
# -------------------------------
def generate_feedback(role, missing, score):
    feedback = []

    if score < 40:
        feedback.append(f"Your profile is not aligned with {role}. Add core skills.")
    elif score < 70:
        feedback.append(f"You are partially fit for {role}. Improve missing skills.")
    else:
        feedback.append(f"You are a strong candidate for {role}.")

    if missing:
        feedback.append(f"Critical missing skills: {', '.join(missing[:5])}")

    feedback.append("Add projects to demonstrate practical experience.")
    feedback.append("Use action verbs and quantify achievements.")

    return feedback

# -------------------------------
# 🔥 UI Styling
# -------------------------------
st.markdown("""
<style>
.title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #4CAF50;
}

.subtitle {
    text-align: center;
    color: gray;
    margin-bottom: 25px;
}

/* ✅ FIXED SKILL TAGS */
.badge {
    display: inline-block;
    padding: 6px 12px;
    margin: 5px;
    border-radius: 10px;
    background-color: #d1e7dd;  /* soft green */
    color: #0f5132;             /* dark text */
    font-weight: 500;
}

/* ❌ FIXED MISSING SKILLS */
.missing {
    background-color: #f8d7da;  /* soft red */
    color: #842029;             /* dark red text */
    font-weight: 500;
}

/* Optional hover effect (looks premium ) */
.badge:hover {
    transform: scale(1.05);
    transition: 0.2s;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 🔥 Header
# -------------------------------
st.markdown('<div class="title"> AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Industry-Level Resume Screening System</div>', unsafe_allow_html=True)

# -------------------------------
# 🔥 Upload
# -------------------------------
file = st.file_uploader("📤 Upload Resume", type=["pdf", "docx", "jpg", "png"])

# -------------------------------
# 🔥 MAIN LOGIC
# -------------------------------
if file:
    with st.spinner("🔍 Analyzing resume..."):
        text = extract_text(file)

        if text:
            cleaned = clean_resume(text)
            vectorized = tfidf.transform([cleaned])

            # Model prediction (secondary)
            model_role = model.predict(vectorized)[0]

            # Skill extraction
            skills = extract_skills(text)

            # Multi-role detection
            top_roles = infer_roles_from_skills(skills)
            primary_role = top_roles[0][0]

            # Score
            score = calculate_score(skills, primary_role)

            # Missing skills
            missing = missing_skills(primary_role, skills)

            # Resume completeness
            sections = analyze_resume_sections(text)

            # Feedback
            feedback = generate_feedback(primary_role, missing, score)

            st.success("✅ Analysis Complete")

            # -------------------------------
            # 🎯 Top Roles
            # -------------------------------
            st.markdown("### 🎯 Top Matching Roles")
            for role, val in top_roles:
                st.write(f"**{role}** → {val} skill matches")

            # -------------------------------
            # 📊 Score
            # -------------------------------
            st.markdown("### 📊 Resume Strength")
            st.progress(score)

            if score < 40:
                st.error(f"Weak Resume ({score}%)")
            elif score < 70:
                st.warning(f"Moderate Resume ({score}%)")
            else:
                st.success(f"Strong Resume ({score}%)")

            # -------------------------------
            # 🏷️ Skills
            # -------------------------------
            st.markdown("### 🏷️ Detected Skills")
            st.markdown(" ".join([f"<span class='badge'>{s}</span>" for s in skills]), unsafe_allow_html=True)

            # -------------------------------
            # ❌ Missing Skills
            # -------------------------------
            st.markdown("### ❌ Missing Skills")
            st.markdown(" ".join([f"<span class='badge missing'>{m}</span>" for m in missing]), unsafe_allow_html=True)

            # -------------------------------
            # 📄 Resume Sections
            # -------------------------------
            st.markdown("### 📄 Resume Completeness")
            st.write("Projects:", "✅" if sections["has_projects"] else "❌")
            st.write("Experience:", "✅" if sections["has_experience"] else "❌")
            st.write("Education:", "✅" if sections["has_education"] else "❌")

            # -------------------------------
            # 🤖 Feedback
            # -------------------------------
            st.markdown("### 🤖 AI Feedback")
            for f in feedback:
                st.info(f)

            # -------------------------------
            # 🔍 Debug
            # -------------------------------
            with st.expander("🔍 Detailed Analysis"):
                st.write("Model Role:", model_role)
                st.write("Skills:", skills)
                st.write("Missing:", missing)

        else:
            st.error("❌ Could not extract text from file")