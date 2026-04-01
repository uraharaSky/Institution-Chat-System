import streamlit as st
import requests

# ---------------- CONFIG ----------------
BASE_URL = "http://127.0.0.1:5000/api"

st.set_page_config(
    page_title="Institution Chat System",
    page_icon="🎓",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "token" not in st.session_state:
    st.session_state["token"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "welcome"

# ---------------- WELCOME PAGE ----------------
# def welcome_page():
#     st.markdown("<h1>🎓 Institution System</h1>", unsafe_allow_html=True)
#     st.markdown("<div class='subtitle'>Seamless communication between students & admins</div>", unsafe_allow_html=True)
#
#     col1, col2 = st.columns(2)
#
#     with col1:
#         if st.button("🔐 Login", key="login_btn", use_container_width=True):
#             st.session_state.page = "login"
#             st.rerun()
#
#     with col2:
#         if st.button("📝 Register", key="register_btn", use_container_width=True):
#             st.session_state.page = "register"
#             st.rerun()

# ---------------- STYLING ----------------
# st.markdown("""
# <style>
#     .main {
#         background-color: #0E1117;
#     }
#     .block-container {
#         padding-top: 6rem;
#     }
# </style>
# """, unsafe_allow_html=True)

st.markdown("""
<style>

/* Background */
.main {
    background-color: #0E1117;
}

/* Container */
.block-container {
    padding-top: 4rem;
    max-width: 1000px;
}

/* Title */
h1 {
    text-align: center;
    font-weight: 700;
    font-size: 48px;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #9CA3AF;
    font-size: 18px;
    margin-bottom: 2rem;
}

/* Buttons */
.stButton>button {
    width: 100%;
    height: 50px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    border: none;
    color: white;
    background: linear-gradient(90deg, #6366F1, #22D3EE);
    transition: all 0.25s ease;

}

.stButton>button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0px 8px 20px rgba(99,102,241,0.3);
}

</style>
""", unsafe_allow_html=True)


# # 🔥 CARD START
# st.markdown("""
# <div style='
#     padding: 40px;
#     border-radius: 20px;
#     background: rgba(255,255,255,0.03);
#     backdrop-filter: blur(10px);
# '>
# """, unsafe_allow_html=True)


# 👉 THIS is "your content"
# st.markdown("<h1>🎓 Institution System</h1>", unsafe_allow_html=True)
# st.markdown("<div class='subtitle'>Seamless communication between students & admins</div>", unsafe_allow_html=True)
#
#
# col1, col2 = st.columns(2)
#
# with col1:
#     st.button("🔐 Login", key="login_btn", use_container_width=True)
#
# with col2:
#     st.button("📝 Register", key="register_btn", use_container_width=True)
# 🔥 CARD END
# st.markdown("</div>", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------
def sidebar():
    st.sidebar.markdown("## 🎓 Navigation")
    role = st.session_state.get("role", "")
    st.sidebar.markdown(f"👤 **Role:** {role}")
    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout", key="logout"):
        st.session_state.clear()
        st.rerun()

# ---------------- LOGIN ----------------
def login_page():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", key="login_btn"):
        res = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })

        if res.status_code == 200:
            data = res.json()
            st.session_state["token"] = data["token"]
            st.session_state["role"] = data["user"]["role"]
            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Invalid credentials ❌")

    if st.button("⬅ Back", key="login_back"):
        st.session_state.page = "welcome"
        st.rerun()

# ---------------- REGISTER ----------------
def register_page():
    st.title("📝 Register")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    # 🔐 Admin toggle
    admin_mode = st.toggle("🔐 Register as Admin")

    if admin_mode:
        role = "admin"
        st.info("Admin mode enabled 👑")
    else:
        role = st.selectbox("Select Role", ["student", "faculty", "cr"])

    if st.button("Register", key="register_btn"):
        res = requests.post(f"{BASE_URL}/auth/register", json={
            "name": name,
            "email": email,
            "password": password,
            "role": role
        })

        if res.status_code == 201:
            st.success("Registered successfully ✅")
        else:
            st.error("Registration failed ❌")
            st.write(res.text)

    if st.button("⬅ Back", key="register_back"):
        st.session_state.page = "welcome"
        st.rerun()

# ---------------- STUDENT DASHBOARD ----------------
def student_dashboard():
    sidebar()

    st.markdown("## 👨‍🎓 Student Dashboard")
    st.divider()

    menu = st.sidebar.selectbox(
        "Menu",
        ["Mark Attendance", "My Attendance", "Notices", "Polls"]
    )

    # MARK ATTENDANCE
    if menu == "Mark Attendance":
        code = st.text_input("Enter Code")

        if st.button("Mark", key="mark_btn"):
            res = requests.post(
                f"{BASE_URL}/attendance/mark",
                json={"code": code},
                headers={"Authorization": f"Bearer {st.session_state['token']}"}
            )
            st.json(res.json())

    # MY ATTENDANCE
    elif menu == "My Attendance":
        res = requests.get(
            f"{BASE_URL}/attendance/my",
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )

        data = res.json()

        if not data:
            st.info("No attendance records")
        else:
            st.table(data)

    # NOTICES
    elif menu == "Notices":
        res = requests.get(
            f"{BASE_URL}/notices/",
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )

        for n in res.json():
            st.subheader(n["title"])
            st.write(n["content"])

            col1, col2, col3 = st.columns(3)

            if col1.button("👍", key=f"like_{n['id']}"):
                requests.post(f"{BASE_URL}/notices/{n['id']}/react",
                              json={"reaction": "👍"},
                              headers={"Authorization": f"Bearer {st.session_state['token']}"})

            if col2.button("❤️", key=f"love_{n['id']}"):
                requests.post(f"{BASE_URL}/notices/{n['id']}/react",
                              json={"reaction": "❤️"},
                              headers={"Authorization": f"Bearer {st.session_state['token']}"})

            if col3.button("👀", key=f"view_{n['id']}"):
                requests.post(f"{BASE_URL}/notices/{n['id']}/react",
                              json={"reaction": "👀"},
                              headers={"Authorization": f"Bearer {st.session_state['token']}"})

            st.divider()

    # POLLS
    elif menu == "Polls":
        res = requests.get(
            f"{BASE_URL}/polls/",
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )

        for p in res.json():
            st.subheader(p["question"])

            choice = st.radio(
                "Choose option",
                p["options"],
                key=f"poll_{p['id']}"
            )

            if st.button("Vote", key=f"vote_{p['id']}"):
                requests.post(
                    f"{BASE_URL}/polls/{p['id']}/vote",
                    json={"option": choice},
                    headers={"Authorization": f"Bearer {st.session_state['token']}"}
                )
                st.success("Voted ✅")
                st.rerun()

# ---------------- FACULTY ----------------
def faculty_dashboard():
    sidebar()

    st.markdown("## 👨‍🏫 Faculty Dashboard")
    st.caption("Manage sessions, notices, and polls")
    st.divider()

    menu = st.sidebar.selectbox(
        "Menu",
        [
            "Start Session",
            "Live Attendance",
            "Create Notice",
            "Create Poll",
            "View Polls"
        ]
    )

    # ---------------- START SESSION ----------------
    if menu == "Start Session":
        if st.button("🚀 Start Session", key="start_session"):
            res = requests.post(
                f"{BASE_URL}/attendance/start",
                headers={"Authorization": f"Bearer {st.session_state['token']}"}
            )
            st.json(res.json())

    # ---------------- LIVE ATTENDANCE ----------------
    elif menu == "Live Attendance":
        session_id = st.text_input("Session ID")

        if st.button("Fetch", key="fetch_attendance"):
            res = requests.get(
                f"{BASE_URL}/attendance/session/{session_id}",
                headers={"Authorization": f"Bearer {st.session_state['token']}"}
            )

            if res.status_code != 200:
                st.error("Failed to fetch attendance")
                st.write(res.text)
                return

            data = res.json()

            if not data:
                st.info("No students marked yet")
            else:
                for entry in data:
                    st.write(f"👨‍🎓 {entry['student_id']} | {entry['time']}")

    # ---------------- CREATE NOTICE ----------------
    elif menu == "Create Notice":
        title = st.text_input("Title")
        content = st.text_area("Content")

        if st.button("Post Notice", key="post_notice"):
            res = requests.post(
                f"{BASE_URL}/notices/",
                json={"title": title, "content": content},
                headers={"Authorization": f"Bearer {st.session_state['token']}"}
            )
            st.success("Notice posted ✅")

    # ---------------- CREATE POLL ----------------
    elif menu == "Create Poll":
        question = st.text_input("Poll Question")
        options = st.text_area("Options (comma separated)")

        if st.button("Create Poll", key="create_poll_faculty"):
            if not question or not options:
                st.warning("Fill all fields")
                return

            option_list = [opt.strip() for opt in options.split(",")]

            res = requests.post(
                f"{BASE_URL}/polls/",
                json={
                    "question": question,
                    "options": option_list
                },
                headers={"Authorization": f"Bearer {st.session_state['token']}"}
            )

            st.success("Poll created ✅")

    # ---------------- VIEW POLLS ----------------
    elif menu == "View Polls":
        res = requests.get(
            f"{BASE_URL}/polls/",
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )

        polls = res.json()

        if not polls:
            st.info("No polls available")
            return

        for p in polls:
            st.subheader(f"📊 {p['question']}")

            result_res = requests.get(
                f"{BASE_URL}/polls/{p['id']}/results",
                headers={"Authorization": f"Bearer {st.session_state['token']}"}
            )

            st.json(result_res.json())
            st.divider()

# ---------------- ADMIN ----------------
def admin_dashboard():
    sidebar()

    st.markdown("## 👑 Admin Dashboard")
    st.divider()

    menu = st.sidebar.selectbox(
        "Menu",
        ["Users", "Summary"]
    )

    # ---------------- USERS ----------------
    if menu == "Users":
        res = requests.get(
            f"{BASE_URL}/admin/users",
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )
        if res.status_code != 200:
            st.error("API Failed ❌")
            st.write("Status Code:", res.status_code)
            st.write("Response:", res.text)
            return

        data = res.json()
        st.table(data)

    # ---------------- SUMMARY ----------------
    elif menu == "Summary":

        res = requests.get(
            f"{BASE_URL}/admin/summary",
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )

        if res.status_code != 200:
            st.error("API Failed ❌")
            st.write("Status:", res.status_code)
            st.write(res.text)
            return

        data = res.json()
        st.table(data)

        st.markdown("## 📊 System Overview")

        # 🔥 METRICS
        col1, col2, col3 = st.columns(3)
        col4, col5 = st.columns(2)

        col1.metric("👥 Users", data["Total Users"])
        col2.metric("📚 Sessions", data["Total Sessions"])
        col3.metric("✅ Attendance", data["Total Attendance"])
        col4.metric("📢 Notices", data["Total Notices"])
        col5.metric("🗳️ Polls", data["Total Polls"])

        st.divider()

        # 🔥 BAR CHART
        chart_data = {
            "Users": data["Total Users"],
            "Sessions": data["Total Sessions"],
            "Attendance": data["Total Attendance"],
            "Notices": data["Total Notices"],
            "Polls": data["Total Polls"]
        }

        st.markdown("### 📊 Overview Chart")
        st.bar_chart(chart_data)

        # 🔥 PIE CHART
        import matplotlib.pyplot as plt

        st.markdown("### 🥧 Distribution")

        labels = list(chart_data.keys())
        values = list(chart_data.values())

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%')
        ax.axis('equal')

        st.pyplot(fig)
# ---------------- ROUTER ----------------
if not st.session_state["token"]:
    st.title("🎓 Institution Chat System")


    if st.button("Login", key="main_login"):
        st.session_state.page = "login"

    if st.button("Register", key="main_register"):
        st.session_state.page = "register"

    if st.session_state.page == "login":
        login_page()

    elif st.session_state.page == "register":
        register_page()

else:
    role = st.session_state["role"]

    if role == "student":
        student_dashboard()
    elif role == "faculty":
        faculty_dashboard()
    elif role == "admin":
        admin_dashboard()


