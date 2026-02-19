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

# --- 2. PAGE CONFIG & DESIGN ---
st.set_page_config(page_title="My-Task-Box", page_icon="📦", layout="wide")

# Theme Colors
bg_beige = "#F5F5DC"
sidebar_beige = "#EFEFDB"
charcoal_navy = "#1e293b"
pink_highlight = "#FFC0CB"

st.markdown(f"""
    <style>
    /* Global Styles */
    .stApp {{
        background-color: {bg_beige};
    }}
    
    html, body, [class*="st-"], p, div {{
        color: {charcoal_navy} !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_beige} !important;
        border-right: 1px solid #cbd5e1;
    }}

    /* CUSTOM MENU BUTTONS (Replacing the broken radio) */
    .menu-item {{
        display: block;
        padding: 12px 20px;
        margin: 5px 0;
        color: {charcoal_navy};
        text-decoration: none;
        border-radius: 8px;
        transition: all 0.2s ease;
        font-weight: 500;
        background: none;
        border: none;
        width: 100%;
        text-align: left;
        cursor: pointer;
    }}

    .menu-item:hover {{
        background-color: rgba(30, 41, 59, 0.08);
        padding-left: 28px; /* The "Pop" effect */
        color: #000 !important;
    }}

    .active-menu {{
        background-color: {pink_highlight} !important;
        font-weight: 700 !important;
        color: #000 !important;
    }}

    /* Fix column overlap */
    div[data-testid="stColumn"] {{
        padding: 20px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📂 My-Task-Box")
    st.write("---")
    
    # Define our menu items
    menu_options = [
        "🏗️ Projects", "👥 Employees", "✅ Tasks", "📄 Licenses & Permits",
        "🏦 Bonds", "💰 Payroll", "👔 HR", "🔍 Exploration",
        "🏢 Commercial", "🏠 Residential"
    ]
    
    # Initialize page in session state
    if 'page' not in st.session_state:
        st.session_state.page = "🏗️ Projects"

    # Create the buttons manually for total control
    for option in menu_options:
        is_active = "active-menu" if st.session_state.page == option else ""
        if st.button(option, key=f"menu_{option}", use_container_width=True, help=f"Go to {option}"):
            st.session_state.page = option
            st.rerun()

# --- 4. NAVIGATION LOGIC ---
page = st.session_state.page

if 'active_project_id' not in st.session_state:
    st.session_state.active_project_id = None

if page == "🏗️ Projects":
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
                    if st.button("Open Details", key=f"p_{p[0]}"):
                        st.session_state.active_project_id = p[0]
                        st.rerun()
    else:
        # PROJECT DETAIL VIEW
        p_id = st.session_state.active_project_id
        p_data = c.execute('SELECT * FROM projects WHERE id = ?', (p_id,)).fetchone()
        
        st.title(f"📍 {p_data[1]}")
        col_left, col_right = st.columns([1, 1])
        with col_left:
            if st.button("⬅️ Back to Dashboard"):
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

elif page == "👥 Employees":
    st.title("Employee Directory")
    new_emp = st.text_input("Name")
    if st.button("Add"):
        c.execute('INSERT INTO employees (name) VALUES (?)', (new_emp,))
        conn.commit()
        st.rerun()
    emps = c.execute('SELECT name FROM employees').fetchall()
    for e in emps: st.write(f"• {e[0]}")

else:
    st.title(page)
    st.write(f"Section for {page} is under construction.")
