import streamlit as st
import requests
import json

st.set_page_config(page_title="AI Recruitment Assistant", page_icon="📄", layout="wide")

# ── Custom CSS — Dark Mode ──
st.markdown("""
<style>
    /* Overall background */
    .stApp {
        background: #0F1117 !important;
    }

    /* Default text */
    .stApp, .stApp p, .stApp span, .stApp li, .stApp label, .stApp div {
        color: #E5E7EB !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #F9FAFB !important;
    }

    /* Header badge */
    .ai-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid #22C55E;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 13px;
        color: #4ADE80 !important;
        font-weight: 500;
        margin-bottom: 12px;
    }
    .ai-badge::before {
        content: "";
        width: 8px;
        height: 8px;
        background: #22C55E;
        border-radius: 50%;
    }

    /* Main title */
    .hero-title {
        font-size: 2.6rem;
        font-weight: 700;
        color: #F9FAFB !important;
        line-height: 1.2;
        margin-bottom: 8px;
    }
    .hero-title span {
        color: #FB923C !important;
    }

    /* Subtitle */
    .hero-desc {
        font-size: 1.05rem;
        color: #9CA3AF !important;
        line-height: 1.7;
        margin-bottom: 24px;
    }
    .hero-desc strong {
        color: #F9FAFB !important;
    }

    /* Metric cards */
    .metric-row {
        display: flex;
        gap: 16px;
        margin-top: 28px;
        margin-bottom: 20px;
    }
    .metric-card {
        flex: 1;
        background: #1F2937;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 20px 16px;
        text-align: center;
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FB923C !important;
    }
    .metric-card .label {
        font-size: 0.75rem;
        color: #9CA3AF !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
        font-weight: 500;
    }

    /* Upload widget */
    [data-testid="stFileUploader"] {
        background: #1F2937 !important;
        border: 2px dashed #FB923C !important;
        border-radius: 16px !important;
        padding: 16px !important;
    }
    [data-testid="stFileUploader"] * {
        color: #E5E7EB !important;
    }
    [data-testid="stFileUploader"] section {
        background: #1F2937 !important;
    }
    [data-testid="stFileUploader"] button {
        background: #FB923C !important;
        color: #1A1A1A !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background: #F97316 !important;
    }
    [data-testid="stFileUploader"] small {
        color: #6B7280 !important;
    }
    /* File name after upload */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"],
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] * {
        background: #111827 !important;
        color: #E5E7EB !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        background: #FB923C !important;
        color: #111827 !important;
        border: none !important;
        border-radius: 24px !important;
        padding: 12px 32px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #F97316 !important;
    }

    /* Status widget */
    .stStatus, .stStatus * {
        color: #E5E7EB !important;
    }

    /* LIVE indicator */
    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #374151;
        color: #F9FAFB !important;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid #4B5563;
    }
    .live-indicator::before {
        content: "";
        width: 8px;
        height: 8px;
        background: #EF4444;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* Result cards */
    .result-card {
        background: #1F2937;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
    }
    .result-card .job-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #F9FAFB !important;
        margin-bottom: 8px;
    }
    .result-card .score-badge {
        display: inline-block;
        border-radius: 12px;
        padding: 4px 12px;
        font-size: 0.85rem;
        font-weight: 700;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #1F2937 !important;
        color: #E5E7EB !important;
        border: 1px solid #374151 !important;
        border-radius: 12px !important;
    }
    .streamlit-expanderContent {
        background: #111827 !important;
        border: 1px solid #374151 !important;
        border-top: none !important;
    }

    /* Success / Warning / Error / Info boxes */
    .stAlert {
        background: #1F2937 !important;
        border: 1px solid #374151 !important;
        color: #E5E7EB !important;
    }

    /* Divider */
    hr {
        border-color: #374151 !important;
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# ── HERO SECTION ──
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown('<div class="ai-badge">AI Career Coach · Available 24/7 · Accurate Analysis</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="hero-title">
            Find your next job <span>faster</span>,<br>
            chính xác hơn với AI.
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div class="hero-desc">
            Upload your resume in just <strong>one step</strong>. Our AI analyzes your skills,
            matches them against hundreds of job openings,
            and recommends the <strong>Top 3 most suitable positions</strong>
            along with personalized improvement suggestions.
        </div>
    """, unsafe_allow_html=True)

    # Metric cards
    st.markdown("""
        <div class="metric-row">
            <div class="metric-card">
                <div class="value">~30s</div>
                <div class="label">Resume Analysis</div>
            </div>
            <div class="metric-card">
                <div class="value">100+</div>
                <div class="label">Job Openings</div>
            </div>
            <div class="metric-card">
                <div class="value">24/7</div>
                <div class="label">AI Assistant</div>
            </div>
            <div class="metric-card">
                <div class="value">Top 3</div>
                <div class="label">Top Recommendations</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("<br>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "📤 Upload Your Resume (PDF)",
        type=["pdf"],
        help="Supports PDF files up to 10 MB"
    )

    if uploaded_file:
        st.success(f"📎 **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔍 Analyze Resume & Find Matching Jobs →", type="primary", use_container_width=True):
        if not uploaded_file:
            st.warning("⚠️ Please upload your resume first.")
        else:
            status_container = st.empty()
            status_container.markdown('<div class="live-indicator">LIVE — Analyzing...</div>', unsafe_allow_html=True)

            try:
                files = {"resume": ("resume.pdf", uploaded_file, "application/pdf")}
                response = requests.post(
                    "http://localhost:8000/find_jobs",
                    files=files,
                    stream=True,
                )
                response.raise_for_status()

                final_json = None

                for line in response.iter_lines():
                    if not line:
                        continue
                    line = line.decode("utf-8") if isinstance(line, bytes) else line
                    if line.startswith("data: "):
                        payload = line[6:]
                        try:
                            data = json.loads(payload)
                            msg_type = data.get("type")
                            content = data.get("content")

                            if msg_type == "status":
                                status_container.status(content, state="running")

                            elif msg_type == "result":
                                final_json = content
                                status_container.status("✅ Analysis completed!", state="complete")

                            elif msg_type == "done":
                                break

                        except json.JSONDecodeError:
                            pass

            except requests.exceptions.ConnectionError:
                st.error("❌ Unable to connect to the server. Please make sure the backend is running on port 8000.")
                final_json = None
            except Exception as e:
                st.error(f"❌ Connection error: {e}")
                final_json = None

# ── DISPLAY RESULTS ──
if "final_json" not in dir():
    final_json = None

if final_json:
    st.markdown("---")
    st.markdown("### 🎯 Job Matching Results")

    try:
        if isinstance(final_json, str):
            final_json = final_json.replace("```json", "").replace("```", "").strip()
            matches = json.loads(final_json)
        else:
            matches = final_json

        if isinstance(matches, dict) and "matches" in matches:
            matches = matches["matches"]

        for idx, job in enumerate(matches, 1):
            score = job.get("match_score", 0)
            title = job.get("job_title", "Unknown")

            if score >= 80:
                score_color = "#4ADE80"
                score_bg = "rgba(34, 197, 94, 0.15)"
            elif score >= 60:
                score_color = "#FB923C"
                score_bg = "rgba(251, 146, 60, 0.15)"
            else:
                score_color = "#F87171"
                score_bg = "rgba(248, 113, 113, 0.15)"

            st.markdown(f"""
                <div class="result-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="job-title">#{idx} — {title}</div>
                        <div class="score-badge" style="background: {score_bg}; color: {score_color}; border: 1px solid {score_color};">
                            Score: {score}/100
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            with st.expander(f"View Details — {title}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    reasoning = job.get("reasoning") or job.get("reason") or job.get("explanation") or ""
                    if not reasoning:
                        # Fallback: Build the reasoning from the candidate's strengths
                        strengths_list = job.get("strengths", [])
                        reasoning = "; ".join(strengths_list) if strengths_list else "No information available"
                    st.markdown(f"**📝 Match Reason:** {reasoning}")

                    strengths_raw = job.get("strengths", [])
                    if isinstance(strengths_raw, list):
                        st.markdown(f"**💪 Strengths:** {', '.join(strengths_raw)}")
                    else:
                        st.markdown(f"**💪 Strengths:** {strengths_raw}")
                with col_b:
                    missing = job.get("missing_skills", [])
                    if missing:
                        if isinstance(missing, list):
                            st.markdown(f"**📚 Cần bổ sung:** {', '.join(missing)}")
                        else:
                            st.markdown(f"**📚 Cần bổ sung:** {missing}")

                    tip = job.get("improvement_tips", "")
                    # Handle the case where improvement_tips is still a list
                    # (e.g., parsed from JSON before Pydantic validation)
                    if isinstance(tip, list):
                        tip = "; ".join(str(t) for t in tip)
                    if tip:
                        st.info(f"💡 {tip}")

                job_url = job.get("job_url", "")
                if job_url:
                    st.markdown(f"[🔗 Apply Here →]({job_url})")

    except Exception as e:
        st.error(f"❌ Error while processing the result: {e}")
        st.code(final_json)