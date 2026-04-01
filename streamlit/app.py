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

def auth_layout():

    st.markdown("""
    <style>

    .block-container {
        padding-top: 10rem;
    }

    .glow-container {
        position: relative;
        display: inline-block;
    }

    .glow-container::before {
        content: "";
        position: absolute;
        top: -30px;
        left: -50px;
        width: 140%;
        height: 180%;
        background: radial-gradient(circle, rgba(139,92,246,0.35), transparent 70%);
        filter: blur(50px);
        z-index: -1;
    }
    
        /* Buttons */
    .stButton>button {
        width: 100%;
        height: 55px;
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

    
    .brand-title {
        font-size: 64px;
        font-weight: 800;
        background: linear-gradient(90deg, #8B5CF6, #6366F1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .brand-sub {
        font-size: 20px;
        color: #9CA3AF;
        margin-top: 10px;
    }

    .divider {
        border-left: 2px solid rgba(255,255,255,0.1);
        height: 300px;
        margin: auto;
    }
    



    /* Right panel scroll */
    .scroll-box {
       
    overflow-y: auto;
    padding-right: 10px;
    }

    /* Optional: nice scrollbar */
    .scroll-box::-webkit-scrollbar {
        width: 6px;
    }
    .scroll-box::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.2);
    border-radius: 10px;
    }
    
    /* Align columns vertically center */
    div[data-testid="column"] {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
          </style>
          """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 0.1, 1])

    # ---------------- LEFT (STATIC) ----------------
    with col1:
        st.markdown("""
        <div class="glow-container">
            <div class="brand-title">UniConnect</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='brand-sub'>Institution Chat System</div>", unsafe_allow_html=True)

    # ---------------- DIVIDER ----------------
    with col2:
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ---------------- RIGHT (DYNAMIC) ----------------
    with col3:

        # 👇 START SCROLL AREA
        st.markdown("<div class='scroll-box'>", unsafe_allow_html=True)

        page = st.session_state.page

        if page == "welcome":
            if st.button("Login", key="main_login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Register", key="main_register", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()

        elif page == "login":
            st.markdown("### Login")

            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")

            if st.button("Login", key="login_btn", use_container_width=True):
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

        elif page == "register":
            st.markdown("### 📝 Register")

            name = st.text_input("Name", key="reg_name")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_pass")

            admin_mode = st.toggle("🔐 Register as Admin")

            if admin_mode:
                role = "admin"
            else:
                role = st.selectbox("Select Role", ["student", "faculty", "cr"])

            if st.button("Register", key="register_btn", use_container_width=True):
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

        # 👇 END SCROLL AREA
        st.markdown("</div>", unsafe_allow_html=True)
# ---------------- SIDEBAR ----------------
def sidebar():
    role = st.session_state.get("role", "")
    st.sidebar.markdown(f"👤 **Role:** {role}")
    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout", key="logout"):
        st.session_state.clear()
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
    auth_layout()


else:
    role = st.session_state["role"]

    if role == "student":
        student_dashboard()
    elif role == "faculty":
        faculty_dashboard()
    elif role == "admin":
        admin_dashboard()


