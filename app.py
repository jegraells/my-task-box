import streamlit as st
import sqlite3

# --- 1. DATABASE SETUP ---
conn = sqlite3.connect('tasks_v6.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT)')
c.execute('''CREATE TABLE IF NOT EXISTS projects 
             (id INTEGER PRIMARY KEY, name TEXT, duration TEXT, 
              phase TEXT, progress INTEGER, details TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS project_chat 
             (id INTEGER PRIMARY KEY, project_id INTEGER, user TEXT, msg TEXT)''')
conn.commit()

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="My-Task-Box", page_icon="📦", layout="wide")

# Get the current page from URL or default to Projects
query_params = st.query_params
current_page = query_params.get("page", "Projects")

# --- 3. THE ULTIMATE CSS ---
st.markdown(f"""
    <style>
    /* Global Background & Font */
    .stApp {{ background-color: #F5F5DC; }}
    
    html, body, [class*="st-"], p, div {{
        color: #24292e !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }}

    /* Sidebar Background */
    [data-testid="stSidebar"] {{
        background-color: #EFEFDB !important;
        border-right: 1px solid #d0d7de;
    }}

    /* CUSTOM MENU LINKS */
    .nav-link {{
        display: block;
        padding: 12px 20px;
        margin: 4px 0;
        color: #24292e !important;
        text-decoration: none !important;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
    }}

    .nav-link:hover {{
        background-color: rgba(30, 41, 59, 0.05);
        padding-left: 30px; /* The "Pop" effect */
        color: #0f172a !important;
    }}

    .nav-link.active {{
        background-color: #FFC0CB !important; /* PINK */
        color: #000000 !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}

    /* Hide default Streamlit sidebar nav elements */
    [data-testid="stSidebarNav"] {{ display: none; }}
    
    h1 {{ font-weight: 600 !important; margin-bottom: 25px !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. CUSTOM SIDEBAR MENU ---
with st.sidebar:
    st.title("📂 My-Task-Box")
    
    menu_options = [
        ("🏗️ Projects", "Projects"),
        ("👥 Employees", "Employees"),
        ("✅ Tasks", "Tasks"),
        ("📄 Licenses & Permits", "Permits"),
        ("🏦 Bonds", "Bonds"),
        ("💰 Payroll", "Payroll"),
        ("👔 HR", "HR"),
        ("🔍 Exploration", "Exploration"),
        ("🏢 Commercial", "Commercial"),
        ("🏠 Residential", "Residential")
    ]

    for label, internal_name in menu_options:
        # Determine if this link is active
        active_class = "active" if current_page == internal_name else ""
        
        # Create a clickable HTML link that updates the URL query parameter
        st.markdown(
            f'<a href="/?page={internal_name}" target="_self" class="nav-link {active_class}">{label}</a>', 
            unsafe_allow_html=True
        )

# --- 5. NAVIGATION LOGIC ---
if 'active_project_id' not in st.session_state:
    st.session_state.active_project_id = None

if current_page == "Projects":
    if st.session_state.active_project_id is None:
        st.title("Projects Dashboard")
        with st.expander("➕ Create New Project"):
            p_name = st.text_input("Project Name")
            p_dur = st.text_input("Estimated Duration")
            p_phase = st.text_input("Current Phase")
            p_prog = st.slider("Phase Progress %", 0, 100, 0)
            if st.button("Launch Project"):
                if p_name:
                    c.execute('INSERT INTO projects (name, duration, phase, progress) VALUES (?,?,?,?)', 
                              (p_name, p_dur, p_phase, p_prog))
                    conn.commit()
                    st.rerun()

        projs = c.execute('SELECT id, name, phase, progress FROM projects').fetchall()
        cols = st.columns(3)
        for i, p in enumerate(projs):
            with cols[i % 3]:
                with st.container(border=True):
                    st.write(f"### {p[1]}")
                    st.write(f"**Phase:** {p[2]}")
                    st.progress(p[3]/100)
                    if st.button("Open Details", key=f"p_view_{p[0]}"):
                        st.session_state.active_project_id = p[0]
                        st.rerun()
    else:
        # PROJECT DETAIL VIEW
        p_id = st.session_state.active_project_id
        p_data = c.execute('SELECT * FROM projects WHERE id = ?', (p_id,)).fetchone()
        
        st.title(f"📍 {p_data[1]}")
        col_left, col_right = st.columns([1, 1])
        with col_left:
            if st.button("⬅️ Back"):
                st.session_state.active_project_id = None
                st.rerun()
            st.subheader("📋 Job Details")
            st.write(f"⏱️ **Est. Duration:** {p_data[2]}")
            st.write(f"🏗️ **Current Phase:** {p_data[3]}")
            st.write(f"📈 **Phase Progress:** {p_data[4]}%")
            st.progress(p_data[4]/100)
        
        with col_right:
            st.subheader("💬 Project Chat")
            chat_box = st.container(height=400, border=True)
            msgs = c.execute('SELECT user, msg FROM project_chat WHERE project_id = ?', (p_id,)).fetchall()
            for m in msgs: chat_box.write(f"**{m[0]}**: {m[1]}")
            
            chat_input = st.text_input("Message", key="msg_input")
            if st.button("Send"):
                if chat_input:
                    c.execute('INSERT INTO project_chat (project_id, user, msg) VALUES (?,?,?)', (p_id, "Admin", chat_input))
                    conn.commit()
                    st.rerun()

elif current_page == "Employees":
    st.title("Employee Directory")
    new_emp = st.text_input("Name")
    if st.button("Add"):
        c.execute('INSERT INTO employees (name) VALUES (?)', (new_emp,))
        conn.commit()
        st.rerun()
    emps = c.execute('SELECT name FROM employees').fetchall()
    for e in emps: st.write(f"• {e[0]}")

else:
    st.title(current_page)
    st.write(f"Welcome to the {current_page} section.")
