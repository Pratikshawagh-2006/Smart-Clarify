import streamlit as st
import requests

# =========================================================
# SMARTCLARIFY - UNIFIED APP (Teacher + Student in one file)
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
    animation: fadeIn 0.8s ease-in-out;
}

.section-heading {
    font-size: 25px;
    font-weight: 700;
    color: #ffffff;
    margin-top: 20px;
    margin-bottom: 15px;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

.login-box {
    padding: 25px;
    border-radius: 15px;
    background: linear-gradient(135deg, rgba(124,77,255,0.18), rgba(0,198,255,0.10));
    border: 1px solid rgba(124,77,255,0.4);
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(124,77,255,0.18), rgba(0,198,255,0.08));
    padding: 18px;
    border-radius: 15px;
    border: 1px solid rgba(124,77,255,0.35);
}

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #17142b, #10131d);
}

.doubt-card {
    padding: 18px;
    border-radius: 15px;
    background: linear-gradient(135deg, rgba(124,77,255,0.12), rgba(0,198,255,0.05));
    border: 1px solid rgba(124,77,255,0.25);
    margin-bottom: 12px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "logged_in": False,
    "role": None,          # "teacher" or "student"
    "user_id": None,
    "email": "",
    "token": None,
    "page": "Dashboard",
    "selected_doubt": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# LOGIN / REGISTER (role comes back from /auth/login)
# =========================================================

if not st.session_state.logged_in:

    st.markdown('<div class="main-title">🤖 SmartClarify</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-heading">🔐 Login</div>', unsafe_allow_html=True)
    st.write("Login as a student or a teacher — the right dashboard opens automatically.")

    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    email = st.text_input("📧 Email", key="login_email")
    password = st.text_input("🔑 Password", type="password", key="login_password")

    if st.button("🚀 Login", use_container_width=True):

        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": email.strip(),
                "password": password.strip()
            })

            if response.status_code == 200:
                data = response.json()

                st.session_state.logged_in = True
                st.session_state.token = data["access_token"]
                st.session_state.user_id = data["id"]
                st.session_state.role = data["role"]   # "teacher" or "student"
                st.session_state.email = email.strip()
                st.session_state.page = "Dashboard"

                st.success(f"✅ Login successful! Logged in as {data['role']}.")
                st.rerun()
            else:
                st.error("❌ Invalid email or password")

        except requests.exceptions.ConnectionError:
            st.error("⚠️ Backend se connect nahi ho paaya — check karo uvicorn chal raha hai ya nahi.")

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # REGISTER (choose role here)
    # -------------------------------------------------

    with st.expander("🆕 New here? Register"):

        reg_name = st.text_input("👤 Full Name", key="reg_name")
        reg_email = st.text_input("📧 Email", key="reg_email")
        reg_password = st.text_input("🔑 Password", type="password", key="reg_password")
        reg_role = st.selectbox("👥 I am a", ["student", "teacher"], key="reg_role")

        if st.button("📝 Register", use_container_width=True):

            if not reg_name.strip() or not reg_email.strip() or not reg_password.strip():
                st.warning("⚠️ Please fill in all fields.")
            else:
                try:
                    response = requests.post(f"{API_BASE}/auth/register", json={
                        "name": reg_name.strip(),
                        "email": reg_email.strip(),
                        "password": reg_password.strip(),
                        "role": reg_role
                    })

                    if response.status_code == 200:
                        st.success("✅ Registered successfully! You can now login above.")
                    else:
                        try:
                            detail = response.json().get("detail", "Registration failed")
                        except ValueError:
                            detail = f"Registration failed (status {response.status_code}): {response.text[:300]}"
                        st.error(f"❌ {detail}")

                except requests.exceptions.ConnectionError:
                    st.error("⚠️ Backend se connect nahi ho paaya.")

    st.stop()


# =========================================================
# SIDEBAR (menu changes based on role)
# =========================================================

st.sidebar.markdown('<div class="main-title">🤖 SmartClarify</div>', unsafe_allow_html=True)
st.sidebar.write(f"### {'👩‍🏫 Teacher' if st.session_state.role == 'teacher' else '🎓 Student'} Panel")
st.sidebar.markdown("---")

if st.sidebar.button("🏠 Dashboard", use_container_width=True):
    st.session_state.page = "Dashboard"
    st.session_state.selected_doubt = None
    st.rerun()

if st.session_state.role == "teacher":

    if st.sidebar.button("❓ Pending Doubts", use_container_width=True):
        st.session_state.page = "Pending Doubts"
        st.rerun()

    if st.sidebar.button("📊 Analytics", use_container_width=True):
        st.session_state.page = "Analytics"
        st.rerun()

else:  # student

    if st.sidebar.button("➕ Ask a Doubt", use_container_width=True):
        st.session_state.page = "Ask Doubt"
        st.session_state.selected_doubt = None
        st.rerun()

    if st.sidebar.button("❓ My Doubts", use_container_width=True):
        st.session_state.page = "My Doubts"
        st.session_state.selected_doubt = None
        st.rerun()

    if st.sidebar.button("👩‍🏫 Teacher Answers", use_container_width=True):
        st.session_state.page = "Teacher Answers"
        st.session_state.selected_doubt = None
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.write(f"### 👤 {st.session_state.role.title()}")
st.sidebar.caption(f"Logged in as {st.session_state.role} (ID: {st.session_state.user_id})")
st.sidebar.caption(st.session_state.email)

if st.sidebar.button("🚪 Logout", use_container_width=True):
    for key, value in defaults.items():
        st.session_state[key] = value
    st.rerun()


# =========================================================
# HELPERS
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


def fetch_my_doubts():
    try:
        response = requests.get(f"{API_BASE}/student/questions/{st.session_state.user_id}")
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Backend se connect nahi ho paaya")
        return []


def status_badge(status):
    if status == "pending":
        st.warning("⏳ Pending")
    else:
        st.success("👩‍🏫 Teacher Answered")


# =========================================================
# =====================  TEACHER VIEWS  ====================
# =========================================================

def teacher_dashboard():

    st.markdown('<div class="main-title">🤖 SmartClarify</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-heading">📊 Teacher Dashboard</div>', unsafe_allow_html=True)
    st.write("Welcome back! Here is an overview of your classroom doubts.")
    st.markdown("---")

    st.markdown('<div class="section-heading">📈 Dashboard Overview</div>', unsafe_allow_html=True)

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

    st.markdown('<div class="section-heading">❓ Pending Doubts</div>', unsafe_allow_html=True)

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

    if st.session_state.selected_doubt:

        selected_q = next(
            (q for q in pending_questions if q['id'] == st.session_state.selected_doubt),
            None
        )

        if selected_q:

            st.markdown("---")
            st.markdown('<div class="section-heading">📌 Selected Doubt</div>', unsafe_allow_html=True)

            st.info(
                f"❓ {selected_q['question_text']}\n\n"
                f"👤 Student ID: {selected_q['student_id']}\n"
                f"📘 Subject: {selected_q['subject']}"
            )

            answer = st.text_area("✍️ Write your answer", key=f"answer_{selected_q['id']}")

            if st.button("📤 Submit Answer", key=f"submit_{selected_q['id']}"):

                if answer.strip():
                    response = requests.post(
                        f"{API_BASE}/teacher/questions/{selected_q['id']}/answer",
                        json={
                            "teacher_id": st.session_state.user_id,
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


def teacher_pending_page():

    st.markdown('<div class="main-title">🤖 SmartClarify</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-heading">❓ Pending Doubts</div>', unsafe_allow_html=True)
    st.write("Review and answer doubts submitted by students.")
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
                st.session_state.page = "Dashboard"
                st.rerun()

        st.markdown("---")


def teacher_analytics_page():

    st.markdown('<div class="main-title">🤖 SmartClarify</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-heading">📊 Analytics</div>', unsafe_allow_html=True)
    st.info(
        "Analytics (confusion hotspots, topic trends) will be wired up "
        "once the RAG/confidence-scoring pipeline is built — Phase 2."
    )


# =========================================================
# =====================  STUDENT VIEWS  ====================
# =========================================================

def student_dashboard():

    st.markdown('<div class="main-title">🤖 SmartClarify</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-heading">🎓 Student Dashboard</div>', unsafe_allow_html=True)
    st.write("Welcome back! Here is your doubt activity.")
    st.markdown("---")

    my_doubts = fetch_my_doubts()

    total = len(my_doubts)
    pending = len([d for d in my_doubts if d["status"] == "pending"])
    resolved = len([d for d in my_doubts if d["status"] == "resolved"])

    st.markdown('<div class="section-heading">📊 My Learning Overview</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("❓ Total Doubts", total)
    with col2:
        st.metric("👩‍🏫 Teacher Answered", resolved)
    with col3:
        st.metric("⏳ Pending", pending)

    st.markdown("---")

    st.markdown('<div class="section-heading">⚡ Quick Actions</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕ Ask New Doubt", use_container_width=True):
            st.session_state.page = "Ask Doubt"
            st.rerun()

    with col2:
        if st.button("❓ View My Doubts", use_container_width=True):
            st.session_state.page = "My Doubts"
            st.rerun()

    st.markdown("---")

    st.markdown('<div class="section-heading">🕐 Recent Doubts</div>', unsafe_allow_html=True)

    if not my_doubts:
        st.info("You haven't asked any doubts yet 🎉")

    for doubt in my_doubts[:3]:

        col1, col2, col3 = st.columns([4, 2, 1])

        with col1:
            st.write(f"**❓ {doubt['question_text']}**")
            st.caption(f"📚 {doubt['subject']}")

        with col2:
            status_badge(doubt["status"])

        with col3:
            if st.button("View", key=f"dashboard_view_{doubt['id']}"):
                st.session_state.selected_doubt = doubt["id"]

        st.markdown("---")

    if st.session_state.selected_doubt:

        selected = next((d for d in my_doubts if d["id"] == st.session_state.selected_doubt), None)

        if selected:

            st.markdown('<div class="section-heading">📌 Doubt Details</div>', unsafe_allow_html=True)

            st.info(
                f"❓ {selected['question_text']}\n\n"
                f"📚 Subject: {selected['subject']}"
            )

            if selected["status"] == "pending":
                st.warning("⏳ Your doubt is waiting for a teacher to answer.")
            else:
                st.write("### 👩‍🏫 Teacher's Answer")
                st.success(selected["answer_text"])


def student_ask_doubt_page():

    st.markdown('<div class="main-title">🤖 SmartClarify</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-heading">➕ Ask a New Doubt</div>', unsafe_allow_html=True)
    st.write("Ask your question and get help from your teacher.")
    st.markdown("---")

    st.markdown('<div class="section-heading">📝 Doubt Details</div>', unsafe_allow_html=True)

    subject = st.selectbox(
        "📚 Select Subject",
        ["Computer Science", "DBMS", "Python", "Java", "Computer Networks",
         "Operating Systems", "Mathematics", "Other"]
    )

    question = st.text_input("❓ Your Question", placeholder="Example: What is inheritance in Java?")

    description = st.text_area(
        "📝 Explain Your Doubt (optional)",
        placeholder="Add more details to help your teacher answer better.",
        height=150
    )

    st.markdown("---")

    if st.button("📤 Submit Doubt", use_container_width=True):

        if not question.strip():
            st.warning("⚠️ Please enter your question.")
        else:
            full_text = question.strip()
            if description.strip():
                full_text += f"\n\nDetails: {description.strip()}"

            try:
                response = requests.post(f"{API_BASE}/student/questions", json={
                    "student_id": st.session_state.user_id,
                    "subject": subject,
                    "question_text": full_text
                })

                if response.status_code == 200:
                    st.success("✅ Your doubt has been submitted successfully!")
                    st.info("⏳ Your doubt is now waiting for a teacher to answer.")
                    st.session_state.page = "My Doubts"
                    st.rerun()
                else:
                    st.error("❌ Submission failed")

            except requests.exceptions.ConnectionError:
                st.error("⚠️ Backend se connect nahi ho paaya")


def student_my_doubts_page():

    st.markdown('<div class="main-title">🤖 SmartClarify</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-heading">❓ My Doubts</div>', unsafe_allow_html=True)
    st.write("View and track all the doubts you have submitted.")
    st.markdown("---")

    search = st.text_input("🔎 Search your doubts", placeholder="Search by question or subject...")
    filter_status = st.selectbox("📌 Filter by Status", ["All", "Pending", "Teacher Answered"])

    st.markdown("---")

    my_doubts = fetch_my_doubts()
    filtered = my_doubts

    if search.strip():
        filtered = [
            d for d in filtered
            if search.lower() in d["question_text"].lower() or search.lower() in d["subject"].lower()
        ]

    if filter_status == "Pending":
        filtered = [d for d in filtered if d["status"] == "pending"]
    elif filter_status == "Teacher Answered":
        filtered = [d for d in filtered if d["status"] == "resolved"]

    if not filtered:
        st.info("🔍 No doubts found.")

    for doubt in filtered:

        col1, col2, col3 = st.columns([4, 2, 1])

        with col1:
            st.write(f"**❓ {doubt['question_text']}**")
            st.caption(f"📚 {doubt['subject']}")

        with col2:
            status_badge(doubt["status"])

        with col3:
            if st.button("👁️ View", key=f"my_doubt_{doubt['id']}"):
                st.session_state.selected_doubt = doubt["id"]

        st.markdown("---")

    if st.session_state.selected_doubt:

        selected = next((d for d in my_doubts if d["id"] == st.session_state.selected_doubt), None)

        if selected:

            st.markdown('<div class="section-heading">📌 Selected Doubt</div>', unsafe_allow_html=True)

            st.info(
                f"❓ {selected['question_text']}\n\n"
                f"📚 Subject: {selected['subject']}"
            )

            if selected["status"] == "pending":
                st.warning("⏳ Your doubt is still pending.")
                st.caption("You will see the answer here once your teacher responds.")
            else:
                st.write("### 👩‍🏫 Teacher Answer")
                st.success(selected["answer_text"])


def student_teacher_answers_page():

    st.markdown('<div class="main-title">🤖 SmartClarify</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-heading">👩‍🏫 Teacher Answers</div>', unsafe_allow_html=True)
    st.write("View doubts that have been reviewed and answered by your teacher.")
    st.markdown("---")

    my_doubts = fetch_my_doubts()
    teacher_doubts = [d for d in my_doubts if d["status"] == "resolved"]

    if not teacher_doubts:
        st.info("👩‍🏫 No teacher answers yet.")

    for doubt in teacher_doubts:

        st.markdown('<div class="doubt-card">', unsafe_allow_html=True)
        st.write(f"### ❓ {doubt['question_text']}")
        st.caption(f"📚 {doubt['subject']}")
        st.write("### 👩‍🏫 Teacher's Answer")
        st.success(doubt["answer_text"])
        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# ROUTER
# =========================================================

if st.session_state.role == "teacher":

    if st.session_state.page == "Dashboard":
        teacher_dashboard()
    elif st.session_state.page == "Pending Doubts":
        teacher_pending_page()
    elif st.session_state.page == "Analytics":
        teacher_analytics_page()

else:  # student

    if st.session_state.page == "Dashboard":
        student_dashboard()
    elif st.session_state.page == "Ask Doubt":
        student_ask_doubt_page()
    elif st.session_state.page == "My Doubts":
        student_my_doubts_page()
    elif st.session_state.page == "Teacher Answers":
        student_teacher_answers_page()