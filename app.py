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

# --- 2. PAGE CONFIG (Desktop-Wide) ---
st.set_page_config(page_title="My-Task-Box | Command Center", page_icon="📦", layout="wide")

# Initialize page state
if 'page' not in st.session_state:
    st.session_state.page = "🏗️ Projects"

# --- 3. THE "DESKTOP COMMAND" CSS ---
st.markdown("""
    <style>
    /* Global Styles */
    .stApp { background-color: #F5F5DC; }
    
    /* Charcoal Navy Blend & Modern Font Stack */
    html, body, [class*="st-"], p, div {
        color: #24292e !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }

    /* Sidebar - Fixed Desktop Width */
    [data-testid="stSidebar"] {
        background-color: #EFEFDB !important;
        border-right: 1px solid #d0d7de;
        min-width: 250px !important;
    }

    /* THE CLEAN SIDEBAR MENU */
    div.stButton > button {
        background-color: transparent !important;
        color: #24292e !important;
        border: none !important;
        text-align: left !important;
        padding: 12px 20px !important;
        width: 100% !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        transition: all 0.2s ease-in-out !important;
        display: block !important;
        border-radius: 0px !important;
    }

    /* Desktop Hover: Subtle Pop & Border-left */
    div.stButton > button:hover {
        background-color: rgba(30, 41, 59, 0.05) !important;
        padding-left: 30px !important;
        border-left: 4px solid #24292e !important;
    }

    /* --- THE PINK HIGHLIGHT (State-Locked) --- */
    /* This ensures that when a button is wrapped in our 'active-pill' div, it stays pink */
    .active-pill div.stButton > button {
        background-color: #FFC0CB !important; /* PINK */
        color: #000 !important;
        font-weight: 700 !important;
        border-left: 4px solid #000 !important;
    }

    /* Layout Spacing */
    .main-header { margin-bottom: 40px !important; }
    
    /* Card Container for Desktop Grid */
    .project-card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #d0d7de;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📂 My-Task-Box")
    st.write("---")
    
    menu_options = [
        "🏗️ Projects", "👥 Employees", "✅ Tasks", "📄 Licenses & Permits",
        "🏦 Bonds", "💰 Payroll", "👔 HR", "🔍 Exploration",
        "🏢 Commercial", "🏠 Residential"
    ]

    for option in menu_options:
        # Wrap the current active page in the 'active-pill' CSS class
        if st.session_state.page == option:
            st.markdown('<div class="active-pill">', unsafe_allow_html=True)
            st.button(option, key=f"active_{option}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            if st.button(option, key=f"nav_{option}"):
                st.session_state.page = option
                st.rerun()

# --- 5. MAIN CONTENT LOGIC ---
page = st.session_state.page
if 'active_project_id' not in st.session_state:
    st.session_state.active_project_id = None

if page == "🏗️ Projects":
    if st.session_state.active_project_id is None:
        st.title("Projects Command Center")
        
        with st.expander("➕ Register New Project"):
            c1, c2 = st.columns(2)
            with c1:
                p_name = st.text_input("Project Name")
                p_dur = st.text_input("Estimated Duration")
            with c2:
                p_phase = st.text_input("Current Phase")
                p_prog = st.slider("Initial Progress %", 0, 100, 0)
            if st.button("Initialize Project"):
                if p_name:
                    c.execute('INSERT INTO projects (name, duration, phase, progress) VALUES (?,?,?,?)', 
                              (p_name, p_dur, p_phase, p_prog))
                    conn.commit()
                    st.rerun()

        st.write("---")
        
        # Wide Desktop Grid (4 columns)
        projs = c.execute('SELECT id, name, phase, progress FROM projects').fetchall()
        cols = st.columns(4)
        for i, p in enumerate(projs):
            with cols[i % 4]:
                with st.container(border=True):
                    st.write(f"### {p[1]}")
                    st.caption(f"Status: {p[2]}")
                    st.progress(p[3]/100)
                    if st.button("Enter Dashboard", key=f"p_view_{p[0]}", use_container_width=True):
                        st.session_state.active_project_id = p[0]
                        st.rerun()
    else:
        # PROJECT DETAIL VIEW (FULL DESKTOP WORKSPACE)
        p_id = st.session_state.active_project_id
        p_data = c.execute('SELECT * FROM projects WHERE id = ?', (p_id,)).fetchone()
        
        st.title(f"📍 Project: {p_data[1]}")
        
        # 1:1 Split for maximum functional space
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            if st.button("⬅️ Return to Command Center"):
                st.session_state.active_project_id = None
                st.rerun()
            
            with st.container(border=True):
                st.subheader("📋 Core Job Details")
                st.write(f"⏱️ **Duration:** {p_data[2]}")
                st.write(f"🏗️ **Current Phase:** {p_data[3]}")
                st.write(f"📈 **Progress:** {p_data[4]}%")
                st.progress(p_data[4]/100)
                
                st.write("---")
                st.write("**Next Roadmap Milestones:**")
                st.caption("• Material Sourcing\n• Final Inspection")

        with col_right:
            st.subheader("💬 Active Communication")
            chat_box = st.container(height=500, border=True)
            msgs = c.execute('SELECT user, msg FROM project_chat WHERE project_id = ?', (p_id,)).fetchall()
            for m in msgs:
                chat_box.markdown(f"**{m[0]}**: {m[1]}")
            
            # Desktop-style chat input at the bottom
            c_in, c_btn = st.columns([4, 1])
            with c_in:
                chat_input = st.text_input("Message Team", label_visibility="collapsed", placeholder="Enter message...", key="msg_input")
            with c_btn:
                if st.button("Send", use_container_width=True):
                    if chat_input:
                        c.execute('INSERT INTO project_chat (project_id, user, msg) VALUES (?,?,?)', (p_id, "Admin", chat_input))
                        conn.commit()
                        st.rerun()

elif page == "👥 Employees":
    st.title("Human Capital Management")
    c1, c2 = st.columns([1, 2])
    with c1:
        new_emp = st.text_input("Register Name")
        if st.button("Add to Database"):
            c.execute('INSERT INTO employees (name) VALUES (?)', (new_emp,))
            conn.commit()
            st.rerun()
    with c2:
        st.write("### Active Personnel")
        emps = c.execute('SELECT name FROM employees').fetchall()
        for e in emps: st.info(f"👤 {e[0]}")

else:
    st.title(page)
    st.write(f"The **{page}** module is currently in standby mode.")
