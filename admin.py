import streamlit as st
import requests

# =========================================================
# SMARTCLARIFY - TEACHER PANEL
# =========================================================

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="SmartClarify",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

body {
    background-color: #0e1117;
}

/* Main headings */
.main-title {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg, #7c4dff, #00c6ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}

.page-heading {
    font-size: 32px;
    font-weight: 750;
    color: #ffffff;
    padding: 12px 0;
    border-bottom: 2px solid #6c63ff;
    margin-bottom: 25px;
}

.section-heading {
    font-size: 25px;
    font-weight: 700;
    color: #ffffff;
    margin-top: 20px;
    margin-bottom: 15px;
}

/* Heading animation */
.page-heading {
    animation: fadeIn 0.8s ease-in-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Login box */
.login-box {
    padding: 25px;
    border-radius: 15px;
    background: linear-gradient(
        135deg,
        rgba(124,77,255,0.18),
        rgba(0,198,255,0.10)
    );
    border: 1px solid rgba(124,77,255,0.4);
}

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(
        135deg,
        rgba(124,77,255,0.18),
        rgba(0,198,255,0.08)
    );
    padding: 18px;
    border-radius: 15px;
    border: 1px solid rgba(124,77,255,0.35);
}

/* Buttons */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #17142b,
        #10131d
    );
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "selected_doubt" not in st.session_state:
    st.session_state.selected_doubt = None

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "teacher_id" not in st.session_state:
    st.session_state.teacher_id = None

if "token" not in st.session_state:
    st.session_state.token = None


# =========================================================
# TEACHER LOGIN (now calls real /auth/login API)
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        '<div class="main-title">🤖 SmartClarify</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-heading">🔐 Teacher Login</div>',
        unsafe_allow_html=True
    )

    st.write("Please login to access the teacher dashboard.")

    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    email = st.text_input(
        "📧 Email",
        key="teacher_email"
    )

    password = st.text_input(
        "🔑 Password",
        type="password",
        key="teacher_password"
    )

    if st.button("🚀 Login", use_container_width=True):

        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": email.strip(),
                "password": password.strip()
            })

            if response.status_code == 200:
                data = response.json()

                if data.get("role") != "teacher":
                    st.error("❌ This account is not a teacher account")
                else:
                    st.session_state.logged_in = True
                    st.session_state.token = data["access_token"]
                    st.session_state.teacher_id = data["id"]
                    st.session_state.page = "Dashboard"
                    st.success("✅ Login successful!")
                    st.rerun()
            else:
                st.error("❌ Invalid email or password")

        except requests.exceptions.ConnectionError:
            st.error("⚠️ Backend se connect nahi ho paaya — check karo uvicorn chal raha hai ya nahi.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.info(
        "Demo Login → Use a teacher account registered via /auth/register"
    )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown(
    '<div class="main-title">🤖 SmartClarify</div>',
    unsafe_allow_html=True
)

st.sidebar.write("### 👩‍🏫 Teacher Panel")

st.sidebar.markdown("---")


if st.sidebar.button("🏠 Dashboard", use_container_width=True):
    st.session_state.page = "Dashboard"
    st.session_state.selected_doubt = None
    st.rerun()


if st.sidebar.button("❓ Pending Doubts", use_container_width=True):
    st.session_state.page = "Pending Doubts"
    st.rerun()


if st.sidebar.button("📊 Analytics", use_container_width=True):
    st.session_state.page = "Analytics"
    st.rerun()


st.sidebar.markdown("---")

st.sidebar.write("### 👤 Teacher")
st.sidebar.caption(f"Logged in as Teacher (ID: {st.session_state.teacher_id})")


if st.sidebar.button("🚪 Logout", use_container_width=True):

    st.session_state.logged_in = False
    st.session_state.selected_doubt = None
    st.session_state.page = "Dashboard"
    st.session_state.teacher_id = None
    st.session_state.token = None

    st.rerun()


# =========================================================
# HELPER: fetch pending doubts from backend
# =========================================================

def fetch_pending_questions():
    try:
        response = requests.get(f"{API_BASE}/teacher/questions", params={"status": "pending"})
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Backend se connect nahi ho paaya")
        return []


# =========================================================
# DASHBOARD PAGE
# =========================================================

if st.session_state.page == "Dashboard":

    st.markdown(
        '<div class="main-title">🤖 SmartClarify</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-heading">📊 Teacher Dashboard</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Welcome back! Here is an overview of your classroom doubts."
    )

    st.markdown("---")


    # -----------------------------------------------------
    # DASHBOARD OVERVIEW
    # NOTE: these counts are still placeholders — wiring them
    # to real numbers needs a /teacher/stats endpoint (Phase 2)
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-heading">📈 Dashboard Overview</div>',
        unsafe_allow_html=True
    )

    pending_questions = fetch_pending_questions()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("👨‍🎓 Students", "60")

    with col2:
        st.metric("❓ Total Doubts", "120")

    with col3:
        st.metric("🤖 AI Resolved", "70")

    with col4:
        st.metric("👩‍🏫 Teacher Resolved", "35")

    with col5:
        st.metric("⏳ Pending", str(len(pending_questions)))


    st.markdown("---")


    # -----------------------------------------------------
    # PENDING DOUBTS (real data, top 2 shown on dashboard)
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-heading">❓ Pending Doubts</div>',
        unsafe_allow_html=True
    )

    if not pending_questions:
        st.info("No pending doubts right now 🎉")

    for q in pending_questions[:2]:

        doubt_col, subject_col, action_col = st.columns([3, 2, 1])

        with doubt_col:
            st.write(f"**{q['question_text']}**")
            st.caption(f"👤 Asked by: Student ID {q['student_id']}")

        with subject_col:
            st.write(f"📘 {q['subject']}")

        with action_col:
            if st.button("View", key=f"dashboard_view_{q['id']}"):
                st.session_state.selected_doubt = q['id']


    # -----------------------------------------------------
    # SELECTED DOUBT (answer form)
    # -----------------------------------------------------

    if st.session_state.selected_doubt:

        selected_q = next(
            (q for q in pending_questions if q['id'] == st.session_state.selected_doubt),
            None
        )

        if selected_q:

            st.markdown("---")

            st.markdown(
                '<div class="section-heading">📌 Selected Doubt</div>',
                unsafe_allow_html=True
            )

            st.info(
                f"❓ {selected_q['question_text']}\n\n"
                f"👤 Student ID: {selected_q['student_id']}\n"
                f"📘 Subject: {selected_q['subject']}"
            )

            answer = st.text_area(
                "✍️ Write your answer",
                key=f"answer_{selected_q['id']}"
            )

            if st.button("📤 Submit Answer", key=f"submit_{selected_q['id']}"):

                if answer.strip():

                    response = requests.post(
                        f"{API_BASE}/teacher/questions/{selected_q['id']}/answer",
                        json={
                            "teacher_id": st.session_state.teacher_id,
                            "answer_text": answer
                        }
                    )

                    if response.status_code == 200:
                        st.success("✅ Answer submitted successfully!")
                        st.session_state.selected_doubt = None
                        st.rerun()
                    else:
                        st.error("❌ Submission failed")

                else:
                    st.warning("⚠️ Please write an answer first.")


# =========================================================
# PENDING DOUBTS PAGE (full list, real data)
# =========================================================

elif st.session_state.page == "Pending Doubts":

    st.markdown(
        '<div class="main-title">🤖 SmartClarify</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-heading">❓ Pending Doubts</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Review and answer doubts submitted by students."
    )

    st.markdown("---")

    all_pending = fetch_pending_questions()

    if not all_pending:
        st.info("No pending doubts right now 🎉")

    for q in all_pending:

        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            st.write(f"### ❓ {q['question_text']}")
            st.caption(f"👤 Student ID: {q['student_id']}")

        with col2:
            st.write(f"📘 {q['subject']}")

        with col3:
            if st.button("👁️ View", key=f"pending_view_{q['id']}"):
                st.session_state.selected_doubt = q['id']
                st.session_state.page = "Dashboard"  # answer form lives on Dashboard page
                st.rerun()

        st.markdown("---")


# =========================================================
# ANALYTICS PAGE (placeholder — plug in real charts later)
# =========================================================

elif st.session_state.page == "Analytics":

    st.markdown(
        '<div class="main-title">🤖 SmartClarify</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-heading">📊 Analytics</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Analytics (confusion hotspots, topic trends) will be wired up "
        "once the RAG/confidence-scoring pipeline is built — Phase 2."
    )