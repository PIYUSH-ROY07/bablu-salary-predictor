import re
from typing import Optional
import requests
import streamlit as st
from groq import Groq
from streamlit_lottie import st_lottie

# 1. THE SINGLE PAGE CONFIG (Must be first, and only used once)
st.set_page_config(
    page_title="Bablu Salary Predictor",
    page_icon="💰",
    layout="wide",
)

# 2. MEMORIZE THE ANIMATION (Prevents reloading on every click)
@st.cache_data
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_anim = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_0yfsb3a1.json")

# 3. CREATE TWO COLUMNS (Form on left, Animation on right)
col_form, col_anim = st.columns([1.5, 1])

# 4. PUT ANIMATION IN RIGHT COLUMN WITH A STATIC KEY
with col_anim:
    if lottie_anim:
        st_lottie(lottie_anim, height=450, key="salary_animation")

# 5. START THE FORM ON THE LEFT COLUMN
with col_form:
    with st.form("salary_prediction_form"):
        st.title("Bablu Salary Predictor")
        st.markdown("Enter your profile details below to get a market-aligned salary prediction.")

        PROFESSIONAL_ROLES = [
        "Software Engineer",
        "Data Scientist",
        "Product Manager",
        "Business Analyst",
        "Marketing Manager",
        "Sales Executive",
        "HR Manager",
        "Accountant / CA",
        "Civil Engineer",
        "Mechanical Engineer",
        "Electrical Engineer",
        "Doctor / Physician",
        "Nurse",
        "Teacher / Professor",
        "Graphic Designer",
        "UI/UX Designer",
        "Operations Manager",
        "Supply Chain Manager",
        "Customer Support Lead",
        "Administrative Officer",
        "Legal Associate",
        "Architect",
        "Content Writer",
        "Digital Marketing Specialist",
        "DevOps Engineer",
        "Cybersecurity Analyst",
        "Other",
]

        INDIAN_STATES = [
        "Andhra Pradesh",
        "Arunachal Pradesh",
        "Assam",
        "Bihar",
        "Chhattisgarh",
        "Goa",
        "Gujarat",
        "Haryana",
        "Himachal Pradesh",
        "Jharkhand",
        "Karnataka",
        "Kerala",
        "Madhya Pradesh",
        "Maharashtra",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Nagaland",
        "Odisha",
        "Punjab",
        "Rajasthan",
        "Sikkim",
        "Tamil Nadu",
        "Telangana",
        "Tripura",
        "Uttar Pradesh",
        "Uttarakhand",
        "West Bengal",
        "Delhi (NCT)",
        "Jammu and Kashmir",
        "Ladakh",
        "Puducherry",
        "Chandigarh",
]

        METRIC_OPTIONS = [
        "Below 10th",
        "10th / SSC",
        "12th / HSC",
        "Diploma (after 10th)",
        "Diploma (after 12th)",
        "ITI",
        "Not applicable",
]

        COLLEGE_DEGREES = [
        "None / Not applicable",
        "B.A.",
        "B.Com",
        "B.Sc",
        "B.Tech / B.E.",
        "BBA",
        "BCA",
        "B.Pharm",
        "B.Arch",
        "LLB",
        "MBBS",
        "BDS",
        "B.Ed",
        "M.A.",
        "M.Com",
        "M.Sc",
        "M.Tech / M.E.",
        "MBA",
        "MCA",
        "M.Pharm",
        "LLM",
        "MD / MS",
        "Ph.D",
        "CA (Chartered Accountant)",
        "CS (Company Secretary)",
        "Other",
]

        INDUSTRY_TYPES = [
        "Information Technology (IT)",
        "Healthcare & Pharmaceuticals",
        "Banking & Financial Services",
        "Manufacturing",
        "Retail & E-commerce",
        "Education & EdTech",
        "Real Estate & Construction",
        "Telecommunications",
        "Media & Entertainment",
        "Hospitality & Tourism",
        "Logistics & Transportation",
        "Energy & Utilities",
        "Agriculture & Agri-business",
        "Government / Public Sector",
        "Consulting & Professional Services",
        "Automotive",
        "FMCG",
        "Other",
]
        
GROQ_MODEL = "llama-3.3-70b-versatile"


def build_prompt(
    role: str,
    total_experience: int,
    age: int,
    state: str,
    district: str,
    gender: str,
    metric_school: str,
    college_degree: str,
    extra_certificates: str,
    past_company: str,
    past_years: Optional[int],
    past_role: str,
    expected_min: Optional[int],
    expected_max: Optional[int],
    industry_type: str,
    industry_description: str,
) -> str:
    past_years_str = str(past_years) if past_years is not None else "Not specified"
    expected_min_str = str(expected_min) if expected_min is not None else "Not specified"
    expected_max_str = str(expected_max) if expected_max is not None else "Not specified"

    return f"""You are an expert HR recruiter and compensation analyst with deep knowledge of the Indian job market.

Analyze the candidate profile below and provide:
1. Predicted Salary: A realistic annual market salary prediction in INR (Indian Rupees). Give a single figure or a tight range.
2. Justification: Exactly three sentences justifying why you chose that number, referencing location, education, past experience, and role.
3. Future Growth Plan: Suggest 2 to 3 specific skills, tools, or certifications the candidate should acquire to level up.
4. Estimated Future Salary: Give a new, higher salary range they could expect after acquiring those specific skills.

Candidate profile:
- Role / Title / Post: {role}
- Total Experience (years in job market): {total_experience}
- Age: {age}
- Location: {district}, {state}, India
- Gender: {gender}
- Educational Qualification — Metric/School: {metric_school}
- Educational Qualification — College Degree: {college_degree}
- Extra Certificates: {extra_certificates or "None"}
- Past Job — Company Name: {past_company or "Not provided"}
- Past Job — Years there: {past_years_str}
- Past Job — Post/Role: {past_role or "Not provided"}
- Candidate's Expected Salary Range (INR per annum): Min {expected_min_str}, Max {expected_max_str}
- Industry Type: {industry_type}
- Industry Description: {industry_description or "Not provided"}
"""


def predict_salary(prompt: str) -> str:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert HR recruiter and compensation analyst with deep knowledge of the Indian job market. "
                    "Return a realistic, market-aligned salary estimate in INR.\n\n"
                    "IMPORTANT OUTPUT FORMAT RULES (must follow exactly):\n"
                    "1) Output MUST contain EXACTLY these four Markdown sections in this exact order, with these exact headings:\n"
                    "   - ## Predicted Salary\n"
                    "   - ## Justification\n"
                    "   - ## Future Growth Plan\n"
                    "   - ## Estimated Future Salary\n"
                    "2) Do NOT include any other headings, sections, preambles, disclaimers, greetings, or conclusions.\n"
                    "3) Use bold text for key numbers (e.g., **₹12–14 LPA**).\n"
                    "4) In **Justification**, write EXACTLY three sentences.\n"
                    "5) In **Future Growth Plan**, provide 2–3 bullet points. Each bullet MUST be a specific skill, tool, or certification.\n"
                    "6) In **Estimated Future Salary**, give a higher INR salary range than the Predicted Salary, and keep it realistic for India."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=512,
    )
    return completion.choices[0].message.content


def parse_prediction_response(text: str) -> dict[str, str]:
    headings = [
        ("predicted_salary", "Predicted Salary"),
        ("justification", "Justification"),
        ("future_growth_plan", "Future Growth Plan"),
        ("estimated_future_salary", "Estimated Future Salary"),
    ]
    sections: dict[str, str] = {}

    for idx, (key, title) in enumerate(headings):
        start_pattern = rf"##\s*{re.escape(title)}\s*"
        start = re.search(start_pattern, text, re.IGNORECASE)
        if not start:
            continue

        content_start = start.end()
        if idx + 1 < len(headings):
            next_title = headings[idx + 1][1]
            end_pattern = rf"##\s*{re.escape(next_title)}\s*"
            end = re.search(end_pattern, text[content_start:], re.IGNORECASE)
            content = text[content_start : content_start + end.start()] if end else text[content_start:]
        else:
            content = text[content_start:]

        sections[key] = content.strip()

    return sections


def display_prediction_result(result: str) -> None:
    sections = parse_prediction_response(result)

    if not sections:
        st.subheader("📈 Salary Prediction")
        st.markdown(result)
        return

    st.subheader("📈 Salary Prediction")

    predicted = sections.get("predicted_salary", "")
    if predicted:
        st.success("Your AI-powered salary estimate is ready.")
        st.markdown("## 💰 Predicted Salary (INR per annum)")
        st.markdown(predicted)
    else:
        st.markdown(result)
        return

    with st.expander("📝 Justification", expanded=False):
        st.markdown(sections.get("justification", "_No justification provided._"))

    with st.expander("🚀 Future Growth Plan", expanded=False):
        st.markdown(sections.get("future_growth_plan", "_No growth plan provided._"))

    with st.expander("💹 Estimated Future Salary", expanded=False):
        st.markdown(sections.get("estimated_future_salary", "_No future salary estimate provided._"))


def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def render_lottie_animation(url: str, height: int = 300) -> None:
    lottie_json = load_lottieurl(url)
    if lottie_json:
        st_lottie(lottie_json, height=height)
    else:
        st.error("Animation failed to load")


# --- UI ---
with st.sidebar:
    st.markdown("### 💡 About this app")
    st.markdown(
        "Get an **AI-powered salary prediction** tailored to the Indian job market. "
        "Fill in your profile and discover your estimated worth, growth plan, and future earning potential."
    )
    st.markdown("---")
    st.markdown("**Powered by Groq AI**")

header_col, lottie_col = st.columns([3, 1])

left_col, right_col = st.columns(2)

with left_col:
    st.markdown("**Career Profile**")
    role = st.selectbox("💼 Role / Title / Post", PROFESSIONAL_ROLES)
    total_experience = st.slider(
        "📊 Total Experience (Job)",
        min_value=0,
        max_value=40,
        value=0,
    )
    age = st.number_input("🎂 Age", min_value=18, max_value=70, value=25, step=1)
    gender = st.radio("⚧ Gender", ["Male", "Female", "Other"], horizontal=True)

    st.markdown("**Location**")
    state = st.selectbox("📍 State", INDIAN_STATES)
    district = st.text_input("📍 District", placeholder="e.g. Pune, Lucknow")

with right_col:
    st.markdown("**Education & Industry**")
    metric_school = st.selectbox("🎓 Metric/School", METRIC_OPTIONS)
    college_degree = st.selectbox("🎓 College Degree", COLLEGE_DEGREES)
    extra_certificates = st.text_input(
        "🎓 Extra Certificates",
        placeholder="e.g. AWS, PMP",
    )
    industry_type = st.selectbox("🏭 Industry Type", INDUSTRY_TYPES)
    industry_description = st.text_area(
        "🏭 Describe your industry",
        placeholder="Briefly describe your industry, company size, or niche...",
        height=100,
    )

    st.markdown("**Expected Salary** (INR per annum)")
    sal_col1, sal_col2 = st.columns(2)
    with sal_col1:
        expected_min = st.number_input(
            "💵 Min",
            min_value=0,
            value=0,
            step=50_000,
            format="%d",
        )
    with sal_col2:
        expected_max = st.number_input(
            "💵 Max",
            min_value=0,
            value=0,
            step=50_000,
            format="%d",
        )

with st.expander("🏢 Past Job Work Place", expanded=False):
    past_col1, past_col2, past_col3 = st.columns(3)
    with past_col1:
        past_company = st.text_input("Company Name", key="past_company")
    with past_col2:
        past_years = st.number_input(
            "Years there",
            min_value=0,
            max_value=40,
            value=0,
            step=1,
            key="past_years",
        )
    with past_col3:
        past_role = st.text_input("Post/Role", key="past_role")

st.divider()

predict_clicked = st.button(
    "PREDICT SALARY",
    type="primary",
    use_container_width=True,
)

if predict_clicked:
    if not district.strip():
        st.warning("Please enter your district for a more accurate location-based prediction.")
    try:
        with st.spinner("Analyzing market data and calculating optimal salary..."):
            prompt = build_prompt(
                role=role,
                total_experience=total_experience,
                age=int(age),
                state=state,
                district=district.strip() or "Not specified",
                gender=gender,
                metric_school=metric_school,
                college_degree=college_degree,
                extra_certificates=extra_certificates,
                past_company=past_company,
                past_years=int(past_years) if past_years else None,
                past_role=past_role,
                expected_min=int(expected_min) if expected_min else None,
                expected_max=int(expected_max) if expected_max else None,
                industry_type=industry_type,
                industry_description=industry_description,
            )
            result = predict_salary(prompt)
        st.balloons()
        st.divider()
        display_prediction_result(result)
    except KeyError:
        st.error(
            "GROQ_API_KEY not found. Add it to `.streamlit/secrets.toml`:\n\n"
            '```toml\nGROQ_API_KEY = "your-key-here"\n```'
        )
    except Exception as exc:
        st.error(f"Prediction failed: {exc}")
