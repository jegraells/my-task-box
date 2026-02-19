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

if 'page' not in st.session_state:
    st.session_state.page = "🏗️ Projects"

# --- 3. THE GITHUB-STYLE DESKTOP CSS ---
st.markdown("""
    <style>
    /* Global Background (Beige) */
    .stApp { background-color: #F5F5DC; }
    
    /* Charcoal Navy Blend & GitHub Font Stack */
    html, body, [class*="st-"], p, div {
        color: #24292e !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
        font-size: 14px;
    }

    /* --- THE ULTIMATE FIX FOR 'keyboard_double_arrow' --- */
    /* 1. Target the button containing the text */
    button[data-testid="sidebar-toggle"], 
    button[kind="headerNoPadding"] {
        background-color: transparent !important;
    }
    
    /* 2. Hide the actual text element inside the button */
    span[data-testid="stSidebarCollapseIcon"],
    button[kind="headerNoPadding"] div {
        font-size: 0px !important; /* Makes the text invisible */
    }

    /* 3. Add back a clean icon manually */
    span[data-testid="stSidebarCollapseIcon"]::after,
    button[kind="headerNoPadding"]::after {
        content: "≡"; /* Clean Hamburger menu icon */
        font-size: 22px !important;
        visibility: visible !important;
        color: #24292e !important;
        display: block;
    }

    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #EFEFDB !important;
        border-right: 1px solid #d0d7de;
        min-width: 260px !important;
    }

    /* KILL ALL DEFAULT BUTTON STYLING */
    div.stButton > button {
        background-color: transparent !important;
        color: #24292e !important;
        border: none !important;
        box-shadow: none !important;
        text-align: left !important;
        width: 100% !important;
        padding: 6px 12px !important;
        margin: 0 !important;
        border-radius: 6px !important;
        transition: background 0.1s ease-in-out !important;
        display: block !important;
    }

    div.stButton > button:hover {
        background-color: rgba(30, 41, 59, 0.08) !important;
        color: #000 !important;
    }

    /* THE PINK HIGHLIGHT (Active State) */
    .active-highlight {
        background-color: #FFC0CB !important;
        color: #000 !important;
        font-weight: 600 !important;
        padding: 6px 12px !important;
        border-radius: 6px !important;
        margin: 2px 0 !important;
        display: block !important;
    }

    [data-testid="stSidebarUserContent"] { padding-top: 1rem; }
    div[data-testid="stColumn"] { padding: 15px !important; }
    h1 { font-size: 22px !important; font-weight: 600 !important; }

    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("### 📦 My-Task-Box")
    st.write("") 
    
    menu_options = [
        ("🏗️ Projects", "🏗️ Projects"), ("👥 Employees", "👥 Employees"), 
        ("✅ Tasks", "✅ Tasks"), ("📄 Licenses & Permits", "📄 Licenses & Permits"),
        ("🏦 Bonds", "🏦 Bonds"), ("💰 Payroll", "💰 Payroll"), 
        ("👔 HR", "👔 HR"), ("🔍 Exploration", "🔍 Exploration"),
        ("🏢 Commercial", "🏢 Commercial"), ("🏠 Residential", "🏠 Residential")
    ]

    for label, name in menu_options:
        if st.session_state.page == name:
            st.markdown(f'<div class="active-highlight">{label}</div>', unsafe_allow_html=True)
        else:
            if st.button(label, key=f"nav_{name}"):
                st.session_state.page = name
                st.rerun()

# --- 5. MAIN CONTENT LOGIC ---
page = st.session_state.page
if 'active_project_id' not in st.session_state:
    st.session_state.active_project_id = None

if page == "🏗️ Projects":
    if st.session_state.active_project_id is None:
        st.title("Projects")
        with st.expander("➕ New Project"):
            p_name = st.text_input("Name")
            if st.button("Create"):
                if p_name:
                    c.execute('INSERT INTO projects (name, progress) VALUES (?,?)', (p_name, 0))
                    conn.commit()
                    st.rerun()
        projs = c.execute('SELECT id, name, progress FROM projects').fetchall()
        cols = st.columns(4) 
        for i, p in enumerate(projs):
            with cols[i % 4]:
                with st.container(border=True):
                    st.write(f"**{p[1]}**")
                    if st.button("Open", key=f"v_{p[0]}", use_container_width=True):
                        st.session_state.active_project_id = p[0]
                        st.rerun()
    else:
        # Detail view
        p_id = st.session_state.active_project_id
        p_data = c.execute('SELECT * FROM projects WHERE id = ?', (p_id,)).fetchone()
        st.title(f"📍 {p_data[1]}")
        if st.button("⬅️ Back"):
            st.session_state.active_project_id = None
            st.rerun()

elif page == "👥 Employees":
    st.title("Employees")
    emps = c.execute('SELECT name FROM employees').fetchall()
    for e in emps: st.write(f"• {e[0]}")

else:
    st.title(page)
    st.info(f"The {page} dashboard is ready.")
