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

# Initialize page state
if 'page' not in st.session_state:
    st.session_state.page = "🏗️ Projects"

# --- 3. THE GITHUB-STYLE DESKTOP CSS ---
st.markdown("""
    <style>
    /* Global Background (Beige) */
    .stApp { background-color: #F5F5DC; }
    
    /* GitHub Font Stack & Charcoal Navy */
    html, body, [class*="st-"], p, div {
        color: #24292e !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
        font-size: 14px;
    }

    /* Sidebar - Desktop Compact */
    [data-testid="stSidebar"] {
        background-color: #EFEFDB !important;
        border-right: 1px solid #d0d7de;
        min-width: 260px !important;
    }

    /* THE MENU ITEM STYLING (GitHub NavList Style) */
    .nav-item {
        display: flex;
        align-items: center;
        padding: 6px 12px; /* Close together */
        margin: 2px 8px;
        text-decoration: none;
        color: #24292e !important;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.1s ease;
    }

    /* Hover: Slight highlight, no move */
    .nav-item:hover {
        background-color: rgba(209, 213, 218, 0.4);
    }

    /* ACTIVE STATE: Pink Highlight */
    .nav-item-active {
        background-color: #FFC0CB !important; /* PINK */
        color: #000 !important;
        font-weight: 600;
    }

    /* Remove default Streamlit padding at top of sidebar */
    [data-testid="stSidebarUserContent"] {
        padding-top: 1rem;
    }

    /* UI Containers */
    div[data-testid="stColumn"] { padding: 15px !important; }
    
    /* Main Content Headers */
    h1 { font-size: 20px !important; font-weight: 600 !important; color: #1b1f23; }
    h3 { font-size: 16px !important; font-weight: 600 !important; }

    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📂 My-Task-Box")
    st.write("") # Spacer
    
    menu_options = [
        ("🏗️ Projects", "🏗️ Projects"),
        ("👥 Employees", "👥 Employees"),
        ("✅ Tasks", "✅ Tasks"),
        ("📄 Licenses & Permits", "📄 Licenses & Permits"),
        ("🏦 Bonds", "🏦 Bonds"),
        ("💰 Payroll", "💰 Payroll"),
        ("👔 HR", "👔 HR"),
        ("🔍 Exploration", "🔍 Exploration"),
        ("🏢 Commercial", "🏢 Commercial"),
        ("🏠 Residential", "🏠 Residential")
    ]

    # Render each menu item using a button styled to look like a GitHub NavLink
    for label, name in menu_options:
        is_active = st.session_state.page == name
        
        # We use a container to wrap the button so we can apply the Pink class
        button_type = "secondary" # Base style
        
        # Custom logic to force the highlight via a CSS wrapper
        if is_active:
            st.markdown(f'<div class="nav-item nav-item-active">{label}</div>', unsafe_allow_html=True)
        else:
            # If user clicks the button, update session state
            if st.button(label, key=f"nav_{name}", use_container_width=True):
                st.session_state.page = name
                st.rerun()

# --- 5. MAIN CONTENT LOGIC ---
page = st.session_state.page
if 'active_project_id' not in st.session_state:
    st.session_state.active_project_id = None

if page == "🏗️ Projects":
    if st.session_state.active_project_id is None:
        st.title("Projects")
        with st.expander("➕ Create Project"):
            p_name = st.text_input("Name")
            p_dur = st.text_input("Duration")
            p_phase = st.text_input("Phase")
            p_prog = st.slider("Progress %", 0, 100, 0)
            if st.button("Save"):
                if p_name:
                    c.execute('INSERT INTO projects (name, duration, phase, progress) VALUES (?,?,?,?)', 
                              (p_name, p_dur, p_phase, p_prog))
                    conn.commit()
                    st.rerun()

        st.divider()
        projs = c.execute('SELECT id, name, phase, progress FROM projects').fetchall()
        cols = st.columns(4) # Desktop Grid
        for i, p in enumerate(projs):
            with cols[i % 4]:
                with st.container(border=True):
                    st.write(f"**{p[1]}**")
                    st.caption(f"Phase: {p[2]}")
                    st.progress(p[3]/100)
                    if st.button("Open", key=f"v_{p[0]}", use_container_width=True):
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
            st.subheader("Details")
            st.write(f"Duration: {p_data[2]}")
            st.write(f"Phase: {p_data[3]}")
            st.progress(p_data[4]/100)
        
        with col_right:
            st.subheader("Chat")
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
    st.title("Employees")
    new_emp = st.text_input("Register Personnel")
    if st.button("Add"):
        c.execute('INSERT INTO employees (name) VALUES (?)', (new_emp,))
        conn.commit()
        st.rerun()
    emps = c.execute('SELECT name FROM employees').fetchall()
    for e in emps: st.write(f"• {e[0]}")

else:
    st.title(page)
    st.info(f"The {page} dashboard is ready for desktop data entry.")
