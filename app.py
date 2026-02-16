import streamlit as st
import sqlite3

# Database Setup (v5 for Phase/Progress columns)
conn = sqlite3.connect('tasks_v5.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT)')
c.execute('''CREATE TABLE IF NOT EXISTS projects 
             (id INTEGER PRIMARY KEY, name TEXT, lead TEXT, duration TEXT, 
              phase TEXT, progress INTEGER, details TEXT)''')
c.execute('CREATE TABLE IF NOT EXISTS project_chat (id INTEGER PRIMARY KEY, project_id INTEGER, user TEXT, msg TEXT)')
conn.commit()

st.set_page_config(page_title="My-Task-Box", page_icon="📦", layout="wide")

# --- FIXED CSS (No Overlapping) ---
st.markdown("""
    <style>
    html, body, [class*="st-"] {
        font-size: 13px;
        line-height: 1.6; /* Fixes the overlapping text */
    }
    h1 { font-size: 18px !important; padding-bottom: 10px; }
    h2 { font-size: 15px !important; margin-top: 20px; }
    .stChatFloatingInputContainer { bottom: 20px; }
    /* Make containers look like GitHub cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("📂 My-Task-Box")
    page = st.radio("Menu", ["Projects", "Employees", "Tasks"])

# --- SHARED STATE ---
if 'active_project_id' not in st.session_state:
    st.session_state.active_project_id = None

# --- PROJECTS PAGE ---
if page == "Projects":
    if st.session_state.active_project_id is None:
        st.title("🏗️ Projects")
        with st.expander("➕ Create New Project"):
            p_name = st.text_input("Project Name")
            p_dur = st.text_input("Estimated Duration")
            p_phase = st.text_input("Current Phase")
            p_prog = st.slider("Phase Progress %", 0, 100, 0)
            if st.button("Launch Project"):
                c.execute('INSERT INTO projects (name, duration, phase, progress) VALUES (?,?,?,?)', 
                          (p_name, p_dur, p_phase, p_prog))
                conn.commit()
                st.rerun()

        # Grid of Projects
        projs = c.execute('SELECT id, name, phase FROM projects').fetchall()
        cols = st.columns(4)
        for i, p in enumerate(projs):
            with cols[i % 4]:
                with st.container(border=True):
                    st.write(f"**{p[1]}**")
                    st.caption(f"Phase: {p[2]}")
                    if st.button("Open Project", key=f"open_{p[0]}"):
                        st.session_state.active_project_id = p[0]
                        st.rerun()
    
    else:
        # --- PROJECT DETAIL VIEW (The Vision) ---
        p_id = st.session_state.active_project_id
        p_data = c.execute('SELECT * FROM projects WHERE id = ?', (p_id,)).fetchone()
        
        col_left, col_right = st.columns([1, 1]) # Split Screen

        with col_left:
            if st.button("⬅️ Back to All Projects"):
                st.session_state.active_project_id = None
                st.rerun()
            
            st.title(f"Project: {p_data[1]}") # Top Left Name
            
            with st.container(border=True):
                st.subheader("📋 Job Details")
                st.write(f"⏱️ **Est. Duration:** {p_data[3]}")
                st.write(f"🏗️ **Current Phase:** {p_data[4]}")
                st.write(f"📈 **Phase Progress:** {p_data[5]}%")
                st.progress(p_data[5]/100)
                
                st.divider()
                st.write("**Next Phases:** TBD")
                st.write("**Employees Involved:** Admin")

        with col_right:
            st.subheader("💬 Project Chat")
            # Portrait Chat Box
            chat_container = st.container(height=400, border=True)
            
            # Show messages
            msgs = c.execute('SELECT user, msg FROM project_chat WHERE project_id = ?', (p_id,)).fetchall()
            for m in msgs:
                chat_container.write(f"**{m[0]}**: {m[1]}")
            
            # Send message
            chat_input = st.text_input("Type message...", key="chat_in")
            if st.button("Send"):
                if chat_input:
                    c.execute('INSERT INTO project_chat (project_id, user, msg) VALUES (?,?,?)', (p_id, "Admin", chat_input))
                    conn.commit()
                    st.rerun()

# --- EMPLOYEES PAGE (Simplified for now) ---
elif page == "Employees":
    st.title("👥 Employees")
    # ... previous employee code ...
