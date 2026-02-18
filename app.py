import streamlit as st
import sqlite3

# --- 1. DATABASE SETUP (v6) ---
conn = sqlite3.connect('tasks_v6.db', check_same_thread=False)
c = conn.cursor()

# Create tables for the new features
c.execute('CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT)')
c.execute('''CREATE TABLE IF NOT EXISTS projects 
             (id INTEGER PRIMARY KEY, name TEXT, duration TEXT, 
              phase TEXT, progress INTEGER, details TEXT)''')
c.execute('CREATE TABLE IF NOT EXISTS project_chat 
             (id INTEGER PRIMARY KEY, project_id INTEGER, user TEXT, msg TEXT)')
conn.commit()

# --- 2. PAGE CONFIG & STYLE ---
st.set_page_config(page_title="My-Task-Box", page_icon="📦", layout="wide")

# CSS to fix overlapping, shrink fonts, and create the "GitHub" look
st.markdown("""
    <style>
    /* Base Font Size & Line Height */
    html, body, [class*="st-"] {
        font-size: 13px;
        line-height: 1.6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }
    
    /* Title Adjustments (Slightly larger by ~2pts) */
    h1 { font-size: 18px !important; font-weight: 600 !important; padding-bottom: 10px; }
    h2 { font-size: 15px !important; font-weight: 600 !important; }
    h3 { font-size: 13px !important; font-weight: 600 !important; }
    
    /* Column Spacing to prevent overlap */
    div[data-testid="stColumn"] { 
        padding: 15px; 
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f6f8fa;
        border-right: 1px solid #d0d7de;
    }
    
    /* Card Container Look */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #d0d7de !important;
        border-radius: 6px !important;
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📂 My-Task-Box")
    page = st.radio("Menu", [
        "🏗️ Projects", 
        "👥 Employees", 
        "✅ Tasks",
        "📄 Licenses & Permits",
        "🏦 Bonds",
        "💰 Payroll",
        "👔 HR",
        "🔍 Exploration",
        "🏢 Commercial",
        "🏠 Residential"
    ])
    st.divider()
    st.caption("Admin Mode")

# Session State for navigation within Projects
if 'active_project_id' not in st.session_state:
    st.session_state.active_project_id = None

# --- 4. NAVIGATION LOGIC ---

# PROJECTS PAGE
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

        st.divider()
        
        # Display Project Cards
        projs = c.execute('SELECT id, name, phase, progress FROM projects').fetchall()
        if not projs:
            st.info("No projects yet. Create one above!")
        else:
            cols = st.columns(4)
            for i, p in enumerate(projs):
                with cols[i % 4]:
                    with st.container(border=True):
                        st.write(f"**{p[1]}**")
                        st.caption(f"Phase: {p[2]}")
                        st.progress(p[3]/100)
                        if st.button("Open Details", key=f"p_{p[0]}"):
                            st.session_state.active_project_id = p[0]
                            st.rerun()

    else:
        # PROJECT DETAIL VIEW (The Vision)
        p_id = st.session_state.active_project_id
        p_data = c.execute('SELECT * FROM projects WHERE id = ?', (p_id,)).fetchone()
        
        # Top Header
        st.title(f"📍 Project: {p_data[1]}")
        
        col_left, col_right = st.columns([1, 1]) # Split Screen

        with col_left:
            if st.button("⬅️ Back to Dashboard"):
                st.session_state.active_project_id = None
                st.rerun()
            
            with st.container(border=True):
                st.subheader("📋 Job Details")
                st.write(f"⏱️ **Est. Duration:** {p_data[2]}")
                st.write(f"🏗️ **Current Phase:** {p_data[3]}")
                st.write(f"📈 **Phase Progress:** {p_data[4]}%")
                st.progress(p_data[4]/100)
                
                st.divider()
                st.write("**Next Phases:** TBD")
                st.write("**Employees Involved:** Admin")
                
                if st.button("🗑️ Delete Project", type="secondary"):
                    c.execute('DELETE FROM projects WHERE id = ?', (p_id,))
                    conn.commit()
                    st.session_state.active_project_id = None
                    st.rerun()

        with col_right:
            st.subheader("💬 Project Chat")
            # Portrait Chat Box
            chat_box = st.container(height=450, border=True)
            
            # Show messages from database
            msgs = c.execute('SELECT user, msg FROM project_chat WHERE project_id = ?', (p_id,)).fetchall()
            for m in msgs:
                chat_box.write(f"**{m[0]}**: {m[1]}")
            
            # Chat input
            chat_input = st.text_input("New Message", placeholder="Type here...", key="msg_input")
            if st.button("Send Message"):
                if chat_input:
                    c.execute('INSERT INTO project_chat (project_id, user, msg) VALUES (?,?,?)', 
                              (p_id, "Admin", chat_input))
                    conn.commit()
                    st.rerun()

# EMPLOYEES PAGE
elif page == "👥 Employees":
    st.title("Employee Directory")
    new_emp = st.text_input("Add Employee Name")
    if st.button("Add Employee"):
        if new_emp:
            c.execute('INSERT INTO employees (name) VALUES (?)', (new_emp,))
            conn.commit()
            st.rerun()
    
    st.write("### Active Team")
    emps = c.execute('SELECT name FROM employees').fetchall()
    for e in emps:
        st.write(f"• {e[0]}")

# PLACEHOLDERS FOR NEW SECTIONS
else:
    st.title(page)
    st.info(f"The **{page}** module is ready for integration.")
    st.write("This section will be linked to your main database to track specific documents and data.")
