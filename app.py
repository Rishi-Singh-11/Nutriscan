"""
app.py — NutriScan Pro  🥗
Senior Full-Stack AI Engineer implementation.
Glassmorphism UI · Gemini 1.5 Flash · SQLite · Mifflin-St Jeor
"""

import json
import re
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
from PIL import Image
import io

import database as db

# ─────────────────────────────────────────────
#  Page config  (must be first Streamlit call)
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="NutriScan Pro",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  Bootstrap DB & Gemini
# ─────────────────────────────────────────────

db.init_db()

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # CHANGE THE LINE BELOW (Line 43)
    gemini = genai.GenerativeModel("gemini-1.5-flash")
except Exception:
    gemini = None
# ─────────────────────────────────────────────
#  Session State defaults
# ─────────────────────────────────────────────

for key, default in {
    "authenticated": False,
    "user_id": None,
    "username": None,
    "profile": None,
    "page": "login",          # login | signup | onboard | dashboard | scan
    "scan_result": None,
    "auth_error": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
#  Global CSS — Glassmorphism Dark Theme
# ─────────────────────────────────────────────

GLOBAL_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── CSS Variables ── */
:root {
    --neon-a:    #00f2fe;
    --neon-b:    #4facfe;
    --neon-c:    #00ff88;
    --bg-deep:   #050d1a;
    --bg-mid:    #071221;
    --glass-bg:  rgba(255,255,255,0.04);
    --glass-bd:  rgba(0,242,254,0.18);
    --text-hi:   #e8f4ff;
    --text-lo:   #7a9bbf;
    --danger:    #ff4f6d;
    --warn:      #ffb347;
    --radius:    18px;
}

/* ── App shell ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-deep) !important;
    color: var(--text-hi) !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 60% at 20% -10%, rgba(0,242,254,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 110%, rgba(79,172,254,0.10) 0%, transparent 60%),
        var(--bg-deep) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }

/* ── Glass card ── */
.glass {
    background: var(--glass-bg);
    border: 1px solid var(--glass-bd);
    border-radius: var(--radius);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06);
    transition: box-shadow 0.3s ease, border-color 0.3s ease;
}
.glass:hover {
    border-color: rgba(0,242,254,0.35);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(0,242,254,0.08), inset 0 1px 0 rgba(255,255,255,0.06);
}

/* ── Glass card — compact ── */
.glass-sm {
    background: var(--glass-bg);
    border: 1px solid var(--glass-bd);
    border-radius: 12px;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    padding: 1.2rem 1.5rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}

/* ── Typography ── */
h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.02em;
}
.brand {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--neon-a), var(--neon-b));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.brand-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    color: var(--text-lo);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 4px;
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-hi);
    margin-bottom: 0.25rem;
}
.section-sub {
    font-size: 0.82rem;
    color: var(--text-lo);
    margin-bottom: 1.5rem;
}

/* ── Neon divider ── */
.neon-hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--neon-a), var(--neon-b), transparent);
    margin: 1.5rem 0;
    opacity: 0.5;
}

/* ── Metric card ── */
.metric-wrap {
    background: rgba(0,242,254,0.05);
    border: 1px solid rgba(0,242,254,0.15);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    text-align: center;
}
.metric-val {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--neon-a), var(--neon-b));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.metric-lbl {
    font-size: 0.75rem;
    color: var(--text-lo);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 2px;
}

/* ── Neon badge ── */
.badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(0,242,254,0.15), rgba(79,172,254,0.15));
    border: 1px solid rgba(0,242,254,0.3);
    border-radius: 999px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--neon-a);
    letter-spacing: 0.05em;
}

/* ── Tag pill ── */
.pill {
    display: inline-block;
    background: rgba(0,255,136,0.1);
    border: 1px solid rgba(0,255,136,0.25);
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 0.72rem;
    color: var(--neon-c);
    font-weight: 500;
}

/* ── Input fields ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] select {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(0,242,254,0.2) !important;
    border-radius: 10px !important;
    color: var(--text-hi) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--neon-a) !important;
    box-shadow: 0 0 0 2px rgba(0,242,254,0.12) !important;
}

/* ── Streamlit buttons ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--neon-a), var(--neon-b)) !important;
    color: #050d1a !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    padding: 0.55rem 1.6rem !important;
    transition: opacity 0.2s, transform 0.15s !important;
    box-shadow: 0 0 18px rgba(0,242,254,0.3) !important;
}
[data-testid="stButton"] > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button[kind="secondary"],
[data-testid="stButton"] > button[data-secondary="true"] {
    background: rgba(255,255,255,0.06) !important;
    color: var(--neon-a) !important;
    box-shadow: none !important;
    border: 1px solid rgba(0,242,254,0.2) !important;
}

/* ── Progress bar ── */
[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg, var(--neon-a), var(--neon-b)) !important;
    border-radius: 999px !important;
}
[data-testid="stProgress"] > div > div {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 999px !important;
}

/* ── Streamlit metric ── */
[data-testid="stMetric"] {
    background: rgba(0,242,254,0.04) !important;
    border: 1px solid rgba(0,242,254,0.12) !important;
    border-radius: 14px !important;
    padding: 1rem 1.2rem !important;
}
[data-testid="stMetricLabel"] { color: var(--text-lo) !important; font-size: 0.75rem !important; }
[data-testid="stMetricValue"] { color: var(--neon-a) !important; font-family: 'Syne', sans-serif !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border: 1.5px dashed rgba(0,242,254,0.3) !important;
    border-radius: 16px !important;
    background: rgba(0,242,254,0.03) !important;
    padding: 1rem !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
    color: var(--text-lo) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--neon-a) !important;
    border-bottom-color: var(--neon-a) !important;
}

/* ── Meal row ── */
.meal-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 0.9rem;
}
.meal-row:last-child { border-bottom: none; }
.meal-name { font-weight: 500; color: var(--text-hi); }
.meal-cal  { font-family: 'Syne', sans-serif; font-weight: 700; color: var(--neon-b); }

/* ── Nav bar ── */
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.8rem 1.5rem;
    background: rgba(5,13,26,0.85);
    border-bottom: 1px solid rgba(0,242,254,0.1);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    position: sticky;
    top: 0;
    z-index: 999;
    margin-bottom: 1.5rem;
}

/* ── Scan result card ── */
.scan-card {
    background: linear-gradient(135deg, rgba(0,242,254,0.07), rgba(79,172,254,0.05));
    border: 1px solid rgba(0,242,254,0.25);
    border-radius: var(--radius);
    padding: 1.5rem 2rem;
}

/* ── Alert box ── */
.alert-err {
    background: rgba(255,79,109,0.1);
    border: 1px solid rgba(255,79,109,0.3);
    border-radius: 10px;
    padding: 0.7rem 1rem;
    color: #ff8ca0;
    font-size: 0.85rem;
}
.alert-ok {
    background: rgba(0,255,136,0.08);
    border: 1px solid rgba(0,255,136,0.25);
    border-radius: 10px;
    padding: 0.7rem 1rem;
    color: var(--neon-c);
    font-size: 0.85rem;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(var(--neon-a), var(--neon-b));
    border-radius: 999px;
}

/* ── Spacing helpers ── */
.mt-1 { margin-top: 0.5rem; }
.mt-2 { margin-top: 1rem; }
.mt-3 { margin-top: 1.5rem; }
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Gemini AI helper
# ─────────────────────────────────────────────

NUTRITION_PROMPT = """
You are a professional dietitian AI. Analyze this food/meal image carefully.

Return ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{
  "meal_name": "Name of the meal or food",
  "calories": 450,
  "protein_g": 28.5,
  "carbs_g": 35.0,
  "fats_g": 18.0,
  "confidence": "high|medium|low",
  "notes": "Brief note about the meal if needed"
}

All numeric values should be realistic estimates for a typical single serving.
If you cannot identify food, return: {"error": "Could not identify food in image."}
"""


def analyze_food_image(image_bytes: bytes) -> dict:
    """Send image to Gemini 1.5 Flash and parse nutrition JSON."""
    if gemini is None:
        return {"error": "Gemini API key not configured. Add GEMINI_API_KEY to .streamlit/secrets.toml"}

    try:
        img = Image.open(io.BytesIO(image_bytes))
        response = gemini.generate_content([NUTRITION_PROMPT, img])
        raw = response.text.strip()

        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        result = json.loads(raw)
        return result
    except json.JSONDecodeError:
        return {"error": "AI returned unparseable response. Please try another image."}
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}


# ─────────────────────────────────────────────
#  Reusable UI components
# ─────────────────────────────────────────────

def render_brand(size: str = "large") -> None:
    if size == "large":
        st.markdown("""
        <div style="text-align:center; padding: 2rem 0 1.5rem;">
            <div class="brand">NutriScan Pro</div>
            <div class="brand-sub">AI-Powered Nutrition Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="brand" style="font-size:1.6rem">🥗 NutriScan Pro</div>',
                    unsafe_allow_html=True)


def render_nav() -> None:
    col_brand, col_nav = st.columns([1, 1])
    with col_brand:
        st.markdown('<div class="brand" style="font-size:1.4rem; padding:0.2rem 0">🥗 NutriScan Pro</div>',
                    unsafe_allow_html=True)
    with col_nav:
        cols = st.columns(4)
        pages = [("📊 Dashboard", "dashboard"), ("📷 Scan", "scan"),
                 ("⚙️ Profile", "onboard"), ("🚪 Logout", "logout")]
        for i, (label, page) in enumerate(pages):
            with cols[i]:
                if st.button(label, key=f"nav_{page}"):
                    if page == "logout":
                        for k in ["authenticated", "user_id", "username", "profile",
                                  "scan_result", "auth_error"]:
                            st.session_state[k] = False if k == "authenticated" else None
                        st.session_state.page = "login"
                    else:
                        st.session_state.page = page
                    st.rerun()
    st.markdown('<hr class="neon-hr">', unsafe_allow_html=True)


def render_weekly_chart(user_id: int, daily_goal: int) -> None:
    weekly = db.get_weekly_calories(user_id)
    df = pd.DataFrame(weekly)

    fig = go.Figure()

    # Goal line
    fig.add_trace(go.Scatter(
        x=df["date"], y=[daily_goal] * len(df),
        mode="lines", name="Daily Goal",
        line=dict(color="rgba(0,242,254,0.4)", width=2, dash="dot"),
        hoverinfo="skip",
    ))

    # Area fill
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["calories"],
        fill="tozeroy",
        fillcolor="rgba(79,172,254,0.08)",
        line=dict(color="#4facfe", width=0),
        name="", showlegend=False, hoverinfo="skip",
    ))

    # Main line
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["calories"],
        mode="lines+markers",
        name="Calories",
        line=dict(color="#00f2fe", width=3),
        marker=dict(size=8, color="#00f2fe",
                    line=dict(color="#050d1a", width=2)),
        hovertemplate="<b>%{x}</b><br>%{y:.0f} kcal<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#7a9bbf"),
        margin=dict(l=0, r=0, t=10, b=0),
        height=260,
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False,
                   tickfont=dict(size=11)),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False,
                   ticksuffix=" kcal", tickfont=dict(size=11)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1,
                    font=dict(size=11, color="#7a9bbf")),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────
#  Page: Login
# ─────────────────────────────────────────────

def page_login() -> None:
    render_brand()

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown('<div class="section-title" style="text-align:center">Welcome back</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-sub" style="text-align:center">Sign in to your account</div>',
                    unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="your_username", key="li_user")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="li_pass")

        st.markdown("<div class='mt-1'>", unsafe_allow_html=True)
        if st.button("Sign In →", key="btn_login", use_container_width=True):
            user = db.authenticate_user(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user_id = user["id"]
                st.session_state.username = user["username"]
                st.session_state.profile = db.get_profile(user["id"])
                st.session_state.page = "onboard" if not st.session_state.profile else "dashboard"
                st.rerun()
            else:
                st.markdown('<div class="alert-err">⚠️ Invalid username or password.</div>',
                            unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<hr class="neon-hr">', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center; color:var(--text-lo); font-size:0.85rem">'
                    'New here?</div>', unsafe_allow_html=True)

        if st.button("Create Account", key="btn_goto_signup", use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Page: Signup
# ─────────────────────────────────────────────

def page_signup() -> None:
    render_brand()

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown('<div class="section-title" style="text-align:center">Create Account</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-sub" style="text-align:center">'
                    'Join NutriScan Pro — it\'s free</div>', unsafe_allow_html=True)

        username = st.text_input("Choose a username", placeholder="cooluser42", key="su_user")
        password = st.text_input("Password (min 6 chars)", type="password",
                                  placeholder="••••••••", key="su_pass")
        confirm  = st.text_input("Confirm password", type="password",
                                  placeholder="••••••••", key="su_conf")

        st.markdown("<div class='mt-1'>", unsafe_allow_html=True)
        if st.button("Create Account →", key="btn_signup", use_container_width=True):
            if not username.strip():
                st.markdown('<div class="alert-err">⚠️ Username cannot be empty.</div>',
                            unsafe_allow_html=True)
            elif len(password) < 6:
                st.markdown('<div class="alert-err">⚠️ Password must be at least 6 characters.</div>',
                            unsafe_allow_html=True)
            elif password != confirm:
                st.markdown('<div class="alert-err">⚠️ Passwords do not match.</div>',
                            unsafe_allow_html=True)
            else:
                uid = db.create_user(username, password)
                if uid is None:
                    st.markdown('<div class="alert-err">⚠️ Username already taken.</div>',
                                unsafe_allow_html=True)
                else:
                    st.session_state.authenticated = True
                    st.session_state.user_id = uid
                    st.session_state.username = username.strip().lower()
                    st.session_state.profile = None
                    st.session_state.page = "onboard"
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<hr class="neon-hr">', unsafe_allow_html=True)
        if st.button("← Back to Login", key="btn_back_login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Page: Onboarding / Profile Setup
# ─────────────────────────────────────────────

def page_onboard() -> None:
    render_nav()

    _, col, _ = st.columns([0.3, 2, 0.3])
    with col:
        st.markdown('<div class="glass">', unsafe_allow_html=True)

        is_new = st.session_state.profile is None
        emoji = "👋" if is_new else "⚙️"
        title = "Let's Set Up Your Profile" if is_new else "Update Your Profile"
        sub   = ("We'll calculate your personalized daily calorie goal." if is_new
                 else "Adjust your details to recalculate your calorie target.")

        st.markdown(f'<div class="section-title">{emoji} {title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-sub">{sub}</div>', unsafe_allow_html=True)

        p = st.session_state.profile or {}

        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 10, 100, value=p.get("age", 25), key="ob_age")
            weight = st.number_input("Weight (kg)", 30.0, 300.0,
                                      value=float(p.get("weight_kg", 70.0)),
                                      step=0.5, key="ob_wt")
        with col2:
            height = st.number_input("Height (cm)", 100.0, 250.0,
                                      value=float(p.get("height_cm", 170.0)),
                                      step=0.5, key="ob_ht")
            gender = st.selectbox("Gender", ["Male", "Female"],
                                   index=0 if p.get("gender","Male")=="Male" else 1,
                                   key="ob_gender")

        activity = st.selectbox("Activity Level", list(db.ACTIVITY_MULTIPLIERS.keys()),
                                 index=list(db.ACTIVITY_MULTIPLIERS.keys()).index(
                                     p.get("activity_level",
                                           "Moderate (3-5 days/week)")),
                                 key="ob_act")
        goal = st.selectbox("Your Goal", list(db.GOAL_ADJUSTMENTS.keys()),
                             index=list(db.GOAL_ADJUSTMENTS.keys()).index(
                                 p.get("goal", "Maintain weight")),
                             key="ob_goal")

        # Live preview
        cal_preview = db.calculate_daily_calories(age, weight, height, gender, activity, goal)
        st.markdown(f"""
        <div style="margin:1rem 0; text-align:center;">
            <div class="badge">Estimated Daily Goal</div>
            <div style="font-family:'Syne',sans-serif; font-size:2.4rem; font-weight:800;
                        background:linear-gradient(135deg,#00f2fe,#4facfe);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                        background-clip:text; line-height:1.2; margin-top:0.5rem;">
                {cal_preview:,} <span style="font-size:1rem;opacity:0.7">kcal/day</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Save Profile & Continue →", key="btn_save_profile",
                      use_container_width=True):
            db.upsert_profile(st.session_state.user_id, age, weight, height,
                               gender, activity, goal, cal_preview)
            st.session_state.profile = db.get_profile(st.session_state.user_id)
            st.session_state.page = "dashboard"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Page: Dashboard — Command Center
# ─────────────────────────────────────────────

def page_dashboard() -> None:
    render_nav()

    profile  = st.session_state.profile
    user_id  = st.session_state.user_id
    username = st.session_state.username
    goal     = profile["daily_cal_goal"] if profile else 2000

    totals   = db.get_today_totals(user_id)
    consumed = totals["calories"]
    remain   = max(0, goal - consumed)
    progress = min(1.0, consumed / goal) if goal > 0 else 0

    # ── Greeting ──────────────────────────────────────
    import datetime
    hour = datetime.datetime.now().hour
    greet = "Good morning" if hour < 12 else ("Good afternoon" if hour < 18 else "Good evening")

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem;">
        <div>
            <div style="font-family:'Syne',sans-serif; font-size:1.7rem; font-weight:800; color:var(--text-hi)">
                {greet}, <span style="background:linear-gradient(135deg,#00f2fe,#4facfe);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text">{username.capitalize()}</span> 👋
            </div>
            <div style="font-size:0.85rem; color:var(--text-lo); margin-top:2px">
                Here's your nutrition command center for today.
            </div>
        </div>
        <div>
            <span class="badge">{datetime.date.today().strftime('%A, %b %d')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metric row ────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    metrics = [
        ("🔥 Calories In",  f"{consumed:.0f}",          "kcal today"),
        ("🎯 Daily Goal",   f"{goal:,}",                 "kcal target"),
        ("⚡ Remaining",    f"{remain:.0f}",              "kcal left"),
        ("💪 Protein",      f"{totals['protein_g']:.1f}", "grams"),
        ("🧩 Carbs",        f"{totals['carbs_g']:.1f}",  "grams"),
    ]
    for col, (lbl, val, unit) in zip([m1, m2, m3, m4, m5], metrics):
        with col:
            st.metric(lbl, val, unit)

    # ── Progress bar ──────────────────────────────────
    st.markdown('<div class="mt-2">', unsafe_allow_html=True)
    progress_pct = int(progress * 100)
    bar_color = "#00f2fe" if progress < 0.85 else ("#ffb347" if progress < 1.0 else "#ff4f6d")
    status_msg = ("🟢 On track!" if progress < 0.85 else
                  ("🟡 Getting close to your limit" if progress < 1.0 else "🔴 Goal exceeded"))

    st.markdown(f"""
    <div class="glass-sm" style="margin-bottom:1.5rem">
        <div style="display:flex; justify-content:space-between; margin-bottom:0.6rem">
            <span style="font-family:'Syne',sans-serif; font-weight:700; font-size:0.95rem">
                Daily Calorie Progress
            </span>
            <span style="font-size:0.82rem; color:{bar_color}; font-weight:600">
                {progress_pct}% · {status_msg}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(progress)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Two-column layout ─────────────────────────────
    left, right = st.columns([1.4, 1], gap="large")

    with left:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 Weekly Calorie Trend</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Last 7 days vs your daily goal</div>',
                    unsafe_allow_html=True)
        render_weekly_chart(user_id, goal)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass" style="height:100%">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🍽️ Today\'s Meals</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Everything logged today</div>',
                    unsafe_allow_html=True)

        meals = db.get_today_meals(user_id)
        if not meals:
            st.markdown("""
            <div style="text-align:center; padding:2rem 0; color:var(--text-lo)">
                <div style="font-size:2rem">🥗</div>
                <div style="margin-top:0.5rem; font-size:0.85rem">No meals logged yet today.</div>
                <div style="font-size:0.8rem; margin-top:0.25rem; opacity:0.6">
                    Use the Scan tab to analyze your food!
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for m in meals:
                st.markdown(f"""
                <div class="meal-row">
                    <div>
                        <div class="meal-name">{m['meal_name']}</div>
                        <div style="font-size:0.72rem; color:var(--text-lo); margin-top:2px">
                            <span class="pill">P {m['protein_g']:.0f}g</span> &nbsp;
                            <span class="pill">C {m['carbs_g']:.0f}g</span> &nbsp;
                            <span class="pill">F {m['fats_g']:.0f}g</span>
                        </div>
                    </div>
                    <div class="meal-cal">{m['calories']:.0f} kcal</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<hr class="neon-hr">', unsafe_allow_html=True)
        if st.button("📷 Scan New Meal", key="btn_goto_scan", use_container_width=True):
            st.session_state.page = "scan"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Page: Scan — AI Nutrition Analyzer
# ─────────────────────────────────────────────

def page_scan() -> None:
    render_nav()

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📷 AI Food Scanner</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-sub">'
                    'Upload a photo of your meal — Gemini AI does the rest.</div>',
                    unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Drop or click to upload a food photo",
            type=["jpg", "jpeg", "png", "webp"],
            key="food_img",
        )

        if uploaded:
            st.image(uploaded, caption="Your meal preview", use_container_width=True)
            st.markdown("<div class='mt-1'>", unsafe_allow_html=True)
            if st.button("🔬 Analyze with Gemini AI", key="btn_analyze",
                          use_container_width=True):
                with st.spinner("Scanning your meal with AI…"):
                    result = analyze_food_image(uploaded.read())
                    st.session_state.scan_result = result
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass" style="min-height:300px">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Analysis Results</div>',
                    unsafe_allow_html=True)

        result = st.session_state.scan_result

        if result is None:
            st.markdown("""
            <div style="text-align:center; padding:3rem 0; color:var(--text-lo)">
                <div style="font-size:2.5rem">🤖</div>
                <div style="margin-top:0.8rem; font-size:0.9rem">
                    Upload a food photo and hit Analyze
                </div>
                <div style="font-size:0.78rem; opacity:0.6; margin-top:0.3rem">
                    Powered by Gemini 1.5 Flash
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif "error" in result:
            st.markdown(f'<div class="alert-err">⚠️ {result["error"]}</div>',
                        unsafe_allow_html=True)

        else:
            conf_color = {"high": "#00ff88", "medium": "#ffb347", "low": "#ff4f6d"}.get(
                result.get("confidence", "medium"), "#7a9bbf")

            st.markdown(f"""
            <div class="scan-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1rem;">
                    <div>
                        <div style="font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:800; color:var(--text-hi)">
                            {result.get('meal_name','Unknown Meal')}
                        </div>
                        <div style="font-size:0.75rem; color:var(--text-lo); margin-top:3px">
                            {result.get('notes','')}
                        </div>
                    </div>
                    <div style="font-size:0.72rem; color:{conf_color}; font-weight:600;
                                border:1px solid {conf_color}40; border-radius:999px;
                                padding:2px 10px; white-space:nowrap">
                        {result.get('confidence','?').upper()} CONFIDENCE
                    </div>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; margin-bottom:1rem;">
                    <div class="metric-wrap" style="grid-column:span 2">
                        <div class="metric-val">{result.get('calories',0):.0f}</div>
                        <div class="metric-lbl">Calories (kcal)</div>
                    </div>
                    <div class="metric-wrap">
                        <div class="metric-val" style="font-size:1.4rem">{result.get('protein_g',0):.1f}g</div>
                        <div class="metric-lbl">Protein</div>
                    </div>
                    <div class="metric-wrap">
                        <div class="metric-val" style="font-size:1.4rem">{result.get('carbs_g',0):.1f}g</div>
                        <div class="metric-lbl">Carbohydrates</div>
                    </div>
                    <div class="metric-wrap" style="grid-column:span 2">
                        <div class="metric-val" style="font-size:1.4rem">{result.get('fats_g',0):.1f}g</div>
                        <div class="metric-lbl">Fats</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div class='mt-2'>", unsafe_allow_html=True)
            st.markdown('<div class="alert-ok">✅ Looks good? Log this meal to your daily diary.</div>',
                        unsafe_allow_html=True)

            col_log, col_discard = st.columns(2)
            with col_log:
                if st.button("✅ Log This Meal", key="btn_log", use_container_width=True):
                    db.log_meal(
                        st.session_state.user_id,
                        result.get("meal_name", "Unknown"),
                        result.get("calories", 0),
                        result.get("protein_g", 0),
                        result.get("carbs_g", 0),
                        result.get("fats_g", 0),
                    )
                    st.session_state.scan_result = None
                    st.session_state.page = "dashboard"
                    st.rerun()
            with col_discard:
                if st.button("🗑️ Discard", key="btn_discard", use_container_width=True):
                    st.session_state.scan_result = None
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Router
# ─────────────────────────────────────────────

def main() -> None:
    page = st.session_state.page

    if not st.session_state.authenticated:
        if page == "signup":
            page_signup()
        else:
            page_login()
        return

    # Authenticated routes
    if page == "dashboard":
        page_dashboard()
    elif page == "scan":
        page_scan()
    elif page == "onboard":
        page_onboard()
    else:
        page_dashboard()


if __name__ == "__main__" or True:
    main()