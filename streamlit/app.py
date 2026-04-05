import streamlit as st
import requests

# ---------------- CONFIG ----------------
BASE_URL = "http://127.0.0.1:5000/api"
BASE_URL_Chat = "http://127.0.0.1:5000"

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
                    st.session_state["user_id"] = data["user"]["id"]
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
        ["Mark Attendance", "My Attendance","Chat", "Notices", "Polls"]
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
    # CHAT
    elif menu == "Chat":

        import time

        st.subheader("💬 Chat System")

        # 🔐 Headers
        headers = {
            "Authorization": f"Bearer {st.session_state['token']}"
        }

        # 🔧 Initialize session state
        if "auto_refresh" not in st.session_state:
            st.session_state["auto_refresh"] = True

        if "chat_user" not in st.session_state:
            st.session_state["chat_user"] = None

        if "chat_input" not in st.session_state:
            st.session_state["chat_input"] = ""



        # 👥 Fetch users
        res = requests.get(f"{BASE_URL_Chat}/chat/users", headers=headers)

        if res.status_code != 200:
            st.error(f"Error {res.status_code}: {res.text}")
        else:
            users = res.json()

            # 🔍 SEARCH BAR
            search_query = st.text_input("🔍 Search users", key="user_search")

            st.write("### 👥 Start a Conversation")

            # 🔍 Filter users
            filtered_users = [
                user for user in users
                if search_query.lower() in user["name"].lower()
            ]

            if not filtered_users:
                st.info("No users found")

            # 📌 Select user
            for idx, user in enumerate(filtered_users):
                if st.button(
                        f"{user['name']} ({user['role']})",
                        key=f"user_{user['id']}_{idx}"):

                    # 🔥 Reset chat-related state
                    st.session_state["chat_user"] = user
                    st.session_state["chat_input"] = ""   # clear old message
                    st.session_state.pop("last_sent", None)
                    st.rerun()

        # 💬 If user selected → open chat
        if "chat_user" in st.session_state:

            selected_user = st.session_state.get("chat_user")

            if selected_user:

                st.divider()
                st.write(f"## 💬 Chat with {selected_user['name']}")


                # 📥 Fetch messages
                messages_res = requests.get(
                    f"{BASE_URL_Chat}/chat/messages/{selected_user['id']}",
                    headers=headers
                )
                st.empty()
                if messages_res.status_code != 200:
                    st.error("Failed to load messages")
                else:
                    messages = messages_res.json()

                    # 💬 Display messages (cleaner)
                    for msg in messages:
                        if msg["sender_id"] == int(st.session_state["user_id"]):
                            st.markdown(
                                f"""
                            <div style='display:flex; justify-content:flex-end;'>
                                <div style='
                                    background:#25D366;
                                    color:white;
                                    padding:8px 12px;
                                    border-radius:15px;
                                    max-width:60%;
                                    margin:5px;
                                    word-wrap:break-word;
                                '>
                                    <b>You</b><br>
                                    {msg['content']}<br>
                                    <small style='opacity:0.8'>{msg['timestamp']}</small>
                                </div>
                            </div>
                            """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f"""
                            <div style='display:flex; justify-content:flex-start;'>
                                <div style='
                                    background:#E5E5EA;
                                    color:black;
                                    padding:8px 12px;
                                    border-radius:15px;
                                    max-width:60%;
                                    margin:5px;
                                    word-wrap:break-word;
                                '>
                                    <b>{selected_user['name']}</b><br>
                                    {msg['content']}<br>
                                    <small style='opacity:0.6'>{msg['timestamp']}</small>
                                </div>
                            </div>
                            """,
                                unsafe_allow_html=True
                            )

                st.divider()

                # ✉️ Send message
                def send_message_callback(selected_user, headers):

                    msg = st.session_state.get("chat_input", "")

                    if not msg.strip():
                        st.warning("Message cannot be empty")
                        return

                    res = requests.post(
                        f"{BASE_URL_Chat}/chat/send",
                        json={
                            "receiver_id": selected_user["id"],
                            "content": msg
                        },
                        headers=headers
                    )

                    if res.status_code == 200:
                        st.session_state["chat_input"] = ""  # ✅ clear input
                    else:
                        st.error("Failed to send message")
                # ✉️ Input box
                st.text_input("Type a message", key="chat_input")

                # 📤 Send button
                st.button(
                    "Send",
                    key="send_msg",
                    on_click=send_message_callback,
                    args=(selected_user, headers)
    )
                # 🔄 Auto refresh ONLY when chat open
                if selected_user in st.session_state and st.session_state["auto_refresh"]:
                    time.sleep(2)
                    st.rerun()

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

            if p.get("multi_select"):
                choice = st.multiselect(
                    "Select options",
                    p["options"],
                    key=f"poll_{p['id']}"
                )
            else:
                choice = st.radio(
                    "Choose option",
                    p["options"],
                    key=f"poll_{p['id']}"
                )

            if st.button("Vote", key=f"vote_{p['id']}"):
                requests.post(
                    f"{BASE_URL}/polls/{p['id']}/vote",
                    json={
                        "options": choice if isinstance(choice, list) else [choice]
                    },
                    headers={"Authorization": f"Bearer {st.session_state['token']}"}
                )
                st.success("Voted ✅")
                st.rerun()


# ---------------- CR DASHBOARD ----------------
def cr_dashboard():
    sidebar()

    st.markdown("## 👨‍🎓 Class Representative Dashboard")
    st.divider()

    menu = st.sidebar.selectbox(
        "Menu",
        ["Mark Attendance", "My Attendance","Chat", "Create Notice","View Notices","Create Poll", "View Polls"]
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

    # CHAT
    elif menu == "Chat":

        import time

        st.subheader("💬 Chat System")

        # 🔐 Headers
        headers = {
            "Authorization": f"Bearer {st.session_state['token']}"
        }

        # 👥 Fetch users
        res = requests.get(f"{BASE_URL_Chat}/chat/users", headers=headers)

        if res.status_code != 200:
            st.error(f"Error {res.status_code}: {res.text}")
        else:
            users = res.json()

            # 🔍 SEARCH BAR
            search_query = st.text_input("🔍 Search users", key="user_search")

            st.write("### 👥 Start a Conversation")

            # 🔍 Filter users
            filtered_users = [
                user for user in users
                if search_query.lower() in user["name"].lower()
            ]

            if not filtered_users:
                st.info("No users found")

            # 📌 Select user
            for user in filtered_users:
                if st.button(f"{user['name']} ({user['role']})", key=f"user_{user['id']}"):
                    st.session_state["chat_user"] = user
                    st.rerun()  # 👈 important for instant switch

        # 💬 If user selected → open chat
        if "chat_user" in st.session_state:

            selected_user = st.session_state["chat_user"]

            st.divider()
            st.write(f"## 💬 Chat with {selected_user['name']}")

            # 📥 Fetch messages
            messages_res = requests.get(
                f"{BASE_URL_Chat}/chat/messages/{selected_user['id']}",
                headers=headers
            )

            if messages_res.status_code != 200:
                st.error("Failed to load messages")
            else:
                messages = messages_res.json()

                # 💬 Display messages (cleaner)
                for msg in messages:
                    if msg["sender_id"] == int(st.session_state["user_id"]):
                        st.markdown(
                            f"""
                            <div style='display:flex; justify-content:flex-end;'>
                                <div style='
                                    background:#25D366;
                                    color:white;
                                    padding:8px 12px;
                                    border-radius:15px;
                                    max-width:60%;
                                    margin:5px;
                                    word-wrap:break-word;
                                '>
                                    <b>You</b><br>
                                    {msg['content']}<br>
                                    <small style='opacity:0.8'>{msg['timestamp']}</small>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <div style='display:flex; justify-content:flex-start;'>
                                <div style='
                                    background:#E5E5EA;
                                    color:black;
                                    padding:8px 12px;
                                    border-radius:15px;
                                    max-width:60%;
                                    margin:5px;
                                    word-wrap:break-word;
                                '>
                                    <b>{selected_user['name']}</b><br>
                                    {msg['content']}<br>
                                    <small style='opacity:0.6'>{msg['timestamp']}</small>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            st.divider()

            # ✉️ Send message
            if "chat_input" not in st.session_state:
                st.session_state["chat_input"] = ""

            new_msg = st.text_input("Type a message", key="chat_input")

            col1, col2 = st.columns([5,1])

            with col2:
                if st.button("Send", key="send_msg"):

                    if not new_msg.strip():
                        st.warning("Message cannot be empty")

                    else:
                        send_res = requests.post(
                            f"{BASE_URL_Chat}/chat/send",
                            json={
                                "receiver_id": selected_user["id"],
                                "content": new_msg
                            },
                            headers=headers
                        )

                        if send_res.status_code == 200:
                            st.session_state["chat_input"] = ""  # 🔥 FIX
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Failed to send message")

            # 🔄 Auto refresh ONLY when chat open
            time.sleep(2)
            st.rerun()
    # NOTICES

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

    elif menu == "View Notices":
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

    # ---------------- CREATE POLL ----------------
    elif menu == "Create Poll":
        question = st.text_input("Poll Question")
        options = st.text_area("Options (comma separated)")

        multi_select = st.toggle("Allow multiple selections")

        if st.button("Create Poll", key="create_poll_faculty"):
            if not question or not options:
                st.warning("Fill all fields")
                return

        option_list = [opt.strip() for opt in options.split(",")]

        res = requests.post(
            f"{BASE_URL}/polls/",
            json={
                "question": question,
                "options": option_list,
                "multi_select": multi_select   # 👈 NEW
            },
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )

        st.success("Poll created ✅")

    elif menu == "View Polls":
        res = requests.get(
            f"{BASE_URL}/polls/",
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )

        for p in res.json():
            st.subheader(p["question"])

            if p.get("multi_select"):
                choice = st.multiselect(
                    "Select options",
                    p["options"],
                    key=f"poll_{p['id']}"
                )
            else:
                choice = st.radio(
                    "Choose option",
                    p["options"],
                    key=f"poll_{p['id']}"
                )

            if st.button("Vote", key=f"vote_{p['id']}"):
                requests.post(
                    f"{BASE_URL}/polls/{p['id']}/vote",
                    json={
                        "options": choice if isinstance(choice, list) else [choice]
                    },
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
            "Sessions",
            "Live Attendance",
            "Create Notice",
            "View Notices",
            "Create Poll",
            "View Polls",
            "Chat"
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

    # ---------------- LIVE SESSIONS----------------
    elif menu == "Sessions":

        st.subheader("📡 Live Sessions")

        res = requests.get(
            f"{BASE_URL}/attendance/live",
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )

        if res.status_code != 200:
            st.error("Failed to fetch sessions")
            st.write(res.text)
            return

        sessions = res.json()

        # ✅ EMPTY STATE
        if not sessions:
            st.markdown("""
            <div style='
                text-align: center;
                padding: 30px;
                border-radius: 12px;
                background: rgba(255,255,255,0.03);
                color: #9CA3AF;
            '>
                <h4>📡 No Live Sessions</h4>
                <p>Start a session to begin tracking attendance.</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 Start Session", use_container_width=True):
                res = requests.post(
                    f"{BASE_URL}/attendance/start",
                    headers={"Authorization": f"Bearer {st.session_state['token']}"}
                )

                if res.status_code == 201:
                    st.success("Session started ✅")
                    st.rerun()

            return

        # ✅ ACTIVE SESSIONS
        st.metric("Active Sessions", len(sessions))

        for s in sessions:
            st.markdown(f"### 🧑‍🏫 Session {s['session_id']}")
            st.write(f"🔑 Code: {s['code']}")
            st.write(f"⏱ Started: {s['start_time']}")

            if st.button("❌ End Session", key=f"end_{s['session_id']}"):

                end_res = requests.post(
                    f"{BASE_URL}/attendance/end/{s['session_id']}",
                    headers={"Authorization": f"Bearer {st.session_state['token']}"}
                )

                if end_res.status_code == 200:
                    st.success("Session ended ✅")
                    st.rerun()
                else:
                    st.error("Failed to end session")
                    st.write(end_res.text)

            st.divider()

            st.markdown("---")

        #Past sessions
        st.markdown("## 📜 Past Sessions")

        res = requests.get(
            f"{BASE_URL}/attendance/past",
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )

        if res.status_code != 200:
            st.error("Failed to fetch past sessions")
            st.write(res.text)
        else:
            past_sessions = res.json()

            if not past_sessions:
                st.markdown("""
                <div style='
                    padding: 20px;
                    border-radius: 10px;
                    background: rgba(255,255,255,0.02);
                    color: #9CA3AF;
                '>
                    No past sessions yet
                </div>
                """, unsafe_allow_html=True)
            else:
                for s in past_sessions:
                    st.markdown(f"### 🧑‍🏫 Session {s['session_id']}")
                    st.write(f"🔑 Code: {s['code']}")
                    st.write(f"⏹ Ended at: {s['ended_at']}")

                    st.divider()

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

    # ---------------- VIEW NOTICE ----------------
    elif menu == "View Notices":

        st.subheader("📢 Notices")

        res = requests.get(
            f"{BASE_URL}/notices/",
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )

        if res.status_code != 200:
            st.error("Failed to fetch notices")
            st.write(res.text)
            return

        notices = res.json()

        if not notices:
            st.info("No notices available")
            return

        for n in notices:

            # 🔥 NOTICE CARD
            st.markdown(f"""
            <div style='
                padding: 20px;
                border-radius: 12px;
                background: rgba(255,255,255,0.03);
                margin-bottom: 15px;
            '>
                <h4>{n['title']}</h4>
                <p>{n['content']}</p>
            </div>
            """, unsafe_allow_html=True)

            # 🔢 Reaction counts
            reactions = n.get("reactions", {})

            col1, col2, col3 = st.columns(3)

            col1.metric("👍 Likes", reactions.get("👍", 0))
            col2.metric("❤️ Love", reactions.get("❤️", 0))
            col3.metric("👀 Views", reactions.get("👀", 0))

            # 🎯 Reaction buttons
            col1, col2, col3 = st.columns(3)

            if col1.button("👍", key=f"like_{n['id']}"):
                requests.post(
                    f"{BASE_URL}/notices/{n['id']}/react",
                    json={"reaction": "👍"},
                    headers={"Authorization": f"Bearer {st.session_state['token']}"}
                )
                st.rerun()

            if col2.button("❤️", key=f"love_{n['id']}"):
                requests.post(
                    f"{BASE_URL}/notices/{n['id']}/react",
                    json={"reaction": "❤️"},
                    headers={"Authorization": f"Bearer {st.session_state['token']}"}
                )
                st.rerun()

            if col3.button("👀", key=f"view_{n['id']}"):
                requests.post(
                    f"{BASE_URL}/notices/{n['id']}/react",
                    json={"reaction": "👀"},
                    headers={"Authorization": f"Bearer {st.session_state['token']}"}
                )
                st.rerun()

            st.divider()

    # ---------------- CREATE POLL ----------------
    elif menu == "Create Poll":
        question = st.text_input("Poll Question")
        options = st.text_area("Options (comma separated)")

        multi_select = st.toggle("Allow multiple selections")

        if st.button("Create Poll", key="create_poll_faculty"):
            if not question or not options:
                st.warning("Fill all fields")
                return

            option_list = [opt.strip() for opt in options.split(",")]

            res = requests.post(
                f"{BASE_URL}/polls/",
                json={
                    "question": question,
                    "options": option_list,
                    "multi_select": multi_select   # 👈 NEW
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

        if res.status_code != 200:
            st.error("Failed to fetch polls")
            st.write(res.text)
            return

        try:
            polls = res.json()
        except:
            st.error("Invalid server response")
            st.write(res.text)
            return

        if not polls:
            st.markdown("""
            <div style='text-align:center; padding:30px; color:#9CA3AF'>
                <h4>No polls available</h4>
            </div>
            """, unsafe_allow_html=True)
            return

        for p in polls:

            # 🔥 POLL CARD START
            st.markdown("""
            <div style='
                padding: 20px;
                border-radius: 14px;
                background: rgba(255,255,255,0.03);
                margin-bottom: 20px;
            '>
            """, unsafe_allow_html=True)

            st.markdown(f"### 📊 {p['question']}")

            # 👇 Input type
            if p.get("multi_select"):
                selected = st.multiselect(
                    "Select options",
                    p["options"],
                    key=f"poll_{p['id']}"
                )
            else:
                selected = st.radio(
                    "Choose option",
                    p["options"],
                    key=f"poll_{p['id']}"
                )

            # 👇 Vote button
            # if st.button("Vote", key=f"vote_{p['id']}", use_container_width=True):
            #
            #     payload = {
            #         "options": selected if isinstance(selected, list) else [selected]
            #     }
            #
            #     vote_res = requests.post(
            #         f"{BASE_URL}/polls/{p['id']}/vote",
            #         json=payload,
            #         headers={"Authorization": f"Bearer {st.session_state['token']}"}
            #     )
            #
            #     if vote_res.status_code == 200:
            #         st.success("Vote recorded ✅")
            #         st.rerun()
            #     else:
            #         st.error("Failed to vote")
            #         st.write(vote_res.text)

            # 👇 RESULTS
            result_res = requests.get(
                f"{BASE_URL}/polls/{p['id']}/results",
                headers={"Authorization": f"Bearer {st.session_state['token']}"}
            )

            if result_res.status_code == 200:
                results = result_res.json()

                if results:
                    st.markdown("#### 📈 Results")

                    total_votes = sum(results.values())

                    for opt, count in results.items():
                        percentage = (count / total_votes * 100) if total_votes > 0 else 0

                        st.markdown(f"**{opt}** — {count} votes ({percentage:.1f}%)")
                        st.progress(percentage / 100)

            else:
                st.warning("Could not load results")

            # 🔥 POLL CARD END
            st.markdown("</div>", unsafe_allow_html=True)

        # CHAT
    elif menu == "Chat":

        import time


        st.subheader("💬 Chat System")

        # 🔐 Headers
        headers = {
            "Authorization": f"Bearer {st.session_state['token']}"
        }

        # 👥 Fetch users
        res = requests.get(f"{BASE_URL_Chat}/chat/users", headers=headers)

        if res.status_code != 200:
            st.error("Failed to load users")
        else:
            users = res.json()

            st.write("### 👥 Start a Conversation")

            # 📌 Select user
            for user in users:
                if st.button(f"{user['name']} ({user['role']})", key=f"user_{user['id']}"):
                    st.session_state["chat_user"] = user

        # 💬 If user selected → open chat
        if "chat_user" in st.session_state:

            selected_user = st.session_state["chat_user"]

            st.divider()
            st.write(f"## 💬 Chat with {selected_user['name']}")

            # 📥 Fetch messages
            messages_res = requests.get(
                f"{BASE_URL_Chat}/chat/messages/{selected_user['id']}",
                headers=headers
            )

            if messages_res.status_code != 200:
                st.error("Failed to load messages")
            else:
                messages = messages_res.json()

                # 💬 Display messages
                for msg in messages:
                    if msg["sender_id"] == int(st.session_state["user_id"]):
                        st.markdown(f"🟢 **You:** {msg['content']}  \n🕒 {msg['timestamp']}")
                    else:
                        st.markdown(f"🔵 **{selected_user['name']}:** {msg['content']}  \n🕒 {msg['timestamp']}")

            st.divider()

            # ✉️ Send message
            new_msg = st.text_input("Type a message", key="chat_input")

            if st.button("Send", key="send_msg"):

                if not new_msg.strip():
                    st.warning("Message cannot be empty")

                else:
                    send_res = requests.post(
                        f"{BASE_URL_Chat}/chat/send",
                        json={
                            "receiver_id": selected_user["id"],
                            "content": new_msg
                        },
                        headers=headers
                    )

                    if send_res.status_code == 200:
                        st.success("Message sent ✅")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to send message")

            # 🔄 Auto refresh (simulate real-time)
            time.sleep(2)
            st.rerun()
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
    elif role == "cr":
         cr_dashboard()
    elif role == "faculty":
        faculty_dashboard()
    elif role == "admin":
        admin_dashboard()


